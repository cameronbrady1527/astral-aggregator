#!/usr/bin/env python3
"""
Minimal uvicorn startup script for Railway deployment
Directly handles PORT environment variable issues
"""

import os
import sys
import subprocess

def main():
    print("🚀 Starting Astral Aggregator (Uvicorn startup)...")
    
    # Get port with fallback
    port = os.environ.get('PORT', '8000')
    print(f"Using port: {port}")
    
    # Validate port is a number
    if not port.isdigit():
        print(f"Warning: PORT '{port}' is not a valid number, using 8000")
        port = '8000'
    
    # Set environment variables
    os.environ['PYTHONPATH'] = '/app'
    os.environ['PYTHONUNBUFFERED'] = '1'
    
    # Create output directory
    os.makedirs('output', exist_ok=True)
    
    # Start uvicorn directly
    cmd = [
        sys.executable, '-m', 'uvicorn',
        'app.main:app',
        '--host', '0.0.0.0',
        '--port', port,
        '--workers', '1',
        '--log-level', 'info'
    ]
    
    print(f"Executing: {' '.join(cmd)}")
    
    # Execute uvicorn
    subprocess.run(cmd)

if __name__ == '__main__':
    main() 