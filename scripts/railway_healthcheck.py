#!/usr/bin/env python3
"""
Railway-specific healthcheck script
"""

import os
import sys
import time
import urllib.request
import urllib.error

def check_health():
    """Check if the application is healthy."""
    try:
        # Get port from environment
        port = os.environ.get('PORT', '8000')
        
        # Try ping endpoint first (simplest)
        ping_url = f"http://localhost:{port}/ping"
        print(f"Checking ping at: {ping_url}")
        
        try:
            with urllib.request.urlopen(ping_url, timeout=10) as response:
                if response.getcode() == 200:
                    print("✅ Ping check passed")
                    return True
                else:
                    print(f"❌ Ping returned status {response.getcode()}")
                    return False
        except urllib.error.URLError as e:
            print(f"❌ Ping failed: {e}")
            
            # Try health endpoint as fallback
            health_url = f"http://localhost:{port}/health"
            print(f"Trying health endpoint: {health_url}")
            
            try:
                with urllib.request.urlopen(health_url, timeout=10) as response:
                    if response.getcode() == 200:
                        print("✅ Health check passed")
                        return True
                    else:
                        print(f"❌ Health returned status {response.getcode()}")
                        return False
            except urllib.error.URLError as e:
                print(f"❌ Health check failed: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def main():
    """Main healthcheck function."""
    print("🔍 Railway Healthcheck Starting...")
    
    # Wait a bit for app to start
    print("Waiting 30 seconds for app to start...")
    time.sleep(30)
    
    # Try multiple times
    for attempt in range(5):
        print(f"Health check attempt {attempt + 1}/5")
        
        if check_health():
            print("✅ Health check successful")
            sys.exit(0)
        
        if attempt < 4:  # Don't sleep after last attempt
            print("Waiting 15 seconds before retry...")
            time.sleep(15)
    
    print("❌ All health check attempts failed")
    sys.exit(1)

if __name__ == "__main__":
    main() 