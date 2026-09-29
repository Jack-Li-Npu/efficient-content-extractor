from unittest.mock import MagicMock

import pytest
import requests
from fastapi.testclient import TestClient

import main
from app import transcript_service as service

VIDEO = "Hrbq66XqtCo"
URL = f"https://www.youtube.com/watch?v={VIDEO}"


def formats(language="en", translated=False):
    return [
        {
            "ext": "json3",
            "name": language,
            "url": f"https://www.youtube.com/api/timedtext?lang={language}" + ("&tlang=es" if translated else ""),
        }
    ]


@pytest.fixture
def metadata(monkeypatch):
    info = {
        "id": VIDEO,
        "title": "A talk",
        "duration": 6192,
        "language": "en",
        "subtitles": {"en": formats(), "fr": formats("fr")},
        "automatic_captions": {"en-orig": formats(), "es-en": formats("en", True)},
    }
    monkeypatch.setattr(service, "_metadata", lambda _video: info)
    return info


@pytest.fixture
def client():
    return TestClient(main.app, base_url="http://127.0.0.1:8000")


@pytest.mark.parametrize(
    "value",
    [
        VIDEO,
        URL,
        f"https://youtu.be/{VIDEO}?si=123",
        f"https://m.youtube.com/watch?list=123&v={VIDEO}&t=10",
        *[f"https://www.youtube.com/{kind}/{VIDEO}" for kind in ("shorts", "embed", "live", "v")],
        f"https://www.youtube-nocookie.com/embed/{VIDEO}",
    ],
)
def test_video_urls(value):
    assert service.extract_video_id(value) == VIDEO


@pytest.mark.parametrize(
    "value",
    [
        "",
        "https://youtube.com.evil.test/watch?v=" + VIDEO,
        "https://evil.test/youtube.com/watch?v=" + VIDEO,
        "file:///etc/passwd",
        "https://youtube.com/playlist?list=123",
        "https://youtube.com/@channel",
        "https://user:password@youtube.com/watch?v=" + VIDEO,
        "https://youtube.com/watch?v=bad",
        "https://youtu.be/" + VIDEO + "/extra",
        "https://[broken",
    ],
)
def test_rejects_invalid_urls(value):
    with pytest.raises(service.ExtractionError) as exc:
        service.extract_video_id(value)
    assert exc.value.code == "invalid_url"


def test_inspection_prefers_uploaded_original_and_excludes_translation(metadata):
    result = service.get_video_info(URL)
    assert result["recommended_track_id"] == "uploaded:en"
    assert [track["id"] for track in result["tracks"]] == ["uploaded:en", "uploaded:fr", "automatic:en-orig"]
    assert all("formats" not in track for track in result["tracks"])


def test_unknown_original_requires_choice(metadata):
    metadata["language"] = None
    assert service.get_video_info(URL)["recommended_track_id"] is None


def test_automatic_original_when_no_uploaded(metadata):
    metadata["subtitles"] = {}
    assert service.get_video_info(URL)["recommended_track_id"] == "automatic:en-orig"


def test_selected_language_and_source_reach_primary(metadata, monkeypatch):
    primary = MagicMock(return_value=[service.TranscriptSegment(0.48, 4.123, "Bonjour 世界")])
    monkeypatch.setattr(service, "_primary", primary)
    result = service.fetch_selected(URL, "uploaded:fr")
    assert primary.call_args.args[1]["language"] == "fr"
    assert primary.call_args.args[1]["source"] == "uploaded"
    assert result["language"] == "fr"
    assert result["provider"] == "youtube-transcript-api"


def test_library_uses_selected_track_without_translation(monkeypatch):
    api = MagicMock()
    finder = api.list.return_value.find_generated_transcript
    finder.return_value.fetch.return_value = [service.TranscriptSegment(0, 1.5, "Hi")]
    monkeypatch.setattr(service, "YouTubeTranscriptApi", MagicMock(return_value=api))
    result = service._primary(VIDEO, {"language": "en", "source": "automatic"})
    finder.assert_called_once_with(["en"])
    api.list.return_value.find_manually_created_transcript.assert_not_called()
    assert result[0].duration == 1.5


@pytest.mark.parametrize("primary_result", ["failure", "empty"])
def test_caption_only_fallback(metadata, monkeypatch, primary_result):
    primary = (
        MagicMock(side_effect=requests.ConnectionError("blocked"))
        if primary_result == "failure"
        else MagicMock(return_value=[])
    )
    fallback = MagicMock(return_value=[service.TranscriptSegment(0, 2, "Complete caption")])
    monkeypatch.setattr(service, "_primary", primary)
    monkeypatch.setattr(service, "_fallback", fallback)
    result = service.fetch_selected(URL, "uploaded:en")
    assert result["provider"] == "yt-dlp"
    assert fallback.call_args.args[1]["id"] == "uploaded:en"


def test_both_providers_fail_explicitly(metadata, monkeypatch, client):
    monkeypatch.setattr(service, "_primary", MagicMock(side_effect=requests.ConnectionError("blocked")))
    monkeypatch.setattr(
        service, "_fallback", MagicMock(side_effect=service.ExtractionError("request_blocked", "Try again later."))
    )
    response = client.post("/api/extract", json={"url": URL, "track_id": "uploaded:en"})
    assert response.status_code == 502
    assert response.json()["success"] is False
    assert response.json()["code"] == "request_blocked"


