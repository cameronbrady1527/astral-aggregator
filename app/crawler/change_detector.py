# ==============================================================================
# change_detector.py — Main Change Detection Orchestrator
# ==============================================================================
# Purpose: Coordinate different detection methods and manage the overall process
# Sections: Imports, ChangeDetector Class
# ==============================================================================

# ==============================================================================
# Imports
# ==============================================================================

# Standard Library -----
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import os
import re

# Internal -----
from .base_detector import BaseDetector, ChangeResult
from .sitemap_detector import SitemapDetector
from .firecrawl_detector import FirecrawlDetector
from .content_detector import ContentDetector
from .hybrid_detector import HybridDetector
from ..utils.json_writer import ChangeDetectionWriter
from ..utils.config import ConfigManager
from ..utils.baseline_manager import BaselineManager

# ==============================================================================
# Public exports
# ==============================================================================
__all__ = ['ChangeDetector']


class ChangeDetector:
    """Main orchestrator for change detection across multiple sites and methods."""
    
    def __init__(self, config_file: str = None):
        """Initialize the change detector."""
        # Use environment variable for config file if set (Railway deployment)
        if config_file is None:
            config_file = os.environ.get('CONFIG_FILE', "config/sites.yaml")
        
        self.config_manager = ConfigManager(config_file)
        self.writer = ChangeDetectionWriter()
        self.baseline_manager = BaselineManager()
        self.firecrawl_config = self.config_manager.get_firecrawl_config()
    
    def _preserve_failed_urls_in_baseline(self, site_name: str, baseline: Dict[str, Any]):
        """Preserve failed URLs from progress files in the baseline before deleting them."""
        try:
            progress_dir = "progress"
            if not os.path.exists(progress_dir):
                return
            
            # Create safe site name (same logic as in ContentDetector)
            safe_site_name = re.sub(r'[^a-zA-Z0-9]', '_', site_name)
            
            # Look for progress file
            simple_progress_file = os.path.join(progress_dir, f"{safe_site_name}_progress.json")
            if os.path.exists(simple_progress_file):
                with open(simple_progress_file, 'r') as f:
                    progress_data = json.load(f)
                
                # Extract failed URLs from progress file
                failed_urls = progress_data.get('failed_urls', {})
                if failed_urls:
                    # Add failed URLs to baseline
                    baseline['failed_urls'] = failed_urls
                    failed_count = sum(len(urls) for urls in failed_urls.values())
                    print(f"💾 Preserved {failed_count} failed URLs in baseline")
                    
                    # Add failed URL metadata
                    baseline['failed_urls_metadata'] = {
                        'preserved_at': datetime.now().isoformat(),
                        'total_failed_urls': failed_count,
                        'failure_types': list(failed_urls.keys())
                    }
                    
        except Exception as e:
            print(f"⚠️ Warning: Failed to preserve failed URLs for {site_name}: {e}")

    def _is_processing_complete(self, site_name: str, current_state: Dict[str, Any]) -> bool:
        """Check if processing is complete (all URLs processed successfully)."""
        # If rate limited, processing is not complete
        if current_state.get("rate_limited", False):
            return False
        
        # Check if we have a progress file and compare with total URLs
        try:
            progress_dir = "progress"
            if not os.path.exists(progress_dir):
                return True  # No progress file means no processing was done
            
            # Create safe site name
            safe_site_name = re.sub(r'[^a-zA-Z0-9]', '_', site_name)
            progress_file = os.path.join(progress_dir, f"{safe_site_name}_progress.json")
            
            if not os.path.exists(progress_file):
                return True  # No progress file means no processing was done
            
            # Load progress data
            import json
            with open(progress_file, 'r') as f:
                progress_data = json.load(f)
            
            # Get counts
            urls_processed = len(progress_data.get('urls_processed', []))
            total_urls = len(progress_data.get('total_urls', []))
            failed_urls = sum(len(urls) for urls in progress_data.get('failed_urls', {}).values())
            
            # Processing is complete if all URLs have been handled (processed + failed)
            is_complete = (urls_processed + failed_urls) >= total_urls
            
            if is_complete:
                print(f"📊 Processing complete: {urls_processed} processed + {failed_urls} failed = {urls_processed + failed_urls}/{total_urls} URLs")
            else:
                print(f"📊 Processing incomplete: {urls_processed} processed + {failed_urls} failed = {urls_processed + failed_urls}/{total_urls} URLs")
            
            return is_complete
            
        except Exception as e:
            print(f"⚠️ Warning: Error checking processing completion for {site_name}: {e}")
            return False  # Assume incomplete if we can't determine

    def _delete_progress_files(self, site_name: str):
        """Delete progress files for a site after baseline creation."""
        try:
            progress_dir = "progress"
            if not os.path.exists(progress_dir):
                return
            
            # Create safe site name (same logic as in ContentDetector)
            safe_site_name = re.sub(r'[^a-zA-Z0-9]', '_', site_name)
            
            # Delete simple progress file
            simple_progress_file = os.path.join(progress_dir, f"{safe_site_name}_progress.json")
            if os.path.exists(simple_progress_file):
                os.remove(simple_progress_file)
                print(f"🗑️ Deleted progress file: {simple_progress_file}")
            
            # Delete any timestamped progress files for this site
            progress_files = [f for f in os.listdir(progress_dir) if f.startswith(f"{safe_site_name}_progress_") and f.endswith('.json')]
            for progress_file in progress_files:
                file_path = os.path.join(progress_dir, progress_file)
                os.remove(file_path)
                print(f"🗑️ Deleted progress file: {file_path}")
                
        except Exception as e:
            print(f"⚠️ Warning: Failed to delete progress files for {site_name}: {e}")

    async def detect_changes_for_site(self, site_id: str) -> Dict[str, Any]:
        """Detect changes for a specific site using all configured methods."""
        site_config = self.config_manager.get_site(site_id)
        if not site_config:
            raise ValueError(f"Site '{site_id}' not found in configuration")
        
        results = {
            "site_id": site_id,
            "site_name": site_config.name,
            "detection_time": datetime.now().isoformat(),
            "methods": {},
            "baseline_updated": False,
            "baseline_file": None
        }
        
        for method in site_config.detection_methods:
            try:
                method_result = await self._run_detection_method(site_config, method)
                results["methods"][method] = method_result
                
                # Check if baseline was updated in this method
                if method_result.get("baseline_updated", False):
                    results["baseline_updated"] = True
                    results["baseline_file"] = method_result.get("baseline_file")
                    
            except Exception as e:
                results["methods"][method] = {
                    "error": str(e),
                    "detection_time": datetime.now().isoformat()
                }
        
        output_file = self.writer.write_changes(site_config.name, results)
        results["output_file"] = output_file
        
        return results
    
    async def detect_changes_for_all_sites(self) -> Dict[str, Any]:
        """Detect changes for all active sites."""
        active_sites = self.config_manager.get_active_sites()
        all_results = {
            "detection_time": datetime.now().isoformat(),
            "sites": {}
        }
        
        for site in active_sites:
            site_id = self._get_site_id(site)
            try:
                site_results = await self.detect_changes_for_site(site_id)
                all_results["sites"][site_id] = site_results
            except Exception as e:
                all_results["sites"][site_id] = {
                    "error": str(e),
                    "detection_time": datetime.now().isoformat()
                }
        
        return all_results
    
    async def _run_detection_method(self, site_config: Any, method: str) -> Dict[str, Any]:
        """Run a specific detection method for a site with baseline evolution."""
        # Get current baseline (not just previous state)
        current_baseline = self.baseline_manager.get_latest_baseline(site_config.name)
        
        # Create detector and get current state
        detector = self._create_detector(site_config, method)
        current_state = await detector.get_current_state()
        
        # If no baseline exists, create initial baseline
        if current_baseline is None:
            # Check if the current state indicates rate limiting
            if current_state.get("rate_limited", False):
                progress_pages = len(current_state.get("content_hashes", {}))
                print(f"🛑 Rate limiting detected for {site_config.name} - skipping baseline creation")
                print(f"📊 Progress from previous runs: {progress_pages} URLs with content hashes preserved")
                print(f"💡 Note: Content hashes from previous successful runs are preserved but not used for baseline creation")
                
                return {
                    "detection_method": method,
                    "site_name": site_config.name,
                    "detection_time": datetime.now().isoformat(),
                    "error": "Severe rate limiting detected - baseline creation skipped",
                    "rate_limited": True,
                    "changes": [],
                    "summary": {
                        "total_changes": 0,
                        "new_pages": 0,
                        "modified_pages": 0,
                        "deleted_pages": 0
                    },
                    "metadata": {
                        "message": "Baseline creation skipped due to rate limiting",
                        "baseline_created": False,
                        "rate_limited": True,
                        "progress_pages": progress_pages,
                        "note": f"Content hashes from {progress_pages} URLs from previous runs are preserved but not used for baseline creation"
                    },
                    "baseline_updated": False,
                    "baseline_file": None
                }
            
            print(f"📋 No baseline found for {site_config.name}, creating initial baseline...")
            
            # For initial baseline, we need to fetch content hashes if this is a sitemap-only detection
            if method == "sitemap" and "content_hashes" not in current_state:
                print(f"🔍 Fetching content hashes for initial baseline...")
                try:
                    # Create a content detector to fetch hashes for all URLs
                    from .content_detector import ContentDetector
                    content_detector = ContentDetector(site_config)
                    
                    # Get content hashes for all URLs in the sitemap
                    urls = current_state.get("urls", [])
                    if urls:
                        content_hashes = await content_detector._fetch_content_hashes(urls)
                        current_state["content_hashes"] = content_hashes
                        print(f"✅ Fetched content hashes for {len(content_hashes)} URLs")
                    else:
                        current_state["content_hashes"] = {}
                        print("⚠️ No URLs found in sitemap for content hash fetching")
                except Exception as e:
                    print(f"⚠️ Error fetching content hashes: {e}")
                    current_state["content_hashes"] = {}
            
            # For hybrid method, extract content hashes from content_state and flatten sitemap_state
            elif method == "hybrid" and "content_state" in current_state:
                content_state = current_state.get("content_state")
                if content_state and "content_hashes" in content_state:
                    current_state["content_hashes"] = content_state["content_hashes"]
                    print(f"✅ Extracted content hashes from hybrid detection: {len(content_state['content_hashes'])} URLs")
                else:
                    current_state["content_hashes"] = {}
                    print("⚠️ No content hashes found in hybrid content_state")
                
                # Flatten sitemap_state for baseline creation
                sitemap_state = current_state.get("sitemap_state", {})
                if sitemap_state:
                    current_state["sitemap_state"] = sitemap_state
                    print(f"✅ Flattened sitemap state: {len(sitemap_state.get('urls', []))} URLs")
            
            initial_baseline = self.baseline_manager.merger.create_initial_baseline(
                site_config.name, site_config.name, current_state
            )
            
            # Check if we have an existing baseline that might be incorrect
            existing_baseline = self.baseline_manager.get_latest_baseline(site_config.name)
            if existing_baseline:
                # Check if the existing baseline is incorrect (has wrong number of content hashes)
                existing_content_hashes = len(existing_baseline.get('content_hashes', {}))
                new_content_hashes = len(initial_baseline.get('content_hashes', {}))
                existing_sitemap_urls = len(existing_baseline.get('sitemap_state', {}).get('urls', []))
                new_sitemap_urls = len(initial_baseline.get('sitemap_state', {}).get('urls', []))
                
                # If the existing baseline has significantly fewer content hashes than sitemap URLs, it's likely incorrect
                if (existing_content_hashes < existing_sitemap_urls * 0.5 and 
                    new_content_hashes >= new_sitemap_urls * 0.9):
                    print(f"⚠️ Existing baseline appears incorrect ({existing_content_hashes} vs {existing_sitemap_urls} URLs)")
                    print(f"🔄 Replacing with correct baseline ({new_content_hashes} content hashes)")
                    baseline_file = self.baseline_manager.replace_baseline(site_config.name, initial_baseline)
                else:
                    # Existing baseline looks correct, create new one
                    baseline_file = self.baseline_manager.save_baseline(site_config.name, initial_baseline)
            else:
                # No existing baseline, create new one
                baseline_file = self.baseline_manager.save_baseline(site_config.name, initial_baseline)
            
            # Still write current state for historical tracking
            self.writer.write_site_state(site_config.name, current_state)
            
            # Preserve failed URLs from progress files in the baseline
            self._preserve_failed_urls_in_baseline(site_config.name, initial_baseline)
            
            # Check if processing is complete
            is_complete = self._is_processing_complete(site_config.name, current_state)
            
            if is_complete:
                print(f"✅ Processing complete - deleting progress files")
                self._delete_progress_files(site_config.name)
            else:
                print(f"⚠️ Processing incomplete - keeping progress files for next run")
            
            return {
                "detection_method": method,
                "site_name": site_config.name,
                "detection_time": datetime.now().isoformat(),
                "changes": [],
                "summary": {
                    "total_changes": 0,
                    "new_pages": 0,
                    "modified_pages": 0,
                    "deleted_pages": 0
                },
                "metadata": {
                    "message": "Initial baseline created",
                    "baseline_created": True,
                    "baseline_file": baseline_file
                },
                "baseline_updated": True,
                "baseline_file": baseline_file
            }
        
        # Check if the current state indicates rate limiting (even with existing baseline)
        if current_state.get("rate_limited", False):
            progress_pages = len(current_state.get("content_hashes", {}))
            baseline_pages = len(current_baseline.get("content_hashes", {})) if current_baseline else 0
            print(f"🛑 Rate limiting detected for {site_config.name} - skipping change detection")
            print(f"📊 Progress from previous runs: {progress_pages} URLs with content hashes preserved")
            print(f"📋 Existing baseline: {baseline_pages} URLs")
            print(f"💡 Note: Content hashes from previous successful runs are preserved but change detection is skipped")
            
            return {
                "detection_method": method,
                "site_name": site_config.name,
                "detection_time": datetime.now().isoformat(),
                "error": "Severe rate limiting detected - change detection skipped",
                "rate_limited": True,
                "changes": [],
                "summary": {
                    "total_changes": 0,
                    "new_pages": 0,
                    "modified_pages": 0,
                    "deleted_pages": 0
                },
                "metadata": {
                    "message": "Change detection skipped due to rate limiting",
                    "baseline_created": False,
                    "rate_limited": True,
                    "progress_pages": progress_pages,
                    "baseline_pages": baseline_pages,
                    "note": f"Content hashes from {progress_pages} URLs from previous runs are preserved but change detection is skipped"
                },
                "baseline_updated": False,
                "baseline_file": None
            }
        
        # Detect changes against the current baseline
        change_result = await detector.detect_changes(current_baseline)
        
        # Update baseline if changes were detected
        baseline_updated = False
        baseline_file = None
        
        if change_result.changes:
            print(f"🔄 Changes detected for {site_config.name}, updating baseline...")
            
            # Create new baseline by merging with current state and changes
            new_baseline = self.baseline_manager.update_baseline_from_changes(
                site_config.name, current_baseline, current_state, change_result.changes
            )
            
            # Save the new baseline
            baseline_file = self.baseline_manager.save_baseline(site_config.name, new_baseline)
            baseline_updated = True
            
            print(f"✅ Baseline updated: {baseline_file}")
            
            # Log the baseline update event
            self.baseline_manager._log_baseline_event("baseline_updated", site_config.name, {
                "file_path": baseline_file,
                "changes_applied": len(change_result.changes),
                "new_urls": len([c for c in change_result.changes if c.get("change_type") == "new"]),
                "modified_urls": len([c for c in change_result.changes if c.get("change_type") == "modified"]),
                "deleted_urls": len([c for c in change_result.changes if c.get("change_type") == "deleted"]),
                "previous_baseline_date": current_baseline.get("baseline_date") if current_baseline else None,
                "baseline_date": new_baseline.get("baseline_date"),
                "evolution_type": "automatic_update"
            })
            
            # Validate the merge result
            validation_result = self.baseline_manager.merger.validate_merge_result(
                current_baseline, new_baseline, change_result.changes
            )
            
            # Log validation results
            self.baseline_manager._log_baseline_event("baseline_validation", site_config.name, {
                "is_valid": validation_result["is_valid"],
                "errors": validation_result.get("errors", []),
                "warnings": validation_result.get("warnings", []),
                "baseline_file": baseline_file
            })
            
            if not validation_result["is_valid"]:
                print(f"⚠️ Baseline merge validation failed: {validation_result['errors']}")
            elif validation_result["warnings"]:
                print(f"⚠️ Baseline merge warnings: {validation_result['warnings']}")
            
            # Preserve failed URLs from progress files in the baseline
            self._preserve_failed_urls_in_baseline(site_config.name, new_baseline)
            
            # Check if processing is complete
            is_complete = self._is_processing_complete(site_config.name, current_state)
            
            if is_complete:
                print(f"✅ Processing complete - deleting progress files")
                self._delete_progress_files(site_config.name)
            else:
                print(f"⚠️ Processing incomplete - keeping progress files for next run")
        
        # Still write current state for historical tracking
        self.writer.write_site_state(site_config.name, current_state)
        
        # Convert result to dict and add baseline information
        result_dict = change_result.to_dict()
        result_dict.update({
            "baseline_updated": baseline_updated,
            "baseline_file": baseline_file,
            "baseline_evolution": {
                "previous_baseline_date": current_baseline.get("baseline_date") if current_baseline else None,
                "changes_applied": len(change_result.changes) if baseline_updated else 0,
                "evolution_type": "automatic_update" if baseline_updated else "no_changes"
            }
        })
        
        return result_dict
    
    def _create_detector(self, site_config: Any, method: str) -> BaseDetector:
        """Create a detector instance for the specified method."""
        if method == "sitemap":
            return SitemapDetector(site_config)
        elif method == "firecrawl":
            api_key = self.firecrawl_config.get("api_key")
            base_url = self.firecrawl_config.get("base_url", "https://api.firecrawl.dev")
            detector = FirecrawlDetector(site_config, api_key, base_url)
            # Pass firecrawl configuration to the detector
            detector.firecrawl_config = self.firecrawl_config
            return detector
        elif method == "content":
            return ContentDetector(site_config)
        elif method == "hybrid":
            return HybridDetector(site_config)
        else:
            raise ValueError(f"Unknown detection method: {method}")
    
    async def _get_previous_state(self, site_name: str, method: str) -> Optional[Dict[str, Any]]:
        """Get the previous state for a site and method (legacy method for backward compatibility)."""
        try:
            # Use get_previous_state_file to ensure we get a state from a different run
            previous_state_file = self.writer.get_previous_state_file(site_name, method)
            if previous_state_file:
                state_data = self.writer.read_json_file(previous_state_file)
                return state_data.get("state")
        except Exception as e:
            print(f"Error reading previous state for {site_name}: {e}")
        
        return None
    
    def _get_site_id(self, site_config: Any) -> str:
        """Get the site ID from site configuration."""
        for site_id, config in self.config_manager.sites.items():
            if config.name == site_config.name:
                return site_id
        return site_config.name.lower().replace(" ", "_")
    
    def get_site_status(self, site_id: str) -> Dict[str, Any]:
        """Get the current status and recent changes for a site."""
        site_config = self.config_manager.get_site(site_id)
        if not site_config:
            return {"error": f"Site '{site_id}' not found"}
        
        change_files = self.writer.list_change_files(site_config.name)
        latest_state_file = self.writer.get_latest_state_file(site_config.name)
        latest_baseline = self.baseline_manager.get_latest_baseline(site_config.name)
        
        return {
            "site_id": site_id,
            "site_name": site_config.name,
            "url": site_config.url,
            "is_active": site_config.is_active,
            "detection_methods": site_config.detection_methods,
            "recent_change_files": change_files[:5],
            "latest_state_file": latest_state_file,
            "latest_baseline": {
                "date": latest_baseline.get("baseline_date") if latest_baseline else None,
                "total_urls": latest_baseline.get("total_urls") if latest_baseline else 0,
                "total_content_hashes": latest_baseline.get("total_content_hashes") if latest_baseline else 0
            } if latest_baseline else None
        }
    
    def list_sites(self) -> List[Dict[str, Any]]:
        """List all configured sites with their status."""
        sites = []
        for site_id, site_config in self.config_manager.sites.items():
            latest_baseline = self.baseline_manager.get_latest_baseline(site_config.name)
            sites.append({
                "site_id": site_id,
                "name": site_config.name,
                "url": site_config.url,
                "is_active": site_config.is_active,
                "detection_methods": site_config.detection_methods,
                "check_interval_minutes": site_config.check_interval_minutes,
                "latest_baseline": {
                    "date": latest_baseline.get("baseline_date") if latest_baseline else None,
                    "total_urls": latest_baseline.get("total_urls") if latest_baseline else 0
                } if latest_baseline else None
            })
        return sites 