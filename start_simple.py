#!/usr/bin/env python3
"""
Simplified startup script for Railway deployment
Minimal dependencies and error handling
"""

import os
import sys
import subprocess
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("🚀 Starting Astral Aggregator (Simple startup script)...")
    
    # Set essential environment variables
    os.environ['PYTHONPATH'] = '/app'
    os.environ['PYTHONUNBUFFERED'] = '1'
    
    logger.info(f"Current directory: {os.getcwd()}")
    logger.info(f"Python version: {sys.version}")
    
    # Create output directory
    try:
        os.makedirs('output', exist_ok=True)
        logger.info("✅ Output directory created")
    except Exception as e:
        logger.warning(f"⚠️ Could not create output directory: {e}")
    
    # Get port with fallback
    port = os.environ.get('PORT', '8000')
    if not port.isdigit():
        logger.warning(f"⚠️ Invalid PORT '{port}', using default 8000")
        port = '8000'
    
    logger.info(f"🎯 Using port: {port}")
    
    # Build uvicorn command
    cmd = [
        sys.executable, '-m', 'uvicorn',
        'app.main:app',
        '--host', '0.0.0.0',
        '--port', port,
        '--workers', '1',
        '--log-level', 'info'
    ]
    
    logger.info(f"Executing: {' '.join(cmd)}")
    
    # Execute uvicorn
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Uvicorn failed to start: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("🛑 Shutdown requested")
        sys.exit(0)

if __name__ == '__main__':
    main() 