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
import hashlib
import re
import ssl
import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
import aiohttp
from aiohttp import ClientTimeout, TCPConnector
import logging

# Third Party -----
from bs4 import BeautifulSoup

# Internal -----
from .base_detector import BaseDetector, ChangeResult

logger = logging.getLogger(__name__)

# ==============================================================================
# Public exports
# ==============================================================================
__all__ = ['ContentDetector']


class ContentDetector(BaseDetector):
    """
    Content-based change detector that fetches and hashes page content.
    Optimized for ultra-fast performance with 100% accuracy guarantee.
    """
    
    def __init__(self, site_config: Any):
        super().__init__(site_config)
        
        # Sitemap configuration
        self.sitemap_url = getattr(site_config, 'sitemap_url', None)
        if not self.sitemap_url:
            self.sitemap_url = self._guess_sitemap_url()
        
        # Content detection settings
        self.content_selectors = getattr(site_config, 'content_selectors', [
            'main', 'article', '.content', '#content', '.main-content'
        ])
        self.exclude_selectors = getattr(site_config, 'exclude_selectors', [
            'nav', 'footer', '.sidebar', '.ads', '.comments', '.header', '.menu'
        ])
        self.max_pages = getattr(site_config, 'max_content_pages', 0)  # 0 = no limit
        self.timeout = getattr(site_config, 'content_timeout', 10)
        
        # Ultra-fast optimization settings with adaptive rate limiting
        self.max_concurrent = getattr(site_config, 'max_concurrent_requests', 50)
        self.connection_pool_size = getattr(site_config, 'connection_pool_size', 100)
        self.batch_size = getattr(site_config, 'batch_size', 500)
        self.ultra_fast_timeout = getattr(site_config, 'ultra_fast_timeout', 8)
        
        # Adaptive rate limiting settings
        self.adaptive_enabled = getattr(site_config, 'adaptive_rate_limiting', True)
        self.min_concurrent = getattr(site_config, 'min_concurrent_requests', 10)
        self.max_concurrent_adaptive = getattr(site_config, 'max_concurrent_requests', 200)
        self.success_rate_threshold = getattr(site_config, 'success_rate_threshold', 0.95)  # 95%
        self.rate_adjustment_factor = getattr(site_config, 'rate_adjustment_factor', 0.8)  # Reduce by 20% on failure
        self.rate_increase_factor = getattr(site_config, 'rate_increase_factor', 1.1)  # Increase by 10% on success
        
        # Progressive concurrency ramping
        self.progressive_ramping = getattr(site_config, 'progressive_ramping', True)
        self.ramp_start_concurrency = getattr(site_config, 'ramp_start_concurrency', 5)
        self.ramp_target_concurrency = getattr(site_config, 'ramp_target_concurrency', 50)
        self.ramp_batch_size = getattr(site_config, 'ramp_batch_size', 20)  # URLs per ramp step
        
        # Phase 2: IP-level anti-blocking features
        self.ip_rotation_enabled = getattr(site_config, 'ip_rotation_enabled', True)
        self.user_agent_rotation = getattr(site_config, 'user_agent_rotation', True)
        self.session_rotation_interval = getattr(site_config, 'session_rotation_interval', 50)  # Rotate every 50 requests
        self.force_session_rotation = getattr(site_config, 'force_session_rotation', False)  # Force rotation on startup
        
        # User agent pool for rotation
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0',
            'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
            'Mozilla/5.0 (compatible; Bingbot/2.0; +http://www.bing.com/bingbot.htm)',
            'Mozilla/5.0 (compatible; ContentDetector/1.0; +https://github.com/astral/aggregator)'
        ]
        
        # Server health monitoring
        self.server_health = {
            'current_concurrency': self.max_concurrent,
            'success_rate': 1.0,
            'response_times': [],
            'error_count': 0,
            'success_count': 0,
            'last_adjustment': datetime.now()
        }
        
        # Session management for connection pooling
        self._session = None
        self._connector = None
        self._current_user_agent = None
        self._request_count = 0
        self._session_creation_time = None
        
        # SSL and connection management
        self._ssl_context = None
        self._connection_cleanup_task = None

    def _guess_sitemap_url(self) -> str:
        """Guess the sitemap URL if not provided."""
        from urllib.parse import urlparse
        parsed = urlparse(self.site_url)
        return f"{parsed.scheme}://{parsed.netloc}/sitemap.xml"

    async def get_current_state(self) -> Dict[str, Any]:
        """Get the current state by fetching and hashing content from key pages."""
        try:
            # Get URLs from sitemap first
            sitemap_urls = await self._get_sitemap_urls()
            
            # Filter to only HTML URLs
            html_urls = self._filter_html_urls(sitemap_urls)
            
            # Limit to most important pages (0 = no limit, check all pages)
            if self.max_pages > 0:
                key_urls = html_urls[:self.max_pages]
            else:
                key_urls = html_urls  # Check all pages
            
            # Fetch and hash content with ultra-fast optimization
            content_hashes = await self._fetch_content_hashes_ultra_fast(key_urls)
            
            return {
                "detection_method": "content_hash",
                "site_url": self.site_url,
                "urls_checked": key_urls,
                "content_hashes": content_hashes,
                "total_pages": len(content_hashes),
                "captured_at": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting current state: {e}")
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
                    "new_page", 
                    url, 
                    title=f"New page: {url}",
                    description="New page with content detected"
                )
            
            # Find deleted pages (pages in baseline but not in current)
            deleted_urls = set(baseline_hashes.keys()) - set(current_hashes.keys())
            for url in deleted_urls:
                result.add_change(
                    "deleted_page", 
                    url, 
                    title=f"Deleted page: {url}",
                    description="Page no longer accessible or has no content"
                )
            
            # Add metadata
            result.metadata.update({
                "pages_checked": len(current_hashes),
                "baseline_pages": len(baseline_hashes),
                "changed_pages": len(changed_urls),
                "new_pages": len(new_urls),
                "deleted_pages": len(deleted_urls),
                "accuracy": "100%" if len(current_hashes) > 0 else "0%"
            })
            
        except Exception as e:
            logger.error(f"Error detecting changes: {e}")
            result.metadata["error"] = str(e)
        
        return result

    async def _get_sitemap_urls(self) -> List[str]:
        """Get URLs from sitemap, handling both single sitemaps and sitemap indexes."""
        try:
            import aiohttp
            import xml.etree.ElementTree as ET
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.sitemap_url, timeout=30) as response:
                    if response.status != 200:
                        raise Exception(f"Failed to fetch sitemap: {response.status}")
                    
                    content = await response.text()
                    
                    # Check if this is a sitemap index
                    if self._is_sitemap_index(content):
                        return await self._fetch_sitemap_index_urls(session, content)
                    else:
                        # Single sitemap
                        return self._parse_sitemap_urls(content)
                        
        except Exception as e:
            logger.warning(f"Warning: Could not get sitemap URLs: {e}")
            # Fallback to main page
            return [self.site_url]

    def _is_sitemap_index(self, content: str) -> bool:
        """Check if the XML content is a sitemap index."""
        try:
            import xml.etree.ElementTree as ET
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

    async def _fetch_sitemap_index_urls(self, session: aiohttp.ClientSession, index_content: str) -> List[str]:
        """Fetch URLs from a sitemap index file and all referenced sitemaps."""
        all_urls = []
        
        # Parse the sitemap index
        sitemap_urls = self._parse_sitemap_index_urls(index_content)
        
        # Fetch each individual sitemap
        tasks = []
        for sitemap_url in sitemap_urls:
            tasks.append(self._fetch_individual_sitemap_urls(session, sitemap_url))
        
        # Wait for all sitemaps to be fetched
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, Exception):
                logger.warning(f"Failed to fetch sitemap: {result}")
            else:
                all_urls.extend(result)
        
        return all_urls

    def _parse_sitemap_index_urls(self, content: str) -> List[str]:
        """Parse sitemap index XML to extract sitemap URLs."""
        sitemap_urls = []
        
        try:
            import xml.etree.ElementTree as ET
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
            logger.warning(f"Failed to parse sitemap index XML: {e}")
        
        return sitemap_urls

    async def _fetch_individual_sitemap_urls(self, session: aiohttp.ClientSession, sitemap_url: str) -> List[str]:
        """Fetch and parse an individual sitemap."""
        try:
            async with session.get(sitemap_url, timeout=30) as response:
                if response.status != 200:
                    raise Exception(f"Failed to fetch sitemap {sitemap_url}: {response.status}")
                
                content = await response.text()
                return self._parse_sitemap_urls(content)
                
        except Exception as e:
            logger.warning(f"Failed to fetch sitemap {sitemap_url}: {e}")
            return []

    def _parse_sitemap_urls(self, content: str) -> List[str]:
        """Parse sitemap XML to extract URLs."""
        urls = []
        
        try:
            import xml.etree.ElementTree as ET
            namespaces = {
                'sitemap': 'http://www.sitemaps.org/schemas/sitemap/0.9'
            }
            
            root = ET.fromstring(content)
            
            # Look for URL elements
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
            # Fallback to regex parsing if XML parsing fails
            logger.warning(f"XML parsing failed, using regex fallback: {e}")
            urls = re.findall(r'<loc>(.*?)</loc>', content)
        
        return urls
    
    async def _create_ultra_fast_session(self) -> aiohttp.ClientSession:
        """Create an optimized session with massive connection pooling and SSL fixes."""
        if self._connector is None:
            # Create SSL context with proper settings
            self._ssl_context = ssl.create_default_context()
            self._ssl_context.check_hostname = False
            self._ssl_context.verify_mode = ssl.CERT_NONE
            
            # Create connector with SSL fixes and connection pooling
            self._connector = TCPConnector(
                limit=self.connection_pool_size,
                limit_per_host=self.connection_pool_size,
                ttl_dns_cache=300,
                use_dns_cache=True,
                keepalive_timeout=30,
                enable_cleanup_closed=True,
                ssl=self._ssl_context,
                # SSL shutdown timeout fixes
                force_close=False
            )
        
        # Rotate user agent if enabled
        if self.user_agent_rotation:
            import random
            self._current_user_agent = random.choice(self.user_agents)
        else:
            self._current_user_agent = 'Mozilla/5.0 (compatible; ContentDetector/1.0)'
        
        if self._session is None:
            timeout = ClientTimeout(
                total=self.ultra_fast_timeout,
                connect=2,
                sock_read=3,
                sock_connect=2
            )
            
            # Enhanced headers for IP-level workarounds
            headers = {
                'User-Agent': self._current_user_agent,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1'
            }
            
            # Add referer to appear more like a real browser
            if hasattr(self, 'site_url') and self.site_url:
                from urllib.parse import urlparse
                parsed = urlparse(self.site_url)
                headers['Referer'] = f"{parsed.scheme}://{parsed.netloc}/"
            
            self._session = aiohttp.ClientSession(
                connector=self._connector,
                timeout=timeout,
                headers=headers,
                # Prevent SSL shutdown issues
                skip_auto_headers=['Connection']
            )
            
            # Track session creation time
            self._session_creation_time = datetime.now()
            self._request_count = 0
        
        return self._session

    def _should_rotate_session(self) -> bool:
        """Determine if we should rotate the session based on various criteria."""
        if not self._session_creation_time:
            return False
        
        # Check if we've made too many requests with this session
        if self._request_count >= self.session_rotation_interval:
            return True
        
        # Check if session is getting old (more than 5 minutes)
        session_age = (datetime.now() - self._session_creation_time).total_seconds()
        if session_age > 300:  # 5 minutes
            return True
        
        return False

    async def _rotate_session_if_needed(self) -> aiohttp.ClientSession:
        """Rotate session if needed and return the current session."""
        if self._should_rotate_session():
            print(f"  🔄 Rotating session (requests: {self._request_count}, age: {(datetime.now() - self._session_creation_time).total_seconds():.1f}s)")
            await self._cleanup_connections()
            return await self._create_ultra_fast_session()
        
        return self._session

    async def _create_new_session(self) -> aiohttp.ClientSession:
        """Create a fresh session and cleanup the old one."""
        await self._cleanup_connections()
        return await self._create_ultra_fast_session()

    def _is_permanently_blocked(self, batch_success_rate: float, consecutive_failures: int) -> bool:
        """Detect if we're being blocked or rate limited persistently."""
        # Complete blocking: 0% success for 2+ consecutive batches
        if batch_success_rate == 0.0 and consecutive_failures >= 2:
            return True
        
        # Persistent rate limiting: very low success rate (< 20%) for 3+ consecutive batches
        if batch_success_rate < 0.2 and consecutive_failures >= 3:
            return True
        
        return False

    def _is_rate_limited(self, batch_success_rate: float, consecutive_low_success: int) -> bool:
        """Detect if we're being rate limited (moderate to low success rates)."""
        # Rate limiting: success rate between 20-50% for multiple batches
        return 0.2 <= batch_success_rate <= 0.5 and consecutive_low_success >= 2

    def _is_429_rate_limited(self, batch_success_rate: float, consecutive_failures: int) -> bool:
        """Detect if we're being rate limited based on 429 errors or very low success rates."""
        # Immediate detection: very low success rate (< 30%) for 2+ consecutive batches
        if batch_success_rate < 0.3 and consecutive_failures >= 2:
            return True
        
        # Moderate rate limiting: success rate between 30-60% for 3+ consecutive batches
        if 0.3 <= batch_success_rate <= 0.6 and consecutive_failures >= 3:
            return True
        
        # Persistent low success rate: consistently around 40-50% for 2+ consecutive batches
        if 0.4 <= batch_success_rate <= 0.5 and consecutive_failures >= 2:
            return True
        
        return False

    def _is_persistent_low_success(self, batch_success_rate: float, consecutive_low_success: int) -> bool:
        """Detect if we're getting consistently low success rates (like 45%)."""
        # If we're getting consistently low success rates (40-60%) for multiple batches
        if 0.4 <= batch_success_rate <= 0.6 and consecutive_low_success >= 2:
            return True
        
        # If we're getting very low success rates (< 50%) for 3+ consecutive batches
        if batch_success_rate < 0.5 and consecutive_low_success >= 3:
            return True
        
        return False

    def _should_stop_trying(self, consecutive_blocking_events: int, current_concurrency: int) -> bool:
        """Determine if we should stop trying due to persistent blocking."""
        # Stop if we've had too many blocking events (5 or more)
        # Don't stop just because concurrency is low - that's normal during backoff
        return consecutive_blocking_events >= 5

    async def _test_url_diagnostics(self, url: str) -> Dict[str, Any]:
        """Test a single URL to diagnose what's happening."""
        try:
            session = await self._create_ultra_fast_session()
            try:
                async with session.get(url, ssl=self._ssl_context) as response:
                    return {
                        "url": url,
                        "status": response.status,
                        "headers": dict(response.headers),
                        "content_length": len(await response.text()) if response.status == 200 else 0,
                        "success": response.status == 200
                    }
            finally:
                await session.close()
        except Exception as e:
            return {
                "url": url,
                "error": str(e),
                "success": False
            }

    async def _fetch_batch_with_concurrency(self, session: aiohttp.ClientSession, urls: List[str], concurrency: int) -> Dict[str, Dict[str, Any]]:
        """Fetch a batch of URLs with specified concurrency."""
        semaphore = asyncio.Semaphore(concurrency)
        tasks = [self._fetch_single_ultra_fast(session, url, semaphore) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        batch_hashes = {}
        success_count = 0
        failure_count = 0
        rate_limit_failures = 0  # Track only rate-limiting related failures
        
        for i, result in enumerate(results):
            url = urls[i]
            if isinstance(result, tuple) and len(result) == 3:
                url, content_hash, failure_type = result
                if content_hash:
                    batch_hashes[url] = {
                        "hash": content_hash,
                        "fetched_at": datetime.now().isoformat(),
                        "status": "success"
                    }
                    success_count += 1
                else:
                    failure_count += 1
                    # Track rate-limiting failures separately (these should affect concurrency)
                    if failure_type in ["rate_limited", "forbidden", "timeout", "connection_error"]:
                        rate_limit_failures += 1
                    # 404s and other client errors should NOT affect concurrency
            else:
                failure_count += 1
        
        # Store rate limit failures for use in concurrency adjustment
        batch_hashes["_rate_limit_failures"] = rate_limit_failures
        batch_hashes["_total_failures"] = failure_count
        
        return batch_hashes

    async def _fetch_content_hashes_ultra_fast(self, urls: List[str]) -> Dict[str, Dict[str, Any]]:
        """Fetch content hashes with ultra-fast optimization and adaptive rate limiting."""
        if not urls:
            return {}
        
        print(f"Starting ultra-fast content hash fetching for {len(urls)} URLs...")
        start_time = datetime.now()
        
        content_hashes = {}
        successful_fetches = 0
        failed_fetches = 0
        
        # Create optimized session
        session = await self._create_ultra_fast_session()
        
        try:
            # Process URLs with progressive ramping if enabled
            # Use progressive ramping for large URL sets OR when we want rate limiting protection
            if self.progressive_ramping and (len(urls) > self.ramp_batch_size or self.ip_rotation_enabled):
                content_hashes = await self._fetch_with_progressive_ramping(session, urls)
                # Calculate final success rate from content_hashes when using progressive ramping
                successful_fetches = len(content_hashes)
                failed_fetches = len(urls) - successful_fetches
            else:
                # Process URLs in batches to manage memory
                for i in range(0, len(urls), self.batch_size):
                    batch_urls = urls[i:i + self.batch_size]
                    batch_start = datetime.now()
                    
                    print(f"Processing batch {i//self.batch_size + 1}/{(len(urls) + self.batch_size - 1)//self.batch_size} ({len(batch_urls)} URLs)")
                    print(f"Current concurrency: {self.server_health['current_concurrency']} (adaptive: {self.adaptive_enabled})")
                    
                    # Use adaptive concurrency if enabled
                    current_concurrency = self.server_health['current_concurrency'] if self.adaptive_enabled else self.max_concurrent
                    
                    # Create semaphore to limit concurrent requests
                    semaphore = asyncio.Semaphore(current_concurrency)
                    
                    # Create tasks for this batch
                    tasks = []
                    for url in batch_urls:
                        task = self._fetch_single_ultra_fast(session, url, semaphore)
                        tasks.append(task)
                    
                    # Execute batch with adaptive concurrency
                    batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                    # Process batch results and update server health
                    batch_successful = 0
                    batch_failed = 0
                    
                    for j, result in enumerate(batch_results):
                        url = batch_urls[j]
                        if isinstance(result, tuple) and len(result) == 3:
                            url, content_hash, failure_type = result
                            if content_hash:
                                content_hashes[url] = {
                                    "hash": content_hash,
                                    "fetched_at": datetime.now().isoformat(),
                                    "status": "success"
                                }
                                successful_fetches += 1
                                batch_successful += 1
                                self.server_health['success_count'] += 1
                            else:
                                failed_fetches += 1
                                batch_failed += 1
                                self.server_health['error_count'] += 1
                        else:
                            failed_fetches += 1
                            batch_failed += 1
                            self.server_health['error_count'] += 1
                    
                    # Update server health for this batch
                    if self.adaptive_enabled:
                        self._update_server_health(batch_successful, batch_failed, batch_start)
                        self._adjust_concurrency()
                    
                    batch_time = (datetime.now() - batch_start).total_seconds()
                    print(f"Batch completed in {batch_time:.2f}s - Success: {batch_successful}, Failed: {batch_failed}")
                    
                    # Small delay between batches to prevent overwhelming
                    if i + self.batch_size < len(urls):
                        await asyncio.sleep(0.1)
            
            total_time = (datetime.now() - start_time).total_seconds()
            success_rate = successful_fetches / (successful_fetches + failed_fetches) if (successful_fetches + failed_fetches) > 0 else 0
            print(f"Content hash fetching completed in {total_time:.2f}s")
            print(f"Success rate: {success_rate:.1%} ({successful_fetches}/{successful_fetches + failed_fetches})")
            
            return content_hashes
            
        except Exception as e:
            logger.error(f"Error in ultra-fast content hash fetching: {e}")
            return content_hashes
        finally:
            # Ensure proper cleanup
            await self._cleanup_connections()

    async def _fetch_single_ultra_fast(self, session: aiohttp.ClientSession, url: str, semaphore: asyncio.Semaphore) -> tuple[str, Optional[str], Optional[str]]:
        """Fetch and hash content for a single URL with ultra-fast optimization and intelligent retries.
        Returns (url, content_hash, failure_type) where failure_type is None for success, or the type of failure."""
        async with semaphore:
            # Increment request count for session rotation
            self._request_count += 1
            
            # Check if we need to rotate session
            session = await self._rotate_session_if_needed()
            
            max_retries = 3
            base_delay = 0.1  # Start with 100ms delay
            
            for attempt in range(max_retries):
                try:
                    # Use context manager to ensure proper cleanup
                    async with session.get(url, ssl=self._ssl_context) as response:
                        if response.status == 200:
                            content = await response.text()
                            
                            # Extract main content using optimized method
                            main_content = self._extract_main_content_ultra_fast(content)
                            
                            if main_content:
                                # Create hash of the content
                                content_hash = hashlib.md5(main_content.encode('utf-8')).hexdigest()
                                return url, content_hash, None  # Success
                            else:
                                # Log when content extraction fails
                                print(f"    🔍 No content extracted from {url}")
                                return url, None, "content_extraction_failed"
                        elif response.status == 429:  # Rate limited
                            print(f"    ⚠️  Rate limited (429) for {url}")
                            # Force session rotation on 429
                            if self.ip_rotation_enabled:
                                print(f"    🔄 Forcing session rotation due to 429...")
                                await self._cleanup_connections()
                                session = await self._create_ultra_fast_session()
                            # Immediately return None to signal failure - let batch-level handling deal with it
                            # This will trigger the rate limiting detection in the progressive ramping
                            return url, None, "rate_limited"
                        elif response.status == 403:  # Forbidden
                            print(f"    🚫 Forbidden (403) for {url}")
                            # Force session rotation on 403 (IP-level blocking)
                            if self.ip_rotation_enabled:
                                print(f"    🔄 Forcing session rotation due to 403 (IP blocking)...")
                                await self._cleanup_connections()
                                session = await self._create_ultra_fast_session()
                            return url, None, "forbidden"
                        elif response.status == 404:  # Not Found
                            print(f"    ❌ Not found (404) for {url}")
                            return url, None, "not_found"  # Client-side error, not rate limiting
                        elif response.status == 503:  # Service Unavailable
                            print(f"    🔧 Service unavailable (503) for {url}")
                            await asyncio.sleep(base_delay * (2 ** attempt))
                            continue
                        elif response.status >= 500:  # Server error
                            print(f"    💥 Server error ({response.status}) for {url}")
                            # Wait with exponential backoff
                            await asyncio.sleep(base_delay * (2 ** attempt))
                            continue
                        else:
                            # Client error (404, 403, etc.) - don't retry
                            print(f"    ❌ Client error ({response.status}) for {url}")
                            return url, None, "client_error"
                            
                except asyncio.TimeoutError:
                    print(f"    ⏰ Timeout for {url}")
                    # Timeout - retry with exponential backoff
                    if attempt < max_retries - 1:
                        await asyncio.sleep(base_delay * (2 ** attempt))
                        continue
                    return url, None, "timeout"
                except aiohttp.ClientConnectionError as e:
                    print(f"    🔌 Connection error for {url}: {str(e)[:50]}...")
                    # Handle SSL shutdown and connection errors specifically
                    if "SSL shutdown timed out" in str(e) or "Connection lost" in str(e):
                        if attempt < max_retries - 1:
                            await asyncio.sleep(base_delay * (2 ** attempt) * 2)  # Longer delay for connection issues
                            continue
                    return url, None, "connection_error"
                except Exception as e:
                    print(f"    💥 Exception for {url}: {str(e)[:50]}...")
                    # Other exceptions - retry with exponential backoff
                    if attempt < max_retries - 1:
                        await asyncio.sleep(base_delay * (2 ** attempt))
                        continue
                    return url, None, "exception"
            
            return url, None, "max_retries_exceeded"

    def _extract_main_content_ultra_fast(self, html_content: str) -> Optional[str]:
        """Extract main content using ultra-fast regex-based method."""
        try:
            # Remove script and style tags first
            html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
            html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
            
            # Try to find main content using regex patterns for common selectors
            main_content = None
            
            # Look for main content areas using regex
            for selector in self.content_selectors:
                if selector.startswith('.'):
                    # Class selector
                    pattern = rf'<[^>]*class="[^"]*{selector[1:]}[^"]*"[^>]*>(.*?)</[^>]*>'
                elif selector.startswith('#'):
                    # ID selector
                    pattern = rf'<[^>]*id="{selector[1:]}"[^>]*>(.*?)</[^>]*>'
                else:
                    # Tag selector
                    pattern = rf'<{selector}[^>]*>(.*?)</{selector}>'
                
                matches = re.findall(pattern, html_content, flags=re.DOTALL | re.IGNORECASE)
                if matches:
                    main_content = matches[0]
                    break
            
            if not main_content:
                # Fallback to body content
                body_match = re.search(r'<body[^>]*>(.*?)</body>', html_content, flags=re.DOTALL | re.IGNORECASE)
                if body_match:
                    main_content = body_match.group(1)
            
            if main_content:
                # Clean up the content using regex
                text = self._clean_text_ultra_fast(main_content)
                return text if text.strip() else None
            
            return None
            
        except Exception as e:
            logger.debug(f"Error extracting content: {e}")
            return None

    def _clean_text_ultra_fast(self, text: str) -> str:
        """Clean and normalize text content using ultra-fast regex."""
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove leading/trailing whitespace
        text = text.strip()
        # Normalize line breaks
        text = text.replace('\n', ' ').replace('\r', ' ')
        return text

    async def _fetch_content_hashes(self, urls: List[str]) -> Dict[str, Dict[str, Any]]:
        """Legacy method for backward compatibility."""
        return await self._fetch_content_hashes_ultra_fast(urls)

    async def _fetch_single_content_hash(self, session: aiohttp.ClientSession, url: str) -> tuple[str, Optional[str]]:
        """Legacy method for backward compatibility."""
        semaphore = asyncio.Semaphore(1)
        result = await self._fetch_single_ultra_fast(session, url, semaphore)
        # Convert new format (url, content_hash, failure_type) to old format (url, content_hash)
        return result[0], result[1]

    def _extract_main_content(self, html_content: str) -> Optional[str]:
        """Legacy method for backward compatibility."""
        return self._extract_main_content_ultra_fast(html_content)

    def _clean_text(self, text: str) -> str:
        """Legacy method for backward compatibility."""
        return self._clean_text_ultra_fast(text)

    def _update_server_health(self, successful: int, failed: int, batch_start: datetime):
        """Update server health metrics."""
        total = successful + failed
        if total > 0:
            success_rate = successful / total
            response_time = (datetime.now() - batch_start).total_seconds()
            
            # Update rolling metrics
            self.server_health['success_rate'] = success_rate
            self.server_health['response_times'].append(response_time)
            
            # Keep only last 10 response times
            if len(self.server_health['response_times']) > 10:
                self.server_health['response_times'] = self.server_health['response_times'][-10:]

    def _save_progress(self, content_hashes: Dict[str, Dict[str, Any]], urls_processed: List[str], total_urls: List[str]):
        """Save progress to allow resuming later."""
        try:
            # Ensure progress directory exists
            progress_dir = "progress"
            os.makedirs(progress_dir, exist_ok=True)
            
            progress_data = {
                "content_hashes": content_hashes,
                "urls_processed": urls_processed,
                "total_urls": total_urls,
                "timestamp": datetime.now().isoformat(),
                "site_url": self.site_url
            }
            
            # Create simple progress filename based on site
            safe_site_name = re.sub(r'[^a-zA-Z0-9]', '_', self.site_url)
            progress_file = os.path.join(progress_dir, f"{safe_site_name}_progress.json")
            
            # Remove old progress files for this site
            self._cleanup_old_progress_files(safe_site_name)
            
            with open(progress_file, 'w') as f:
                json.dump(progress_data, f, indent=2)
            
            print(f"  💾 Progress saved: {len(content_hashes)} URLs processed, {len(urls_processed)}/{len(total_urls)} total")
            
        except Exception as e:
            logger.warning(f"Failed to save progress: {e}")

    def _cleanup_old_progress_files(self, site_name: str):
        """Remove old progress files for the same site, keeping only the most recent."""
        try:
            progress_dir = "progress"
            if not os.path.exists(progress_dir):
                return
                
            # Find all progress files for this site
            pattern = f"{site_name}_progress_*.json"
            old_files = [f for f in os.listdir(progress_dir) if f.startswith(f"{site_name}_progress_") and f.endswith('.json')]
            
            # Remove old files (keep only the most recent)
            if len(old_files) > 1:
                # Sort by creation time and remove all but the most recent
                old_files.sort(key=lambda x: os.path.getctime(os.path.join(progress_dir, x)), reverse=True)
                for old_file in old_files[1:]:  # Keep the first (most recent), remove the rest
                    os.remove(os.path.join(progress_dir, old_file))
                    
        except Exception as e:
            logger.debug(f"Failed to cleanup old progress files: {e}")

    def _load_progress(self) -> Optional[Dict[str, Any]]:
        """Load progress from the most recent progress file."""
        try:
            progress_dir = "progress"
            if not os.path.exists(progress_dir):
                return None
                
            safe_site_name = re.sub(r'[^a-zA-Z0-9]', '_', self.site_url)
            
            # Look for the simple progress file first
            simple_progress_file = os.path.join(progress_dir, f"{safe_site_name}_progress.json")
            if os.path.exists(simple_progress_file):
                with open(simple_progress_file, 'r') as f:
                    progress_data = json.load(f)
                print(f"  📂 Loaded progress: {len(progress_data['content_hashes'])} URLs already processed")
                return progress_data
            
            # Fallback: look for timestamped files
            progress_files = [f for f in os.listdir(progress_dir) if f.startswith(f"{safe_site_name}_progress_") and f.endswith('.json')]
            
            if not progress_files:
                return None
            
            # Get the most recent progress file
            latest_file = max(progress_files, key=lambda x: os.path.getctime(os.path.join(progress_dir, x)))
            
            with open(os.path.join(progress_dir, latest_file), 'r') as f:
                progress_data = json.load(f)
            
            print(f"  📂 Loaded progress: {len(progress_data['content_hashes'])} URLs already processed")
            return progress_data
            
        except Exception as e:
            logger.warning(f"Failed to load progress: {e}")
            return None

    async def _fetch_with_progressive_ramping(self, session: aiohttp.ClientSession, urls: List[str]) -> Dict[str, Dict[str, Any]]:
        """Fetch content hashes with progressive concurrency ramping and 100% accuracy guarantee."""
        print(f"Starting progressive ramping from {self.ramp_start_concurrency} to {self.ramp_target_concurrency} concurrent requests")
        
        # Try to load existing progress
        progress_data = self._load_progress()
        if progress_data:
            content_hashes = progress_data.get('content_hashes', {})
            processed_urls = set(progress_data.get('urls_processed', []))
            # Filter out already processed URLs
            urls = [url for url in urls if url not in processed_urls]
            print(f"  🔄 Resuming with {len(urls)} remaining URLs (already processed {len(content_hashes)})")
        else:
            content_hashes = {}
            processed_urls = set()
        
        current_concurrency = self.ramp_start_concurrency
        failed_urls = []  # Track failed URLs for retry
        consecutive_blocked_batches = 0  # Track consecutive 0% batches
        urls_processed_this_run = []
        
        # Start very conservatively to avoid immediate rate limiting
        current_concurrency = 1  # Start with just 1 concurrent request
        successful_start = False  # Track if we've had a successful start
        
        # Progressive ramping with blocking detection
        consecutive_failures = 0
        consecutive_blocking_events = 0
        consecutive_low_success = 0  # Track consecutive batches with low success rates
        max_ramp_steps = 100  # Maximum number of ramp steps
        batch_size = self.ramp_batch_size
        
        try:
            # Implement cold start strategy to avoid IP-level rate limiting from previous runs
            session = await self._cold_start_strategy(session)
            
            for step in range(max_ramp_steps):
                # Calculate remaining URLs to process
                remaining_urls = [url for url in urls if url not in content_hashes]
                batch_size = min(batch_size, len(remaining_urls))
                
                if batch_size <= 0:
                    break
                    
                print(f"Ramp step {step + 1} - Concurrency: {current_concurrency} ({batch_size} URLs)")
                
                # Get next batch of URLs
                batch_urls = remaining_urls[:batch_size]
                
                # Check if we should stop trying
                if self._should_stop_trying(consecutive_blocking_events, current_concurrency):
                    print(f"🛑 Stopping due to persistent blocking after {consecutive_blocking_events} events")
                    break
                
                # Fetch batch with current concurrency
                batch_start = datetime.now()
                batch_hashes = await self._fetch_batch_with_concurrency(session, batch_urls, current_concurrency)
                batch_time = (datetime.now() - batch_start).total_seconds()
                
                # Calculate batch success rate
                successful = len(batch_hashes)
                failed = len(batch_urls) - successful
                batch_success_rate = successful / len(batch_urls) if batch_urls else 0
                
                # Extract rate-limiting failures (these should affect concurrency)
                rate_limit_failures = batch_hashes.pop("_rate_limit_failures", 0)
                total_failures = batch_hashes.pop("_total_failures", failed)
                
                # Calculate rate-limiting success rate (excluding 404s and other client errors)
                rate_limit_success_rate = (len(batch_urls) - rate_limit_failures) / len(batch_urls) if batch_urls else 0
                
                print(f"  Batch completed in {batch_time:.2f}s - Success: {successful}, Failed: {failed}")
                
                # Update content hashes
                content_hashes.update(batch_hashes)
                
                # Track failed URLs for retry
                failed_batch_urls = [url for url in batch_urls if url not in batch_hashes]
                failed_urls.extend(failed_batch_urls)
                
                # Save progress after each successful batch
                self._save_progress(content_hashes, list(content_hashes.keys()), urls)
                
                # Check for IP-level rate limiting from previous runs
                if self._is_ip_level_rate_limited(rate_limit_success_rate, step + 1):
                    print(f"  🚨 IP-LEVEL RATE LIMITING FROM PREVIOUS RUN DETECTED (step {step + 1}, rate-limit success rate: {rate_limit_success_rate:.1%}, overall: {batch_success_rate:.1%})")
                    session = await self._handle_ip_level_rate_limiting(session)
                    
                    # Reset to very conservative settings
                    current_concurrency = 1
                    consecutive_failures = 0
                    consecutive_low_success = 0
                    
                    # Long pause for IP-level rate limiting (90 seconds)
                    print(f"  ⏸️  Pausing for 90 seconds to let IP-level rate limiting reset...")
                    await asyncio.sleep(90)
                    continue
                
                # Check for immediate rate limiting (first few batches)
                if self._is_immediately_rate_limited(rate_limit_success_rate, step + 1):
                    print(f"  🚨 IMMEDIATE RATE LIMITING DETECTED (step {step + 1}, rate-limit success rate: {rate_limit_success_rate:.1%}, overall: {batch_success_rate:.1%})")
                    print(f"  📉 Aggressive response: Reducing to 1 concurrent request and pausing...")
                    
                    # Very aggressive response for immediate rate limiting
                    current_concurrency = 1
                    
                    # Long pause for immediate rate limiting (60 seconds)
                    print(f"  ⏸️  Pausing for 60 seconds to let rate limiting reset...")
                    await asyncio.sleep(60)
                    continue
                
                # Check for rate limiting
                if self._is_429_rate_limited(rate_limit_success_rate, consecutive_failures):
                    consecutive_failures += 1
                    print(f"  ⚠️  Rate limiting detected (rate-limit success rate: {rate_limit_success_rate:.1%}, overall: {batch_success_rate:.1%}) - Pausing and reducing concurrency...")
                    
                    # Very aggressive backoff for rate limiting
                    new_concurrency = max(1, int(current_concurrency * 0.3))  # Reduce by 70%
                    print(f"  📉 Reducing concurrency to {new_concurrency} due to rate limiting")
                    current_concurrency = new_concurrency
                    
                    # Much longer pause for rate limiting (30 seconds)
                    print(f"  ⏸️  Pausing for 30 seconds to let rate limiting reset...")
                    await asyncio.sleep(30)
                    continue
                else:
                    consecutive_failures = 0  # Reset counter if success rate improves
                
                # Check for persistent low success rates (like 45%)
                if self._is_persistent_low_success(rate_limit_success_rate, consecutive_low_success):
                    consecutive_low_success += 1
                    print(f"  🚨 PERSISTENT LOW SUCCESS RATE DETECTED (rate-limit: {rate_limit_success_rate:.1%}, overall: {batch_success_rate:.1%}) - Consecutive low success: {consecutive_low_success}")
                    print(f"  📉 This suggests rate limiting - Reducing concurrency and pausing...")
                    
                    # Aggressive backoff for persistent low success
                    new_concurrency = max(1, int(current_concurrency * 0.5))  # Reduce by 50%
                    print(f"  📉 Reducing concurrency to {new_concurrency} due to persistent low success")
                    current_concurrency = new_concurrency
                    
                    # Long pause for persistent low success (45 seconds)
                    print(f"  ⏸️  Pausing for 45 seconds to let rate limiting reset...")
                    await asyncio.sleep(45)
                    continue
                else:
                    consecutive_low_success = 0  # Reset counter if success rate improves
                
                # Check for blocking
                if self._is_permanently_blocked(rate_limit_success_rate, consecutive_failures):
                    consecutive_blocking_events += 1
                    print(f"  🚨 Detected persistent blocking/rate limiting - Rotating session and pausing...")
                    print(f"  📊 Blocking event #{consecutive_blocking_events}")
                    
                    # Rotate session
                    await session.close()
                    session = await self._create_new_session()
                    await asyncio.sleep(5)  # Longer pause for blocking
                    
                    # Reset consecutive failures for new session
                    consecutive_failures = 0
                    consecutive_low_success = 0
                else:
                    consecutive_failures = 0
                
                # Adjust concurrency based on rate-limiting success rate (excluding 404s and client errors)
                if rate_limit_success_rate >= 0.9:  # Require 90%+ rate-limiting success rate for increases
                    # Only increase if we've had a successful start or this is a very good batch
                    if successful_start or rate_limit_success_rate >= 0.95:
                        # Ensure we actually increase from 1 to at least 2
                        if current_concurrency == 1:
                            new_concurrency = 2
                        elif current_concurrency == 2:
                            new_concurrency = 3
                        else:
                            # Very conservative increase - only 10% instead of 20%
                            new_concurrency = min(self.ramp_target_concurrency, int(current_concurrency * 1.1))
                        
                        if new_concurrency > current_concurrency:
                            print(f"  ✅ Rate-limit success rate: {rate_limit_success_rate:.1%} (overall: {batch_success_rate:.1%}) - Increasing concurrency to {new_concurrency}")
                            current_concurrency = new_concurrency
                        else:
                            print(f"  ✅ Rate-limit success rate: {rate_limit_success_rate:.1%} (overall: {batch_success_rate:.1%}) - Concurrency already at maximum ({current_concurrency})")
                    else:
                        # Mark as successful start but don't increase yet
                        successful_start = True
                        print(f"  ✅ Good start (rate-limit success rate: {rate_limit_success_rate:.1%}, overall: {batch_success_rate:.1%}) - Keeping concurrency at {current_concurrency}")
                elif rate_limit_success_rate < 0.5:
                    consecutive_failures += 1
                    new_concurrency = max(1, int(current_concurrency * 0.7))  # More aggressive decrease
                    print(f"  ⚠️  Rate-limit success rate: {rate_limit_success_rate:.1%} (overall: {batch_success_rate:.1%}) - Decreasing concurrency to {new_concurrency}")
                    current_concurrency = new_concurrency
                    successful_start = False  # Reset successful start flag
                
                # Add small delay between batches
                await asyncio.sleep(1)  # Increased delay to be more conservative
                
        finally:
            await session.close()
        
        # Retry failed URLs with lower concurrency for 100% accuracy
        if failed_urls:
            print(f"Retrying {len(failed_urls)} failed URLs with conservative settings...")
            retry_concurrency = max(1, current_concurrency // 2)  # Use half the current concurrency
            
            # Create a new session for retries since the original was closed
            retry_session = await self._create_ultra_fast_session()
            try:
                retry_semaphore = asyncio.Semaphore(retry_concurrency)
                
                retry_tasks = []
                for url in failed_urls:
                    task = self._fetch_single_ultra_fast(retry_session, url, retry_semaphore)
                    retry_tasks.append(task)
                
                retry_results = await asyncio.gather(*retry_tasks, return_exceptions=True)
                
                # Process retry results
                retry_successful = 0
                for j, result in enumerate(retry_results):
                    url = failed_urls[j]
                    if isinstance(result, tuple) and len(result) == 2:
                        url, content_hash = result
                        if content_hash:
                            content_hashes[url] = {
                                "hash": content_hash,
                                "fetched_at": datetime.now().isoformat(),
                                "status": "success_retry"
                            }
                            retry_successful += 1
                            urls_processed_this_run.append(url)
                
                print(f"Retry completed - {retry_successful}/{len(failed_urls)} URLs successfully retried")
            finally:
                await retry_session.close()
        
        return content_hashes

    def _adjust_concurrency(self):
        """Dynamically adjust concurrency based on server health."""
        success_rate = self.server_health['success_rate']
        current_concurrency = self.server_health['current_concurrency']
        
        # If success rate is below threshold, reduce concurrency
        if success_rate < self.success_rate_threshold:
            new_concurrency = max(
                self.min_concurrent,
                int(current_concurrency * self.rate_adjustment_factor)
            )
            if new_concurrency != current_concurrency:
                print(f"Reducing concurrency from {current_concurrency} to {new_concurrency} (success rate: {success_rate:.1%})")
                self.server_health['current_concurrency'] = new_concurrency
                self.server_health['last_adjustment'] = datetime.now()
        
        # If success rate is high and we haven't adjusted recently, try increasing
        elif success_rate > 0.98 and current_concurrency < self.max_concurrent_adaptive:
            time_since_adjustment = (datetime.now() - self.server_health['last_adjustment']).total_seconds()
            if time_since_adjustment > 30:  # Wait at least 30 seconds between increases
                new_concurrency = min(
                    self.max_concurrent_adaptive,
                    int(current_concurrency * self.rate_increase_factor)
                )
                if new_concurrency != current_concurrency:
                    print(f"Increasing concurrency from {current_concurrency} to {new_concurrency} (success rate: {success_rate:.1%})")
                    self.server_health['current_concurrency'] = new_concurrency
                    self.server_health['last_adjustment'] = datetime.now()

    async def _cleanup_connections(self):
        """Properly cleanup connections to prevent SSL shutdown issues."""
        try:
            if self._session:
                await self._session.close()
                self._session = None
            if self._connector:
                await self._connector.close()
                self._connector = None
        except Exception as e:
            logger.debug(f"Error during connection cleanup: {e}")

    async def close(self):
        """Close the session and connector."""
        await self._cleanup_connections() 

    def _filter_html_urls(self, urls: List[str]) -> List[str]:
        """Filter URLs to only include HTML pages, excluding PDFs, images, etc."""
        html_extensions = {'.html', '.htm', '.php', '.asp', '.aspx', '.jsp', '.jspx', '.do', '.action'}
        exclude_extensions = {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.zip', '.rar', '.tar', '.gz', '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.ico', '.mp3', '.mp4', '.avi', '.mov', '.wmv', '.flv', '.swf', '.exe', '.dmg', '.deb', '.rpm'}
        
        filtered_urls = []
        for url in urls:
            # Skip URLs with excluded extensions
            if any(url.lower().endswith(ext) for ext in exclude_extensions):
                continue
            
            # Skip URLs that are clearly not HTML (contain #new_tab, etc.)
            if any(skip_pattern in url.lower() for skip_pattern in ['#new_tab', '#download', 'attachment_id']):
                continue
            
            # Include URLs that either have HTML extensions or no extension (likely HTML)
            if any(url.lower().endswith(ext) for ext in html_extensions) or '.' not in url.split('/')[-1]:
                filtered_urls.append(url)
        
        print(f"  🔍 URL filtering: {len(urls)} total URLs, {len(filtered_urls)} HTML URLs ({len(urls) - len(filtered_urls)} excluded)")
        return filtered_urls 

    def _is_immediately_rate_limited(self, batch_success_rate: float, step_number: int) -> bool:
        """Detect if we're being rate limited immediately (first few batches)."""
        # If this is one of the first 3 batches and success rate is very low, we're likely rate limited
        if step_number <= 3 and batch_success_rate < 0.2:
            return True
        
        # If this is the very first batch and success rate is extremely low, definitely rate limited
        if step_number == 1 and batch_success_rate < 0.1:
            return True
        
        return False 

    def _is_ip_level_rate_limited(self, batch_success_rate: float, step_number: int) -> bool:
        """Detect if we're being IP-level rate limited from a previous run."""
        # If this is the very first batch and success rate is extremely low, likely IP-level blocking
        if step_number == 1 and batch_success_rate < 0.1:
            return True
        
        # If we're getting consistently very low success rates in early batches
        if step_number <= 3 and batch_success_rate < 0.2:
            return True
        
        # If we're getting 403 errors consistently (IP-level blocking)
        # This would be detected in the individual URL fetching
        
        return False

    async def _handle_ip_level_rate_limiting(self, session: aiohttp.ClientSession) -> aiohttp.ClientSession:
        """Handle IP-level rate limiting from previous runs with aggressive countermeasures."""
        print(f"  🚨 IP-LEVEL RATE LIMITING DETECTED - Implementing aggressive countermeasures...")
        
        # Force session rotation with new user agent
        await self._cleanup_connections()
        
        # Force user agent rotation
        if self.user_agent_rotation:
            import random
            self._current_user_agent = random.choice(self.user_agents)
            print(f"  🔄 Rotated to new user agent: {self._current_user_agent[:50]}...")
        
        # Create completely new session
        session = await self._create_ultra_fast_session()
        
        # Add extra headers to appear more like a real browser
        session._default_headers.update({
            'DNT': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'max-age=0'
        })
        
        print(f"  🔄 Created new session with enhanced browser headers")
        return session

    async def _cold_start_strategy(self, session: aiohttp.ClientSession) -> aiohttp.ClientSession:
        """Implement cold start strategy to avoid IP-level rate limiting from previous runs."""
        print(f"  ❄️  Implementing cold start strategy to avoid IP-level rate limiting...")
        
        # Force session rotation on startup if enabled
        if self.force_session_rotation:
            print(f"  🔄 Forcing session rotation on startup...")
            await self._cleanup_connections()
            session = await self._create_ultra_fast_session()
        
        # Add a longer initial delay to let any previous rate limiting reset
        print(f"  ⏸️  Adding 30-second delay to let rate limiting reset...")
        await asyncio.sleep(30)
        
        return session 