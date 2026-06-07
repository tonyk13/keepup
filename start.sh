#!/bin/bash
set -e

cd "$(dirname "$0")"

echo "Starting KeepUp backend..."
cd backend
source ../venv/bin/activate
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > uvicorn.log 2>&1 &
echo $! > .pid
echo "Backend started on http://localhost:8000"
echo ""
echo "Frontend is served automatically at http://localhost:8000"
echo "API docs at http://localhost:8000/docs"
