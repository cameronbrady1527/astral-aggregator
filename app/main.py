# ============================================================================== #
# main.py — Astral API Main Application                                        #
# ============================================================================== #
# FastAPI application entry point with document processing capabilities.        #
# ==============================================================================#

# ─── Standard Library ─────────────────────────────────────────────────────────
import json
import os
from typing import List, Dict, Any

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# ─── Third Party ──────────────────────────────────────────────────────────────
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse

# ─── Pydantic ──────────────────────────────────────────────────────────────────
from pydantic import BaseModel

# ─── FastAPI Application ───────────────────────────────────────────────────────
app = FastAPI(title="Astral API", description="Website Change Detection System")

# Global flag to track if app is fully initialized
app_initialized = False
routers_loaded = False

# Add startup logging
@app.on_event("startup")
async def startup_event():
    """Log startup information and include routers."""
    global app_initialized, routers_loaded
    
    print("🚀 Astral API starting up...")
    print(f"PORT environment variable: {os.getenv('PORT', 'NOT SET')}")
    print(f"PYTHONPATH environment variable: {os.getenv('PYTHONPATH', 'NOT SET')}")
    print(f"Current working directory: {os.getcwd()}")
    
    # Set Railway-specific configuration if in Railway environment
    if os.environ.get('RAILWAY_ENVIRONMENT'):
        print("📍 Railway environment detected - using optimized configuration")
        os.environ['CONFIG_FILE'] = 'config/sites_railway.yaml'
        print("✅ Railway configuration set")
    
    # Try to include routers (but don't fail if they don't work)
    try:
        print("Attempting to load routers...")
        from app.routers import listeners, dashboard
        app.include_router(listeners.router)
        app.include_router(dashboard.router)
        print("✅ Listeners and dashboard routers included successfully")
        routers_loaded = True
    except ImportError as e:
        print(f"⚠️ Router import failed: {e}")
        print("Continuing without routers...")
    except Exception as e:
        print(f"⚠️ Router loading failed: {e}")
        print("Continuing without routers...")
    
    # Create fallback endpoints if routers failed
    if not routers_loaded:
        @app.get("/api/listeners/status")
        async def fallback_status():
            return {
                "status": "initializing",
                "message": "System is starting up. Please try again in a moment.",
                "note": "Routers not loaded"
            }
    
    print("✅ Astral API startup complete!")
    app_initialized = True

@app.get("/ping")
async def ping():
    """Simple ping endpoint for Railway health checks."""
    print("📡 Ping endpoint called")
    return {"pong": "ok", "status": "healthy"}

@app.get("/health")
async def health_check():
    """Health check endpoint for Railway."""
    print("📡 Health endpoint called")
    return {
        "status": "healthy" if app_initialized else "initializing",
        "service": "astral-api",
        "version": "0.0.1",
        "initialized": app_initialized,
        "routers_loaded": routers_loaded
    }

@app.get("/")
async def root():
    print("📡 Root endpoint called")
    return {
        "status": "healthy" if app_initialized else "initializing",
        "service": "astral-api",
        "version": "0.0.1",
        "message": "Welcome to the Astral API - Website Change Detection System",
        "endpoints": {
            "health_check": "/health",
            "ping": "/ping",
            "api_docs": "/docs",
            "dashboard": "/dashboard/"
        },
        "initialized": app_initialized,
        "routers_loaded": routers_loaded
    }

# Add a simple test endpoint
@app.get("/test")
async def test():
    """Test endpoint to verify the app is working."""
    print("📡 Test endpoint called")
    return {
        "message": "Astral API is working!",
        "timestamp": "now",
        "status": "success",
        "initialized": app_initialized,
        "routers_loaded": routers_loaded
    }

@app.get("/debug")
async def debug_info():
    """Debug endpoint for troubleshooting deployment issues."""
    print("📡 Debug endpoint called")
    import sys
    import platform
    
    return {
        "status": "debug",
        "app_initialized": app_initialized,
        "routers_loaded": routers_loaded,
        "environment": {
            "python_version": sys.version,
            "platform": platform.platform(),
            "current_directory": os.getcwd(),
            "pythonpath": os.environ.get('PYTHONPATH', 'NOT SET'),
            "port": os.environ.get('PORT', 'NOT SET'),
            "railway_environment": os.environ.get('RAILWAY_ENVIRONMENT', 'NOT SET'),
            "railway_public_domain": os.environ.get('RAILWAY_PUBLIC_DOMAIN', 'NOT SET'),
            "config_file": os.environ.get('CONFIG_FILE', 'config/sites.yaml')
        },
        "available_modules": {
            "fastapi": "fastapi" in sys.modules,
            "uvicorn": "uvicorn" in sys.modules,
            "aiohttp": "aiohttp" in sys.modules,
            "pyyaml": "yaml" in sys.modules,
            "python_dotenv": "dotenv" in sys.modules,
            "firecrawl": "firecrawl" in sys.modules,
            "sqlalchemy": "sqlalchemy" in sys.modules,
            "passlib": "passlib" in sys.modules,
            "python_jose": "jose" in sys.modules,
            "beautifulsoup4": "bs4" in sys.modules
        }
    }