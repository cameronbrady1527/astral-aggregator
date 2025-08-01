#!/usr/bin/env python3
"""
Simple healthcheck script for testing the application
"""

import requests
import sys
import time

def check_endpoint(url, endpoint, expected_status=200):
    """Check if an endpoint is responding correctly."""
    try:
        full_url = f"{url}{endpoint}"
        print(f"Checking {full_url}...")
        
        response = requests.get(full_url, timeout=10)
        
        if response.status_code == expected_status:
            print(f"✅ {endpoint} - Status: {response.status_code}")
            try:
                data = response.json()
                print(f"   Response: {data}")
            except:
                print(f"   Response: {response.text[:100]}...")
            return True
        else:
            print(f"❌ {endpoint} - Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ {endpoint} - Error: {e}")
        return False

def main():
    # Get base URL from command line or use default
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    print(f"🔍 Healthcheck for {base_url}")
    print("=" * 50)
    
    # Check basic endpoints
    endpoints = [
        ("/ping", 200),
        ("/health", 200),
        ("/", 200),
        ("/test", 200),
    ]
    
    all_passed = True
    
    for endpoint, expected_status in endpoints:
        if not check_endpoint(base_url, endpoint, expected_status):
            all_passed = False
        print()
    
    # Summary
    print("=" * 50)
    if all_passed:
        print("✅ All healthchecks passed!")
        sys.exit(0)
    else:
        print("❌ Some healthchecks failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 