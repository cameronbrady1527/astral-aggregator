#!/usr/bin/env python3
"""
Simple health check script for Railway deployment.
This is a minimal version that focuses on basic functionality.
"""

import os
import sys
import requests
import time

def simple_health_check():
    """Simple health check that just tries to connect."""
    try:
        # Get port from environment
        port = os.getenv('PORT', '8000')
        
        # Try the simplest possible check - just connect to localhost
        url = f"http://localhost:{port}/ping"
        
        # Very short timeout for quick failure
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            print(f"✅ Health check passed: {response.text}")
            return True
        else:
            print(f"❌ Health check failed: status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection refused - app may not be running")
        return False
    except requests.exceptions.Timeout:
        print("❌ Request timeout")
        return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

if __name__ == "__main__":
    # Wait a bit for startup
    print("Waiting 60 seconds for app to start...")
    time.sleep(60)
    
    # Try a few times
    for attempt in range(3):
        print(f"Health check attempt {attempt + 1}/3")
        if simple_health_check():
            print("✅ Health check successful")
            sys.exit(0)
        
        if attempt < 2:
            print("Waiting 30 seconds before retry...")
            time.sleep(30)
    
    print("❌ All health check attempts failed")
    sys.exit(1) 