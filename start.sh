#!/bin/bash

# Simple startup script for Railway deployment
set -e

echo "Starting Astral Aggregator..."

# Set environment variables
export PYTHONPATH=/app
export PYTHONUNBUFFERED=1

# Create output directory
mkdir -p output

# Start the application
echo "Starting uvicorn server on port ${PORT:-8000}"

exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port ${PORT:-8000} \
    --workers 1 \
    --log-level info 