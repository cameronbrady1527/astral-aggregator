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


# ─── Internal ──────────────────────────────────────────────────────────────────
from app.routers import listeners


# ─── FastAPI Application ───────────────────────────────────────────────────────
app = FastAPI()


@app.get("/health")
async def health_check():
    """Simple health check endpoint for Railway."""
    return {
        "status": "healthy",
        "service": "astral-api",
        "version": "0.0.1"
    }


@app.get("/ping")
async def ping():
    """Simple ping endpoint for basic health checks."""
    return {"pong": "ok"}


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
           "api_docs": "/docs",
           "listeners_api": "/api/listeners",
           "listeners_root": "/api/listeners/",
           "trigger_info": "/api/listeners/trigger",
           "system_status": "/api/listeners/status",
           "all_sites": "/api/listeners/sites"
       },
       "quick_start": {
           "view_system_status": "GET /api/listeners/status",
           "trigger_detection": "POST /api/listeners/trigger/judiciary_uk",
           "view_changes": "GET /api/listeners/changes/judiciary_uk"
       },
       "note": "Use POST for triggers, GET for viewing data. Visit /docs for interactive API documentation."
   }


# ─── Router Configuration ──────────────────────────────────────────────────────
app.include_router(listeners.router)