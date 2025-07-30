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
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

# Third Party -----
from firecrawl import FirecrawlApp, ScrapeOptions

# Internal -----
from .base_detector import BaseDetector, ChangeResult

# ==============================================================================
# Public exports
# ==============================================================================
__all__ = ['FirecrawlDetector']


class FirecrawlDetector(BaseDetector):
    """Detects changes using the Firecrawl API with change tracking."""
    
    def __init__(self, site_config: Any, api_key: str, base_url: str = "https://api.firecrawl.dev"):
        super().__init__(site_config)
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.app = FirecrawlApp(api_key=self.api_key)
    
    async def get_current_state(self) -> Dict[str, Any]:
        """Get the current state using Firecrawl's crawl with change tracking."""
        try:
            crawl_data = await self._crawl_with_change_tracking()
            
            return {
                "detection_method": "firecrawl",
                "site_url": self.site_url,
                "crawl_data": crawl_data,
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
                crawl_data = await self._crawl_with_change_tracking()
                result.metadata["message"] = "First run - established baseline with crawl"
                result.metadata["total_pages_crawled"] = len(crawl_data.get("data", []))
                return result
            
            # For subsequent runs, we'll use the same crawl with change tracking
            # The API will automatically compare with the previous state
            crawl_data = await self._crawl_with_change_tracking()
            
            # Process change tracking data
            for page_data in crawl_data.get("data", []):
                change_tracking = page_data.get("changeTracking", {})
                change_status = change_tracking.get("changeStatus", "unknown")
                visibility = change_tracking.get("visibility", "unknown")
                
                # Only report actual changes
                if change_status in ["new", "changed", "removed"]:
                    url = page_data.get("metadata", {}).get("url", "")
                    title = page_data.get("metadata", {}).get("title", "")
                    
                    result.add_change(
                        change_type=change_status,
                        url=url,
                        title=title,
                        visibility=visibility,
                        previous_scrape_at=change_tracking.get("previousScrapeAt"),
                        firecrawl_data=page_data
                    )
            
            result.metadata.update({
                "firecrawl_response": crawl_data,
                "api_endpoint": "FirecrawlApp SDK",
                "total_pages_crawled": len(crawl_data.get("data", [])),
                "credits_used": crawl_data.get("creditsUsed", 0)
            })
            
        except Exception as e:
            result.metadata["error"] = str(e)
            result.metadata["api_endpoint"] = "FirecrawlApp SDK"
        
        return result
    
    async def _crawl_with_change_tracking(self) -> Dict[str, Any]:
        """Crawl the site with change tracking enabled using the Firecrawl SDK."""
        try:
            # Run the crawl in a thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, 
                self._sync_crawl_with_change_tracking
            )
            return result
        except Exception as e:
            raise Exception(f"Firecrawl SDK error: {e}")
    
    def _sync_crawl_with_change_tracking(self) -> Dict[str, Any]:
        """Synchronous crawl method for the SDK."""
        try:
            scrape_options = ScrapeOptions(formats=['markdown', 'changeTracking'])
            result = self.app.crawl_url(
                self.site_url,
                scrape_options=scrape_options
            )
            return result
        except Exception as e:
            raise Exception(f"Firecrawl SDK crawl error: {e}") 