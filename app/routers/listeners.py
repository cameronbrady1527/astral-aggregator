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

# Lazy initialization of change detector
_change_detector = None

def get_change_detector() -> ChangeDetector:
    """Get or create the change detector instance."""
    global _change_detector
    if _change_detector is None:
        try:
            _change_detector = ChangeDetector()
        except Exception as e:
            # If initialization fails, create a minimal detector for basic endpoints
            print(f"Warning: ChangeDetector initialization failed: {e}")
            _change_detector = None
    return _change_detector

# ==============================================================================
# API Endpoints
# ==============================================================================

@router.get("/")
async def listeners_root() -> Dict[str, Any]:
    """Root endpoint for listeners API with helpful information."""
    try:
        change_detector = get_change_detector()
        if change_detector is None:
            return {
                "message": "Website Change Detection API",
                "description": "Monitor websites for changes using sitemap and Firecrawl detection",
                "status": "initializing",
                "note": "System is starting up. Please try again in a moment."
            }
        
        sites = change_detector.list_sites()
        return {
            "message": "Website Change Detection API",
            "description": "Monitor websites for changes using sitemap and Firecrawl detection",
            "endpoints": {
                "trigger_site": "POST /api/listeners/trigger/{site_id}",
                "trigger_all": "POST /api/listeners/trigger/all",
                "status": "GET /api/listeners/status",
                "sites": "GET /api/listeners/sites",
                "site_status": "GET /api/listeners/sites/{site_id}",
                "site_changes": "GET /api/listeners/changes/{site_id}",
                "all_changes": "GET /api/listeners/changes"
            },
            "available_sites": [site["site_id"] for site in sites],
            "note": "Use POST for triggers, GET for viewing data. Visit /docs for interactive API documentation."
        }
    except Exception as e:
        return {
            "message": "Website Change Detection API",
            "description": "Monitor websites for changes using sitemap and Firecrawl detection",
            "status": "error",
            "error": str(e),
            "note": "System encountered an error. Please check logs."
        }


@router.get("/trigger/{site_id}")
async def trigger_site_info(site_id: str) -> Dict[str, Any]:
    """Show information about triggering detection for a specific site."""
    try:
        change_detector = get_change_detector()
        if change_detector is None:
            raise HTTPException(status_code=503, detail="System is initializing. Please try again.")
        
        site_config = change_detector.config_manager.get_site(site_id)
        if not site_config:
            raise HTTPException(status_code=404, detail=f"Site '{site_id}' not found")
        
        return {
            "message": f"To trigger change detection for {site_config.name}",
            "site_id": site_id,
            "site_name": site_config.name,
            "url": site_config.url,
            "detection_methods": site_config.detection_methods,
            "usage": f"Use: POST /api/listeners/trigger/{site_id}",
            "curl_example": f'curl -X POST "http://localhost:8000/api/listeners/trigger/{site_id}"',
            "powershell_example": f'Invoke-RestMethod -Uri "http://localhost:8000/api/listeners/trigger/{site_id}" -Method POST'
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get site info: {str(e)}")


@router.get("/trigger")
async def trigger_info() -> Dict[str, Any]:
    """Show information about triggering detection."""
    try:
        change_detector = get_change_detector()
        if change_detector is None:
            return {
                "message": "Change Detection Triggers",
                "description": "Use POST requests to trigger change detection",
                "status": "initializing",
                "note": "System is starting up. Please try again in a moment."
            }
        
        sites = change_detector.list_sites()
        return {
            "message": "Change Detection Triggers",
            "description": "Use POST requests to trigger change detection",
            "available_sites": [site["site_id"] for site in sites],
            "endpoints": {
                "trigger_site": "POST /api/listeners/trigger/{site_id}",
                "trigger_all": "POST /api/listeners/trigger/all"
            },
            "examples": {
                "curl": [
                    "curl -X POST \"http://localhost:8000/api/listeners/trigger/judiciary_uk\"",
                    "curl -X POST \"http://localhost:8000/api/listeners/trigger/all\""
                ],
                "powershell": [
                    "Invoke-RestMethod -Uri \"http://localhost:8000/api/listeners/trigger/judiciary_uk\" -Method POST",
                    "Invoke-RestMethod -Uri \"http://localhost:8000/api/listeners/trigger/all\" -Method POST"
                ]
            },
            "note": "These endpoints require POST requests, not GET requests."
        }
    except Exception as e:
        return {
            "message": "Change Detection Triggers",
            "description": "Use POST requests to trigger change detection",
            "status": "error",
            "error": str(e),
            "note": "System encountered an error. Please check logs."
        }


@router.post("/trigger/{site_id}")
async def trigger_site_detection(site_id: str) -> Dict[str, Any]:
    """Manually trigger change detection for a specific site."""
    try:
        change_detector = get_change_detector()
        if change_detector is None:
            raise HTTPException(status_code=503, detail="System is initializing. Please try again.")
        
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
        change_detector = get_change_detector()
        if change_detector is None:
            raise HTTPException(status_code=503, detail="System is initializing. Please try again.")
        
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
        change_detector = get_change_detector()
        if change_detector is None:
            return {
                "status": "initializing",
                "message": "System is starting up",
                "total_sites": 0,
                "active_sites": 0,
                "sites": []
            }
        
        sites = change_detector.list_sites()
        return {
            "status": "healthy",
            "total_sites": len(sites),
            "active_sites": len([s for s in sites if s["is_active"]]),
            "sites": sites
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"System error: {str(e)}",
            "total_sites": 0,
            "active_sites": 0,
            "sites": []
        }


@router.get("/sites")
async def list_sites() -> List[Dict[str, Any]]:
    """List all configured sites."""
    try:
        change_detector = get_change_detector()
        if change_detector is None:
            return []
        
        return change_detector.list_sites()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list sites: {str(e)}")


@router.get("/sites/{site_id}")
async def get_site_status(site_id: str) -> Dict[str, Any]:
    """Get detailed status for a specific site."""
    try:
        change_detector = get_change_detector()
        if change_detector is None:
            raise HTTPException(status_code=503, detail="System is initializing. Please try again.")
        
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
        change_detector = get_change_detector()
        if change_detector is None:
            raise HTTPException(status_code=503, detail="System is initializing. Please try again.")
        
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
        change_detector = get_change_detector()
        if change_detector is None:
            return {
                "recent_changes": [],
                "total_sites": 0,
                "status": "initializing"
            }
        
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