#!/bin/bash
set -euo pipefail
APP_ROOT="$(cd "$(dirname "$0")" && pwd)"
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
for tool in uv node npm; do
  if ! command -v "$tool" >/dev/null 2>&1; then
    echo "Missing $tool. Install uv and Node.js, then run setup.sh again." >&2
    exit 1
  fi
done
cd "$APP_ROOT"
if [ ! -f .env ]; then cp .env.example .env; fi
uv sync --project backend --frozen
(cd frontend && npm ci --no-audit --no-fund && npm run build)
echo "Ready. Double-click start.command or run ./start.command."
