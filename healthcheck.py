#!/usr/bin/env python3
"""
Health check script for Railway deployment.
This script tests if the FastAPI app is running and responding correctly.
"""

import sys
import os
import requests
import time

def check_health():
    """Check if the app is healthy."""
    try:
        # Get port from environment or use default
        port = os.getenv('PORT', '8000')
        
        # Try ping endpoint first (simpler)
        ping_url = f"http://localhost:{port}/ping"
        print(f"Checking ping at: {ping_url}")
        
        response = requests.get(ping_url, timeout=10)
        print(f"Ping response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Ping check passed")
            return True
        
        # If ping fails, try health endpoint
        health_url = f"http://localhost:{port}/health"
        print(f"Checking health at: {health_url}")
        
        response = requests.get(health_url, timeout=10)
        print(f"Health response status: {response.status_code}")
        print(f"Health response content: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'healthy':
                print("✅ Health check passed")
                return True
            else:
                print(f"❌ Health check failed: unexpected status {data.get('status')}")
                return False
        else:
            print(f"❌ Health check failed: status code {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Health check failed: connection error")
        return False
    except requests.exceptions.Timeout:
        print("❌ Health check failed: timeout")
        return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

if __name__ == "__main__":
    # Try multiple times with delays
    for attempt in range(3):
        print(f"Health check attempt {attempt + 1}/3")
        if check_health():
            sys.exit(0)
        
        if attempt < 2:  # Don't sleep after last attempt
            print("Waiting 5 seconds before retry...")
            time.sleep(5)
    
    print("❌ All health check attempts failed")
    sys.exit(1) 