#!/bin/bash

# Simple startup script for Railway deployment
set -e

echo "🚀 Starting Astral Aggregator..."
echo "Current directory: $(pwd)"
echo "Python version: $(python --version)"
echo "PORT environment variable: ${PORT:-NOT SET}"

# Set environment variables
export PYTHONPATH=/app
export PYTHONUNBUFFERED=1

echo "PYTHONPATH set to: $PYTHONPATH"

# Create output directory
mkdir -p output
echo "Output directory created"

# Test app import
echo "Testing app import..."
python -c "import app.main; print('✅ App imported successfully')" || {
    echo "❌ App import failed"
    exit 1
}

# Get the port with proper fallback
PORT_NUM=${PORT:-8000}
echo "Using port: $PORT_NUM"

# Start the application
echo "Starting uvicorn server on port $PORT_NUM"
echo "Host: 0.0.0.0"

exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port $PORT_NUM \
    --workers 1 \
    --log-level info 