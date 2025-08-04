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
from datetime import datetime, timedelta
import json

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

# Global variables for tracking detection progress
current_detection_status = {
    "is_running": False,
    "current_site": None,
    "current_method": None,
    "start_time": None,
    "progress": 0,
    "message": "",
    "estimated_time_remaining": None,
    "pages_processed": 0,
    "total_pages": 0,
    "credits_used": 0
}

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

def update_detection_status(**kwargs):
    """Update the current detection status."""
    global current_detection_status
    current_detection_status.update(kwargs)

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
                "all_changes": "GET /api/listeners/changes",
                "analytics": "GET /api/listeners/analytics",
                "site_analytics": "GET /api/listeners/analytics/{site_id}",
                "realtime": "GET /api/listeners/realtime",
                "history": "GET /api/listeners/history"
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
    """
    Trigger change detection for a specific site.
    
    This endpoint starts the change detection process and returns immediately.
    Use the progress endpoint to monitor the detection status.
    """
    try:
        # Initialize change detector
        change_detector = ChangeDetector()
        
        # Update detection status
        def update_detection_status(current_method: str = "", progress: int = 0, 
                                  message: str = "", is_running: bool = True):
            detection_status.update(
                current_method=current_method,
                progress=progress,
                message=message,
                is_running=is_running,
                total_pages=0,
                credits_used=0
            )
        
        # Run detection with progress updates
        async def run_detection_with_progress():
            try:
                site_config = change_detector.config_manager.get_site(site_id)
                
                # Update status for each method
                for i, method in enumerate(site_config.detection_methods):
                    update_detection_status(
                        current_method=method,
                        progress=int((i / len(site_config.detection_methods)) * 50),
                        message=f"Running {method} detection..."
                    )
                    
                    # Add a small delay to allow progress updates
                    await asyncio.sleep(0.1)
                
                # Run the actual detection
                results = await change_detector.detect_changes_for_site(site_id)
                
                # Update final status
                update_detection_status(
                    progress=100,
                    message="Detection completed successfully",
                    is_running=False
                )
                
                return results
            except Exception as e:
                update_detection_status(
                    progress=0,
                    message=f"Detection failed: {str(e)}",
                    is_running=False
                )
                raise e
        
        # Start detection in background
        asyncio.create_task(run_detection_with_progress())
        
        return {
            "status": "started",
            "message": f"Change detection started for {site_id}",
            "baseline_evolution_enabled": True,
            "baseline_updated": False,  # Will be updated when detection completes
            "progress_url": "/api/listeners/progress",
            "note": "Use GET /api/listeners/progress to monitor progress"
        }
    except ValueError as e:
        update_detection_status(
            progress=0,
            message=f"Detection failed: {str(e)}",
            is_running=False
        )
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        update_detection_status(
            progress=0,
            message=f"Detection failed: {str(e)}",
            is_running=False
        )
        raise HTTPException(status_code=500, detail=str(e))


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
        # Filter out state files (files with "state" in the name)
        actual_change_files = [f for f in change_files if "state" not in f.lower()]
        
        recent_changes = []
        for file_path in actual_change_files[:limit]:
            try:
                change_data = change_detector.writer.read_json_file(file_path)
                detection_time = change_data.get("metadata", {}).get("detection_time")
                
                # Only include files with valid detection times
                if detection_time:
                    # Get summary from the changes data
                    changes_data = change_data.get("changes", {})
                    
                    # Check if there's a direct summary (for older format)
                    summary = changes_data.get("summary", {})
                    
                    # If no direct summary, check methods for summary
                    if not summary and "methods" in changes_data:
                        combined_summary = {
                            "total_changes": 0,
                            "new_pages": 0,
                            "modified_pages": 0,
                            "deleted_pages": 0
                        }
                        for method_name, method_data in changes_data["methods"].items():
                            method_summary = method_data.get("summary", {})
                            combined_summary["total_changes"] += method_summary.get("total_changes", 0)
                            combined_summary["new_pages"] += method_summary.get("new_pages", 0)
                            combined_summary["modified_pages"] += method_summary.get("modified_pages", 0)
                            combined_summary["deleted_pages"] += method_summary.get("deleted_pages", 0)
                        summary = combined_summary
                    
                    recent_changes.append({
                        "file_path": file_path,
                        "detection_time": detection_time,
                        "summary": summary,
                        "methods": list(changes_data.get("methods", {}).keys())
                    })
            except Exception as e:
                print(f"Error processing change file {file_path}: {e}")
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
            # Filter out state files (files with "state" in the name)
            change_files = [f for f in site_changes if "state" not in f.lower()]
            
            for file_path in change_files[:5]:
                try:
                    change_data = change_detector.writer.read_json_file(file_path)
                    detection_time = change_data.get("metadata", {}).get("detection_time")
                    
                    # Only include files with valid detection times
                    if detection_time:
                        # Get summary from the changes data
                        changes_data = change_data.get("changes", {})
                        
                        # Check if there's a direct summary (for older format)
                        summary = changes_data.get("summary", {})
                        
                        # If no direct summary, check methods for summary
                        if not summary and "methods" in changes_data:
                            combined_summary = {
                                "total_changes": 0,
                                "new_pages": 0,
                                "modified_pages": 0,
                                "deleted_pages": 0
                            }
                            for method_name, method_data in changes_data["methods"].items():
                                method_summary = method_data.get("summary", {})
                                combined_summary["total_changes"] += method_summary.get("total_changes", 0)
                                combined_summary["new_pages"] += method_summary.get("new_pages", 0)
                                combined_summary["modified_pages"] += method_summary.get("modified_pages", 0)
                                combined_summary["deleted_pages"] += method_summary.get("deleted_pages", 0)
                            summary = combined_summary
                        
                        all_changes.append({
                            "site_id": site["site_id"],
                            "site_name": site["name"],
                            "file_path": file_path,
                            "detection_time": detection_time,
                            "summary": summary
                        })
                except Exception as e:
                    print(f"Error processing change file {file_path}: {e}")
                    continue
        
        all_changes.sort(key=lambda x: x.get("detection_time", ""), reverse=True)
        
        return {
            "recent_changes": all_changes[:limit],
            "total_sites": len(sites)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get all changes: {str(e)}")


@router.get("/analytics")
async def get_system_analytics() -> Dict[str, Any]:
    """Get comprehensive system analytics and statistics."""
    try:
        change_detector = get_change_detector()
        if change_detector is None:
            return {
                "status": "initializing",
                "message": "System is starting up",
                "analytics": {}
            }
        
        sites = change_detector.list_sites()
        total_urls = 0
        total_changes = 0
        site_analytics = []
        
        for site in sites:
            site_config = change_detector.config_manager.get_site(site["site_id"])
            if not site_config:
                continue
                
            # Get recent changes and state for this site
            change_files = change_detector.writer.list_change_files(site_config.name)
            actual_change_files = [f for f in change_files if "state" not in f.lower()]
            state_files = [f for f in change_files if "state" in f.lower()]
            
            site_total_changes = 0
            site_new_pages = 0
            site_modified_pages = 0
            site_deleted_pages = 0
            site_urls = 0
            last_detection = None
            
            # Get current URL count from latest state file
            if state_files:
                try:
                    latest_state_file = state_files[0]  # Most recent state file
                    state_data = change_detector.writer.read_json_file(latest_state_file)
                    
                    # Try multiple paths to find URL count
                    site_urls = 0
                    
                    # Method 1: Direct sitemap_state.total_urls
                    sitemap_state = state_data.get("state", {}).get("sitemap_state", {})
                    if sitemap_state:
                        site_urls = sitemap_state.get("total_urls", 0)
                    
                    # Method 2: Count URLs array if total_urls is 0
                    if site_urls == 0 and sitemap_state and "urls" in sitemap_state:
                        site_urls = len(sitemap_state["urls"])
                    
                    # Method 3: Look for URLs in other state sections
                    if site_urls == 0:
                        # Check if there are other state sections with URL data
                        state = state_data.get("state", {})
                        for key, value in state.items():
                            if isinstance(value, dict) and "urls" in value:
                                if isinstance(value["urls"], list):
                                    site_urls = len(value["urls"])
                                    break
                                elif isinstance(value["urls"], int):
                                    site_urls = value["urls"]
                                    break
                    
                    # Method 4: Look for total_urls in any state section
                    if site_urls == 0:
                        state = state_data.get("state", {})
                        for key, value in state.items():
                            if isinstance(value, dict) and "total_urls" in value:
                                site_urls = value["total_urls"]
                                break
                    
                    print(f"Found {site_urls} URLs for {site_config.name} using state file")
                    
                except Exception as e:
                    print(f"Error reading state file for {site_config.name}: {e}")
                    site_urls = 0
            
            # Fallback: If no URLs found in state file, try to get from recent change files
            if site_urls == 0 and actual_change_files:
                try:
                    # Look through recent change files for URL data
                    for file_path in actual_change_files[:3]:  # Check last 3 files
                        try:
                            change_data = change_detector.writer.read_json_file(file_path)
                            changes_data = change_data.get("changes", {})
                            
                            # Look for URL data in methods
                            if "methods" in changes_data:
                                for method_name, method_data in changes_data["methods"].items():
                                    if isinstance(method_data, dict):
                                        # Check for URL data in metadata
                                        metadata = method_data.get("metadata", {})
                                        if metadata:
                                            # Try different possible URL count fields
                                            for field in ["current_urls", "total_urls", "urls_count"]:
                                                if field in metadata:
                                                    site_urls = metadata[field]
                                                    print(f"Found {site_urls} URLs for {site_config.name} from change file metadata")
                                                    break
                                            if site_urls > 0:
                                                break
                                        
                                        # Check for URL data in sitemap_info
                                        sitemap_info = method_data.get("sitemap_info", {})
                                        if sitemap_info and "total_urls" in sitemap_info:
                                            site_urls = sitemap_info["total_urls"]
                                            print(f"Found {site_urls} URLs for {site_config.name} from sitemap_info")
                                            break
                                    
                                    if site_urls > 0:
                                        break
                            
                            if site_urls > 0:
                                break
                                
                        except Exception as e:
                            print(f"Error reading change file {file_path}: {e}")
                            continue
                            
                except Exception as e:
                    print(f"Error in fallback URL extraction for {site_config.name}: {e}")
            
            # Analyze recent change files
            for file_path in actual_change_files[:10]:  # Last 10 detections
                try:
                    change_data = change_detector.writer.read_json_file(file_path)
                    detection_time = change_data.get("metadata", {}).get("detection_time")
                    
                    if detection_time:
                        if not last_detection or detection_time > last_detection:
                            last_detection = detection_time
                        
                        # Get change counts from the changes data
                        changes_data = change_data.get("changes", {})
                        
                        # Method 1: Check methods for summary (new format)
                        if "methods" in changes_data:
                            for method_name, method_data in changes_data["methods"].items():
                                if isinstance(method_data, dict):
                                    method_summary = method_data.get("summary", {})
                                    site_total_changes += method_summary.get("total_changes", 0)
                                    site_new_pages += method_summary.get("new_pages", 0)
                                    site_modified_pages += method_summary.get("modified_pages", 0)
                                    site_deleted_pages += method_summary.get("deleted_pages", 0)
                        else:
                            # Method 2: Check for direct summary (for older format)
                            summary = changes_data.get("summary", {})
                            site_total_changes += summary.get("total_changes", 0)
                            site_new_pages += summary.get("new_pages", 0)
                            site_modified_pages += summary.get("modified_pages", 0)
                            site_deleted_pages += summary.get("deleted_pages", 0)
                        
                        # Method 3: Fallback - look for any summary-like data in the changes
                        if site_total_changes == 0:
                            # Search recursively for summary data
                            def find_summary_data(obj, path=""):
                                if isinstance(obj, dict):
                                    for key, value in obj.items():
                                        if key == "summary" and isinstance(value, dict):
                                            return value
                                        elif isinstance(value, (dict, list)):
                                            result = find_summary_data(value, f"{path}.{key}")
                                            if result:
                                                return result
                                elif isinstance(obj, list):
                                    for i, item in enumerate(obj):
                                        result = find_summary_data(item, f"{path}[{i}]")
                                        if result:
                                            return result
                                return None
                            
                            fallback_summary = find_summary_data(changes_data)
                            if fallback_summary:
                                site_total_changes += fallback_summary.get("total_changes", 0)
                                site_new_pages += fallback_summary.get("new_pages", 0)
                                site_modified_pages += fallback_summary.get("modified_pages", 0)
                                site_deleted_pages += fallback_summary.get("deleted_pages", 0)
                        
                except Exception as e:
                    print(f"Error processing change file {file_path}: {e}")
                    continue
            
            total_urls += site_urls
            total_changes += site_total_changes
            
            site_analytics.append({
                "site_id": site["site_id"],
                "site_name": site_config.name,
                "url": site_config.url,
                "total_urls": site_urls,
                "total_changes": site_total_changes,
                "new_pages": site_new_pages,
                "modified_pages": site_modified_pages,
                "deleted_pages": site_deleted_pages,
                "last_detection": last_detection,
                "detection_methods": site_config.detection_methods,
                "is_active": site_config.is_active
            })
        
        return {
            "status": "healthy",
            "analytics": {
                "overview": {
                    "total_sites": len(sites),
                    "active_sites": len([s for s in sites if s["is_active"]]),
                    "total_urls_monitored": total_urls,
                    "total_changes_detected": total_changes
                },
                "sites": site_analytics
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Analytics error: {str(e)}",
            "analytics": {}
        }


@router.get("/analytics/{site_id}")
async def get_site_analytics(site_id: str) -> Dict[str, Any]:
    """Get detailed analytics for a specific site."""
    try:
        change_detector = get_change_detector()
        if change_detector is None:
            raise HTTPException(status_code=503, detail="System is initializing. Please try again.")
        
        site_config = change_detector.config_manager.get_site(site_id)
        if not site_config:
            raise HTTPException(status_code=404, detail=f"Site '{site_id}' not found")
        
        # Get all change files for this site
        change_files = change_detector.writer.list_change_files(site_config.name)
        actual_change_files = [f for f in change_files if "state" not in f.lower()]
        
        # Analyze all detections
        detections = []
        total_changes = 0
        total_new_pages = 0
        total_modified_pages = 0
        total_deleted_pages = 0
        url_history = []
        
        for file_path in actual_change_files:
            try:
                change_data = change_detector.writer.read_json_file(file_path)
                detection_time = change_data.get("metadata", {}).get("detection_time")
                
                if detection_time:
                    # Get sitemap data
                    sitemap_data = change_data.get("changes", {}).get("methods", {}).get("sitemap", {})
                    metadata = sitemap_data.get("metadata", {}) if sitemap_data else {}
                    
                    # Get change summary
                    summary = change_data.get("changes", {}).get("summary", {})
                    
                    detection_info = {
                        "detection_time": detection_time,
                        "current_urls": metadata.get("current_urls", 0),
                        "previous_urls": metadata.get("previous_urls", 0),
                        "new_urls": metadata.get("new_urls", 0),
                        "deleted_urls": metadata.get("deleted_urls", 0),
                        "total_changes": summary.get("total_changes", 0),
                        "new_pages": summary.get("new_pages", 0),
                        "modified_pages": summary.get("modified_pages", 0),
                        "deleted_pages": summary.get("deleted_pages", 0),
                        "sitemap_info": metadata.get("sitemap_info", {})
                    }
                    
                    detections.append(detection_info)
                    total_changes += detection_info["total_changes"]
                    total_new_pages += detection_info["new_pages"]
                    total_modified_pages += detection_info["modified_pages"]
                    total_deleted_pages += detection_info["deleted_pages"]
                    
                    if detection_info["current_urls"] > 0:
                        url_history.append({
                            "date": detection_time,
                            "urls": detection_info["current_urls"]
                        })
                        
            except Exception:
                continue
        
        # Sort detections by time
        detections.sort(key=lambda x: x["detection_time"], reverse=True)
        url_history.sort(key=lambda x: x["date"], reverse=True)
        
        return {
            "site_id": site_id,
            "site_name": site_config.name,
            "url": site_config.url,
            "analytics": {
                "summary": {
                    "total_detections": len(detections),
                    "total_changes": total_changes,
                    "total_new_pages": total_new_pages,
                    "total_modified_pages": total_modified_pages,
                    "total_deleted_pages": total_deleted_pages,
                    "current_urls": detections[0]["current_urls"] if detections else 0,
                    "last_detection": detections[0]["detection_time"] if detections else None
                },
                "detections": detections[:20],  # Last 20 detections
                "url_history": url_history[:30],  # Last 30 data points
                "detection_methods": site_config.detection_methods,
                "is_active": site_config.is_active
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get site analytics: {str(e)}")


@router.get("/realtime")
async def get_realtime_status() -> Dict[str, Any]:
    """Get real-time system status and monitoring data."""
    try:
        change_detector = get_change_detector()
        if change_detector is None:
            return {
                "status": "initializing",
                "timestamp": datetime.now().isoformat(),
                "message": "System is starting up"
            }
        
        sites = change_detector.list_sites()
        realtime_data = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "sites": []
        }
        
        for site in sites:
            site_config = change_detector.config_manager.get_site(site["site_id"])
            if not site_config:
                continue
            
            # Get the most recent detection and state
            change_files = change_detector.writer.list_change_files(site_config.name)
            actual_change_files = [f for f in change_files if "state" not in f.lower()]
            state_files = [f for f in change_files if "state" in f.lower()]
            
            last_detection = None
            current_urls = 0
            last_change_count = 0
            
            # Get current URL count from latest state file
            if state_files:
                try:
                    latest_state_file = state_files[0]  # Most recent state file
                    state_data = change_detector.writer.read_json_file(latest_state_file)
                    
                    # Try multiple paths to find URL count
                    current_urls = 0
                    
                    # Method 1: Direct sitemap_state.total_urls
                    sitemap_state = state_data.get("state", {}).get("sitemap_state", {})
                    if sitemap_state:
                        current_urls = sitemap_state.get("total_urls", 0)
                    
                    # Method 2: Count URLs array if total_urls is 0
                    if current_urls == 0 and sitemap_state and "urls" in sitemap_state:
                        current_urls = len(sitemap_state["urls"])
                    
                    # Method 3: Look for URLs in other state sections
                    if current_urls == 0:
                        # Check if there are other state sections with URL data
                        state = state_data.get("state", {})
                        for key, value in state.items():
                            if isinstance(value, dict) and "urls" in value:
                                if isinstance(value["urls"], list):
                                    current_urls = len(value["urls"])
                                    break
                                elif isinstance(value["urls"], int):
                                    current_urls = value["urls"]
                                    break
                    
                    # Method 4: Look for total_urls in any state section
                    if current_urls == 0:
                        state = state_data.get("state", {})
                        for key, value in state.items():
                            if isinstance(value, dict) and "total_urls" in value:
                                current_urls = value["total_urls"]
                                break
                    
                    print(f"Found {current_urls} URLs for {site_config.name} in realtime")
                    
                except Exception as e:
                    print(f"Error reading state file for {site_config.name}: {e}")
                    current_urls = 0
            
            # Fallback: If no URLs found in state file, try to get from recent change files
            if current_urls == 0 and actual_change_files:
                try:
                    # Look through recent change files for URL data
                    for file_path in actual_change_files[:3]:  # Check last 3 files
                        try:
                            change_data = change_detector.writer.read_json_file(file_path)
                            changes_data = change_data.get("changes", {})
                            
                            # Look for URL data in methods
                            if "methods" in changes_data:
                                for method_name, method_data in changes_data["methods"].items():
                                    if isinstance(method_data, dict):
                                        # Check for URL data in metadata
                                        metadata = method_data.get("metadata", {})
                                        if metadata:
                                            # Try different possible URL count fields
                                            for field in ["current_urls", "total_urls", "urls_count"]:
                                                if field in metadata:
                                                    current_urls = metadata[field]
                                                    print(f"Found {current_urls} URLs for {site_config.name} from change file metadata in realtime")
                                                    break
                                            if current_urls > 0:
                                                break
                                        
                                        # Check for URL data in sitemap_info
                                        sitemap_info = method_data.get("sitemap_info", {})
                                        if sitemap_info and "total_urls" in sitemap_info:
                                            current_urls = sitemap_info["total_urls"]
                                            print(f"Found {current_urls} URLs for {site_config.name} from sitemap_info in realtime")
                                            break
                                    
                                    if current_urls > 0:
                                        break
                            
                            if current_urls > 0:
                                break
                                
                        except Exception as e:
                            print(f"Error reading change file {file_path}: {e}")
                            continue
                            
                except Exception as e:
                    print(f"Error in fallback URL extraction for {site_config.name} in realtime: {e}")
            
            # Get detection info from latest change file
            if actual_change_files:
                try:
                    latest_file = actual_change_files[0]  # Most recent file
                    change_data = change_detector.writer.read_json_file(latest_file)
                    last_detection = change_data.get("metadata", {}).get("detection_time")
                    
                    # Get last change count from the changes data
                    changes_data = change_data.get("changes", {})
                    
                    # Method 1: Check for direct summary (for older format)
                    summary = changes_data.get("summary", {})
                    
                    # Method 2: If no direct summary, check methods for summary
                    if not summary and "methods" in changes_data:
                        for method_name, method_data in changes_data["methods"].items():
                            if isinstance(method_data, dict):
                                method_summary = method_data.get("summary", {})
                                last_change_count += method_summary.get("total_changes", 0)
                    else:
                        # Use direct summary
                        last_change_count = summary.get("total_changes", 0)
                    
                    # Method 3: Fallback - look for any summary-like data in the changes
                    if last_change_count == 0:
                        # Search recursively for summary data
                        def find_summary_data(obj, path=""):
                            if isinstance(obj, dict):
                                for key, value in obj.items():
                                    if key == "summary" and isinstance(value, dict):
                                        return value
                                    elif isinstance(value, (dict, list)):
                                        result = find_summary_data(value, f"{path}.{key}")
                                        if result:
                                            return result
                            elif isinstance(obj, list):
                                for i, item in enumerate(obj):
                                    result = find_summary_data(item, f"{path}[{i}]")
                                    if result:
                                        return result
                            return None
                        
                        fallback_summary = find_summary_data(changes_data)
                        if fallback_summary:
                            last_change_count = fallback_summary.get("total_changes", 0)
                    
                except Exception as e:
                    print(f"Error processing change file {latest_file}: {e}")
                    pass
            
            # Calculate time since last detection
            time_since_last = None
            if last_detection:
                try:
                    last_dt = datetime.fromisoformat(last_detection.replace('Z', '+00:00'))
                    time_since_last = (datetime.now() - last_dt).total_seconds()
                except:
                    pass
            
            realtime_data["sites"].append({
                "site_id": site["site_id"],
                "site_name": site_config.name,
                "url": site_config.url,
                "status": "active" if site_config.is_active else "inactive",
                "last_detection": last_detection,
                "time_since_last_seconds": time_since_last,
                "current_urls": current_urls,
                "last_change_count": last_change_count,
                "detection_methods": site_config.detection_methods
            })
        
        return realtime_data
    except Exception as e:
        return {
            "status": "error",
            "timestamp": datetime.now().isoformat(),
            "message": f"Real-time monitoring error: {str(e)}"
        }


@router.get("/progress")
async def get_detection_progress() -> Dict[str, Any]:
    """Get the current detection progress and status."""
    global current_detection_status
    
    if current_detection_status["is_running"]:
        # Calculate elapsed time and estimated remaining time
        if current_detection_status["start_time"]:
            elapsed = datetime.now() - current_detection_status["start_time"]
            current_detection_status["elapsed_time"] = str(elapsed).split('.')[0]  # Remove microseconds
            
            # Estimate remaining time based on progress
            if current_detection_status["progress"] > 0:
                total_estimated = elapsed.total_seconds() / (current_detection_status["progress"] / 100)
                remaining_seconds = total_estimated - elapsed.total_seconds()
                if remaining_seconds > 0:
                    current_detection_status["estimated_time_remaining"] = f"{int(remaining_seconds)}s"
    
    return {
        "status": "running" if current_detection_status["is_running"] else "idle",
        "detection_status": current_detection_status
    }

@router.get("/history")
async def get_historical_data(
    days: int = Query(default=7, ge=1, le=30, description="Number of days to look back")
) -> Dict[str, Any]:
    """Get historical change detection data."""
    try:
        change_detector = get_change_detector()
        if change_detector is None:
            return {
                "status": "initializing",
                "message": "System is starting up",
                "history": {}
            }
        
        sites = change_detector.list_sites()
        cutoff_date = datetime.now() - timedelta(days=days)
        
        historical_data = {
            "period_days": days,
            "cutoff_date": cutoff_date.isoformat(),
            "sites": {}
        }
        
        for site in sites:
            site_config = change_detector.config_manager.get_site(site["site_id"])
            if not site_config:
                continue
            
            # Get all change files for this site
            change_files = change_detector.writer.list_change_files(site_config.name)
            actual_change_files = [f for f in change_files if "state" not in f.lower()]
            
            site_history = []
            daily_changes = {}
            
            for file_path in actual_change_files:
                try:
                    change_data = change_detector.writer.read_json_file(file_path)
                    detection_time = change_data.get("metadata", {}).get("detection_time")
                    
                    if detection_time:
                        detection_dt = datetime.fromisoformat(detection_time.replace('Z', '+00:00'))
                        
                        # Only include detections within the specified period
                        if detection_dt >= cutoff_date:
                            changes_data = change_data.get("changes", {})
                            
                            # Calculate totals from methods (new format)
                            total_changes = 0
                            new_pages = 0
                            modified_pages = 0
                            deleted_pages = 0
                            
                            if "methods" in changes_data:
                                for method_name, method_data in changes_data["methods"].items():
                                    if isinstance(method_data, dict):
                                        method_summary = method_data.get("summary", {})
                                        total_changes += method_summary.get("total_changes", 0)
                                        new_pages += method_summary.get("new_pages", 0)
                                        modified_pages += method_summary.get("modified_pages", 0)
                                        deleted_pages += method_summary.get("deleted_pages", 0)
                            else:
                                # Fallback to direct summary (older format)
                                summary = changes_data.get("summary", {})
                                total_changes = summary.get("total_changes", 0)
                                new_pages = summary.get("new_pages", 0)
                                modified_pages = summary.get("modified_pages", 0)
                                deleted_pages = summary.get("deleted_pages", 0)
                            
                            detection_info = {
                                "detection_time": detection_time,
                                "total_changes": total_changes,
                                "new_pages": new_pages,
                                "modified_pages": modified_pages,
                                "deleted_pages": deleted_pages
                            }
                            
                            site_history.append(detection_info)
                            
                            # Group by day
                            day_key = detection_dt.strftime("%Y-%m-%d")
                            if day_key not in daily_changes:
                                daily_changes[day_key] = {
                                    "total_changes": 0,
                                    "new_pages": 0,
                                    "modified_pages": 0,
                                    "deleted_pages": 0,
                                    "detections": 0
                                }
                            
                            daily_changes[day_key]["total_changes"] += detection_info["total_changes"]
                            daily_changes[day_key]["new_pages"] += detection_info["new_pages"]
                            daily_changes[day_key]["modified_pages"] += detection_info["modified_pages"]
                            daily_changes[day_key]["deleted_pages"] += detection_info["deleted_pages"]
                            daily_changes[day_key]["detections"] += 1
                            
                except Exception:
                    continue
            
            # Sort history by time
            site_history.sort(key=lambda x: x["detection_time"], reverse=True)
            
            historical_data["sites"][site["site_id"]] = {
                "site_name": site_config.name,
                "detections": site_history,
                "daily_summary": daily_changes
            }
        
        return {
            "status": "success",
            "history": historical_data
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Historical data error: {str(e)}",
            "history": {}
        } 