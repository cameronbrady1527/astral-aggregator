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
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

# Internal -----
from .baseline_merger import BaselineMerger

# ==============================================================================
# Public exports
# ==============================================================================
__all__ = ['BaselineManager']


class BaselineManager:
    """Manages baseline files with automatic updating capabilities."""
    
    def __init__(self, baseline_dir: str = "baselines"):
        """Initialize the baseline manager."""
        self.baseline_dir = Path(baseline_dir)
        self.baseline_dir.mkdir(exist_ok=True)
        self.merger = BaselineMerger()
    
    def get_latest_baseline(self, site_id: str) -> Optional[Dict[str, Any]]:
        """Get the most recent baseline for a site."""
        try:
            baseline_files = list(self.baseline_dir.glob(f"{site_id}_*_baseline.json"))
            if not baseline_files:
                return None
            
            # Sort by modification time and get the most recent
            latest_file = max(baseline_files, key=lambda x: x.stat().st_mtime)
            
            with open(latest_file, 'r', encoding='utf-8') as f:
                baseline_data = json.load(f)
            
            return baseline_data
            
        except Exception as e:
            print(f"Error reading latest baseline for {site_id}: {e}")
            return None
    
    def get_baseline_by_date(self, site_id: str, date: str) -> Optional[Dict[str, Any]]:
        """Get a specific baseline by date (format: YYYYMMDD)."""
        try:
            baseline_file = self.baseline_dir / f"{site_id}_{date}_baseline.json"
            if not baseline_file.exists():
                return None
            
            with open(baseline_file, 'r', encoding='utf-8') as f:
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
            # Generate timestamp for the new baseline
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            baseline_file = self.baseline_dir / f"{site_id}_{timestamp}_baseline.json"
            
            # Ensure the baseline has required metadata
            if "baseline_date" not in baseline_data:
                baseline_data["baseline_date"] = datetime.now().strftime("%Y%m%d")
            
            if "created_at" not in baseline_data:
                baseline_data["created_at"] = datetime.now().isoformat()
            
            # Save the baseline
            with open(baseline_file, 'w', encoding='utf-8') as f:
                json.dump(baseline_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Baseline saved: {baseline_file}")
            return str(baseline_file)
            
        except Exception as e:
            print(f"Error saving baseline for {site_id}: {e}")
            raise
    
    def list_baselines(self, site_id: str = None) -> Dict[str, List[str]]:
        """List all available baselines."""
        baselines = {}
        
        try:
            for baseline_file in self.baseline_dir.glob("*_baseline.json"):
                filename = baseline_file.name
                
                # Handle both old format (site_date_baseline.json) and new format (site_timestamp_baseline.json)
                if filename.endswith("_baseline.json"):
                    base_name = filename.replace("_baseline.json", "")
                    
                    # Find the last underscore that separates site_id from timestamp
                    # Format: site_id_YYYYMMDD_HHMMSS_baseline.json
                    last_underscore = base_name.rfind("_")
                    if last_underscore != -1:
                        # Check if the part after last underscore is a timestamp (HHMMSS)
                        timestamp_part = base_name[last_underscore + 1:]
                        if len(timestamp_part) == 6 and timestamp_part.isdigit():
                            # New format: site_id_YYYYMMDD_HHMMSS
                            site_part = base_name[:last_underscore]
                            date_part = site_part[site_part.rfind("_") + 1:] if "_" in site_part else site_part
                            file_site_id = site_part[:site_part.rfind("_")] if "_" in site_part else site_part
                        else:
                            # Old format: site_id_YYYYMMDD
                            file_site_id = base_name[:last_underscore]
                            date_part = base_name[last_underscore + 1:]
                    else:
                        continue
                    
                    if site_id is None or file_site_id == site_id:
                        if file_site_id not in baselines:
                            baselines[file_site_id] = []
                        # Only add unique dates
                        if date_part not in baselines[file_site_id]:
                            baselines[file_site_id].append(date_part)
            
            # Sort dates for each site
            for site in baselines:
                baselines[site].sort()
            
            return baselines
            
        except Exception as e:
            print(f"Error listing baselines: {e}")
            return {}
    
    def get_baseline_info(self, site_id: str, date: str) -> Dict[str, Any]:
        """Get information about a specific baseline."""
        try:
            baseline_data = self.get_baseline_by_date(site_id, date)
            if not baseline_data:
                return {"error": f"Baseline not found: {site_id}_{date}"}
            
            baseline_file = self.baseline_dir / f"{site_id}_{date}_baseline.json"
            file_size = baseline_file.stat().st_size
            file_size_mb = file_size / (1024 * 1024)
            
            return {
                "site_id": site_id,
                "date": date,
                "file_path": str(baseline_file),
                "file_size_mb": round(file_size_mb, 2),
                "baseline_info": baseline_data
            }
            
        except Exception as e:
            return {"error": f"Error reading baseline: {e}"}
    
    def cleanup_old_baselines(self, site_id: str = None, days_to_keep: int = 30) -> Dict[str, Any]:
        """Clean up baselines older than specified days."""
        from datetime import timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        cutoff_date_str = cutoff_date.strftime("%Y%m%d")
        
        deleted_files = []
        total_size_freed = 0
        
        try:
            pattern = f"{site_id}_*_baseline.json" if site_id else "*_baseline.json"
            
            for baseline_file in self.baseline_dir.glob(pattern):
                filename = baseline_file.name
                parts = filename.replace("_baseline.json", "").split("_")
                
                if len(parts) >= 2:
                    date_str = parts[1]
                    
                    try:
                        file_date = datetime.strptime(date_str, "%Y%m%d")
                        if file_date < cutoff_date:
                            file_size = baseline_file.stat().st_size
                            baseline_file.unlink()
                            deleted_files.append(filename)
                            total_size_freed += file_size
                    except ValueError:
                        # Skip files with invalid date format
                        continue
            
            return {
                "deleted_files": deleted_files,
                "total_files_deleted": len(deleted_files),
                "total_size_freed_mb": round(total_size_freed / (1024 * 1024), 2),
                "cutoff_date": cutoff_date_str
            }
            
        except Exception as e:
            return {"error": f"Error during cleanup: {e}"}
    
    def validate_baseline(self, baseline_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate baseline data structure and integrity."""
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }
        
        try:
            # Check required fields
            required_fields = [
                "site_id", "site_name", "baseline_date", "created_at",
                "sitemap_state", "content_hashes"
            ]
            
            for field in required_fields:
                if field not in baseline_data:
                    validation_result["is_valid"] = False
                    validation_result["errors"].append(f"Missing required field: {field}")
            
            # Check data consistency
            if "sitemap_state" in baseline_data and "content_hashes" in baseline_data:
                sitemap_urls = set(baseline_data["sitemap_state"].get("urls", []))
                content_urls = set(baseline_data["content_hashes"].keys())
                
                # URLs in sitemap but not in content hashes
                missing_content = sitemap_urls - content_urls
                if missing_content:
                    validation_result["warnings"].append(
                        f"URLs in sitemap but missing content hashes: {len(missing_content)}"
                    )
                
                # URLs in content hashes but not in sitemap
                extra_content = content_urls - sitemap_urls
                if extra_content:
                    validation_result["warnings"].append(
                        f"URLs in content hashes but not in sitemap: {len(extra_content)}"
                    )
            
            return validation_result
            
        except Exception as e:
            validation_result["is_valid"] = False
            validation_result["errors"].append(f"Validation error: {e}")
            return validation_result 