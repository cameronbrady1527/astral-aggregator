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
pip list | grep -E "(fastapi|uvicorn)"

# Create output directory if it doesn't exist
mkdir -p output
echo "Output directory created/verified"

# Set environment variables
export PYTHONPATH=/app
export PYTHONUNBUFFERED=1

# Test that the app can be imported
echo "Testing app import..."
python -c "import app.main; print('App imported successfully')"

# Test health endpoint before starting server
echo "Testing health endpoint..."
python -c "
from app.main import app
from fastapi.testclient import TestClient
client = TestClient(app)
response = client.get('/health')
print(f'Health check test: {response.status_code}')
print(f'Response: {response.json()}')
"

# Start the application
echo "Starting uvicorn server..."
exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port ${PORT:-8000} \
    --workers 1 \
    --log-level info 