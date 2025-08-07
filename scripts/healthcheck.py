#!/usr/bin/env python3
# ==============================================================================
# healthcheck.py — Simple healthcheck script for testing the application
# ==============================================================================
# Purpose: Test application endpoints and provide health status
# Sections: Imports, Public Exports, Helper Functions, Main Function
# ==============================================================================

# ==============================================================================
# Imports
# ==============================================================================

# Standard Library -----
import sys

# Third-Party -----
import requests

# ==============================================================================
# Public exports
# ==============================================================================
__all__ = [
    'check_endpoint',
    'main'
]

# ==============================================================================
# Helper Functions
# ==============================================================================

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
            print(f"[ X ] {endpoint} - Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"[ X ] {endpoint} - Error: {e}")
        return False

# ==============================================================================
# Main Function
# ==============================================================================

def main():
    # get base URL from command line or use default
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    print(f"🔍 Healthcheck for {base_url}")
    print("=" * 50)
    
    # check basic endpoints
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
    
    # summary
    print("=" * 50)
    if all_passed:
        print("✅ All healthchecks passed!")
        sys.exit(0)
    else:
        print("[ X ] Some healthchecks failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 