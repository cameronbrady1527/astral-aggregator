# ==============================================================================
# firecrawl_detector.py — Firecrawl-based Change Detector
# ==============================================================================
# Purpose: Detect changes using the Firecrawl API for sophisticated change tracking
# Sections: Imports, FirecrawlDetector Class
# ==============================================================================

# ==============================================================================
# Imports
# ==============================================================================

# Standard Library -----
import aiohttp
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

# Internal -----
from .base_detector import BaseDetector, ChangeResult

# ==============================================================================
# Public exports
# ==============================================================================
__all__ = ['FirecrawlDetector']


class FirecrawlDetector(BaseDetector):
    """Detects changes using the Firecrawl API."""
    
    def __init__(self, site_config: Any, api_key: str, base_url: str = "https://api.firecrawl.dev"):
        super().__init__(site_config)
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
    
    async def get_current_state(self) -> Dict[str, Any]:
        """Get the current state using Firecrawl's site mapping."""
        try:
            mapping_data = await self._get_site_mapping()
            
            return {
                "detection_method": "firecrawl",
                "site_url": self.site_url,
                "mapping_data": mapping_data,
                "captured_at": datetime.now().isoformat(),
                "firecrawl_base_url": self.base_url
            }
        except Exception as e:
            return {
                "detection_method": "firecrawl",
                "site_url": self.site_url,
                "error": str(e),
                "captured_at": datetime.now().isoformat(),
                "firecrawl_base_url": self.base_url
            }
    
    async def detect_changes(self, previous_state: Optional[Dict[str, Any]] = None) -> ChangeResult:
        """Detect changes using Firecrawl's change tracking API."""
        result = self.create_result()
        
        try:
            if previous_state is None:
                mapping_data = await self._get_site_mapping()
                result.metadata["message"] = "First run - established baseline with site mapping"
                result.metadata["total_pages_mapped"] = len(mapping_data.get("pages", []))
                return result
            
            changes_data = await self._track_changes(previous_state)
            
            for change in changes_data.get("changes", []):
                change_type = change.get("status", "unknown")
                url = change.get("url", "")
                title = change.get("title", "")
                
                result.add_change(
                    change_type=change_type,
                    url=url,
                    title=title,
                    previous_hash=change.get("previous_hash"),
                    current_hash=change.get("current_hash"),
                    firecrawl_data=change
                )
            
            result.metadata.update({
                "firecrawl_response": changes_data,
                "api_endpoint": f"{self.base_url}/crawl/change-tracking"
            })
            
        except Exception as e:
            result.metadata["error"] = str(e)
            result.metadata["api_endpoint"] = f"{self.base_url}/crawl/change-tracking"
        
        return result
    
    async def _get_site_mapping(self) -> Dict[str, Any]:
        """Get site mapping using Firecrawl's mapping API."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "url": self.site_url,
            "mode": "map"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/crawl/map",
                headers=headers,
                json=payload,
                timeout=60
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Firecrawl API error: {response.status} - {error_text}")
                
                return await response.json()
    
    async def _track_changes(self, previous_state: Dict[str, Any]) -> Dict[str, Any]:
        """Track changes using Firecrawl's change tracking API."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "url": self.site_url,
            "mode": "change-tracking",
            "previous_state": previous_state.get("mapping_data", {})
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/crawl/change-tracking",
                headers=headers,
                json=payload,
                timeout=120
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Firecrawl change tracking error: {response.status} - {error_text}")
                
                return await response.json()
    
    async def _get_crawl_status(self, crawl_id: str) -> Dict[str, Any]:
        """Get the status of a Firecrawl job."""
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/crawl/status/{crawl_id}",
                headers=headers,
                timeout=30
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Firecrawl status error: {response.status} - {error_text}")
                
                return await response.json() 