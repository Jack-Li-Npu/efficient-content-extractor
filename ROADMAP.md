# Roadmap

The goal is to move from **a video link → complete source captions → a useful brief → the exact moment worth watching**, while keeping source collection and AI analysis separately usable.

This document describes intended work, not shipped functionality or delivery promises. Today, only the local YouTube caption extractor and the separate video-brief skill are implemented.

## 1. Common caption interface

Before adding platforms, extract a small provider interface from the existing YouTube service:

- Inspect a video and return its canonical URL, identity, title, duration, and available caption tracks.
- Retrieve the selected track with original text, language, uploaded/automatic provenance, start times, and actual durations.
- Normalize platform errors without silently substituting translated text or fabricated timings.
- Generate a platform-neutral transcript document while retaining compatibility with existing `youtube-transcript/v1` files.
- Generate a reliable source link or seek target for each cited passage.

Keep this interface separate from the web UI and the analysis skill. Do not create empty implementations that appear to support platforms before they work.

## 2. More video platforms

| Platform | Planned investigation | Completion criteria |
| --- | --- | --- |
| Bilibili | Public captions, video/part identity, multi-part videos, and timestamp navigation | Selected captions preserve wording and timing; the right video part opens or seeks correctly; unavailable captions have explicit errors |
| TikTok | Accessible caption tracks and timing, canonical video identity, player behavior | Captions can be retrieved through supported access and timestamp clicks reliably seek the active video |
| Douyin | Caption availability, distinct URL/player behavior, and access requirements | A separately tested adapter handles supported public videos and reports unsupported or inaccessible sources clearly |

TikTok and Douyin should not be assumed to share the same adapter merely because their products are similar. A platform may expose no usable captions for a given video. In that case, report the limitation; audio transcription would be a separate future feature requiring an explicit design decision.

For every platform, document supported URL types, language/source selection, restrictions, and known timing limitations. Use synthetic or redistributable test fixtures. Do not bundle login cookies, private media, or access-control bypasses.

## 3. Browser extension on the video page

Build an optional browser extension that lives beside the playing video, initially for YouTube and later for the other adapters. The intended experience:

1. The user opens a supported video and clicks the extension.
2. A side panel shows the current video's captions and the existing export/copy handoff.
3. The user analyzes the transcript in Codex or another assistant.
4. The user imports or pastes a structured brief containing key points and source intervals.
5. Clicking a key point seeks the **current video player** to the cited start time, with a visible range and an option to replay that passage.

The initial extension can keep the current manual AI handoff. Embedding model calls or automatically sending video text to a third party is not required for this workflow.

Implementation work includes per-platform player adapters, single-page navigation changes, video identity validation, accessibility, and graceful fallback to a timestamp URL when direct seeking is unavailable. A returned brief must match the active video's platform and ID before enabling seek actions. Treat imported text as data; do not render arbitrary HTML or execute instructions embedded in a transcript.

A browser extension is a different distribution surface from a Codex skill. Its permissions, local-backend connection, packaging, and store submission need their own implementation. The current localhost origin checks should not be loosened to a wildcard to make an extension connect.

## 4. Better analysis handoff

- Define an optional structured brief format: source platform/ID, overview, key points with supporting intervals, suggested viewing ranges, and coverage/uncertainty notes.
- Validate timestamp bounds and source identity before showing clickable passages.
- Preserve the existing readable Markdown export for manual workflows.
- Add user-selected summary language and viewing-time budgets to the external skill workflow where useful.
- Evaluate summaries for full-source coverage, accurate citations, later corrections, and clear attribution of speaker claims.

## Contribution priorities

A useful first contribution is a narrowly scoped adapter or player-seek prototype with documented access limitations and tests. Prefer one platform that works end to end over several platform buttons without implementations. See [CONTRIBUTING.md](CONTRIBUTING.md) and [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).
