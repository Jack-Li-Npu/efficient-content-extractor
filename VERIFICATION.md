# Verification

## Initial GitHub release — 2026-09-29

The release is a clean source snapshot of the local caption-only adaptation. The original application's MIT license is byte-for-byte identical to the license at upstream commit `4928098ffe109df932a8f4bae47f31ebcf314a10`.

Release preparation uses the documented `setup.sh` from an independent checkout, with frozen uv dependencies and `npm ci`. Local checks use Python 3.13.9 and Node.js 25.3.0; GitHub Actions is configured for Python 3.13 and Node.js 22 on Ubuntu.

## Automated checks

- **45 backend tests:** supported URLs, language/source selection, original-language preference, provider fallback, empty/failed results, accurate timing, local origin restrictions, and disabled media downloads.
- **6 frontend tests:** full Markdown text preservation, Unicode and multiline content, millisecond timing beyond an hour, safe source fences, invalid input, repeated/overlapping captions, long transcripts, and safe filenames.
- Frontend lint and production build; backend Ruff; Bash launcher syntax; local API health and static frontend smoke checks.
- CI runs offline tests and the frontend build. Its results appear in the repository's Actions tab; live YouTube access is not required by CI.

## Previous live verification — 2026-09-27

Using the public example video `Hrbq66XqtCo`, the local app retrieved **1,104 uploaded English caption segments**. Browser display, the full clipboard payload, and the generated Markdown were compared against the retrieved source, including every segment in order.

- First cue: `00:00:00.480 → 00:00:04.400`.
- Last cue: `01:43:09.440 → 01:43:10.560`.
- Searching for the final cue left copy/export content complete.
- A selected automatic-English track returned **2,743** segments in a separate live API check.
- A deliberately failed primary provider exercised the real yt-dlp fallback, which returned the same 1,104 uploaded-caption segments.
- The fallback retrieved metadata and caption data, with no audio/video streams, models, or AI-service requests.
- Responsive DOM checks at 1280, 390, and 320 pixels found no horizontal page overflow.

These are historical checks of specific videos and network conditions, not a promise that YouTube access always succeeds. The original multi-format browser downloads were tested in Chrome before the app was simplified. The current single-format handoff was verified through its generated file and complete clipboard content; the embedded Codex browser did not complete Blob downloads. Use Copy for Codex in that browser or a regular browser for downloads.

## Repeat the export comparison

Save the selected `/api/extract` response as JSON and download its Markdown document:

```bash
node scripts/verify-downloads.mjs '/path/to/extract-response.json' '/path/to/download.transcript.md'
```

The script checks exact generated content. Channel and video duration come from `/api/video-info`; include them in the source JSON to validate them independently, otherwise the script takes those two fields from the document being compared.

## Scope

No other media platform or browser extension has been implemented or validated. See [ROADMAP.md](ROADMAP.md). Personal transcripts, local environment settings, screenshots, dependency folders, generated builds, and the original upstream Git history are not included in the published source.
