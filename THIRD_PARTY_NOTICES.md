# Sources and third-party notices

## Upstream application

This project is a source adaptation of [samueladegoke/yt-transcript-web](https://github.com/samueladegoke/yt-transcript-web), based on commit [`4928098ffe109df932a8f4bae47f31ebcf314a10`](https://github.com/samueladegoke/yt-transcript-web/commit/4928098ffe109df932a8f4bae47f31ebcf314a10).

The original [MIT license](LICENSE), including **Copyright (c) 2026 Sam Ade**, is preserved. The upstream React/FastAPI application and caption-library integration provided the foundation. This adaptation changes retrieval and errors, caption selection, accurate timing, exports, interface layout, local setup, and the separate AI analysis handoff. The `video-brief` skill and future-platform roadmap were added for this project.

The published repository starts with a clean snapshot of the adapted application; its Git history does not reproduce the upstream history. This does not remove the upstream attribution or license obligations.

## Main technologies

Dependencies retain their own licenses. Exact installed versions and transitive dependencies are recorded in `backend/uv.lock` and `frontend/package-lock.json`; this table identifies the principal source projects rather than replacing their license files.

| Technology | Role | Public source |
| --- | --- | --- |
| youtube-transcript-api | Primary retrieval of existing YouTube caption tracks | [jdepoix/youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api) |
| yt-dlp | Video metadata and selected-caption fallback, with media downloads disabled | [yt-dlp/yt-dlp](https://github.com/yt-dlp/yt-dlp) |
| FastAPI | Local Python API | [fastapi/fastapi](https://github.com/fastapi/fastapi) |
| Uvicorn | ASGI server | [encode/uvicorn](https://github.com/encode/uvicorn) |
| React | Frontend components and state | [facebook/react](https://github.com/facebook/react) |
| Vite | Frontend development and production build | [vitejs/vite](https://github.com/vitejs/vite) |
| Tailwind CSS | CSS tooling inherited from the frontend | [tailwindlabs/tailwindcss](https://github.com/tailwindlabs/tailwindcss) |
| Lucide | Interface icons | [lucide-icons/lucide](https://github.com/lucide-icons/lucide) |
| Geist / Geist Mono | Self-hosted typography | [vercel/geist-font](https://github.com/vercel/geist-font) |
| Fontsource | npm font packaging | [fontsource/fontsource](https://github.com/fontsource/fontsource) |
| uv | Isolated Python environment and locked installation | [astral-sh/uv](https://github.com/astral-sh/uv) |

Font license copies are included at [Geist OFL](frontend/public/licenses/Geist-OFL.txt) and [Geist Mono OFL](frontend/public/licenses/Geist-Mono-OFL.txt).

## Development guidance

[Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill), especially its existing-project redesign workflow, guided the frontend redesign. It is development guidance, not a runtime dependency or a bundled copy in this repository.

The original local workspace also installed [zhaoxuya520/reverse-skill](https://github.com/zhaoxuya520/reverse-skill) as separate tooling. The extractor does not depend on it, and that independent checkout is not included in this release. Caption retrieval is performed by the providers identified above.

Video text, thumbnails, names, and platform trademarks belong to their respective owners. This repository distributes application code and instructions, not a collection of third-party video transcripts.
