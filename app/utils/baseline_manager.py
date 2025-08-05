# ==============================================================================
# baseline_manager.py — Baseline Management Utility
# ==============================================================================
# Purpose: Centralized baseline management with automatic updating capabilities
# Sections: Imports, BaselineManager Class
# ==============================================================================

# ==============================================================================
# Imports
# ==============================================================================

# Standard Library -----
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Union

# Internal -----
from .baseline_merger import BaselineMerger

# ==============================================================================
# Public exports
# ==============================================================================
__all__ = ['BaselineManager']

# ==============================================================================
# Logging Configuration
# ==============================================================================

# Configure logging for baseline operations
baseline_logger = logging.getLogger('baseline_manager')
baseline_logger.setLevel(logging.INFO)

# Create console handler if it doesn't exist
if not baseline_logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    baseline_logger.addHandler(console_handler)


class BaselineManager:
    """Manages baseline files with automatic updating capabilities."""
    
    def __init__(self, baseline_dir: str = "baselines"):
        """Initialize the baseline manager."""
        self.baseline_dir = Path(baseline_dir)
        self.baseline_dir.mkdir(exist_ok=True)
        self.merger = BaselineMerger()
        
        # Track baseline creation events for dashboard (persistent storage)
        self.events_file = self.baseline_dir / "baseline_events.json"
        self.baseline_events = self._load_events()
    
    def _load_events(self) -> List[Dict[str, Any]]:
        """Load baseline events from persistent storage."""
        try:
            if self.events_file.exists():
                with open(self.events_file, 'r', encoding='utf-8') as f:
                    events = json.load(f)
                    # Ensure we have a list
                    if isinstance(events, list):
                        return events
            return []
        except Exception as e:
            print(f"Error loading baseline events: {e}")
            return []
    
    def _save_events(self):
        """Save baseline events to persistent storage."""
        try:
            with open(self.events_file, 'w', encoding='utf-8') as f:
                json.dump(self.baseline_events, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving baseline events: {e}")
    
    def _log_baseline_event(self, event_type: str, site_id: str, details: Dict[str, Any]):
        """Log baseline events for both terminal and dashboard tracking."""
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "site_id": site_id,
            "details": details
        }
        
        # Add to events list for dashboard
        self.baseline_events.append(event)
        
        # Keep only last 100 events
        if len(self.baseline_events) > 100:
            self.baseline_events = self.baseline_events[-100:]
        
        # Save events persistently
        self._save_events()
        
        # Log to terminal with emoji and formatting
        if event_type == "baseline_created":
            baseline_logger.info(f"🎯 NEW BASELINE CREATED for {site_id}")
            baseline_logger.info(f"   📁 File: {details.get('file_path', 'N/A')}")
            baseline_logger.info(f"   📊 URLs: {details.get('total_urls', 0)}")
            baseline_logger.info(f"   🔗 Content Hashes: {details.get('total_content_hashes', 0)}")
            baseline_logger.info(f"   📅 Date: {details.get('baseline_date', 'N/A')}")
            
        elif event_type == "baseline_updated":
            baseline_logger.info(f"🔄 BASELINE UPDATED for {site_id}")
            baseline_logger.info(f"   📁 File: {details.get('file_path', 'N/A')}")
            baseline_logger.info(f"   📈 Changes Applied: {details.get('changes_applied', 0)}")
            baseline_logger.info(f"   ➕ New URLs: {details.get('new_urls', 0)}")
            baseline_logger.info(f"   ✏️ Modified URLs: {details.get('modified_urls', 0)}")
            baseline_logger.info(f"   🗑️ Deleted URLs: {details.get('deleted_urls', 0)}")
            baseline_logger.info(f"   📅 Previous Date: {details.get('previous_baseline_date', 'N/A')}")
            baseline_logger.info(f"   📅 New Date: {details.get('baseline_date', 'N/A')}")
            
        elif event_type == "baseline_error":
            baseline_logger.error(f"❌ BASELINE ERROR for {site_id}")
            baseline_logger.error(f"   🚨 Error: {details.get('error', 'Unknown error')}")
            
        elif event_type == "baseline_replaced":
            baseline_logger.info(f"🔄 BASELINE REPLACED for {site_id}")
            baseline_logger.info(f"   📁 File: {details.get('file_path', 'N/A')}")
            baseline_logger.info(f"   💾 Backup: {details.get('backup_file', 'N/A')}")
            baseline_logger.info(f"   📊 URLs: {details.get('total_urls', 0)}")
            baseline_logger.info(f"   🔗 Content Hashes: {details.get('total_content_hashes', 0)}")
            baseline_logger.info(f"   📅 Date: {details.get('baseline_date', 'N/A')}")
            
        elif event_type == "baseline_validation":
            if details.get('is_valid', False):
                baseline_logger.info(f"✅ BASELINE VALIDATION PASSED for {site_id}")
            else:
                baseline_logger.warning(f"⚠️ BASELINE VALIDATION FAILED for {site_id}")
                for error in details.get('errors', []):
                    baseline_logger.warning(f"   ❌ {error}")
                for warning in details.get('warnings', []):
                    baseline_logger.warning(f"   ⚠️ {warning}")
    
    def get_baseline_events(self, site_id: str = None, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent baseline events for dashboard display."""
        # Reload events from file to ensure we have the latest
        self.baseline_events = self._load_events()
        
        events = self.baseline_events
        
        if site_id:
            events = [event for event in events if event["site_id"] == site_id]
        

        
        return events[-limit:] if limit else events
    
    def get_latest_baseline(self, site_id: str) -> Optional[Dict[str, Any]]:
        """Get the most recent baseline for a site."""
        try:
            baseline_files = list(self.baseline_dir.glob(f"{site_id}_*_baseline.json"))
            if not baseline_files:
                return None
            
            # Sort by baseline date (not file modification time) and get the most recent
            latest_baseline = None
            latest_date = None
            
            for baseline_file in baseline_files:
                try:
                    with open(baseline_file, 'r', encoding='utf-8') as f:
                        baseline_data = json.load(f)
                    
                    baseline_date = baseline_data.get("baseline_date")
                    if baseline_date and (latest_date is None or baseline_date > latest_date):
                        latest_date = baseline_date
                        latest_baseline = baseline_data
                        
                except Exception as e:
                    print(f"Error reading baseline file {baseline_file}: {e}")
                    continue
            
            return latest_baseline
            
        except Exception as e:
            print(f"Error reading latest baseline for {site_id}: {e}")
            return None
    
    def get_baseline_by_date(self, site_id: str, date: str) -> Optional[Dict[str, Any]]:
        """Get a specific baseline by date (format: YYYYMMDD)."""
        try:
            # Look for files matching the pattern site_id_YYYYMMDD_*_baseline.json
            pattern = f"{site_id}_{date}_*_baseline.json"
            matching_files = list(self.baseline_dir.glob(pattern))
            
            if not matching_files:
                return None
            
            # Get the most recent file if multiple exist
            latest_file = max(matching_files, key=lambda x: x.stat().st_mtime)
            
            with open(latest_file, 'r', encoding='utf-8') as f:
                baseline_data = json.load(f)
            
            return baseline_data
            
        except Exception as e:
            print(f"Error reading baseline for {site_id} on {date}: {e}")
            return None
    
    def update_baseline_from_changes(self, site_id: str, previous_baseline: Dict[str, Any], 
                                   current_state: Dict[str, Any], changes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create new baseline by merging previous baseline with current state and changes."""
        try:
            # Use the merger to create the new baseline
            new_baseline = self.merger.merge_baselines(previous_baseline, current_state, changes)
            
            # Add site-specific metadata
            new_baseline.update({
                "site_id": site_id,
                "baseline_evolution": {
                    "previous_baseline_date": previous_baseline.get("baseline_date"),
                    "changes_applied": len(changes),
                    "evolution_type": "automatic_update"
                }
            })
            
            return new_baseline
            
        except Exception as e:
            print(f"Error updating baseline for {site_id}: {e}")
            # Return the previous baseline as fallback
            return previous_baseline
    
    def save_baseline(self, site_id: str, baseline_data: Dict[str, Any]) -> str:
        """Save new baseline with timestamp."""
        try:
            # Ensure the baseline has required metadata
            if "baseline_date" not in baseline_data:
                baseline_data["baseline_date"] = datetime.now().strftime("%Y%m%d")
            
            if "created_at" not in baseline_data:
                baseline_data["created_at"] = datetime.now().isoformat()
            
            # Use the baseline_date for the filename to maintain consistency
            baseline_date = baseline_data["baseline_date"]
            
            # Generate timestamp for uniqueness (microseconds + process ID + thread ID for better uniqueness)
            import os
            import threading
            timestamp = f"{datetime.now().strftime('%H%M%S_%f')}_{os.getpid()}_{threading.get_ident()}"  # HHMMSS_MMMMMM_PID_THREADID
            
            baseline_file = self.baseline_dir / f"{site_id}_{baseline_date}_{timestamp}_baseline.json"
            
            # Save the baseline
            with open(baseline_file, 'w', encoding='utf-8') as f:
                json.dump(baseline_data, f, indent=2, ensure_ascii=False)
            
            # Verify the file was written successfully
            if baseline_file.exists() and baseline_file.stat().st_size > 0:
                # Determine if this is a new baseline or an update
                evolution_type = baseline_data.get("evolution_type", "unknown")
                
                if evolution_type == "initial_creation":
                    # Log baseline creation
                    self._log_baseline_event("baseline_created", site_id, {
                        "file_path": str(baseline_file),
                        "total_urls": baseline_data.get("total_urls", 0),
                        "total_content_hashes": baseline_data.get("total_content_hashes", 0),
                        "baseline_date": baseline_data.get("baseline_date"),
                        "evolution_type": evolution_type
                    })
                else:
                    # Log baseline update
                    change_summary = baseline_data.get("change_summary", {})
                    self._log_baseline_event("baseline_updated", site_id, {
                        "file_path": str(baseline_file),
                        "changes_applied": baseline_data.get("changes_applied", 0),
                        "new_urls": change_summary.get("new_urls", 0),
                        "modified_urls": change_summary.get("modified_urls", 0),
                        "deleted_urls": change_summary.get("deleted_urls", 0),
                        "previous_baseline_date": baseline_data.get("previous_baseline_date"),
                        "baseline_date": baseline_data.get("baseline_date"),
                        "evolution_type": evolution_type
                    })
                
                # Auto-cleanup old baselines after saving new ones
                self._auto_cleanup_baselines(site_id)
                
                return str(baseline_file)
            else:
                raise Exception(f"Failed to write baseline file or file is empty: {baseline_file}")
            
        except Exception as e:
            # Log error
            self._log_baseline_event("baseline_error", site_id, {
                "error": str(e),
                "operation": "save_baseline"
            })
            raise

    def replace_baseline(self, site_id: str, baseline_data: Dict[str, Any]) -> str:
        """Replace the existing baseline with new data, keeping the same filename."""
        try:
            # Ensure the baseline has required metadata
            if "baseline_date" not in baseline_data:
                baseline_data["baseline_date"] = datetime.now().strftime("%Y%m%d")
            
            if "created_at" not in baseline_data:
                baseline_data["created_at"] = datetime.now().isoformat()
            
            # Find the existing baseline file to replace
            existing_baseline_files = list(self.baseline_dir.glob(f"{site_id}_*_baseline.json"))
            if not existing_baseline_files:
                # No existing baseline, create a new one
                return self.save_baseline(site_id, baseline_data)
            
            # Get the most recent baseline file
            latest_baseline_file = max(existing_baseline_files, key=lambda x: x.stat().st_mtime)
            
            # Create a backup of the existing baseline
            backup_file = latest_baseline_file.with_suffix('.backup.json')
            import shutil
            shutil.copy2(latest_baseline_file, backup_file)
            
            # Replace the existing baseline with new data
            with open(latest_baseline_file, 'w', encoding='utf-8') as f:
                json.dump(baseline_data, f, indent=2, ensure_ascii=False)
            
            # Verify the file was written successfully
            if latest_baseline_file.exists() and latest_baseline_file.stat().st_size > 0:
                # Log baseline replacement
                self._log_baseline_event("baseline_replaced", site_id, {
                    "file_path": str(latest_baseline_file),
                    "backup_file": str(backup_file),
                    "total_urls": baseline_data.get("total_urls", 0),
                    "total_content_hashes": baseline_data.get("total_content_hashes", 0),
                    "baseline_date": baseline_data.get("baseline_date"),
                    "evolution_type": "baseline_replacement"
                })
                
                # Auto-cleanup old baselines after replacement
                self._auto_cleanup_baselines(site_id)
                
                return str(latest_baseline_file)
            else:
                raise Exception(f"Failed to write baseline file or file is empty: {latest_baseline_file}")
            
        except Exception as e:
            # Log error
            self._log_baseline_event("baseline_error", site_id, {
                "error": str(e),
                "operation": "replace_baseline"
            })
            raise
    
    def list_baselines(self, site_id: str = None) -> Union[Dict[str, List[str]], List[str]]:
        """List all available baselines."""
        baselines = {}
        
        try:
            for baseline_file in self.baseline_dir.glob("*_baseline.json"):
                filename = baseline_file.name
                
                # Parse filename: site_id_YYYYMMDD_HHMMSS_MMMMMM_PID_THREADID_baseline.json
                if filename.endswith("_baseline.json"):
                    base_name = filename.replace("_baseline.json", "")
                    parts = base_name.split("_")
                    
                    # Find the date part (8 digits: YYYYMMDD) and everything before it is the site_id
                    date_part = None
                    file_site_id = None
                    
                    for i, part in enumerate(parts):
                        if len(part) == 8 and part.isdigit():
                            date_part = part
                            # Everything before this part is the site_id
                            file_site_id = "_".join(parts[:i])
                            break
                    
                    if date_part and file_site_id:
                        if site_id is None or file_site_id == site_id:
                            if file_site_id not in baselines:
                                baselines[file_site_id] = []
                            # Only add unique dates
                            if date_part not in baselines[file_site_id]:
                                baselines[file_site_id].append(date_part)
            
            # Sort dates for each site
            for site in baselines:
                baselines[site].sort()
            
            # Return format based on whether site_id was provided
            if site_id is not None:
                # Return list of dates for specific site
                return baselines.get(site_id, [])
            else:
                # Return dictionary of all sites
                return baselines
            
        except Exception as e:
            print(f"Error listing baselines: {e}")
            return [] if site_id is not None else {}
    
    def get_baseline_info(self, site_id: str, date: str) -> Dict[str, Any]:
        """Get information about a specific baseline."""
        try:
            baseline_data = self.get_baseline_by_date(site_id, date)
            if not baseline_data:
                return {"error": f"Baseline not found: {site_id}_{date}"}
            
            # Find the actual file path
            pattern = f"{site_id}_{date}_*_baseline.json"
            matching_files = list(self.baseline_dir.glob(pattern))
            if matching_files:
                baseline_file = max(matching_files, key=lambda x: x.stat().st_mtime)
                file_size = baseline_file.stat().st_size
                file_size_mb = file_size / (1024 * 1024)
            else:
                return {"error": f"Baseline file not found: {site_id}_{date}"}
            
            return {
                "site_id": baseline_data.get("site_id", site_id),
                "date": date,
                "file_path": str(baseline_file),
                "file_size_mb": round(file_size_mb, 4),  # More precision for small files
                "baseline_info": baseline_data
            }
            
        except Exception as e:
            return {"error": f"Error reading baseline: {e}"}
    
    def cleanup_old_baselines(self, site_id: str = None, max_baselines_per_site: int = 5) -> Dict[str, Any]:
        """Clean up old baselines, keeping only the most recent ones per site."""
        deleted_files = []
        total_size_freed = 0
        
        try:
            if site_id:
                # Clean up for specific site
                return self._cleanup_site_baselines(site_id, max_baselines_per_site)
            else:
                # Clean up for all sites
                site_ids = set()
                for baseline_file in self.baseline_dir.glob("*_baseline.json"):
                    filename = baseline_file.name
                    if filename.endswith("_baseline.json"):
                        base_name = filename.replace("_baseline.json", "")
                        parts = base_name.split("_")
                        if len(parts) >= 2:
                            site_ids.add(parts[0])
                
                total_deleted = 0
                total_size_freed = 0
                all_deleted_files = []
                
                for site in site_ids:
                    result = self._cleanup_site_baselines(site, max_baselines_per_site)
                    if "error" not in result:
                        total_deleted += result["total_files_deleted"]
                        total_size_freed += result["total_size_freed_mb"]
                        all_deleted_files.extend(result["deleted_files"])
                
                return {
                    "total_files_deleted": total_deleted,
                    "total_size_freed_mb": round(total_size_freed, 4),
                    "deleted_files": all_deleted_files,
                    "sites_processed": len(site_ids)
                }
                
        except Exception as e:
            return {"error": f"Error during cleanup: {e}"}
    
    def _cleanup_site_baselines(self, site_id: str, max_baselines: int) -> Dict[str, Any]:
        """Clean up baselines for a specific site, keeping only the most recent ones."""
        deleted_files = []
        total_size_freed = 0
        
        try:
            # Get all baseline files for this site
            pattern = f"{site_id}_*_baseline.json"
            baseline_files = list(self.baseline_dir.glob(pattern))
            
            if len(baseline_files) <= max_baselines:
                # No cleanup needed
                return {
                    "total_files_deleted": 0,
                    "total_size_freed_mb": 0,
                    "deleted_files": [],
                    "site_id": site_id
                }
            
            # Parse dates and sort files by date (oldest first)
            file_date_pairs = []
            for baseline_file in baseline_files:
                filename = baseline_file.name
                if filename.endswith("_baseline.json"):
                    base_name = filename.replace("_baseline.json", "")
                    parts = base_name.split("_")
                    
                    # Find the date part (8 digits: YYYYMMDD)
                    date_str = None
                    for i, part in enumerate(parts):
                        if len(part) == 8 and part.isdigit():
                            date_str = part
                            break
                    
                    if date_str:
                        file_date_pairs.append((baseline_file, date_str))
            
            # Sort by date (oldest first)
            file_date_pairs.sort(key=lambda x: x[1])
            
            # Delete oldest files, keeping only the most recent max_baselines
            files_to_delete = file_date_pairs[:-max_baselines]
            
            for baseline_file, date_str in files_to_delete:
                try:
                    file_size = baseline_file.stat().st_size
                    baseline_file.unlink()
                    deleted_files.append(baseline_file.name)
                    total_size_freed += file_size
                except Exception as e:
                    print(f"Error deleting {baseline_file.name}: {e}")
            
            return {
                "total_files_deleted": len(deleted_files),
                "total_size_freed_mb": round(total_size_freed / (1024 * 1024), 4),
                "deleted_files": deleted_files,
                "site_id": site_id,
                "kept_baselines": len(file_date_pairs) - len(deleted_files)
            }
            
        except Exception as e:
            return {"error": f"Error cleaning up site {site_id}: {e}"}
    
    def validate_baseline(self, baseline_data: Dict[str, Any]) -> bool:
        """Validate baseline data structure and integrity."""
        try:
            # Check required fields
            required_fields = [
                "site_id", "site_name", "baseline_date", "created_at",
                "sitemap_state", "content_hashes"
            ]
            
            for field in required_fields:
                if field not in baseline_data:
                    return False
            
            # Check data consistency
            if "sitemap_state" in baseline_data and "content_hashes" in baseline_data:
                sitemap_urls = set(baseline_data["sitemap_state"].get("urls", []))
                content_urls = set(baseline_data["content_hashes"].keys())
                
                # URLs in sitemap but not in content hashes
                missing_content = sitemap_urls - content_urls
                if missing_content:
                    # This is a warning, not an error
                    pass
                
                # URLs in content hashes but not in sitemap
                extra_content = content_urls - sitemap_urls
                if extra_content:
                    # This is a warning, not an error
                    pass
            
            return True
            
        except Exception as e:
            return False
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics for all baselines."""
        try:
            total_files = 0
            total_size = 0
            site_stats = {}
            
            for baseline_file in self.baseline_dir.glob("*_baseline.json"):
                if baseline_file.exists():
                    file_size = baseline_file.stat().st_size
                    
                    if file_size > 0:
                        total_files += 1
                        total_size += file_size
                        
                        # Extract site_id from filename
                        filename = baseline_file.name
                        if filename.endswith("_baseline.json"):
                            base_name = filename.replace("_baseline.json", "")
                            parts = base_name.split("_")
                            
                            # Find the date part (8 digits: YYYYMMDD) and everything before it is the site_id
                            site_id = None
                            for i, part in enumerate(parts):
                                if len(part) == 8 and part.isdigit():
                                    # Everything before this part is the site_id
                                    site_id = "_".join(parts[:i])
                                    break
                            
                            if site_id:
                                if site_id not in site_stats:
                                    site_stats[site_id] = {"count": 0, "size": 0}
                                site_stats[site_id]["count"] += 1
                                site_stats[site_id]["size"] += file_size
            
            return {
                "total_files": total_files,
                "total_size_mb": round(total_size / (1024 * 1024), 4),  # More precision for small files
                "site_stats": site_stats
            }
            
        except Exception as e:
            return {"error": f"Error getting storage stats: {e}"}
    
    def _auto_cleanup_baselines(self, site_id: str, max_baselines: int = 3):
        """Automatically clean up old baselines for a site, keeping only the most recent ones."""
        try:
            # Get all baseline files for this site
            pattern = f"{site_id}_*_baseline.json"
            baseline_files = list(self.baseline_dir.glob(pattern))
            
            # Don't clean up if we have fewer than max_baselines + 1 files
            if len(baseline_files) <= max_baselines:
                return
            
            # Parse dates and sort files by date (oldest first)
            file_date_pairs = []
            for baseline_file in baseline_files:
                filename = baseline_file.name
                if filename.endswith("_baseline.json"):
                    base_name = filename.replace("_baseline.json", "")
                    parts = base_name.split("_")
                    
                    # Find the date part (8 digits: YYYYMMDD)
                    date_str = None
                    for i, part in enumerate(parts):
                        if len(part) == 8 and part.isdigit():
                            date_str = part
                            break
                    
                    if date_str:
                        file_date_pairs.append((baseline_file, date_str))
            
            # Sort by date (oldest first)
            file_date_pairs.sort(key=lambda x: x[1])
            
            # Delete oldest files, keeping only the most recent max_baselines
            files_to_delete = file_date_pairs[:-max_baselines]
            
            deleted_count = 0
            for baseline_file, date_str in files_to_delete:
                try:
                    baseline_file.unlink()
                    deleted_count += 1
                except Exception as e:
                    print(f"Warning: Could not delete old baseline {baseline_file.name}: {e}")
            
            if deleted_count > 0:
                print(f"🧹 Auto-cleaned {deleted_count} old baseline files for {site_id}")
                
        except Exception as e:
            print(f"Warning: Auto-cleanup failed for {site_id}: {e}")
    
    def get_baseline_summary(self) -> Dict[str, Any]:
        """Get a summary of baseline storage and management status."""
        try:
            stats = self.get_storage_stats()
            if "error" in stats:
                return stats
            
            # Count files per site
            site_file_counts = {}
            for baseline_file in self.baseline_dir.glob("*_baseline.json"):
                if baseline_file.name.endswith("_baseline.json"):
                    filename = baseline_file.name
                    base_name = filename.replace("_baseline.json", "")
                    parts = base_name.split("_")
                    
                    # Find the date part (8 digits: YYYYMMDD) and everything before it is the site_id
                    site_id = None
                    for i, part in enumerate(parts):
                        if len(part) == 8 and part.isdigit():
                            site_id = "_".join(parts[:i])
                            break
                    
                    if site_id:
                        if site_id not in site_file_counts:
                            site_file_counts[site_id] = 0
                        site_file_counts[site_id] += 1
            
            # Identify sites that need cleanup
            sites_needing_cleanup = []
            for site_id, count in site_file_counts.items():
                if count > 3:  # More than 3 baselines
                    sites_needing_cleanup.append({
                        "site_id": site_id,
                        "baseline_count": count,
                        "recommended_action": "cleanup"
                    })
            
            return {
                "total_files": stats["total_files"],
                "total_size_mb": stats["total_size_mb"],
                "site_stats": stats["site_stats"],
                "site_file_counts": site_file_counts,
                "sites_needing_cleanup": sites_needing_cleanup,
                "recommendations": {
                    "auto_cleanup_enabled": True,
                    "max_baselines_per_site": 3,
                    "total_sites": len(site_file_counts),
                    "sites_with_multiple_baselines": len(sites_needing_cleanup)
                }
            }
            
        except Exception as e:
            return {"error": f"Error getting baseline summary: {e}"} 