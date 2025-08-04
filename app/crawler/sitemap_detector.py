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
    """Detects changes by monitoring sitemap URLs, including sitemap indexes."""
    
    def __init__(self, site_config: Any):
        super().__init__(site_config)
        self.sitemap_url = site_config.sitemap_url or self._guess_sitemap_url()
        # Configuration for URL verification
        self.verify_deleted_urls = getattr(site_config, 'verify_deleted_urls', True)
        self.max_concurrent_checks = getattr(site_config, 'max_concurrent_checks', 5)
        self.verification_timeout = getattr(site_config, 'verification_timeout', 10)
    
    def _guess_sitemap_url(self) -> str:
        """Guess the sitemap URL if not provided."""
        parsed = urlparse(self.site_url)
        return f"{parsed.scheme}://{parsed.netloc}/sitemap.xml"
    
    async def get_current_state(self) -> Dict[str, Any]:
        """Get the current state by fetching and parsing the sitemap(s)."""
        try:
            urls, sitemap_info = await self._fetch_all_sitemap_urls()
            
            return {
                "detection_method": "sitemap",
                "sitemap_url": self.sitemap_url,
                "urls": urls,
                "total_urls": len(urls),
                "sitemap_info": sitemap_info,
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
                "sitemap_info": {},
                "captured_at": datetime.now().isoformat(),
                "site_url": self.site_url
            }
    
    async def detect_changes(self, previous_baseline: Optional[Dict[str, Any]] = None) -> ChangeResult:
        """Detect changes by comparing current sitemap with previous baseline."""
        result = self.create_result()
        
        try:
            current_urls, sitemap_info = await self._fetch_all_sitemap_urls()
            current_state = await self.get_current_state()
            
            if previous_baseline is None:
                result.metadata["message"] = "First run - establishing baseline"
                result.metadata["current_urls"] = len(current_urls)
                result.metadata["sitemap_info"] = sitemap_info
                return result
            
            # Compare against baseline URLs
            baseline_urls = set(previous_baseline.get("sitemap_state", {}).get("urls", []))
            current_urls_set = set(current_urls)
            
            new_urls = current_urls_set - baseline_urls
            for url in new_urls:
                result.add_change("new", url, title=f"New page: {url}")
            
            deleted_urls = baseline_urls - current_urls_set
            
            # Verify that "deleted" URLs are actually deleted by checking if they still exist
            if self.verify_deleted_urls and deleted_urls:
                verified_deleted_urls = await self._verify_deleted_urls(deleted_urls)
            else:
                verified_deleted_urls = deleted_urls
            
            for url in verified_deleted_urls:
                result.add_change("deleted", url, title=f"Removed page: {url}")
            
            # Add metadata about verification
            result.metadata.update({
                "current_urls": len(current_urls),
                "baseline_urls": len(baseline_urls),
                "new_urls": len(new_urls),
                "deleted_urls": len(verified_deleted_urls),
                "unverified_deleted_urls": len(deleted_urls) - len(verified_deleted_urls),
                "sitemap_url": self.sitemap_url,
                "sitemap_info": sitemap_info
            })
            
        except Exception as e:
            result.metadata["error"] = str(e)
            result.metadata["sitemap_url"] = self.sitemap_url
        
        return result
    
    async def _verify_deleted_urls(self, deleted_urls: set) -> set:
        """Verify that URLs marked as deleted are actually deleted by checking their HTTP status."""
        import aiohttp
        
        verified_deleted = set()
        
        # Limit concurrent requests to avoid overwhelming the server
        semaphore = asyncio.Semaphore(self.max_concurrent_checks)
        
        async def check_url(url: str) -> tuple[str, bool]:
            async with semaphore:
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.head(url, timeout=self.verification_timeout, allow_redirects=False) as response:
                            # Consider 404, 410, and 5xx errors as "deleted"
                            # 200, 301, 302, etc. mean the page still exists
                            is_deleted = response.status in [404, 410] or response.status >= 500
                            return url, is_deleted
                except Exception:
                    # If we can't check the URL, assume it might still exist
                    return url, False
        
        # Check all URLs concurrently
        tasks = [check_url(url) for url in deleted_urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, tuple):
                url, is_deleted = result
                if is_deleted:
                    verified_deleted.add(url)
        
        return verified_deleted
    
    async def _fetch_all_sitemap_urls(self) -> tuple[List[str], Dict[str, Any]]:
        """Fetch and parse all sitemaps (including sitemap indexes) to extract URLs."""
        async with aiohttp.ClientSession() as session:
            async with session.get(self.sitemap_url, timeout=30) as response:
                if response.status != 200:
                    raise Exception(f"Failed to fetch sitemap: {response.status}")
                
                content = await response.text()
                
                # Check if this is a sitemap index
                if self._is_sitemap_index(content):
                    return await self._fetch_sitemap_index(session, content)
                else:
                    # Single sitemap
                    urls = self._parse_sitemap(content)
                    
                    # Extract last modified date
                    last_modified = self._extract_last_modified(content)
                    
                    sitemap_info = {
                        "type": "single_sitemap",
                        "sitemap_url": self.sitemap_url,
                        "total_urls": len(urls)
                    }
                    
                    if last_modified:
                        sitemap_info["last_modified"] = last_modified
                    
                    return urls, sitemap_info
    
    def _is_sitemap_index(self, content: str) -> bool:
        """Check if the XML content is a sitemap index."""
        try:
            root = ET.fromstring(content)
            namespaces = {
                'sitemap': 'http://www.sitemaps.org/schemas/sitemap/0.9'
            }
            
            # Look for sitemap elements (indicating an index)
            sitemap_elements = root.findall('.//sitemap:sitemap', namespaces)
            if not sitemap_elements:
                sitemap_elements = root.findall('.//sitemap')
            
            return len(sitemap_elements) > 0
        except ET.ParseError:
            return False
    
    async def _fetch_sitemap_index(self, session: aiohttp.ClientSession, index_content: str) -> tuple[List[str], Dict[str, Any]]:
        """Fetch URLs from a sitemap index file and all referenced sitemaps."""
        all_urls = []
        sitemap_info = {
            "type": "sitemap_index",
            "index_url": self.sitemap_url,
            "sitemaps": []
        }
        
        # Extract last_modified from the sitemap index itself
        index_last_modified = self._extract_last_modified(index_content)
        if index_last_modified:
            sitemap_info["index_last_modified"] = index_last_modified
        
        # Parse the sitemap index
        sitemap_urls = self._parse_sitemap_index(index_content)
        
        # Fetch each individual sitemap
        tasks = []
        for sitemap_url in sitemap_urls:
            tasks.append(self._fetch_individual_sitemap(session, sitemap_url))
        
        # Wait for all sitemaps to be fetched
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(results):
            sitemap_url = sitemap_urls[i]
            if isinstance(result, Exception):
                sitemap_info["sitemaps"].append({
                    "url": sitemap_url,
                    "status": "error",
                    "error": str(result),
                    "urls": 0
                })
            else:
                urls, last_modified = result
                all_urls.extend(urls)
                sitemap_info["sitemaps"].append({
                    "url": sitemap_url,
                    "status": "success",
                    "urls": len(urls),
                    "last_modified": last_modified
                })
        
        sitemap_info["total_urls"] = len(all_urls)
        sitemap_info["total_sitemaps"] = len(sitemap_urls)
        
        return all_urls, sitemap_info
    
    def _parse_sitemap_index(self, content: str) -> List[str]:
        """Parse sitemap index XML to extract sitemap URLs."""
        sitemap_urls = []
        
        try:
            namespaces = {
                'sitemap': 'http://www.sitemaps.org/schemas/sitemap/0.9'
            }
            
            root = ET.fromstring(content)
            
            sitemap_elements = root.findall('.//sitemap:sitemap', namespaces)
            if not sitemap_elements:
                sitemap_elements = root.findall('.//sitemap')
            
            for sitemap_elem in sitemap_elements:
                loc_elem = sitemap_elem.find('sitemap:loc', namespaces)
                if loc_elem is None:
                    loc_elem = sitemap_elem.find('loc')
                
                if loc_elem is not None and loc_elem.text:
                    sitemap_urls.append(loc_elem.text.strip())
            
        except ET.ParseError as e:
            raise Exception(f"Failed to parse sitemap index XML: {e}")
        
        return sitemap_urls
    
    async def _fetch_individual_sitemap(self, session: aiohttp.ClientSession, sitemap_url: str) -> tuple[List[str], Optional[str]]:
        """Fetch and parse an individual sitemap."""
        try:
            async with session.get(sitemap_url, timeout=30) as response:
                if response.status != 200:
                    raise Exception(f"Failed to fetch sitemap {sitemap_url}: {response.status}")
                
                content = await response.text()
                urls = self._parse_sitemap(content)
                
                # Try to extract last modified date
                last_modified = self._extract_last_modified(content)
                
                return urls, last_modified
                
        except Exception as e:
            raise Exception(f"Error fetching sitemap {sitemap_url}: {e}")
    
    def _extract_last_modified(self, content: str) -> Optional[str]:
        """Extract the last modified date from sitemap XML."""
        try:
            namespaces = {
                'sitemap': 'http://www.sitemaps.org/schemas/sitemap/0.9'
            }
            
            root = ET.fromstring(content)
            
            # First, check if this is a sitemap index
            sitemap_elements = root.findall('.//sitemap:sitemap', namespaces)
            if not sitemap_elements:
                sitemap_elements = root.findall('.//sitemap')
            
            if sitemap_elements:
                # This is a sitemap index - extract lastmod from each sitemap element
                last_modified_dates = []
                for sitemap_elem in sitemap_elements:
                    lastmod_elem = sitemap_elem.find('sitemap:lastmod', namespaces)
                    if lastmod_elem is None:
                        lastmod_elem = sitemap_elem.find('lastmod')
                    
                    if lastmod_elem is not None and lastmod_elem.text:
                        last_modified_dates.append(lastmod_elem.text.strip())
                
                # Return the most recent date if any were found
                if last_modified_dates:
                    # Sort dates and return the most recent
                    last_modified_dates.sort(reverse=True)
                    return last_modified_dates[0]
            else:
                # This is a regular sitemap - look for lastmod in individual url elements
                url_elements = root.findall('.//sitemap:url', namespaces)
                if not url_elements:
                    url_elements = root.findall('.//url')
                
                last_modified_dates = []
                for url_elem in url_elements:
                    lastmod_elem = url_elem.find('sitemap:lastmod', namespaces)
                    if lastmod_elem is None:
                        lastmod_elem = url_elem.find('lastmod')
                    
                    if lastmod_elem is not None and lastmod_elem.text:
                        last_modified_dates.append(lastmod_elem.text.strip())
                
                # Return the most recent date if any were found
                if last_modified_dates:
                    # Sort dates and return the most recent
                    last_modified_dates.sort(reverse=True)
                    return last_modified_dates[0]
                
                # Fallback: look for lastmod in the root element
                lastmod_elem = root.find('sitemap:lastmod', namespaces)
                if lastmod_elem is None:
                    lastmod_elem = root.find('lastmod')
                
                if lastmod_elem is not None and lastmod_elem.text:
                    return lastmod_elem.text.strip()
            
            return None
            
        except ET.ParseError:
            return None
    
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
            
        except ET.ParseError as e:
            raise Exception(f"Failed to parse sitemap XML: {e}")
        
        return urls 