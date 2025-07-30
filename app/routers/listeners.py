# ==============================================================================
# listeners.py — API Endpoints for Change Detection Listeners
# ==============================================================================
# Purpose: Provide endpoints for triggering and monitoring change detection
# Sections: Imports, Router Configuration, API Endpoints
# ==============================================================================

# ==============================================================================
# Imports
# ==============================================================================

# Standard Library -----
import asyncio
from typing import Dict, Any, List, Optional

# Third-Party -----
from fastapi import APIRouter, HTTPException, Query

# Internal -----
from ..crawler.change_detector import ChangeDetector

# ==============================================================================
# Router Configuration
# ==============================================================================

router = APIRouter(prefix="/api/listeners", tags=["listeners"])

# Global change detector instance
change_detector = ChangeDetector()

# ==============================================================================
# API Endpoints
# ==============================================================================

@router.post("/trigger/{site_id}")
async def trigger_site_detection(site_id: str) -> Dict[str, Any]:
    """Manually trigger change detection for a specific site."""
    try:
        results = await change_detector.detect_changes_for_site(site_id)
        return {
            "status": "success",
            "message": f"Change detection completed for {site_id}",
            "results": results
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")


@router.post("/trigger/all")
async def trigger_all_sites_detection() -> Dict[str, Any]:
    """Manually trigger change detection for all active sites."""
    try:
        results = await change_detector.detect_changes_for_all_sites()
        return {
            "status": "success",
            "message": "Change detection completed for all sites",
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")


@router.get("/status")
async def get_system_status() -> Dict[str, Any]:
    """Get the overall system status."""
    try:
        sites = change_detector.list_sites()
        return {
            "status": "healthy",
            "total_sites": len(sites),
            "active_sites": len([s for s in sites if s["is_active"]]),
            "sites": sites
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")


@router.get("/sites")
async def list_sites() -> List[Dict[str, Any]]:
    """List all configured sites."""
    try:
        return change_detector.list_sites()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list sites: {str(e)}")


@router.get("/sites/{site_id}")
async def get_site_status(site_id: str) -> Dict[str, Any]:
    """Get detailed status for a specific site."""
    try:
        status = change_detector.get_site_status(site_id)
        if "error" in status:
            raise HTTPException(status_code=404, detail=status["error"])
        return status
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get site status: {str(e)}")


@router.get("/changes/{site_id}")
async def get_site_changes(
    site_id: str,
    limit: int = Query(default=10, ge=1, le=100, description="Number of recent changes to return")
) -> Dict[str, Any]:
    """Get recent changes for a specific site."""
    try:
        site_config = change_detector.config_manager.get_site(site_id)
        if not site_config:
            raise HTTPException(status_code=404, detail=f"Site '{site_id}' not found")
        
        change_files = change_detector.writer.list_change_files(site_config.name)
        
        recent_changes = []
        for file_path in change_files[:limit]:
            try:
                change_data = change_detector.writer.read_json_file(file_path)
                recent_changes.append({
                    "file_path": file_path,
                    "detection_time": change_data.get("metadata", {}).get("detection_time"),
                    "summary": change_data.get("changes", {}).get("summary", {}),
                    "methods": list(change_data.get("changes", {}).get("methods", {}).keys())
                })
            except Exception as e:
                continue
        
        return {
            "site_id": site_id,
            "site_name": site_config.name,
            "recent_changes": recent_changes,
            "total_files": len(change_files)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get changes: {str(e)}")


@router.get("/changes")
async def get_all_changes(
    limit: int = Query(default=20, ge=1, le=100, description="Number of recent changes to return")
) -> Dict[str, Any]:
    """Get recent changes across all sites."""
    try:
        all_changes = []
        sites = change_detector.list_sites()
        
        for site in sites:
            site_changes = change_detector.writer.list_change_files(site["name"])
            for file_path in site_changes[:5]:
                try:
                    change_data = change_detector.writer.read_json_file(file_path)
                    all_changes.append({
                        "site_id": site["site_id"],
                        "site_name": site["name"],
                        "file_path": file_path,
                        "detection_time": change_data.get("metadata", {}).get("detection_time"),
                        "summary": change_data.get("changes", {}).get("summary", {})
                    })
                except Exception:
                    continue
        
        all_changes.sort(key=lambda x: x.get("detection_time", ""), reverse=True)
        
        return {
            "recent_changes": all_changes[:limit],
            "total_sites": len(sites)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get all changes: {str(e)}") 