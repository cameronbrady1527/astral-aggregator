#!/usr/bin/env python3
"""
Railway startup script - Optimized for Railway deployment
"""

import os
import subprocess
import sys
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("🚀 Starting Astral Aggregator on Railway...")
    
    # Set environment variables
    os.environ['PYTHONPATH'] = '/app'
    os.environ['PYTHONUNBUFFERED'] = '1'
    
    logger.info(f"Current directory: {os.getcwd()}")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"PYTHONPATH: {os.environ.get('PYTHONPATH')}")
    
    # Create output directory
    try:
        os.makedirs('output', exist_ok=True)
        logger.info("✅ Output directory created")
    except Exception as e:
        logger.warning(f"⚠️ Could not create output directory: {e}")
    
    # Test app import
    try:
        logger.info("Testing app import...")
        import app.main
        logger.info("✅ App imported successfully")
    except ImportError as e:
        logger.error(f"❌ App import failed: {e}")
        sys.exit(1)
    
    # Get PORT with fallback
    port = os.environ.get('PORT', '8000')
    if not port.isdigit():
        logger.warning(f"⚠️ Invalid PORT '{port}', using default 8000")
        port = '8000'
    
    logger.info(f"🎯 Using port: {port}")
    
    # Railway-optimized uvicorn command
    cmd = [
        sys.executable, '-m', 'uvicorn',
        'app.main:app',
        '--host', '0.0.0.0',
        '--port', port,
        '--workers', '1',
        '--log-level', 'info',
        '--timeout-keep-alive', '5',
        '--limit-concurrency', '50',
        '--limit-max-requests', '500'
    ]
    
    logger.info(f"Executing: {' '.join(cmd)}")
    
    # Start uvicorn with retry logic
    max_retries = 3
    for attempt in range(max_retries):
        try:
            logger.info(f"Starting uvicorn (attempt {attempt + 1}/{max_retries})")
            subprocess.run(cmd, check=True)
            break
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Uvicorn failed to start (attempt {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                wait_time = 5 * (attempt + 1)
                logger.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                logger.error("❌ All startup attempts failed")
                sys.exit(1)
        except KeyboardInterrupt:
            logger.info("🛑 Shutdown requested")
            sys.exit(0)

if __name__ == '__main__':
    main() 