def test_empty_captions_never_succeed(metadata, monkeypatch, client):
    monkeypatch.setattr(service, "_primary", MagicMock(return_value=[]))
    monkeypatch.setattr(service, "_fallback", MagicMock(return_value=[]))
    response = client.post("/api/extract", json={"url": URL, "track_id": "uploaded:en"})
    assert response.status_code == 422
    assert response.json()["code"] == "empty_captions"


def test_missing_track_and_missing_captions(metadata, client):
    assert (
        client.post("/api/extract", json={"url": URL, "track_id": "uploaded:missing"}).json()["code"]
        == "track_unavailable"
    )
    metadata["subtitles"] = {}
    metadata["automatic_captions"] = {}
    assert client.post("/api/extract", json={"url": URL, "track_id": "uploaded:en"}).json()["code"] == "no_captions"


def test_metadata_does_not_extract(metadata, monkeypatch, client):
    primary = MagicMock(side_effect=AssertionError("inspection must not fetch captions"))
    monkeypatch.setattr(service, "_primary", primary)
    response = client.post("/api/video-info", json={"url": URL})
    assert response.status_code == 200
    assert "transcript" not in response.json()
    primary.assert_not_called()


def test_text_and_fractional_timing_preserved(metadata, monkeypatch, client):
    segments = [
        service.TranscriptSegment(0, 1.234, "First <text> & 世界"),
        service.TranscriptSegment(3601.125, 4.375, "Last\ncaption"),
    ]
    monkeypatch.setattr(service, "_primary", MagicMock(return_value=segments))
    response = client.post("/api/extract", json={"url": URL, "track_id": "uploaded:en"})
    result = response.json()
    assert result["plain_text"] == "First <text> & 世界\nLast\ncaption"
    assert result["transcript_lines"][-1]["start"] == 3601.125
    assert result["transcript_lines"][-1]["duration"] == 4.375
    assert result["transcript_lines"][-1]["timestamp"] == "01:00:01"


def test_json3_preserves_repetitions_and_skips_non_text_events():
    data = {
        "events": [
            {"tStartMs": 0, "dDurationMs": 1234, "segs": [{"utf8": "Yes, "}, {"utf8": "yes."}]},
            {"tStartMs": 1234, "dDurationMs": 2345, "segs": [{"utf8": "Yes, yes."}]},
            {"segs": [{"utf8": "\n"}]},
        ]
    }
    result = service.parse_json3(data)
    assert [segment.text for segment in result] == ["Yes, yes.", "Yes, yes."]
    assert result[-1].start == 1.234
    assert result[-1].duration == 2.345


def test_json3_rejects_missing_timing():
    with pytest.raises(service.ExtractionError):
        service.parse_json3({"events": [{"segs": [{"utf8": "Caption"}]}]})


def test_no_media_cookies_or_model_options(monkeypatch):
    factory = MagicMock()
    monkeypatch.setattr(service, "YoutubeDL", factory)
    service.downloader()
    config = factory.call_args.args[0]
    assert config["skip_download"] and config["noplaylist"]
    assert config["cachedir"] is False
    assert config["writesubtitles"] is False
    assert config["writeautomaticsub"] is False
    assert not any(key in config for key in ("cookiefile", "cookiesfrombrowser", "postprocessors", "outtmpl"))


@pytest.mark.parametrize(
    "message,code,status",
    [
        ("Sign in to confirm you are not a bot", "request_blocked", 502),
        ("HTTP Error 429", "request_blocked", 502),
        ("Private video", "video_unavailable", 404),
        ("Connection timed out", "connection_failed", 502),
    ],
)
def test_provider_errors(message, code, status):
    error = service.provider_error(Exception(message))
    assert error.code == code and error.status == status


def test_removed_ai_routes_and_local_origin(client):
    for path in ("/api/analyze", "/api/summary"):
        assert client.post(path, json={}).status_code in (404, 405)
    assert (
        client.post("/api/video-info", json={"url": URL}, headers={"Origin": "https://untrusted.example"}).status_code
        == 403
    )
    assert client.get("/health", headers={"Host": "untrusted.example"}).status_code == 400


def test_duplicate_automatic_language_prefers_original_track(metadata):
    metadata["automatic_captions"]["en"] = formats()
    tracks = service.get_video_info(URL)["tracks"]
    assert [track["id"] for track in tracks if track["source"] == "automatic"] == ["automatic:en-orig"]


def test_fallback_only_requests_selected_caption_document(metadata, monkeypatch):
    import json

    response = MagicMock()
    response.read.return_value = json.dumps(
        {"events": [{"tStartMs": 3601125, "dDurationMs": 2345, "segs": [{"utf8": "Bonjour 世界"}]}]}
    ).encode()
    ydl = MagicMock()
    ydl.urlopen.return_value.__enter__.return_value = response
    factory = MagicMock()
    factory.return_value.__enter__.return_value = ydl
    monkeypatch.setattr(service, "downloader", factory)
    track = next(track for track in service._tracks(metadata) if track["id"] == "uploaded:fr")
    result = service._fallback(metadata, track)
    assert ydl.urlopen.call_args.args[0].url == track["formats"][0]["url"]
    ydl.extract_info.assert_not_called()
    ydl.download.assert_not_called()
    assert result == [service.TranscriptSegment(3601.125, 2.345, "Bonjour 世界")]
