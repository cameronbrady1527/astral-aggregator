#!/usr/bin/env python3
"""
Deployment debug script for Railway
This script helps diagnose environment and startup issues
"""

import os
import sys
import subprocess
import platform

def main():
    print("🔍 Railway Deployment Debug Information")
    print("=" * 50)
    
    # System information
    print(f"Python version: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Python executable: {sys.executable}")
    
    # Environment variables
    print("\n📋 Environment Variables:")
    for key, value in sorted(os.environ.items()):
        print(f"  {key}: {value}")
    
    # File system check
    print("\n📁 File System Check:")
    important_files = [
        'start.sh', 'start.py', 'app/main.py', 'requirements.txt',
        'Dockerfile', 'railway.toml'
    ]
    
    for file_path in important_files:
        if os.path.exists(file_path):
            print(f"  ✅ {file_path} exists")
            if os.path.isfile(file_path):
                size = os.path.getsize(file_path)
                print(f"     Size: {size} bytes")
        else:
            print(f"  ❌ {file_path} missing")
    
    # Python path check
    print("\n🐍 Python Path Check:")
    for path in sys.path:
        print(f"  {path}")
    
    # App import test
    print("\n📦 App Import Test:")
    try:
        import app.main
        print("  ✅ app.main imported successfully")
        
        # Check if app has the expected attributes
        if hasattr(app.main, 'app'):
            print("  ✅ app.main.app exists")
        else:
            print("  ❌ app.main.app missing")
            
    except ImportError as e:
        print(f"  ❌ Failed to import app.main: {e}")
    
    # Uvicorn availability
    print("\n🚀 Uvicorn Check:")
    try:
        import uvicorn
        print(f"  ✅ Uvicorn version: {uvicorn.__version__}")
    except ImportError as e:
        print(f"  ❌ Uvicorn not available: {e}")
    
    # Port configuration test
    print("\n🔌 Port Configuration Test:")
    port = os.environ.get('PORT')
    if port:
        print(f"  PORT environment variable: {port}")
        if port.isdigit():
            print(f"  ✅ PORT is a valid number: {port}")
        else:
            print(f"  ❌ PORT is not a valid number: {port}")
    else:
        print("  ⚠️  PORT environment variable not set")
    
    # Test uvicorn command
    print("\n🧪 Uvicorn Command Test:")
    test_port = port if port and port.isdigit() else '8000'
    cmd = [
        sys.executable, '-m', 'uvicorn',
        'app.main:app',
        '--host', '0.0.0.0',
        '--port', test_port,
        '--help'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("  ✅ Uvicorn command works")
        else:
            print(f"  ❌ Uvicorn command failed: {result.stderr}")
    except subprocess.TimeoutExpired:
        print("  ⏰ Uvicorn command timed out")
    except Exception as e:
        print(f"  ❌ Uvicorn command error: {e}")

if __name__ == '__main__':
    main() 