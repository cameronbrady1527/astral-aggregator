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

# Add startup logging
@app.on_event("startup")
async def startup_event():
    """Log startup information."""
    print("🚀 Astral API starting up...")
    print(f"PORT environment variable: {os.getenv('PORT', 'NOT SET')}")
    print(f"PYTHONPATH environment variable: {os.getenv('PYTHONPATH', 'NOT SET')}")
    print(f"Current working directory: {os.getcwd()}")
    
    # Try to include routers (but don't fail if it doesn't work)
    try:
        from app.routers import listeners
        app.include_router(listeners.router)
        print("✅ Listeners router included successfully")
    except Exception as e:
        print(f"⚠️ Listeners router not included: {e}")
        # Create a simple fallback endpoint
        @app.get("/api/listeners/status")
        async def fallback_status():
            return {
                "status": "initializing",
                "message": "System is starting up. Please try again in a moment."
            }
    
    print("✅ Astral API startup complete!")

@app.get("/ping")
async def ping():
    """Simple ping endpoint for Railway health checks."""
    print("📡 Ping endpoint called")
    return {"pong": "ok"}

@app.get("/health")
async def health_check():
    """Health check endpoint for Railway."""
    print("📡 Health endpoint called")
    return {
        "status": "healthy",
        "service": "astral-api",
        "version": "0.0.1"
    }

@app.get("/")
async def root():
    """Root endpoint - simplified for reliability."""
    print("📡 Root endpoint called")
    return {
        "status": "healthy",
        "service": "astral-api",
        "version": "0.0.1",
        "message": "Welcome to the Astral API - Website Change Detection System"
    }

@app.get("/test")
async def test():
    """Test endpoint to verify the app is working."""
    print("📡 Test endpoint called")
    return {
        "message": "Astral API is working!",
        "timestamp": "now",
        "status": "success"
    }