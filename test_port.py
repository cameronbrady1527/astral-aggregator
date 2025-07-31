#!/usr/bin/env python3
"""
Test script to verify PORT environment variable handling
"""

import os
import sys

def main():
    print("🔍 Testing PORT environment variable...")
    
    # Log all environment variables
    print("Environment variables:")
    for key, value in sorted(os.environ.items()):
        print(f"  {key}: {value}")
    
    # Get PORT
    port = os.environ.get('PORT')
    print(f"\nPORT from environment: {port}")
    print(f"PORT type: {type(port)}")
    
    if port:
        print(f"PORT is digit: {port.isdigit()}")
        print(f"PORT == '$PORT': {port == '$PORT'}")
    
    # Test fallback
    final_port = port if port and port.isdigit() else '8000'
    print(f"\nFinal port: {final_port}")
    
    # Test uvicorn command
    cmd = [
        sys.executable, '-m', 'uvicorn',
        'app.main:app',
        '--host', '0.0.0.0',
        '--port', final_port,
        '--workers', '1'
    ]
    
    print(f"\nWould execute: {' '.join(cmd)}")

if __name__ == '__main__':
    main() 