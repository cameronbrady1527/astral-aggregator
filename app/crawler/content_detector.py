# ==============================================================================
# content_detector.py — Content-based Change Detector
# ==============================================================================
# Purpose: Detect content changes within existing pages using content hashing
# Sections: Imports, ContentDetector Class
# ==============================================================================

# ==============================================================================
# Imports
# ==============================================================================

# Standard Library -----
import asyncio
import aiohttp
import hashlib
import re
from typing import Dict, Any, List, Optional, Set
from datetime import datetime
from urllib.parse import urljoin

# Third Party -----
from bs4 import BeautifulSoup

# Internal -----
from .base_detector import BaseDetector, ChangeResult

# ==============================================================================
# Public exports
# ==============================================================================
__all__ = ['ContentDetector']


class ContentDetector(BaseDetector):
    """Detects content changes within existing pages using content hashing."""
    
    def __init__(self, site_config: Any):
        super().__init__(site_config)
        self.content_selectors = getattr(site_config, 'content_selectors', ['main', 'article', '.content', '#content'])
        self.exclude_selectors = getattr(site_config, 'exclude_selectors', [
            'nav', 'footer', '.sidebar', '.ads', '.comments', '.header', '.menu'
        ])
        self.max_pages = getattr(site_config, 'max_content_pages', 10)
        self.timeout = getattr(site_config, 'content_timeout', 10)
    
    async def get_current_state(self) -> Dict[str, Any]:
        """Get the current state by fetching and hashing content from key pages."""
        try:
            # Get URLs from sitemap first
            sitemap_urls = await self._get_sitemap_urls()
            
            # Limit to most important pages (0 = no limit, check all pages)
            if self.max_pages > 0:
                key_urls = sitemap_urls[:self.max_pages]
            else:
                key_urls = sitemap_urls  # Check all pages
            
            # Fetch and hash content
            content_hashes = await self._fetch_content_hashes(key_urls)
            
            return {
                "detection_method": "content_hash",
                "site_url": self.site_url,
                "urls_checked": key_urls,
                "content_hashes": content_hashes,
                "total_pages": len(content_hashes),
                "captured_at": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "detection_method": "content_hash",
                "site_url": self.site_url,
                "error": str(e),
                "urls_checked": [],
                "content_hashes": {},
                "total_pages": 0,
                "captured_at": datetime.now().isoformat()
            }
    
    async def detect_changes(self, previous_baseline: Optional[Dict[str, Any]] = None) -> ChangeResult:
        """Detect content changes by comparing content hashes against baseline."""
        result = self.create_result()
        
        try:
            current_state = await self.get_current_state()
            
            if previous_baseline is None:
                result.metadata["message"] = "First run - establishing content baseline"
                result.metadata["pages_checked"] = current_state.get("total_pages", 0)
                return result
            
            # Compare content hashes from baseline
            baseline_hashes = previous_baseline.get("content_hashes", {})
            current_hashes = current_state.get("content_hashes", {})
            
            # Find changed content
            changed_urls = []
            for url, current_hash_data in current_hashes.items():
                baseline_hash_data = baseline_hashes.get(url)
                
                # Handle both old string format and new dict format
                current_hash = current_hash_data.get("hash") if isinstance(current_hash_data, dict) else current_hash_data
                baseline_hash = baseline_hash_data.get("hash") if isinstance(baseline_hash_data, dict) else baseline_hash_data
                
                if baseline_hash and current_hash and baseline_hash != current_hash:
                    changed_urls.append(url)
                    result.add_change(
                        "content_changed", 
                        url, 
                        title=f"Content changed: {url}",
                        description=f"Content hash changed from {baseline_hash[:8]} to {current_hash[:8]}"
                    )
            
            # Find new pages with content
            new_urls = set(current_hashes.keys()) - set(baseline_hashes.keys())
            for url in new_urls:
                result.add_change(
                    "new_content", 
                    url, 
                    title=f"New page with content: {url}"
                )
            
            result.metadata.update({
                "pages_checked": len(current_hashes),
                "content_changes": len(changed_urls),
                "new_pages": len(new_urls),
                "urls_checked": current_state.get("urls_checked", [])
            })
            
        except Exception as e:
            result.metadata["error"] = str(e)
        
        return result
    
    async def _get_sitemap_urls(self) -> List[str]:
        """Get URLs from sitemap to check for content changes."""
        try:
            # Use sitemap detector to get URLs
            from .sitemap_detector import SitemapDetector
            sitemap_detector = SitemapDetector(self.site_config)
            state = await sitemap_detector.get_current_state()
            return state.get("urls", [])
        except Exception as e:
            print(f"Warning: Could not get sitemap URLs: {e}")
            # Fallback to main page
            return [self.site_url]
    
    async def _fetch_content_hashes(self, urls: List[str]) -> Dict[str, Dict[str, Any]]:
        """Fetch content hashes for the given URLs."""
        content_hashes = {}
        successful_fetches = 0
        failed_fetches = 0
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
            tasks = []
            for url in urls:
                task = self._fetch_single_content_hash(session, url)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(results):
                if isinstance(result, tuple) and len(result) == 2:
                    url, content_hash = result
                    if content_hash:
                        # Store as dictionary with hash and metadata
                        content_hashes[url] = {
                            "hash": content_hash,
                            "fetched_at": datetime.now().isoformat(),
                            "status": "success"
                        }
                        successful_fetches += 1
                    else:
                        failed_fetches += 1
                else:
                    failed_fetches += 1
                    print(f"Warning: Failed to fetch content for {urls[i]}: {result}")
        
        print(f"📊 Content hash fetching summary:")
        print(f"   ✅ Successful: {successful_fetches}")
        print(f"   ❌ Failed: {failed_fetches}")
        print(f"   📈 Success rate: {(successful_fetches / len(urls) * 100):.1f}%")
        
        return content_hashes
    
    async def _fetch_single_content_hash(self, session: aiohttp.ClientSession, url: str) -> tuple[str, Optional[str]]:
        """Fetch and hash content for a single URL."""
        try:
            async with session.get(url) as response:
                if response.status != 200:
                    return url, None
                
                content = await response.text()
                
                # Extract main content using selectors
                main_content = self._extract_main_content(content)
                
                if main_content:
                    # Create hash of the content
                    content_hash = hashlib.md5(main_content.encode('utf-8')).hexdigest()
                    return url, content_hash
                else:
                    return url, None
                    
        except Exception as e:
            print(f"Error fetching content from {url}: {e}")
            return url, None
    
    def _extract_main_content(self, html_content: str) -> Optional[str]:
        """Extract main content from HTML using CSS selectors."""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove unwanted elements first
            for selector in self.exclude_selectors:
                for element in soup.select(selector):
                    element.decompose()
            
            # Try to find main content using selectors
            main_content = None
            for selector in self.content_selectors:
                elements = soup.select(selector)
                if elements:
                    # Use the first matching element
                    main_content = elements[0]
                    break
            
            if not main_content:
                # Fallback to body content
                main_content = soup.find('body')
            
            if main_content:
                # Clean up the content
                text = self._clean_text(main_content.get_text())
                return text if text.strip() else None
            
            return None
            
        except Exception as e:
            print(f"Error extracting content: {e}")
            return None
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove leading/trailing whitespace
        text = text.strip()
        # Normalize line breaks
        text = re.sub(r'\n+', '\n', text)
        return text 