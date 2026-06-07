#!/bin/bash
# Build script for Render deployment

set -e

echo "=== Building KeepUp for production ==="

# Build frontend
echo "Building frontend..."
cd frontend
npm install
npm run build
cd ..

# Copy built frontend to backend/static so it's bundled with the Python service
echo "Copying frontend build to backend/static..."
rm -rf backend/static
cp -r frontend/dist backend/static

# Install Python deps
echo "Installing Python dependencies..."
cd backend
pip install -r requirements.txt

echo "=== Build complete ==="
