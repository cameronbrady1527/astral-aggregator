#!/bin/bash

# Simple startup script for Railway deployment
# CACHE BUSTER: Enhanced PORT environment variable handling and debugging
set -e

echo "🚀 Starting Astral Aggregator..."
echo "Current directory: $(pwd)"
echo "Python version: $(python --version)"
echo "All environment variables:"
env | sort

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

# Get the port with proper fallback and validation
if [ -z "$PORT" ]; then
    echo "⚠️  PORT environment variable is not set, using default port 8000"
    PORT_NUM=8000
else
    echo "📡 PORT environment variable found: $PORT"
    # Validate that PORT is a number
    if [[ "$PORT" =~ ^[0-9]+$ ]]; then
        PORT_NUM=$PORT
        echo "✅ PORT is valid: $PORT_NUM"
    else
        echo "❌ PORT is not a valid number: $PORT"
        echo "Using default port 8000"
        PORT_NUM=8000
    fi
fi

echo "🎯 Final port configuration: $PORT_NUM"

# Start the application
echo "Starting uvicorn server on port $PORT_NUM"
echo "Host: 0.0.0.0"

exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port "$PORT_NUM" \
    --workers 1 \
    --log-level info 