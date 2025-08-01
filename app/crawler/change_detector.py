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

# Internal -----
from .base_detector import BaseDetector, ChangeResult
from .sitemap_detector import SitemapDetector
from .firecrawl_detector import FirecrawlDetector
from .content_detector import ContentDetector
from .hybrid_detector import HybridDetector
from ..utils.json_writer import ChangeDetectionWriter
from ..utils.config import ConfigManager

# ==============================================================================
# Public exports
# ==============================================================================
__all__ = ['ChangeDetector']


class ChangeDetector:
    """Main orchestrator for change detection across multiple sites and methods."""
    
    def __init__(self, config_file: str = "config/sites.yaml"):
        """Initialize the change detector."""
        self.config_manager = ConfigManager(config_file)
        self.writer = ChangeDetectionWriter()
        self.firecrawl_config = self.config_manager.get_firecrawl_config()
    
    async def detect_changes_for_site(self, site_id: str) -> Dict[str, Any]:
        """Detect changes for a specific site using all configured methods."""
        site_config = self.config_manager.get_site(site_id)
        if not site_config:
            raise ValueError(f"Site '{site_id}' not found in configuration")
        
        results = {
            "site_id": site_id,
            "site_name": site_config.name,
            "detection_time": datetime.now().isoformat(),
            "methods": {}
        }
        
        for method in site_config.detection_methods:
            try:
                method_result = await self._run_detection_method(site_config, method)
                results["methods"][method] = method_result
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
        """Run a specific detection method for a site."""
        previous_state = await self._get_previous_state(site_config.name, method)
        
        detector = self._create_detector(site_config, method)
        
        change_result = await detector.detect_changes(previous_state)
        
        current_state = await detector.get_current_state()
        self.writer.write_site_state(site_config.name, current_state)
        
        return change_result.to_dict()
    
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
        """Get the previous state for a site and method."""
        try:
            latest_state_file = self.writer.get_latest_state_file(site_name, method)
            if latest_state_file:
                state_data = self.writer.read_json_file(latest_state_file)
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
        
        return {
            "site_id": site_id,
            "site_name": site_config.name,
            "url": site_config.url,
            "is_active": site_config.is_active,
            "detection_methods": site_config.detection_methods,
            "recent_change_files": change_files[:5],
            "latest_state_file": latest_state_file
        }
    
    def list_sites(self) -> List[Dict[str, Any]]:
        """List all configured sites with their status."""
        sites = []
        for site_id, site_config in self.config_manager.sites.items():
            sites.append({
                "site_id": site_id,
                "name": site_config.name,
                "url": site_config.url,
                "is_active": site_config.is_active,
                "detection_methods": site_config.detection_methods
            })
        return sites 