#!/usr/bin/env python3
"""
Direct startup script - minimal and reliable
"""

import os
import sys
import subprocess

# Get port with fallback
port = os.environ.get('PORT', '8000')

# Ensure port is a valid number
if not port.isdigit():
    port = '8000'

print(f"Starting on port: {port}")

# Start uvicorn directly
subprocess.run([
    sys.executable, '-m', 'uvicorn',
    'app.main:app',
    '--host', '0.0.0.0',
    '--port', port,
    '--workers', '1'
]) 