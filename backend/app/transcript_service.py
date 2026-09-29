"""Caption-only extraction. Metadata and signed URLs stay briefly in memory."""

from __future__ import annotations

import json
import math
import os
import re
import time
from collections import OrderedDict
from dataclasses import dataclass
from threading import Lock
from urllib.parse import parse_qs, urlparse
from xml.etree.ElementTree import ParseError

import requests
from youtube_transcript_api import YouTubeTranscriptApi, YouTubeTranscriptApiException
from youtube_transcript_api.proxies import GenericProxyConfig
from yt_dlp import YoutubeDL
from yt_dlp.networking import Request


class ExtractionError(Exception):
    def __init__(self, code: str, message: str, status: int = 502):
        super().__init__(message)
        self.code = code
        self.status = status


@dataclass(frozen=True)
class TranscriptSegment:
    start: float
    duration: float
    text: str


def extract_video_id(value: str) -> str:
    value = value.strip()
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", value):
        return value
    try:
        parsed = urlparse(value)
    except ValueError as exc:
        raise ExtractionError("invalid_url", "Enter a valid YouTube video link.", 400) from exc
    if parsed.scheme not in ("http", "https") or parsed.username or parsed.password:
        raise ExtractionError("invalid_url", "Enter a valid YouTube video link.", 400)
    host = (parsed.hostname or "").lower()
    parts = parsed.path.strip("/").split("/")
    video_id = ""
    if host == "youtu.be" and len(parts) == 1:
        video_id = parts[0]
    elif host in ("youtube.com", "www.youtube.com", "m.youtube.com", "www.youtube-nocookie.com"):
        if parsed.path == "/watch":
            video_id = parse_qs(parsed.query).get("v", [""])[0]
        elif len(parts) == 2 and parts[0] in ("shorts", "embed", "live", "v"):
            video_id = parts[1]
    if not re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id):
        raise ExtractionError("invalid_url", "Enter a YouTube link to one video, not a channel or playlist.", 400)
    return video_id


def get_proxy_url() -> str | None:
    return next(
        (os.environ[key] for key in ("YT_PROXY", "HTTPS_PROXY", "HTTP_PROXY", "SOCKS5_PROXY") if os.environ.get(key)),
        None,
    )


class QuietLogger:
    # External diagnostics can contain signed URLs and proxy credentials.
    def debug(self, _message):
        pass

    def warning(self, _message):
        pass

    def error(self, _message):
        pass


def downloader() -> YoutubeDL:
    return YoutubeDL(
        {
            "skip_download": True,
            "noplaylist": True,
            "cachedir": False,
            "quiet": True,
            "no_warnings": True,
            "logger": QuietLogger(),
            "proxy": get_proxy_url() or "",
            "socket_timeout": 15,
            "retries": 1,
            "extractor_retries": 1,
            "js_runtimes": {"node": {}},
            "writesubtitles": False,
            "writeautomaticsub": False,
        }
    )


def provider_error(exc: Exception) -> ExtractionError:
    description = f"{type(exc).__name__} {exc}".lower()
    if any(
        word in description for word in ("requestblocked", "ipblocked", "429", "403", "not a bot", "sign in to confirm")
    ):
        return ExtractionError(
            "request_blocked", "YouTube blocked this request. Try again later or check your proxy connection."
        )
    if any(
        word in description
        for word in (
            "private video",
            "video unavailable",
            "videounavailable",
            "removed",
            "members-only",
            "age-restricted",
            "login required",
            "not available in your country",
        )
    ):
        return ExtractionError(
            "video_unavailable", "This video is unavailable or requires sign-in. Try a public video.", 404
        )
    if any(
        word in description
        for word in ("timeout", "timed out", "connection", "proxyerror", "unable to download", "network", "ssl")
    ):
        return ExtractionError(
            "connection_failed", "Could not connect to YouTube. Check your network and YT_PROXY setting, then retry."
        )
    return ExtractionError(
        "retrieval_failed", "YouTube caption retrieval failed. Retry, or update the extraction dependencies."
    )


_cache: OrderedDict[tuple, tuple[float, dict]] = OrderedDict()
_cache_lock = Lock()


def _metadata(video_id: str) -> dict:
    key = (video_id, get_proxy_url())
    with _cache_lock:
        cached = _cache.get(key)
        if cached and time.monotonic() - cached[0] < 300:
            _cache.move_to_end(key)
            return cached[1]
    try:
        with downloader() as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
    except Exception as exc:
        raise provider_error(exc) from exc
    if not info or info.get("_type") in ("playlist", "multi_video"):
        raise ExtractionError("video_unavailable", "Could not load this video. Try a public video.", 404)
    if info.get("is_live"):
        raise ExtractionError("live_video", "This video is still live. Try again after the broadcast ends.", 400)
    with _cache_lock:
        _cache[key] = (time.monotonic(), info)
        _cache.move_to_end(key)
        while len(_cache) > 8:
            _cache.popitem(last=False)
    return info


