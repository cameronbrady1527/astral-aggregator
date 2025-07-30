# ============================================================================== #
# main.py — Astral API Main Application                                        #
# ============================================================================== #
# FastAPI application entry point with document processing capabilities.        #
# ==============================================================================#


# ─── Standard Library ─────────────────────────────────────────────────────────
import json
from typing import List, Dict, Any


# ─── Third Party ──────────────────────────────────────────────────────────────
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse


# ─── Pydantic ──────────────────────────────────────────────────────────────────
from pydantic import BaseModel


# ─── Internal ──────────────────────────────────────────────────────────────────
from .routers import health_router, pm_router, agents_router


# ─── FastAPI Application ───────────────────────────────────────────────────────
app = FastAPI()




@app.get("/")
async def root():
   return {"status": "healthy",
           "service": "astral-api",
           "version": "0.0.1",
           "message": "Welcome to the Astral API"}


# ─── Router Configuration ──────────────────────────────────────────────────────
app.include_router(health_router)
app.include_router(pm_router)
app.include_router(agents_router)