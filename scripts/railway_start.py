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
    
    # Create output directory
    os.makedirs('output', exist_ok=True)
    
    # Get PORT with fallback
    port = os.environ.get('PORT', '8000')
    print(f"Using port: {port}")
    
    # Start uvicorn
    cmd = [
        sys.executable, '-m', 'uvicorn',
        'app.main:app',
        '--host', '0.0.0.0',
        '--port', port,
        '--workers', '1'
    ]
    
    print(f"Executing: {' '.join(cmd)}")
    subprocess.run(cmd)

if __name__ == '__main__':
    main() 