#!/usr/bin/env python3
"""
Consolidated startup script for Astral Aggregator
Handles both local development and Railway deployment
"""

import os
import sys
import subprocess
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("🚀 Starting Astral Aggregator...")
    
    # Environment detection
    current_dir = os.getcwd()
    is_railway = os.environ.get('RAILWAY_ENVIRONMENT') is not None
    
    if is_railway:
        logger.info("📍 Detected Railway environment")
    else:
        logger.info("📍 Detected local environment")
    
    # Environment setup
    logger.info(f"Current directory: {current_dir}")
    logger.info(f"Python version: {sys.version}")
    
    # Railway environment variables
    port = os.environ.get('PORT', '8000')
    railway_env = os.environ.get('RAILWAY_ENVIRONMENT', 'unknown')
    railway_domain = os.environ.get('RAILWAY_PUBLIC_DOMAIN', 'unknown')
    
    logger.info(f"Railway Environment: {railway_env}")
    logger.info(f"Railway Domain: {railway_domain}")
    logger.info(f"Port: {port}")
    logger.info(f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'NOT SET')}")
    
    # Set PYTHONPATH if not already set (respect Docker environment)
    if not os.environ.get('PYTHONPATH'):
        os.environ['PYTHONPATH'] = current_dir
        logger.info(f"PYTHONPATH set to: {current_dir}")
    else:
        logger.info(f"PYTHONPATH already set to: {os.environ.get('PYTHONPATH')}")
    
    os.environ['PYTHONUNBUFFERED'] = '1'
    
    # Create output directory
    try:
        os.makedirs('output', exist_ok=True)
        logger.info("✅ Output directory created")
    except Exception as e:
        logger.warning(f"⚠️ Could not create output directory: {e}")
    
    # Test basic imports before starting
    try:
        logger.info("Testing basic imports...")
        import fastapi
        import uvicorn
        logger.info("✅ Basic imports successful")
    except ImportError as e:
        logger.error(f"❌ Basic import failed: {e}")
        sys.exit(1)
    
    # Validate port
    if not port.isdigit():
        logger.warning(f"⚠️ Invalid PORT '{port}', using default 8000")
        port = '8000'
    
    logger.info(f"🎯 Using port: {port}")
    
    # Build uvicorn command with environment-specific settings
    if is_railway:
        # Railway-optimized settings
        cmd = [
            sys.executable, '-m', 'uvicorn',
            'app.main:app',
            '--host', '0.0.0.0',
            '--port', port,
            '--workers', '1',
            '--log-level', 'info'
        ]
    else:
        # Local development settings with more features
        cmd = [
            sys.executable, '-m', 'uvicorn',
            'app.main:app',
            '--host', '0.0.0.0',
            '--port', port,
            '--workers', '1',
            '--log-level', 'info',
            '--timeout-keep-alive', '30',
            '--limit-concurrency', '100',
            '--limit-max-requests', '1000'
        ]
    
    logger.info(f"Executing: {' '.join(cmd)}")
    
    # Execute uvicorn with retry logic
    max_retries = 3 if is_railway else 1
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