def _tracks(info: dict) -> list[dict]:
    tracks = []
    seen = set()
    for key, source in (("subtitles", "uploaded"), ("automatic_captions", "automatic")):
        # yt-dlp can expose the same automatic language under both en and en-orig.
        available = sorted((info.get(key) or {}).items(), key=lambda item: not item[0].endswith("-orig"))
        for code, formats in available:
            native = [
                item for item in formats if item.get("url") and "tlang" not in parse_qs(urlparse(item["url"]).query)
            ]
            if not native or code == "live_chat":
                continue
            language = code.removesuffix("-orig")
            identity = (source, language)
            if identity in seen:
                continue
            seen.add(identity)
            tracks.append(
                {
                    "id": f"{source}:{code}",
                    "language": language,
                    "name": native[0].get("name") or language,
                    "source": source,
                    "formats": native,
                }
            )
    return tracks


def get_video_info(value: str) -> dict:
    video_id = extract_video_id(value)
    info = _metadata(video_id)
    tracks = _tracks(info)
    original = info.get("language")
    candidates = [track for track in tracks if original and track["language"].lower() == original.lower()]
    if not candidates and original:
        candidates = [
            track for track in tracks if track["language"].split("-")[0].lower() == original.split("-")[0].lower()
        ]
    return {
        "video_id": video_id,
        "title": info.get("title") or f"YouTube video {video_id}",
        "channel": info.get("uploader") or info.get("channel") or "",
        "duration": info.get("duration"),
        "original_language": original,
        "tracks": [{k: v for k, v in track.items() if k != "formats"} for track in tracks],
        "recommended_track_id": candidates[0]["id"] if candidates else None,
    }


class TimeoutSession(requests.Session):
    def request(self, *args, **kwargs):
        kwargs.setdefault("timeout", (10, 20))
        return super().request(*args, **kwargs)


def _primary(video_id: str, track: dict) -> list[TranscriptSegment]:
    proxy = get_proxy_url()
    config = GenericProxyConfig(http_url=proxy, https_url=proxy) if proxy else None
    with TimeoutSession() as session:
        session.trust_env = False
        api = YouTubeTranscriptApi(proxy_config=config, http_client=session)
        available = api.list(video_id)
        finder = (
            available.find_manually_created_transcript
            if track["source"] == "uploaded"
            else available.find_generated_transcript
        )
        transcript = finder([track["language"]]).fetch()
        return [TranscriptSegment(item.start, item.duration, item.text) for item in transcript]


def parse_json3(data: dict) -> list[TranscriptSegment]:
    segments = []
    for event in data.get("events", []):
        text = "".join(segment.get("utf8", "") for segment in event.get("segs", []))
        if not text.strip():
            continue
        if "tStartMs" not in event or "dDurationMs" not in event:
            raise ExtractionError("invalid_captions", "YouTube returned captions without timing. Retry the extraction.")
        segments.append(TranscriptSegment(event["tStartMs"] / 1000, event["dDurationMs"] / 1000, text))
    return segments


def _fallback(info: dict, track: dict) -> list[TranscriptSegment]:
    selected = next((item for item in track["formats"] if item.get("ext") == "json3"), None)
    if selected is None:
        raise ExtractionError("unsupported_captions", "This caption format is not supported. Try another track.", 422)
    try:
        with downloader() as ydl:
            request = Request(selected["url"], headers=info.get("http_headers") or {})
            with ydl.urlopen(request) as response:
                raw = response.read(20 * 1024 * 1024 + 1)
        if not raw or len(raw) > 20 * 1024 * 1024:
            raise ExtractionError(
                "invalid_captions", "YouTube returned empty or oversized captions. Retry the extraction."
            )
        return parse_json3(json.loads(raw))
    except ExtractionError:
        raise
    except Exception as exc:
        raise provider_error(exc) from exc


def _validate_segments(segments: list[TranscriptSegment]) -> list[TranscriptSegment]:
    result = [segment for segment in segments if segment.text.strip()]
    if not result:
        raise ExtractionError("empty_captions", "The selected caption track is empty. Try another track.", 422)
    for segment in result:
        if not all(math.isfinite(value) and value >= 0 for value in (segment.start, segment.duration)):
            raise ExtractionError("invalid_captions", "YouTube returned invalid caption timing. Retry the extraction.")
    return result


def fetch_selected(value: str, track_id: str) -> dict:
    video_id = extract_video_id(value)
    info = _metadata(video_id)
    tracks = _tracks(info)
    if not tracks:
        raise ExtractionError("no_captions", "This video has no retrievable captions. Try a video with subtitles.", 404)
    track = next((item for item in tracks if item["id"] == track_id), None)
    if track is None:
        raise ExtractionError(
            "track_unavailable", "This caption track is no longer available. Check the video again.", 404
        )
    provider = "youtube-transcript-api"
    try:
        segments = _validate_segments(_primary(video_id, track))
    except (YouTubeTranscriptApiException, requests.RequestException, ExtractionError, ValueError, ParseError):
        provider = "yt-dlp"
        segments = _validate_segments(_fallback(info, track))
    return {
        "segments": segments,
        "provider": provider,
        "language": track["language"],
        "source": track["source"],
        "video_id": video_id,
        "title": info.get("title") or video_id,
    }
