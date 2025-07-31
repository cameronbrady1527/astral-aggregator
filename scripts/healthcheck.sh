#!/bin/bash

# Simple health check script using curl
# This is a fallback for when the Python script fails

set -e

PORT=${PORT:-8000}
MAX_ATTEMPTS=5
WAIT_TIME=15

echo "Starting health check on port $PORT"

for attempt in $(seq 1 $MAX_ATTEMPTS); do
    echo "Health check attempt $attempt/$MAX_ATTEMPTS"
    
    # Try ping endpoint first
    echo "Checking ping endpoint..."
    if curl -f -s --max-time 10 "http://localhost:$PORT/ping" > /dev/null 2>&1; then
        echo "✅ Ping endpoint is healthy"
        exit 0
    else
        echo "❌ Ping endpoint failed"
    fi
    
    # Try root endpoint as fallback
    echo "Checking root endpoint..."
    if curl -f -s --max-time 10 "http://localhost:$PORT/" > /dev/null 2>&1; then
        echo "✅ Root endpoint is healthy"
        exit 0
    else
        echo "❌ Root endpoint failed"
    fi
    
    echo "❌ Health check failed on attempt $attempt"
    
    if [ $attempt -lt $MAX_ATTEMPTS ]; then
        echo "Waiting $WAIT_TIME seconds before retry..."
        sleep $WAIT_TIME
    fi
done

echo "❌ All health check attempts failed"
exit 1 