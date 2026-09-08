#!/bin/sh
set -eu
cd "$(dirname "$0")"
if [ ! -x .venv/bin/python ]; then
  python3 -m venv .venv
fi
.venv/bin/python -m pip install -r requirements.txt
npm ci --cache "${TMPDIR:-/tmp}/just-small-journey-npm-cache"
npm run build
exec .venv/bin/python -m uvicorn app:app --host 127.0.0.1 --port "${PORT:-8000}"
