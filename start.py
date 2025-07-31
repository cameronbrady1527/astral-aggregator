#!/usr/bin/env python3
"""
Python-based startup script for Railway deployment
This provides an alternative to the shell script for better reliability
"""

import os
import sys
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("🚀 Starting Astral Aggregator (Python startup script)...")
    
    # Set environment variables
    os.environ['PYTHONPATH'] = '/app'
    os.environ['PYTHONUNBUFFERED'] = '1'
    
    logger.info(f"Current directory: {os.getcwd()}")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"PYTHONPATH: {os.environ.get('PYTHONPATH')}")
    
    # Log all environment variables for debugging
    logger.info("Environment variables:")
    for key, value in sorted(os.environ.items()):
        logger.info(f"  {key}: {value}")
    
    # Create output directory
    os.makedirs('output', exist_ok=True)
    logger.info("Output directory created")
    
    # Test app import
    try:
        import app.main
        logger.info("✅ App imported successfully")
    except ImportError as e:
        logger.error(f"❌ App import failed: {e}")
        sys.exit(1)
    
    # Get port configuration with multiple strategies
    port = None
    
    # Strategy 1: Direct environment variable
    port = os.environ.get('PORT')
    if port:
        logger.info(f"📡 PORT from environment: {port}")
    
    # Strategy 2: Check if PORT is literal '$PORT' string
    if port == '$PORT':
        logger.warning("⚠️  PORT is literal '$PORT' string - Railway environment expansion failed")
        logger.info("Trying to get PORT from alternative sources...")
        
        # Try to get PORT from Railway's internal environment variables
        railway_vars = ['RAILWAY_STATIC_URL', 'RAILWAY_PUBLIC_DOMAIN', 'PORT']
        for var in railway_vars:
            value = os.environ.get(var)
            if value and ':' in value:
                try:
                    potential_port = value.split(':')[-1]
                    if potential_port.isdigit():
                        port = potential_port
                        logger.info(f"📡 PORT extracted from {var}: {port}")
                        break
                except:
                    continue
        
        # If still no valid port, use default
        if not port or not port.isdigit():
            logger.warning("⚠️  Could not extract valid PORT, using default 8000")
            port = '8000'
    
    # Strategy 3: Validate and fallback
    if not port:
        logger.warning("⚠️  PORT environment variable is not set, using default port 8000")
        port = '8000'
    elif not port.isdigit():
        logger.error(f"❌ PORT is not a valid number: {port}")
        logger.info("Using default port 8000")
        port = '8000'
    else:
        logger.info(f"✅ PORT is valid: {port}")
    
    logger.info(f"🎯 Final port configuration: {port}")
    
    # Start uvicorn
    logger.info(f"Starting uvicorn server on port {port}")
    logger.info("Host: 0.0.0.0")
    
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