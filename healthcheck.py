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
        
        response = requests.get(ping_url, timeout=5)
        print(f"Ping response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Ping check passed")
            return True
        
        # If ping fails, try root endpoint
        root_url = f"http://localhost:{port}/"
        print(f"Checking root at: {root_url}")
        
        response = requests.get(root_url, timeout=5)
        print(f"Root response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Root check passed")
            return True
            
    except requests.exceptions.ConnectionError:
        print("❌ Health check failed: connection error")
        return False
    except requests.exceptions.Timeout:
        print("❌ Health check failed: timeout")
        return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    return False

if __name__ == "__main__":
    # Try multiple times with delays
    for attempt in range(5):
        print(f"Health check attempt {attempt + 1}/5")
        if check_health():
            sys.exit(0)
        
        if attempt < 4:  # Don't sleep after last attempt
            print("Waiting 10 seconds before retry...")
            time.sleep(10)
    
    print("❌ All health check attempts failed")
    sys.exit(1) 