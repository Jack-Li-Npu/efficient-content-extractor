"""Local web interface for the upstream caption extraction service."""

import time
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.transcript_service import ExtractionError, fetch_selected, get_video_info

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

app = FastAPI(title="Local YouTube Transcript", version="2.0.0")
ORIGINS = {"http://127.0.0.1:8000", "http://localhost:8000", "http://127.0.0.1:5173", "http://localhost:5173"}
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost", "[::1]"])
app.add_middleware(
    CORSMiddleware, allow_origins=sorted(ORIGINS), allow_methods=["GET", "POST"], allow_headers=["Content-Type"]
)


@app.middleware("http")
async def local_origin(request: Request, call_next):
    origin = request.headers.get("origin")
    if request.method == "POST" and origin and origin not in ORIGINS:
        return JSONResponse(
            {"code": "invalid_origin", "message": "Open the app on localhost to continue."}, status_code=403
        )
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


@app.exception_handler(ExtractionError)
async def extraction_error(_request: Request, exc: ExtractionError):
    return JSONResponse({"success": False, "code": exc.code, "message": str(exc)}, status_code=exc.status)


class VideoRequest(BaseModel):
    url: str = Field(min_length=1, max_length=2048)


class ExtractRequest(VideoRequest):
    track_id: str = Field(min_length=1, max_length=100)


def timestamp(seconds: float) -> str:
    total = int(seconds)
    hours, rest = divmod(total, 3600)
    minutes, secs = divmod(rest, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}" if hours else f"{minutes:02d}:{secs:02d}"


@app.get("/health")
def health():
    return {"status": "healthy", "mode": "existing-captions-only"}


@app.post("/api/video-info")
def video_info(request: VideoRequest):
    return {"success": True, **get_video_info(request.url)}


@app.post("/api/extract")
def extract(request: ExtractRequest):
    started = time.perf_counter()
    result = fetch_selected(request.url, request.track_id)
    segments = result.pop("segments")
    lines = [
        {
            "start": item.start,
            "duration": item.duration,
            "text": item.text,
            "seconds": int(item.start),
            "timestamp": timestamp(item.start),
        }
        for item in segments
    ]
    return {
        "success": True,
        **result,
        "track_id": request.track_id,
        "transcript_lines": lines,
        "plain_text": "\n".join(item.text for item in segments),
        "generated_at": time.time(),
        "extraction_ms": round((time.perf_counter() - started) * 1000),
    }


DIST = ROOT / "frontend" / "dist"
if DIST.is_dir():
    app.mount("/", StaticFiles(directory=DIST, html=True), name="frontend")
else:

    @app.get("/")
    def setup_needed():
        return JSONResponse({"message": "Run ./setup.sh to build the web interface."}, status_code=503)
