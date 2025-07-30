# ==============================================================================
# sitemap_detector.py — Sitemap-based Change Detector
# ==============================================================================
# Purpose: Detect changes by comparing sitemap URLs between runs
# Sections: Imports, SitemapDetector Class
# ==============================================================================

# ==============================================================================
# Imports
# ==============================================================================

# Standard Library -----
import asyncio
import aiohttp
import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Optional, Set
from urllib.parse import urljoin, urlparse
from datetime import datetime

# Internal -----
from .base_detector import BaseDetector, ChangeResult

# ==============================================================================
# Public exports
# ==============================================================================
__all__ = ['SitemapDetector']


class SitemapDetector(BaseDetector):
    """Detects changes by monitoring sitemap URLs."""
    
    def __init__(self, site_config: Any):
        super().__init__(site_config)
        self.sitemap_url = site_config.sitemap_url or self._guess_sitemap_url()
    
    def _guess_sitemap_url(self) -> str:
        """Guess the sitemap URL if not provided."""
        parsed = urlparse(self.site_url)
        return f"{parsed.scheme}://{parsed.netloc}/sitemap.xml"
    
    async def get_current_state(self) -> Dict[str, Any]:
        """Get the current state by fetching and parsing the sitemap."""
        try:
            urls = await self._fetch_sitemap_urls()
            
            return {
                "detection_method": "sitemap",
                "sitemap_url": self.sitemap_url,
                "urls": urls,
                "total_urls": len(urls),
                "captured_at": datetime.now().isoformat(),
                "site_url": self.site_url
            }
        except Exception as e:
            return {
                "detection_method": "sitemap",
                "sitemap_url": self.sitemap_url,
                "error": str(e),
                "urls": [],
                "total_urls": 0,
                "captured_at": datetime.now().isoformat(),
                "site_url": self.site_url
            }
    
    async def detect_changes(self, previous_state: Optional[Dict[str, Any]] = None) -> ChangeResult:
        """Detect changes by comparing current sitemap with previous state."""
        result = self.create_result()
        
        try:
            current_urls = await self._fetch_sitemap_urls()
            current_state = await self.get_current_state()
            
            if previous_state is None:
                result.metadata["message"] = "First run - no previous state to compare"
                result.metadata["current_urls"] = len(current_urls)
                return result
            
            previous_urls = set(previous_state.get("urls", []))
            current_urls_set = set(current_urls)
            
            new_urls = current_urls_set - previous_urls
            for url in new_urls:
                result.add_change("new", url, title=f"New page: {url}")
            
            deleted_urls = previous_urls - current_urls_set
            for url in deleted_urls:
                result.add_change("deleted", url, title=f"Removed page: {url}")
            
            result.metadata.update({
                "current_urls": len(current_urls),
                "previous_urls": len(previous_urls),
                "new_urls": len(new_urls),
                "deleted_urls": len(deleted_urls),
                "sitemap_url": self.sitemap_url
            })
            
        except Exception as e:
            result.metadata["error"] = str(e)
            result.metadata["sitemap_url"] = self.sitemap_url
        
        return result
    
    async def _fetch_sitemap_urls(self) -> List[str]:
        """Fetch and parse sitemap to extract URLs."""
        async with aiohttp.ClientSession() as session:
            async with session.get(self.sitemap_url, timeout=30) as response:
                if response.status != 200:
                    raise Exception(f"Failed to fetch sitemap: {response.status}")
                
                content = await response.text()
                return self._parse_sitemap(content)
    
    def _parse_sitemap(self, content: str) -> List[str]:
        """Parse sitemap XML content to extract URLs."""
        urls = []
        
        try:
            namespaces = {
                'sitemap': 'http://www.sitemaps.org/schemas/sitemap/0.9',
                'news': 'http://www.google.com/schemas/sitemap-news/0.9'
            }
            
            root = ET.fromstring(content)
            
            url_elements = root.findall('.//sitemap:url', namespaces)
            if not url_elements:
                url_elements = root.findall('.//url')
            
            for url_elem in url_elements:
                loc_elem = url_elem.find('sitemap:loc', namespaces)
                if loc_elem is None:
                    loc_elem = url_elem.find('loc')
                
                if loc_elem is not None and loc_elem.text:
                    urls.append(loc_elem.text.strip())
            
            sitemap_elements = root.findall('.//sitemap:sitemap', namespaces)
            if not sitemap_elements:
                sitemap_elements = root.findall('.//sitemap')
            
            for sitemap_elem in sitemap_elements:
                loc_elem = sitemap_elem.find('sitemap:loc', namespaces)
                if loc_elem is None:
                    loc_elem = sitemap_elem.find('loc')
                
                if loc_elem is not None and loc_elem.text:
                    pass
            
        except ET.ParseError as e:
            raise Exception(f"Failed to parse sitemap XML: {e}")
        
        return urls
    
    async def _fetch_sitemap_index(self, index_url: str) -> List[str]:
        """Fetch URLs from a sitemap index file."""
        return [] 