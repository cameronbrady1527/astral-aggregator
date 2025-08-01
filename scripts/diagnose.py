#!/usr/bin/env python3
"""
Diagnostic script for troubleshooting startup and healthcheck issues
"""

import os
import sys
import importlib
import subprocess
import time

def check_environment():
    """Check environment variables and basic setup."""
    print("🔍 Environment Check")
    print("=" * 40)
    
    env_vars = [
        'PORT', 'PYTHONPATH', 'PYTHONUNBUFFERED', 
        'RAILWAY_ENVIRONMENT', 'RAILWAY_PUBLIC_DOMAIN'
    ]
    
    for var in env_vars:
        value = os.getenv(var, 'NOT SET')
        print(f"{var}: {value}")
    
    print(f"Current directory: {os.getcwd()}")
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print()

def check_imports():
    """Check if all required modules can be imported."""
    print("🔍 Import Check")
    print("=" * 40)
    
    modules = [
        'fastapi',
        'uvicorn',
        'aiohttp',
        'pyyaml',
        'python-dotenv',
        'firecrawl',
        'alembic',
        'sqlalchemy',
        'passlib',
        'python-jose',
        'python-multipart',
        'beautifulsoup4'
    ]
    
    failed_imports = []
    
    for module in modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n❌ Failed imports: {failed_imports}")
    else:
        print("\n✅ All imports successful")
    print()

def check_app_imports():
    """Check if app modules can be imported."""
    print("🔍 App Import Check")
    print("=" * 40)
    
    app_modules = [
        'app.main',
        'app.routers.listeners',
        'app.routers.dashboard',
        'app.crawler.change_detector',
        'app.utils.config',
        'app.utils.json_writer'
    ]
    
    failed_imports = []
    
    for module in app_modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            failed_imports.append(module)
        except Exception as e:
            print(f"⚠️ {module}: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n❌ Failed app imports: {failed_imports}")
    else:
        print("\n✅ All app imports successful")
    print()

def check_files():
    """Check if important files exist."""
    print("🔍 File Check")
    print("=" * 40)
    
    files = [
        'requirements.txt',
        'Dockerfile',
        'start_simple.py',
        'app/main.py',
        'config/sites.yaml',
        'output'
    ]
    
    for file_path in files:
        if os.path.exists(file_path):
            if os.path.isdir(file_path):
                print(f"✅ {file_path} (directory)")
            else:
                size = os.path.getsize(file_path)
                print(f"✅ {file_path} ({size} bytes)")
        else:
            print(f"❌ {file_path} (missing)")
    print()

def check_port():
    """Check if the port is available."""
    print("🔍 Port Check")
    print("=" * 40)
    
    port = os.getenv('PORT', '8000')
    print(f"Target port: {port}")
    
    try:
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', int(port)))
            if result == 0:
                print(f"❌ Port {port} is already in use")
            else:
                print(f"✅ Port {port} is available")
    except Exception as e:
        print(f"⚠️ Could not check port: {e}")
    print()

def main():
    print("🚀 Astral Aggregator Diagnostic Tool")
    print("=" * 50)
    print()
    
    check_environment()
    check_imports()
    check_app_imports()
    check_files()
    check_port()
    
    print("🔍 Summary")
    print("=" * 40)
    print("Diagnostic complete. Check the output above for any issues.")
    print("Common issues:")
    print("- Missing dependencies: Check requirements.txt")
    print("- Import errors: Check module paths and dependencies")
    print("- Port conflicts: Check if another service is using the port")
    print("- File permissions: Ensure files are readable")

if __name__ == "__main__":
    main() 