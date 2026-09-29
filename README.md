# Efficient Content Extractor

Turn a long video into a complete, timestamped transcript that an AI assistant can use to explain the key points and help you decide what to watch.

The current app runs locally, retrieves **existing YouTube captions**, and prepares a single Markdown file for a separate Codex chat. It preserves the original words and caption timings so the resulting brief can link back to the relevant moments.

**Built on [samueladegoke/yt-transcript-web](https://github.com/samueladegoke/yt-transcript-web)**, adapted from commit [`4928098`](https://github.com/samueladegoke/yt-transcript-web/commit/4928098ffe109df932a8f4bae47f31ebcf314a10). The original MIT license and copyright are retained. See [Attribution](#attribution) and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for the sources and technologies used.

## Purpose and workflow

Watching every minute of a long interview, lecture, or news program is often unnecessary when you first need an overview or one specific explanation. This project separates source collection from analysis:

1. Paste a YouTube video URL into the local web app.
2. Retrieve its existing original-language captions and inspect or search the transcript.
3. **Download for Codex** saves one complete `.transcript.md` file. **Copy for Codex** copies the same document with a prepared prompt.
4. Give the file or copied text to Codex with the included **video-brief** skill.
5. Read the overview and key points, then follow timestamp links to the passages worth watching.

The web app does not call an AI service or upload transcripts automatically. The user chooses when and where to submit the text for analysis. The skill is optional; the Markdown source also works with other assistants.

## Demo: from captions to a timestamped brief

These two screenshots show the same Bloomberg Tech video moving through the workflow.

**1. Extract and hand off the transcript.** The local app retrieves 685 caption segments and prepares the complete timestamped Markdown document. Use **Download for Codex** or **Copy for Codex** to bring it into your own chat.

![Local transcript app showing the selected English caption track, 685 segments, and download and copy controls](docs/screenshots/transcript-extraction.png)

**2. Read the brief and choose what to watch.** In a separate Codex chat, the `video-brief` skill guides an overview and key points with clickable YouTube timestamps. The screenshot shows the brief beside the exported source document; analysis happens in Codex, outside the web app.

![Codex showing a video overview and key points with clickable timestamps beside the source transcript](docs/screenshots/codex-timestamped-brief.png)

Example video: *Anthropic Goes Big on Compute, Microsoft Rethinks AI* by Bloomberg Tech. Video imagery and caption excerpts belong to their respective owners; the screenshots illustrate the workflow.

## What works today

- Public individual YouTube videos with accessible uploaded or automatic captions.
- Original-language uploaded captions preferred, automatic captions as a fallback choice; explicit selection when the original language cannot be determined.
- Video metadata, caption-track selection, full-text search, and permanent timestamps.
- One Markdown handoff containing every retrieved segment, exact millisecond start/end times, and source metadata.
- Full-transcript copy/download even while the display is filtered by search.
- `youtube-transcript-api` as the primary caption provider; `yt-dlp` for metadata and a caption-only fallback for the selected track.
- A reusable [video-brief skill](skills/video-brief/SKILL.md) for overviews, source-linked key points, uncertainty notes, and selective watch lists.

There is no audio/video download, speech recognition, translation, model download, transcript history, or AI API key requirement in the web app.

| Capability | Status |
| --- | --- |
| YouTube caption extraction and Codex handoff | Available |
| TikTok, Douyin, and Bilibili adapters | Planned; not implemented |
| Browser extension beside the video player | Planned; not implemented |
| Click a takeaway to seek the current player | Planned; current briefs use timestamp links |

See [ROADMAP.md](ROADMAP.md) for the planned platform and extension work.

## Quick start

The launcher is designed for macOS. Install [uv](https://docs.astral.sh/uv/getting-started/installation/) and Node.js 22.12+ with npm, then run:

```bash
git clone https://github.com/Jack-Li-Npu/efficient-content-extractor.git
cd efficient-content-extractor
./setup.sh
./start.command
```

Open **http://127.0.0.1:8000**. Keep the terminal open while using the app; press Control-C to stop it. On subsequent macOS runs, you can double-click `start.command` in Finder.

Setup creates an isolated Python environment in `backend/.venv`, installs backend dependencies from `backend/uv.lock`, installs frontend dependencies with `npm ci`, and builds React for FastAPI to serve. Setup copies `.env.example` to `.env` only when `.env` does not already exist. Run setup again after changing dependencies or frontend code.

Use a regular browser for file downloads. In testing, the Codex embedded browser displayed and copied transcripts successfully but did not complete Blob downloads; **Copy for Codex** provides a complete handoff there.

### Caption selection

Paste a watch, youtu.be, Shorts, embed, live/replay link, or a video ID and click **Get transcript**. Playlist-only links and active live broadcasts are unsupported. If no original-language track is recommended, choose a caption track and submit again. Machine-translated tracks are excluded.

### Proxy configuration

The default example configuration does not force a local proxy. If your network needs one, edit `.env`:

```dotenv
YT_PROXY=http://127.0.0.1:7890
```

Use your own proxy address and keep that proxy running. Restart the app after changes. `YT_PROXY` takes priority over `HTTPS_PROXY`, `HTTP_PROXY`, and `SOCKS5_PROXY`. For direct access, leave `YT_PROXY` empty and unset those other variables. Existing shell environment variables override `.env`.

This setting covers backend YouTube requests. If npm or uv also needs a proxy, set `HTTPS_PROXY` in the terminal before running setup. Browser cookies are not read or required.

## Use the video-brief skill

Copy `skills/video-brief/` into a personal Codex skills directory, such as `~/.agents/skills/video-brief/`. Install one copy only; an existing installation under `~/.codex/skills/video-brief/` can also be used. If it does not appear, restart Codex. See [Codex skill documentation](https://learn.chatgpt.com/docs/build-skills).

Attach the downloaded transcript and ask:

```text
Use $video-brief to read this entire transcript and give me a short overview,
key points with clickable timestamps, and the sections most worth watching.
Base the brief on the captions and flag uncertainty.
```

You can add a preferred language or viewing-time budget. Copy for Codex already includes the prompt and complete transcript, so you can paste directly instead of attaching a file. For another assistant, provide the skill's `SKILL.md` as workflow instructions alongside the source.

The skill instructs the assistant to read every segment, verify supporting passages, attribute claims to speakers, and distinguish complete retrieved captions from complete audiovisual coverage. It cannot guarantee the accuracy of captions or an AI-generated summary.

## Source format and architecture

The `youtube-transcript/v1` Markdown document includes a JSON metadata block with title, canonical URL, channel, language, caption source, provider, video duration, segment count, and caption coverage. Numbered caption headings retain start/end times as `HH:MM:SS.mmm`; original text is fenced separately. End times use actual durations. Unicode, line breaks, repeated captions, and overlapping cues are preserved.

```text
backend/                 FastAPI API, YouTube retrieval, locked Python dependencies
frontend/                React interface, Markdown export, locked npm dependencies
skills/video-brief/       Portable analysis instructions for a separate AI assistant
scripts/                 Export verification utility
docs/ARCHITECTURE.md      Current boundaries and proposed extension points
ROADMAP.md               Platform and browser-extension plans
```

### API

- `POST /api/video-info` with `{"url":"https://www.youtube.com/watch?v=Hrbq66XqtCo"}` returns metadata, available tracks, and a recommended track ID.
- `POST /api/extract` with `{"url":"Hrbq66XqtCo","track_id":"uploaded:en"}` retrieves the chosen track. Use a track ID returned by video-info.
- `GET /health` reports the service's status and captions-only mode.

Transcript records include `text`, fractional `start` and `duration`, plus display `timestamp` and legacy `seconds`. The response also identifies language, source, provider, and track. Extraction failures are explicit rather than being hidden behind successful metadata retrieval.

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the proposed common platform adapter and player bridge. These are design directions, not APIs implemented today.

## Limitations and data handling

Only accessible public videos with existing captions are supported. Private, removed, restricted, sign-in-required, or captionless videos may fail. Errors distinguish invalid links, unavailable videos, missing or empty captions, blocked requests, and connection failures. YouTube can change caption access; the app does not bypass authentication or access restrictions.

The server binds to `127.0.0.1` and checks local hosts/origins. It is intended for personal local use, not public hosting. Metadata and signed caption URLs are cached in process memory for up to five minutes, with a maximum of eight videos. Transcript results stay in browser memory until copied, downloaded, replaced, or the page is closed. Thumbnails are loaded from YouTube. No transcript library or automatic upload is maintained.

Captions may contain mistakes, omit visuals, or leave gaps. Follow timestamp links to check the original context before relying on an important claim. Users remain responsible for how they use and share source material.

## Development and verification

After setup, run these checks from the repository root:

```bash
backend/.venv/bin/python -m pytest -q
backend/.venv/bin/ruff check backend/main.py backend/app/transcript_service.py backend/tests tests
npm test --prefix frontend
npm run lint --prefix frontend
npm run build --prefix frontend
```

For frontend development, keep the backend running and run `npm run dev --prefix frontend -- --host 127.0.0.1`. Vite forwards local API calls to port 8000. Production uses the same origin as FastAPI.

Tests cover URL formats, selected languages and sources, provider fallback, explicit errors, timing, complete exports, source-fence handling, and disabled media downloads. See [VERIFICATION.md](VERIFICATION.md) for results and limitations. GitHub Actions runs the offline regression checks and frontend build; live YouTube access is not a CI requirement.

Contributions are welcome, particularly caption-provider adapters, player seeking, accessibility, and regression cases. See [CONTRIBUTING.md](CONTRIBUTING.md) before adding a new platform.

## Attribution

- **Application foundation:** [samueladegoke/yt-transcript-web](https://github.com/samueladegoke/yt-transcript-web), by Samuel Adegoke / Sam Ade, under the [MIT license](LICENSE). This adaptation retains its React/FastAPI foundation and caption extraction library, and changes retrieval behavior, timing, export, layout, and the AI handoff workflow. The original upstream AI/MCP services and deployment configuration are not part of this version.
- **Caption retrieval:** [jdepoix/youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api).
- **Metadata and caption fallback:** [yt-dlp/yt-dlp](https://github.com/yt-dlp/yt-dlp), used with media downloads disabled.
- **Frontend design guidance:** [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill), especially its existing-project redesign workflow.
- **Implementation stack:** React, Vite, Tailwind CSS, FastAPI, Uvicorn, Lucide icons, and self-hosted Geist fonts. Source links and license notes are in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

The original copyright notice is preserved unchanged. Local adaptations and the video-brief skill are maintained by [Jack-Li-Npu](https://github.com/Jack-Li-Npu). This repository starts from a clean source snapshot; the upstream commit is recorded above rather than republishing its historical deployment files. This is an independent project, not an official YouTube, TikTok, Douyin, Bilibili, or OpenAI product.
