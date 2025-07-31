#!/usr/bin/env python3
"""
Railway-specific startup script with enhanced PORT environment variable handling
"""

import os
import sys
import subprocess
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def main():
    logger.info("🚀 Starting Astral Aggregator (Railway startup script)...")
    
    # Log all environment variables for debugging
    logger.info("Environment variables:")
    for key, value in sorted(os.environ.items()):
        logger.info(f"  {key}: {value}")
    
    # Set environment variables
    os.environ['PYTHONPATH'] = '/app'
    os.environ['PYTHONUNBUFFERED'] = '1'
    
    logger.info(f"Current directory: {os.getcwd()}")
    logger.info(f"Python version: {sys.version}")
    
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
    
    # Get port with multiple fallback strategies
    port = None
    
    # Strategy 1: Direct environment variable
    port = os.environ.get('PORT')
    if port:
        logger.info(f"📡 PORT from environment: {port}")
    
    # Strategy 2: Check if PORT is a literal string '$PORT' and try to get actual value
    if port == '$PORT':
        logger.warning("⚠️  PORT is literal '$PORT' string, trying alternative methods")
        # Try to get PORT from Railway's internal environment
        port = os.environ.get('RAILWAY_STATIC_URL', '').split(':')[-1] if ':' in os.environ.get('RAILWAY_STATIC_URL', '') else None
        if port:
            logger.info(f"📡 PORT from RAILWAY_STATIC_URL: {port}")
    
    # Strategy 3: Use default if still no valid port
    if not port or not port.isdigit():
        logger.warning("⚠️  No valid PORT found, using default port 8000")
        port = '8000'
    
    # Final validation
    if not port.isdigit():
        logger.error(f"❌ PORT '{port}' is not a valid number")
        port = '8000'
    
    logger.info(f"🎯 Final port configuration: {port}")
    
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