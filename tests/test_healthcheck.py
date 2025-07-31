#!/usr/bin/env python3
"""
Test script to verify healthcheck functionality locally.
Run this after starting the app to test the health endpoints.
"""

import requests
import time
import sys

def test_health_endpoints():
    """Test all health endpoints."""
    base_url = "http://localhost:8000"
    
    endpoints = [
        ("/ping", "Ping endpoint"),
        ("/health", "Health endpoint"), 
        ("/", "Root endpoint")
    ]
    
    print("Testing health endpoints...")
    
    for endpoint, name in endpoints:
        try:
            url = f"{base_url}{endpoint}"
            print(f"\nTesting {name}: {url}")
            
            response = requests.get(url, timeout=5)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            
            if response.status_code == 200:
                print(f"✅ {name} is working")
            else:
                print(f"❌ {name} failed with status {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ {name} - Connection refused (app may not be running)")
        except Exception as e:
            print(f"❌ {name} - Error: {e}")

if __name__ == "__main__":
    test_health_endpoints() 