#!/usr/bin/env python3
"""
Railway startup script
"""

import os
import subprocess
import sys

def main():
    print("Starting Astral Aggregator...")
    
    # Set environment variables
    os.environ['PYTHONPATH'] = '/app'
    os.environ['PYTHONUNBUFFERED'] = '1'
    
    print(f"Current directory: {os.getcwd()}")
    print(f"Python version: {sys.version}")
    print(f"PYTHONPATH: {os.environ.get('PYTHONPATH')}")
    
    # Create output directory
    os.makedirs('output', exist_ok=True)
    print("Output directory created")
    
    # Test app import
    try:
        import app.main
        print("✅ App imported successfully")
    except ImportError as e:
        print(f"❌ App import failed: {e}")
        sys.exit(1)
    
    # Get PORT with fallback
    port = os.environ.get('PORT', '8000')
    print(f"Using port: {port}")
    
    # Start uvicorn
    cmd = [
        sys.executable, '-m', 'uvicorn',
        'app.main:app',
        '--host', '0.0.0.0',
        '--port', port,
        '--workers', '1',
        '--log-level', 'info'
    ]
    
    print(f"Executing: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Uvicorn failed to start: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("🛑 Shutdown requested")
        sys.exit(0)

if __name__ == '__main__':
    main() 