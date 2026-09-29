# Architecture and extension points

## Current implementation

```text
React interface
  ├─ /api/video-info → yt-dlp metadata and caption choices
  ├─ /api/extract → youtube-transcript-api
  │                  └─ selected-track yt-dlp caption fallback
  └─ complete timestamped Markdown / clipboard
                       ↓ user-controlled handoff
                  external AI assistant + video-brief
                       ↓
                  brief with YouTube timestamp links
```

`backend/app/transcript_service.py` handles YouTube URL parsing, metadata, caption selection, retrieval, normalization, and error classification. `backend/main.py` exposes the two API routes and serves the built React app. The frontend keeps results in memory and generates the handoff document in `frontend/src/lib/transcript.js`.

`skills/video-brief/SKILL.md` contains analysis instructions; it is not executed by the web server. It asks the assistant to read all segments, cite source intervals, and flag caption uncertainty. There is no model-service integration in the current app.

## Proposed platform boundary (not yet implemented)

Move platform-specific behavior behind a provider selected from a validated URL. A provider should support metadata inspection, track listing, selected-track retrieval, and timestamp-link generation. Share the normalized segment representation (`start`, `duration`, `text`) and common errors, but retain source-specific identifiers such as a Bilibili part.

A future document version should explicitly carry `platform`, canonical source URL, platform video/part identity, caption provenance, and segment IDs. The current document is deliberately named `youtube-transcript/v1`; do not relabel non-YouTube sources as YouTube or change its meaning silently. Keep compatibility when introducing a new format and update the analysis skill to produce platform-appropriate links.

## Proposed player boundary (not yet implemented)

The browser extension would contain a platform-specific player bridge responsible for identifying the active video, reading its current playback position, and seeking to a validated timestamp. Keep retrieval independent of the player bridge so a transcript can still be exported without an extension.

A brief import should have a source identity and bounded, finite time intervals. Validate them against the active video before seeking. Account for route changes, multiple videos, and unsupported player states. Seek only in response to a user action; a highlighted takeaway need not automatically start playback.

If the extension uses the local FastAPI service, design a narrow, explicit connection and permissions model. Existing host/origin checks are intentionally limited to the local web app; an extension is not supported by simply adding a wildcard origin. No such bridge or permission mechanism is shipped today.

## Stable behavior to preserve

- Existing captions only, with no hidden audio/model download or translation.
- Uploaded versus automatic source selection and original wording.
- Fractional start times and actual durations, including overlap and long videos.
- Explicit extraction errors separate from metadata success.
- Search affects the view; full-document handoff includes every retrieved segment.
- Analysis happens only after the user chooses to send source text to an assistant.
