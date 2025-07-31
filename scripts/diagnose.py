#!/usr/bin/env python3
"""
Diagnostic script for Railway deployment issues.
This script helps identify common problems that cause healthcheck failures.
"""

import os
import sys
import socket
import requests
import subprocess
import time

def check_environment():
    """Check environment variables."""
    print("=== Environment Variables ===")
    important_vars = ['PORT', 'PYTHONPATH', 'FIRECRAWL_API_KEY', 'LOG_LEVEL']
    
    for var in important_vars:
        value = os.getenv(var)
        if value:
            if var == 'FIRECRAWL_API_KEY':
                print(f"{var}: {'*' * len(value)} (hidden)")
            else:
                print(f"{var}: {value}")
        else:
            print(f"{var}: NOT SET")
    
    print()

def check_dependencies():
    """Check if all dependencies are available."""
    print("=== Dependencies ===")
    deps = ['fastapi', 'uvicorn', 'requests', 'yaml', 'aiohttp']
    
    for dep in deps:
        try:
            __import__(dep)
            print(f"✅ {dep}")
        except ImportError:
            print(f"❌ {dep} - MISSING")
    
    print()

def check_configuration():
    """Check configuration loading."""
    print("=== Configuration ===")
    
    try:
        from app.utils.config import ConfigManager
        config = ConfigManager()
        print(f"✅ Configuration loaded successfully")
        print(f"Found {len(config.sites)} sites")
        for site_id, site in config.sites.items():
            print(f"  - {site_id}: {site.name}")
    except Exception as e:
        print(f"❌ Configuration loading failed: {e}")
        import traceback
        traceback.print_exc()
    
    print()

def check_app_import():
    """Check if the app can be imported."""
    print("=== App Import ===")
    
    try:
        from app.main import app
        print("✅ App imported successfully")
    except Exception as e:
        print(f"❌ App import failed: {e}")
        import traceback
        traceback.print_exc()
    
    print()

def check_port_availability():
    """Check if the port is available."""
    print("=== Port Availability ===")
    
    port = int(os.getenv('PORT', '8000'))
    hosts = ['localhost', '127.0.0.1', '0.0.0.0']
    
    for host in hosts:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(5)
                result = sock.connect_ex((host, port))
                if result == 0:
                    print(f"✅ Port {port} is open on {host}")
                else:
                    print(f"❌ Port {port} is closed on {host}")
        except Exception as e:
            print(f"❌ Error checking port {port} on {host}: {e}")
    
    print()

def check_health_endpoints():
    """Check health endpoints."""
    print("=== Health Endpoints ===")
    
    port = int(os.getenv('PORT', '8000'))
    hosts = ['localhost', '127.0.0.1', '0.0.0.0']
    endpoints = ['/ping', '/health', '/']
    
    for host in hosts:
        print(f"Testing {host}:")
        for endpoint in endpoints:
            url = f"http://{host}:{port}{endpoint}"
            try:
                response = requests.get(url, timeout=5)
                print(f"  {endpoint}: {response.status_code} - {response.text[:50]}...")
            except requests.exceptions.RequestException as e:
                print(f"  {endpoint}: ERROR - {e}")
        print()

def check_processes():
    """Check running processes."""
    print("=== Running Processes ===")
    
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        for line in lines:
            if 'python' in line or 'uvicorn' in line:
                print(line)
    except Exception as e:
        print(f"Error checking processes: {e}")
    
    print()

def main():
    """Run all diagnostic checks."""
    print("🔍 Railway Deployment Diagnostics")
    print("=" * 50)
    
    checks = [
        ("Environment", check_environment),
        ("Dependencies", check_dependencies),
        ("Configuration", check_configuration),
        ("App Import", check_app_import),
        ("Port Availability", check_port_availability),
        ("Health Endpoints", check_health_endpoints),
        ("Processes", check_processes),
    ]
    
    for name, check_func in checks:
        try:
            check_func()
        except Exception as e:
            print(f"❌ {name} check failed: {e}")
            print()

if __name__ == "__main__":
    main() 