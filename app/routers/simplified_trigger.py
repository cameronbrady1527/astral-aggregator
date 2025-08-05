#!/usr/bin/env python3
"""
Simplified Trigger Router - High-performance change detection triggers
This module provides simplified trigger endpoints that use the new simplified change detector.
"""

import asyncio
import json
from typing import Dict, Any, List
from pathlib import Path
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

try:
    from app.utils.simplified_change_detector import SimplifiedChangeDetector
except ImportError:
    from ..utils.simplified_change_detector import SimplifiedChangeDetector

router = APIRouter(prefix="/api/simplified", tags=["simplified-trigger"])

# Global detection status tracking
detection_status = {
    "is_running": False,
    "current_site": None,
    "progress": 0,
    "message": "",
    "total_pages": 0
}

def update_detection_status(**kwargs):
    """Update global detection status."""
    global detection_status
    detection_status.update(kwargs)

@router.post("/trigger/{site_id}")
async def trigger_site_detection(site_id: str) -> Dict[str, Any]:
    """
    Trigger simplified change detection for a specific site.
    
    This endpoint uses the new simplified change detector for better performance.
    """
    try:
        # Check if detection is already running
        if detection_status["is_running"]:
            return {
                "status": "busy",
                "message": "Detection already in progress",
                "current_site": detection_status["current_site"]
            }
        
        # Initialize simplified change detector
        detector = SimplifiedChangeDetector()
        
        # Update status
        update_detection_status(
            is_running=True,
            current_site=site_id,
            progress=0,
            message=f"Starting simplified change detection for {site_id}...",
            total_pages=0
        )
        
        # Run detection in background
        async def run_detection():
            try:
                # Update progress
                update_detection_status(progress=25, message="Fetching sitemap URLs...")
                await asyncio.sleep(0.1)
                
                update_detection_status(progress=50, message="Calculating content hashes...")
                await asyncio.sleep(0.1)
                
                # Run actual detection
                results = await detector.detect_changes_for_site(site_id)
                
                # Update final status
                if results.get("baseline_updated"):
                    message = f"Detection completed - {results['summary']['total_changes']} changes detected"
                else:
                    message = "Detection completed - no changes detected"
                
                update_detection_status(
                    is_running=False,
                    current_site=None,
                    progress=100,
                    message=message,
                    total_pages=results.get("summary", {}).get("total_changes", 0)
                )
                
            except Exception as e:
                update_detection_status(
                    is_running=False,
                    current_site=None,
                    progress=0,
                    message=f"Detection failed: {str(e)}"
                )
                raise e
        
        # Start detection in background
        asyncio.create_task(run_detection())
        
        return {
            "status": "started",
            "message": f"Simplified change detection started for {site_id}",
            "progress_url": "/api/simplified/progress",
            "note": "Use GET /api/simplified/progress to monitor progress"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/progress")
async def get_detection_progress() -> Dict[str, Any]:
    """Get current detection progress."""
    global detection_status
    return detection_status

@router.get("/changes/{site_id}")
async def get_site_changes(site_id: str, limit: int = Query(default=10, ge=1, le=100)) -> Dict[str, Any]:
    """Get recent changes for a specific site."""
    try:
        changes_dir = Path("changes")
        if not changes_dir.exists():
            return {
                "site_id": site_id,
                "changes": [],
                "message": "No changes directory found"
            }
        
        # Find change files for this site
        change_files = list(changes_dir.glob(f"{site_id}_*_changes.json"))
        change_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        all_changes = []
        for file_path in change_files[:limit]:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    changes = data.get("changes", [])
                    all_changes.extend(changes)
            except Exception as e:
                print(f"Error reading change file {file_path}: {e}")
        
        return {
            "site_id": site_id,
            "total_changes": len(all_changes),
            "changes": all_changes[:limit],
            "files_checked": len(change_files)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_system_status() -> Dict[str, Any]:
    """Get overall system status."""
    try:
        detector = SimplifiedChangeDetector()
        
        # Get baseline info
        baseline_manager = detector.baseline_manager
        baseline_events = baseline_manager.get_baseline_events(limit=5)
        
        return {
            "status": "operational",
            "simplified_detector": "available",
            "recent_baseline_events": baseline_events,
            "detection_status": detection_status
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

@router.get("/baselines")
async def list_baselines() -> Dict[str, Any]:
    """List all baselines managed by the simplified system."""
    try:
        detector = SimplifiedChangeDetector()
        baseline_manager = detector.baseline_manager
        
        # Get all baselines
        all_baselines = baseline_manager.list_baselines()
        
        return {
            "status": "success",
            "baselines": all_baselines,
            "total_sites": len(all_baselines) if isinstance(all_baselines, dict) else 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/baselines/{site_id}")
async def get_site_baseline(site_id: str) -> Dict[str, Any]:
    """Get the latest baseline for a specific site."""
    try:
        detector = SimplifiedChangeDetector()
        baseline_manager = detector.baseline_manager
        
        # Get latest baseline
        baseline = baseline_manager.get_latest_baseline(site_id)
        
        if not baseline:
            return {
                "site_id": site_id,
                "baseline": None,
                "message": "No baseline found for this site"
            }
        
        return {
            "site_id": site_id,
            "baseline": {
                "baseline_date": baseline.get("baseline_date"),
                "total_urls": baseline.get("total_urls", 0),
                "total_content_hashes": baseline.get("total_content_hashes", 0),
                "created_at": baseline.get("created_at")
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 