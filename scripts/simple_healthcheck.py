#!/usr/bin/env python3
"""
Simple healthcheck script for Railway
Minimal and fast health check
"""

import os
import sys
import urllib.request
import urllib.error

def main():
    """Simple health check for Railway."""
    try:
        port = os.environ.get('PORT', '8000')
        url = f"http://localhost:{port}/ping"
        
        with urllib.request.urlopen(url, timeout=5) as response:
            if response.getcode() == 200:
                print("✅ Health check passed")
                sys.exit(0)
            else:
                print(f"❌ Health check failed: status {response.getcode()}")
                sys.exit(1)
                
    except Exception as e:
        print(f"❌ Health check error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 