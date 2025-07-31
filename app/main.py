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

@app.get("/ping")
async def ping():
    """Simple ping endpoint for Railway health checks."""
    return {"pong": "ok"}

@app.get("/health")
async def health_check():
    """Health check endpoint for Railway."""
    return {
        "status": "healthy",
        "service": "astral-api",
        "version": "0.0.1"
    }

@app.get("/")
async def root():
    return {
        "status": "healthy",
        "service": "astral-api",
        "version": "0.0.1",
        "message": "Welcome to the Astral API - Website Change Detection System",
        "endpoints": {
            "health_check": "/health",
            "ping": "/ping",
            "api_docs": "/docs"
        }
    }

# Only include the router if we can import it successfully
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