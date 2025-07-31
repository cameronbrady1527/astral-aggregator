#!/bin/bash

# Startup script for Railway deployment
set -e

echo "Starting Astral Aggregator..."

# Check if we're in the right directory
echo "Current directory: $(pwd)"
echo "Contents: $(ls -la)"

# Check Python version
echo "Python version: $(python --version)"

# Check if requirements are installed
echo "Checking installed packages..."
pip list

# Create output directory if it doesn't exist
mkdir -p output
echo "Output directory created/verified"

# Set environment variables
export PYTHONPATH=/app
export PYTHONUNBUFFERED=1

# Start the application
echo "Starting uvicorn server..."
exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port ${PORT:-8000} \
    --workers 1 \
    --log-level info 