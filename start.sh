#!/bin/bash

# Simple startup script for Railway deployment
set -e

echo "Starting Astral Aggregator..."
echo "Current directory: $(pwd)"
echo "Python version: $(python --version)"

# Set environment variables
export PYTHONPATH=/app
export PYTHONUNBUFFERED=1

echo "PYTHONPATH set to: $PYTHONPATH"

# Create output directory
mkdir -p output
echo "Output directory created"

# Test app import
echo "Testing app import..."
python -c "import app.main; print('App imported successfully')" || {
    echo "App import failed"
    exit 1
}

# Get PORT with explicit expansion and validation
echo "Getting PORT environment variable..."
echo "Raw PORT value: '$PORT'"

# Use explicit expansion with fallback
PORT_NUM="${PORT:-8000}"
echo "Expanded PORT: $PORT_NUM"

# Validate PORT is a number
if [[ ! "$PORT_NUM" =~ ^[0-9]+$ ]]; then
    echo "PORT '$PORT_NUM' is not a valid number, using 8000"
    PORT_NUM=8000
fi

echo "Final port configuration: $PORT_NUM"

# Start the application
echo "Starting uvicorn server on port $PORT_NUM"
echo "Host: 0.0.0.0"

exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port "$PORT_NUM" \
    --workers 1 \
    --log-level info 