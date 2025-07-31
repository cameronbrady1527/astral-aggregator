#!/bin/bash

# Simple health check script using curl
# This is a fallback for when the Python script fails

set -e

PORT=${PORT:-8000}
MAX_ATTEMPTS=5
WAIT_TIME=15

echo "Starting health check on port $PORT"

# Wait for app to start
echo "Waiting 30 seconds for app to start..."
sleep 30

for attempt in $(seq 1 $MAX_ATTEMPTS); do
    echo "Health check attempt $attempt/$MAX_ATTEMPTS"
    
    # Try multiple host addresses
    for host in localhost 127.0.0.1 0.0.0.0; do
        echo "Trying host: $host"
        
        # Try ping endpoint first
        echo "Checking ping endpoint..."
        if curl -f -s --max-time 10 "http://$host:$PORT/ping" > /dev/null 2>&1; then
            echo "✅ Ping endpoint is healthy on $host"
            exit 0
        else
            echo "❌ Ping endpoint failed on $host"
        fi
        
        # Try root endpoint as fallback
        echo "Checking root endpoint..."
        if curl -f -s --max-time 10 "http://$host:$PORT/" > /dev/null 2>&1; then
            echo "✅ Root endpoint is healthy on $host"
            exit 0
        else
            echo "❌ Root endpoint failed on $host"
        fi
    done
    
    echo "❌ Health check failed on attempt $attempt"
    
    if [ $attempt -lt $MAX_ATTEMPTS ]; then
        echo "Waiting $WAIT_TIME seconds before retry..."
        sleep $WAIT_TIME
    fi
done

echo "❌ All health check attempts failed"
exit 1 