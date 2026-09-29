#!/bin/bash
set -euo pipefail
APP_ROOT="$(cd "$(dirname "$0")" && pwd)"
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
cd "$APP_ROOT"
if [ ! -x backend/.venv/bin/python ] || [ ! -f frontend/dist/index.html ]; then
  echo "Run ./setup.sh first." >&2
  exit 1
fi
backend/.venv/bin/python - <<'PY'
import socket
with socket.socket() as sock:
    try:
        sock.bind(('127.0.0.1', 8000))
    except OSError:
        raise SystemExit('Port 8000 is already in use. Close the other server, then launch again.')
PY
echo "YouTube Transcript: http://127.0.0.1:8000"
echo "Keep this window open. Press Control-C to stop."
exec backend/.venv/bin/python -m uvicorn main:app --app-dir "$APP_ROOT/backend" --host 127.0.0.1 --port 8000
