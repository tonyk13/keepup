#!/bin/bash
set -e

cd "$(dirname "$0")/backend"

PORT="${PORT:-8000}"

# Use the virtual env if it exists, otherwise system Python
if [ -d "../venv" ]; then
    source ../venv/bin/activate
fi

echo "Starting KeepUp on port $PORT..."
uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
