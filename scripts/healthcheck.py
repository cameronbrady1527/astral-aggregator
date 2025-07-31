#!/usr/bin/env python3
"""
Health check script for Railway deployment.
This script tests if the FastAPI app is running and responding correctly.
"""

import sys
import os
import requests
import time
import socket

def is_port_open(port: int, host: str = 'localhost') -> bool:
    """Check if a port is open and listening."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(5)
            result = sock.connect_ex((host, port))
            return result == 0
    except Exception:
        return False

def check_health():
    """Check if the app is healthy."""
    try:
        # Get port from environment or use default
        port = int(os.getenv('PORT', '8000'))
        
        # Try multiple host addresses for Railway
        hosts = ['localhost', '127.0.0.1', '0.0.0.0']
        
        for host in hosts:
            print(f"Trying host: {host}")
            
            # First check if the port is open
            if not is_port_open(port, host):
                print(f"❌ Port {port} is not open on {host}")
                continue
            
            # Try ping endpoint first (simpler)
            ping_url = f"http://{host}:{port}/ping"
            print(f"Checking ping at: {ping_url}")
            
            try:
                response = requests.get(ping_url, timeout=10)
                print(f"Ping response status: {response.status_code}")
                print(f"Ping response content: {response.text}")
                
                if response.status_code == 200:
                    print("✅ Ping check passed")
                    return True
            except requests.exceptions.RequestException as e:
                print(f"❌ Ping failed on {host}: {e}")
                continue
            
            # If ping fails, try root endpoint
            root_url = f"http://{host}:{port}/"
            print(f"Checking root at: {root_url}")
            
            try:
                response = requests.get(root_url, timeout=10)
                print(f"Root response status: {response.status_code}")
                print(f"Root response content: {response.text[:200]}...")
                
                if response.status_code == 200:
                    print("✅ Root check passed")
                    return True
            except requests.exceptions.RequestException as e:
                print(f"❌ Root failed on {host}: {e}")
                continue
            
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    print("❌ Health check failed: no endpoints responded")
    return False

if __name__ == "__main__":
    # Wait a bit for the app to start up
    print("Waiting 30 seconds for app to start...")
    time.sleep(30)
    
    # Try multiple times with delays
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