# Efficient Content Extractor

**Find the moments worth watching.**

Extract existing YouTube captions, bring the complete transcript to Codex, and get key points linked to the original video.

[Quick start](#quick-start) &nbsp; / &nbsp; [See the demo](#demo-from-captions-to-a-timestamped-brief) &nbsp; / &nbsp; [Roadmap](ROADMAP.md) &nbsp; / &nbsp; [Attribution](#attribution)

![The local app with a complete YouTube transcript, caption-track selection, search, and copy or download for Codex](docs/screenshots/transcript-extraction.png)

Built on [samueladegoke/yt-transcript-web](https://github.com/samueladegoke/yt-transcript-web), with its MIT license preserved. Runs locally on your Mac; analysis happens in your own AI chat.

## Purpose and workflow

A long interview, lecture, or news program becomes easier to navigate when you can read a brief and open the passages that matter.

1. **Get the source.** Paste a YouTube link and retrieve existing captions in their original language.
2. **Bring it to Codex.** Copy or download one complete Markdown transcript with every retrieved caption and its timestamps.
3. **Choose what to watch.** Use the included `video-brief` skill for an overview, key points, and links back to supporting passages.

You choose when and where to submit the transcript. The app makes no AI-service requests or automatic uploads; the Markdown also works with other assistants.

## Demo: from captions to a timestamped brief

### Read the brief. Open the passage.

The app above extracts **685 caption segments** from a Bloomberg Tech video. Below, a separate Codex chat turns that source into a timestamped brief.

![Codex displaying an overview and key points with clickable YouTube timestamps beside the exported source transcript](docs/screenshots/codex-timestamped-brief.png)

The transcript stays available beside the analysis. Follow a timestamp link to check the original context or watch only a relevant section.

<details>
<summary>About this example</summary>

Both screenshots show *Anthropic Goes Big on Compute, Microsoft Rethinks AI* by Bloomberg Tech. Video imagery and caption excerpts belong to their respective owners. The summary is produced in a separate Codex chat, not inside the extractor. Current timestamp links open YouTube; seeking inside the active player is planned.

</details>

## What works today

| What you need | What the app provides |
| --- | --- |
| Original source text | Uploaded or automatic captions, explicit track selection, and full-text search |
| A complete AI handoff | One Markdown document with all retrieved captions, source metadata, and millisecond timings |
| Reliable source context | Language and caption provenance; original words, durations, and overlapping cues preserved |
| Control over analysis | Copy/download for your own assistant, with an optional `video-brief` skill |

Copy and download always include the entire retrieved transcript, even when search filters the display. Uploaded original-language captions are preferred when that language can be determined.

### Where this is going

**YouTube works today.** The next direction is broader platform support and a brief beside the video you are watching.

| Direction | Status |
| --- | --- |
| TikTok, Douyin, and Bilibili caption adapters | Planned |
| Browser extension beside the video player | Planned |
| Click a key point to seek the active player | Planned |

See the [Roadmap](ROADMAP.md) for scope, proposed interfaces, and contribution priorities. These integrations and the extension are not implemented yet.

## Quick start

The launcher is designed for macOS. Install [uv](https://docs.astral.sh/uv/getting-started/installation/) and Node.js 22.12+ with npm, then run:

```bash
git clone https://github.com/Jack-Li-Npu/efficient-content-extractor.git
cd efficient-content-extractor
./setup.sh
./start.command
```

Open **http://127.0.0.1:8000**. Keep the terminal open while using the app; press Control-C to stop it. On subsequent macOS runs, you can double-click `start.command` in Finder.

<details>
<summary>Setup details and download troubleshooting</summary>

Setup creates an isolated Python environment in `backend/.venv`, installs backend dependencies from `backend/uv.lock`, installs frontend dependencies with `npm ci`, and builds React for FastAPI to serve. Setup copies `.env.example` to `.env` only when `.env` does not already exist. Run setup again after changing dependencies or frontend code.

Use a regular browser for file downloads. In testing, the Codex embedded browser displayed and copied transcripts successfully but did not complete Blob downloads; **Copy for Codex** provides a complete handoff there.

</details>

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

<details>
<summary>Explore the transcript format, project structure, and API</summary>

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

</details>

## Limitations and data handling

The app retrieves existing captions only. It does not download audio/video, transcribe speech, translate captions, download models, or require an AI API key.

Only accessible public videos with existing captions are supported. Private, removed, restricted, sign-in-required, or captionless videos may fail. Errors distinguish invalid links, unavailable videos, missing or empty captions, blocked requests, and connection failures. YouTube can change caption access; the app does not bypass authentication or access restrictions.

The server binds to `127.0.0.1` and checks local hosts/origins. It is intended for personal local use, not public hosting. Metadata and signed caption URLs are cached in process memory for up to five minutes, with a maximum of eight videos. Transcript results stay in browser memory until copied, downloaded, replaced, or the page is closed. Thumbnails are loaded from YouTube. No transcript library or automatic upload is maintained.

Captions may contain mistakes, omit visuals, or leave gaps. Follow timestamp links to check the original context before relying on an important claim. Users remain responsible for how they use and share source material.

## Development and verification

<details>
<summary>Development commands, tests, and contribution notes</summary>

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

</details>

## Attribution

- **Application foundation:** [samueladegoke/yt-transcript-web](https://github.com/samueladegoke/yt-transcript-web), by Samuel Adegoke / Sam Ade, adapted from commit [`4928098`](https://github.com/samueladegoke/yt-transcript-web/commit/4928098ffe109df932a8f4bae47f31ebcf314a10) under the [MIT license](LICENSE). This adaptation retains its React/FastAPI foundation and caption extraction library, and changes retrieval behavior, timing, export, layout, and the AI handoff workflow. The original upstream AI/MCP services and deployment configuration are not part of this version.
- **Caption retrieval:** [jdepoix/youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api).
- **Metadata and caption fallback:** [yt-dlp/yt-dlp](https://github.com/yt-dlp/yt-dlp), used with media downloads disabled.
- **Frontend design guidance:** [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill), especially its existing-project redesign workflow.
- **Implementation stack:** React, Vite, Tailwind CSS, FastAPI, Uvicorn, Lucide icons, and self-hosted Geist fonts. Source links and license notes are in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

The original copyright notice is preserved unchanged. Local adaptations and the video-brief skill are maintained by [Jack-Li-Npu](https://github.com/Jack-Li-Npu). This repository starts from a clean source snapshot; the upstream commit is recorded in this section rather than republishing its historical deployment files. This is an independent project, not an official YouTube, TikTok, Douyin, Bilibili, or OpenAI product.
