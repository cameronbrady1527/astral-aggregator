#!/usr/bin/env python3
"""
Simplified Change Detector - High-performance change detection system
This module provides a simplified, efficient approach to change detection
that performs better than the current complex system.
"""

import asyncio
import json
import hashlib
import aiohttp
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from bs4 import BeautifulSoup
from urllib.parse import urlparse

from .baseline_manager import BaselineManager
from .config import ConfigManager


# Image and file extensions to ignore
IMAGE_EXTENSIONS = {
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', 
    '.svg', '.ico', '.pdf', '.doc', '.docx', '.xls', '.xlsx',
    '.ppt', '.pptx', '.zip', '.rar', '.tar', '.gz'
}


class SimplifiedChangeDetector:
    """Simplified, high-performance change detection system."""
    
    def __init__(self, config_file: str = None):
        """Initialize the simplified change detector."""
        if config_file is None:
            import os
            config_file = os.environ.get('CONFIG_FILE', "config/sites.yaml")
        
        self.config_manager = ConfigManager(config_file)
        self.baseline_manager = BaselineManager()
        self.changes_dir = Path("changes")
        self.changes_dir.mkdir(exist_ok=True)
        
        # Proxy support
        self.proxy_manager = None
        self.proxy_enabled = True  # Enable by default for large sites
        self.proxy_threshold = 50  # Use proxy if more than 50 URLs
        self._consecutive_429s = 0
        self._last_429_time = None
        self._rate_limit_backoff = 0
        
        # Initialize proxy manager (will be done when first needed)
        self._proxy_initialized = False
    
    async def _initialize_proxy_manager(self):
        """Initialize proxy manager for residential proxy support."""
        try:
            from app.utils.proxy_manager import create_proxy_manager_from_env
            self.proxy_manager = await create_proxy_manager_from_env()
            if self.proxy_manager:
                print(f"✅ Proxy manager initialized: {self.proxy_manager.config.provider.value}")
            else:
                print("⚠️ Proxy manager initialization failed, continuing without proxy")
        except Exception as e:
            print(f"❌ Error initializing proxy manager: {e}")
    
    async def _check_proxy_health(self) -> bool:
        """Check if proxy is healthy and working."""
        if not self.proxy_manager:
            return False
        
        try:
            # Test proxy with a simple request
            test_url = "http://httpbin.org/ip"
            proxy_connector = await self.proxy_manager.get_proxy_connector()
            
            if proxy_connector:
                async with aiohttp.ClientSession(connector=proxy_connector) as session:
                    async with session.get(test_url, timeout=10) as response:
                        if response.status == 200:
                            print("✅ Proxy health check passed")
                            return True
            
            print("❌ Proxy health check failed")
            return False
        except Exception as e:
            print(f"❌ Proxy health check error: {e}")
            return False
    
    def _is_ignorable_file(self, url: str) -> bool:
        """Check if URL points to an ignorable file (images, documents, etc.)."""
        parsed = urlparse(url)
        path = parsed.path.lower()
        
        # Check file extension
        for ext in IMAGE_EXTENSIONS:
            if path.endswith(ext):
                return True
        
        # Check for common image patterns in URL
        image_patterns = [
            r'/images?/', r'/img/', r'/photos?/', r'/pics?/', 
            r'/assets/', r'/static/', r'/media/', r'/uploads/',
            r'\.(jpg|jpeg|png|gif|bmp|tiff|webp|svg|ico)$'
        ]
        
        for pattern in image_patterns:
            if re.search(pattern, path):
                return True
        
        return False
    
    def _get_file_type(self, url: str) -> str:
        """Get the file type from URL."""
        parsed = urlparse(url)
        path = parsed.path.lower()
        
        for ext in IMAGE_EXTENSIONS:
            if path.endswith(ext):
                return ext[1:].upper()  # Remove dot and uppercase
        
        return "unknown"
    
    async def detect_changes_for_site(self, site_id: str) -> Dict[str, Any]:
        """Detect changes for a specific site using simplified approach."""
        site_config = self.config_manager.get_site(site_id)
        if not site_config:
            raise ValueError(f"Site '{site_id}' not found in configuration")
        
        print(f"🔍 Starting simplified change detection for {site_id}...")
        
        # Get current baseline
        current_baseline = self.baseline_manager.get_latest_baseline(site_config.name)
        
        # Get current state (sitemap + content hashes)
        current_state = await self._get_current_state(site_config)
        
        # If no baseline exists, create initial baseline
        if current_baseline is None:
            print(f"📋 No baseline found for {site_config.name}, creating initial baseline...")
            return await self._create_initial_baseline(site_config, current_state)
        
        # Detect changes against baseline
        changes = await self._detect_changes(current_baseline, current_state)
        
        # Check if we need to create a new baseline due to hash format mismatch
        if not changes and self._should_create_new_baseline(current_baseline, current_state):
            print(f"🔄 Hash format mismatch detected, creating new baseline...")
            return await self._create_initial_baseline(site_config, current_state)
        
        # Handle results based on whether changes were found
        if changes:
            return await self._handle_changes_found(site_config, current_baseline, current_state, changes)
        else:
            return await self._handle_no_changes(site_config, current_baseline)
    
    async def _get_current_state(self, site_config: Any) -> Dict[str, Any]:
        """Get current state (sitemap + content hashes) with adaptive proxy usage."""
        print("📋 Step 1: Fetching sitemap URLs...")
        
        # Get sitemap URLs first
        sitemap_urls = await self._get_sitemap_urls(site_config)
        print(f"✅ Found {len(sitemap_urls)} URLs in sitemap")
        
        # Decide whether to use proxy based on URL count
        use_proxy = len(sitemap_urls) > self.proxy_threshold
        if use_proxy and self.proxy_manager:
            print(f"🌐 Large site detected ({len(sitemap_urls)} URLs), using residential proxy")
        elif use_proxy and not self.proxy_manager:
            print(f"⚠️ Large site detected ({len(sitemap_urls)} URLs) but no proxy available")
        else:
            print(f"📊 Small site ({len(sitemap_urls)} URLs), using direct connection")
        
        # Get content hashes (proxy decision made in _get_content_hashes)
        print("🔍 Step 2: Calculating content hashes...")
        content_hashes = await self._get_content_hashes(sitemap_urls)
        print(f"✅ Successfully processed {len(content_hashes)} URLs")
        
        return {
            "urls": sitemap_urls,
            "content_hashes": content_hashes,
            "detection_time": datetime.now().isoformat(),
            "total_urls": len(sitemap_urls),
            "total_content_hashes": len(content_hashes),
            "proxy_used": use_proxy and self.proxy_manager is not None
        }
    
    async def _get_sitemap_urls(self, site_config: Any) -> List[str]:
        """Get URLs from sitemap using simplified approach."""
        try:
            async with aiohttp.ClientSession() as session:
                # Try sitemap URL first
                sitemap_url = getattr(site_config, 'sitemap_url', None)
                if not sitemap_url:
                    # Guess sitemap URL
                    sitemap_url = f"{site_config.url.rstrip('/')}/sitemap.xml"
                
                async with session.get(sitemap_url, timeout=30) as response:
                    if response.status != 200:
                        print(f"⚠️ Sitemap not found at {sitemap_url}, trying sitemap_index.xml")
                        sitemap_url = f"{site_config.url.rstrip('/')}/sitemap_index.xml"
                        async with session.get(sitemap_url, timeout=30) as response2:
                            if response2.status != 200:
                                raise Exception(f"Could not fetch sitemap from {sitemap_url}")
                            content = await response2.text()
                    else:
                        content = await response.text()
                
                # Check if this is a sitemap index
                if self._is_sitemap_index(content):
                    print("📋 Found sitemap index, processing all sitemaps...")
                    urls = await self._process_sitemap_index(session, content)
                else:
                    # Regular sitemap
                    urls = self._parse_sitemap(content)
                
                # Filter out images and files
                filtered_urls = []
                ignored_count = 0
                
                for url in urls:
                    if self._is_ignorable_file(url):
                        ignored_count += 1
                        continue
                    filtered_urls.append(url)
                
                print(f"📊 Filtered URLs: {len(filtered_urls)} valid, {ignored_count} ignored (images/files)")
                return filtered_urls
                
        except Exception as e:
            print(f"❌ Error fetching sitemap: {e}")
            return []
    
    def _parse_sitemap(self, content: str) -> List[str]:
        """Parse sitemap XML to extract URLs."""
        try:
            soup = BeautifulSoup(content, 'lxml-xml')
            urls = []
            
            # Regular sitemap - extract URLs from loc tags
            loc_tags = soup.find_all('loc')
            for loc in loc_tags:
                url = loc.get_text().strip()
                if url:
                    urls.append(url)
            
            return urls
            
        except Exception as e:
            print(f"❌ Error parsing sitemap: {e}")
            return []
    
    def _is_sitemap_index(self, content: str) -> bool:
        """Check if the XML content is a sitemap index."""
        try:
            soup = BeautifulSoup(content, 'lxml-xml')
            sitemaps = soup.find_all('sitemap')
            return len(sitemaps) > 0
        except Exception:
            return False
    
    async def _process_sitemap_index(self, session: aiohttp.ClientSession, index_content: str) -> List[str]:
        """Process a sitemap index and fetch URLs from all individual sitemaps."""
        all_urls = []
        
        try:
            # Parse the sitemap index to get individual sitemap URLs
            sitemap_urls = self._parse_sitemap_index(index_content)
            print(f"📋 Found {len(sitemap_urls)} individual sitemaps in index")
            
            # Fetch each individual sitemap
            for i, sitemap_url in enumerate(sitemap_urls):
                print(f"   Processing sitemap {i+1}/{len(sitemap_urls)}: {sitemap_url}")
                try:
                    urls = await self._fetch_individual_sitemap(session, sitemap_url)
                    all_urls.extend(urls)
                    print(f"     ✅ Found {len(urls)} URLs")
                except Exception as e:
                    print(f"     ❌ Error processing sitemap {sitemap_url}: {e}")
            
            print(f"📊 Total URLs from all sitemaps: {len(all_urls)}")
            return all_urls
            
        except Exception as e:
            print(f"❌ Error processing sitemap index: {e}")
            return []
    
    def _parse_sitemap_index(self, content: str) -> List[str]:
        """Parse sitemap index XML to extract sitemap URLs."""
        try:
            soup = BeautifulSoup(content, 'lxml-xml')
            sitemap_urls = []
            
            # Find all sitemap elements and extract their loc URLs
            sitemaps = soup.find_all('sitemap')
            for sitemap in sitemaps:
                loc = sitemap.find('loc')
                if loc and loc.get_text().strip():
                    sitemap_urls.append(loc.get_text().strip())
            
            return sitemap_urls
            
        except Exception as e:
            print(f"❌ Error parsing sitemap index: {e}")
            return []
    
    async def _fetch_individual_sitemap(self, session: aiohttp.ClientSession, sitemap_url: str) -> List[str]:
        """Fetch and parse an individual sitemap."""
        try:
            async with session.get(sitemap_url, timeout=30) as response:
                if response.status != 200:
                    raise Exception(f"Failed to fetch sitemap {sitemap_url}: {response.status}")
                
                content = await response.text()
                urls = self._parse_sitemap(content)
                return urls
                
        except Exception as e:
            raise Exception(f"Error fetching sitemap {sitemap_url}: {e}")
    
    async def _get_content_hashes(self, urls: List[str]) -> Dict[str, Any]:
        """Get content hashes for URLs using proxy support."""
        if not urls:
            return {}
        
        print(f"🔍 Getting content hashes for {len(urls)} URLs...")
        content_data = {}
        
        # Get proxy connector if available and URL count exceeds threshold
        proxy_connector = None
        use_proxy = len(urls) > self.proxy_threshold
        if use_proxy:
            # Initialize proxy manager if not already done
            if not self._proxy_initialized:
                await self._initialize_proxy_manager()
                self._proxy_initialized = True
            
            if self.proxy_manager:
                # Try to get proxy connector, but don't fail if test fails
                try:
                    proxy_connector = await self.proxy_manager.get_proxy_connector()
                    if proxy_connector:
                        print("🌐 Using residential proxy for content fetching")
                    else:
                        print("⚠️ Proxy connector not available, using direct connection")
                except Exception as e:
                    print(f"⚠️ Proxy connector error: {e}, using direct connection")
                    proxy_connector = None
            else:
                print("⚠️ Proxy manager not available, using direct connection")
        else:
            print("📊 Using direct connection (small site or no proxy)")
        
        # Process URLs in batches for efficiency
        batch_size = 20
        total_batches = (len(urls) + batch_size - 1) // batch_size
        
        # Track 429 errors to trigger proxy rotation
        consecutive_429s = 0
        max_429s_before_rotation = 3
        using_proxy = proxy_connector is not None
        
        async with aiohttp.ClientSession(connector=proxy_connector) as session:
            for i in range(0, len(urls), batch_size):
                batch = urls[i:i + batch_size]
                batch_num = i // batch_size + 1
                print(f"   Processing batch {batch_num}/{total_batches} ({len(batch)} URLs)")
                
                # Check if we need to rotate proxy due to rate limiting
                if consecutive_429s >= max_429s_before_rotation:
                    print(f"🔄 Too many consecutive 429s ({consecutive_429s}), attempting rotation...")
                    
                    if self.proxy_manager and using_proxy:
                        try:
                            # For Tor, try to rotate identity first
                            if hasattr(self.proxy_manager, 'rotate_identity_on_rate_limit'):
                                print("🔄 Attempting Tor identity rotation...")
                                await self.proxy_manager.rotate_identity_on_rate_limit()
                            
                            # Get fresh proxy connector
                            new_proxy_connector = await self.proxy_manager.get_proxy_connector()
                            if new_proxy_connector:
                                # Close current session and create new one
                                await session.close()
                                session = aiohttp.ClientSession(connector=new_proxy_connector)
                                consecutive_429s = 0
                                print("✅ Proxy rotated, continuing with new session")
                            else:
                                print("⚠️ Failed to get new proxy connector, switching to direct connection")
                                # Fallback to direct connection
                                await session.close()
                                session = aiohttp.ClientSession()
                                using_proxy = False
                                consecutive_429s = 0
                        except Exception as e:
                            print(f"⚠️ Failed to rotate proxy: {e}, switching to direct connection")
                            # Fallback to direct connection
                            await session.close()
                            session = aiohttp.ClientSession()
                            using_proxy = False
                            consecutive_429s = 0
                    else:
                        print("⚠️ No proxy available or already using direct connection, continuing with current session")
                        # Just reset the counter and continue
                        consecutive_429s = 0
                
                batch_results = await self._process_url_batch(session, batch, consecutive_429s)
                content_data.update(batch_results)
                
                # Update 429 counter based on batch results
                batch_429s = sum(1 for result in batch_results.values() if result.get('status_code') == 429)
                if batch_429s > 0:
                    consecutive_429s += batch_429s
                    print(f"⚠️ Batch had {batch_429s} 429 errors, total consecutive: {consecutive_429s}")
                else:
                    consecutive_429s = 0  # Reset on success
                
                # Small delay between batches
                await asyncio.sleep(0.5)
        
        print(f"✅ Successfully processed {len(content_data)} URLs")
        return content_data
    
    async def _process_url_batch(self, session: aiohttp.ClientSession, urls: List[str], consecutive_429s: int = 0) -> Dict[str, Any]:
        """Process a batch of URLs to get content hashes."""
        tasks = [self._get_single_url_content(session, url, consecutive_429s) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        content_data = {}
        for i, result in enumerate(results):
            url = urls[i]
            if isinstance(result, Exception):
                content_data[url] = {
                    "error": str(result),
                    "hash": None,
                    "content_length": 0,
                    "status_code": None,
                    "extracted_at": datetime.now().isoformat()
                }
            else:
                content_data[url] = result
        
        return content_data
    
    async def _get_single_url_content(self, session: aiohttp.ClientSession, url: str, consecutive_429s: int = 0) -> Dict[str, Any]:
        """Get content hash for a single URL with 429 handling."""
        try:
            async with session.get(url, timeout=15) as response:
                if response.status == 429:
                    # Handle rate limiting
                    self._consecutive_429s += 1
                    self._last_429_time = datetime.now()
                    
                    # Calculate backoff time (exponential backoff)
                    backoff_time = min(2 ** self._consecutive_429s, 30)  # Max 30 seconds
                    print(f"⚠️ Rate limited (429) for {url}, backing off for {backoff_time}s")
                    
                    await asyncio.sleep(backoff_time)
                    
                    # Try again once
                    async with session.get(url, timeout=15) as retry_response:
                        if retry_response.status != 200:
                            return {
                                "error": f"HTTP {retry_response.status} (after 429 retry)",
                                "hash": None,
                                "content_length": 0,
                                "status_code": retry_response.status,
                                "extracted_at": datetime.now().isoformat()
                            }
                        content = await retry_response.text()
                elif response.status != 200:
                    return {
                        "error": f"HTTP {response.status}",
                        "hash": None,
                        "content_length": 0,
                        "status_code": response.status,
                        "extracted_at": datetime.now().isoformat()
                    }
                else:
                    content = await response.text()
                    # Reset 429 counter on success
                    self._consecutive_429s = 0
                
                # Extract main content
                main_content = self._extract_main_content(content)
                
                # Calculate hash
                content_hash = hashlib.sha256(main_content.encode('utf-8')).hexdigest()
                
                return {
                    "hash": content_hash,
                    "content_length": len(main_content),
                    "status_code": response.status,
                    "extracted_at": datetime.now().isoformat(),
                    "content_preview": main_content[:200] + "..." if len(main_content) > 200 else main_content
                }
                
        except Exception as e:
            return {
                "error": str(e),
                "hash": None,
                "content_length": 0,
                "status_code": None,
                "extracted_at": datetime.now().isoformat()
            }
    
    def _extract_main_content(self, html_content: str) -> str:
        """Extract main content from HTML, removing navigation, footer, etc."""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['nav', 'footer', '.sidebar', '.ads', '.comments', '.header', '.menu', 'script', 'style']):
                element.decompose()
            
            # Try to find main content areas
            main_selectors = [
                'main',
                'article',
                '.content',
                '#content',
                '.main-content',
                '.post-content',
                '.entry-content'
            ]
            
            main_content = ""
            for selector in main_selectors:
                element = soup.select_one(selector)
                if element:
                    main_content = element.get_text(separator=' ', strip=True)
                    break
            
            # If no main content found, use body text
            if not main_content:
                main_content = soup.get_text(separator=' ', strip=True)
            
            # Clean up whitespace
            main_content = ' '.join(main_content.split())
            
            return main_content
            
        except Exception:
            # Fallback: return first 1000 characters of text
            return ' '.join(html_content.split())[:1000]
    
    async def _detect_changes(self, baseline: Dict[str, Any], current_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect changes between baseline and current state."""
        changes = []
        
        # Get baseline URLs - handle both old format (sitemap_state.urls) and new format (urls)
        baseline_urls = set(baseline.get("sitemap_state", {}).get("urls", []) or baseline.get("urls", []))
        current_urls = set(current_state.get("urls", []))
        baseline_hashes = baseline.get("content_hashes", {})
        current_hashes = current_state.get("content_hashes", {})
        
        print(f"🔍 Comparing {len(current_urls)} current URLs against {len(baseline_urls)} baseline URLs")
        print(f"🔍 Current hashes: {len(current_hashes)}, Baseline hashes: {len(baseline_hashes)}")
        
        # Check for hash format mismatch (MD5 vs SHA256)
        if baseline_hashes and current_hashes:
            # Find valid hash samples (not None)
            sample_baseline_hash = None
            sample_current_hash = None
            
            # Get first valid baseline hash
            for hash_data in baseline_hashes.values():
                if isinstance(hash_data, dict) and hash_data.get("hash") is not None:
                    sample_baseline_hash = hash_data.get("hash", "")
                    break
            
            # Get first valid current hash
            for hash_data in current_hashes.values():
                if isinstance(hash_data, dict) and hash_data.get("hash") is not None:
                    sample_current_hash = hash_data.get("hash", "")
                    break
            
            # Only compare if we have valid hashes
            if sample_baseline_hash and sample_current_hash:
                # If baseline uses MD5 (32 chars) and current uses SHA256 (64 chars), treat as format mismatch
                if len(sample_baseline_hash) == 32 and len(sample_current_hash) == 64:
                    print(f"⚠️ Hash format mismatch detected: baseline uses MD5, current uses SHA256")
                    print(f"🔄 Creating new baseline with SHA256 format...")
                    return []  # Return empty changes to trigger new baseline creation
        
        # Detect new URLs
        new_urls = current_urls - baseline_urls
        for url in new_urls:
            changes.append({
                "url": url,
                "change_type": "new_page",
                "detected_at": datetime.now().isoformat(),
                "details": "New URL found in sitemap"
            })
        
        # Detect deleted URLs
        deleted_urls = baseline_urls - current_urls
        for url in deleted_urls:
            changes.append({
                "url": url,
                "change_type": "deleted_page",
                "detected_at": datetime.now().isoformat(),
                "details": "URL no longer in sitemap"
            })
        
        # Detect modified content
        for url in current_urls & baseline_urls:  # URLs in both sets
            current_hash = current_hashes.get(url, {}).get("hash")
            baseline_hash = baseline_hashes.get(url, {}).get("hash")
            
            if current_hash and baseline_hash and current_hash != baseline_hash:
                changes.append({
                    "url": url,
                    "change_type": "modified_content",
                    "detected_at": datetime.now().isoformat(),
                    "details": f"Content hash changed from {baseline_hash[:8]}... to {current_hash[:8]}...",
                    "previous_hash": baseline_hash,
                    "new_hash": current_hash
                })
        
        # Add ignored files tracking
        ignored_files = []
        for url in current_urls:
            if self._is_ignorable_file(url):
                ignored_files.append({
                    "url": url,
                    "change_type": "ignored_file",
                    "detected_at": datetime.now().isoformat(),
                    "details": "Skipped: image/document file",
                    "file_type": self._get_file_type(url)
                })
        
        changes.extend(ignored_files)
        
        print(f"🔍 Detected changes: {len(changes)} total ({len(new_urls)} new, {len(deleted_urls)} deleted, {len([c for c in changes if c['change_type'] == 'modified_content'])} modified, {len(ignored_files)} ignored)")
        return changes
    
    def _should_create_new_baseline(self, baseline: Dict[str, Any], current_state: Dict[str, Any]) -> bool:
        """Check if we should create a new baseline due to hash format mismatch."""
        baseline_hashes = baseline.get("content_hashes", {})
        current_hashes = current_state.get("content_hashes", {})
        
        if baseline_hashes and current_hashes:
            # Find valid hash samples (not None)
            sample_baseline_hash = None
            sample_current_hash = None
            
            # Get first valid baseline hash
            for hash_data in baseline_hashes.values():
                if isinstance(hash_data, dict) and hash_data.get("hash") is not None:
                    sample_baseline_hash = hash_data.get("hash", "")
                    break
            
            # Get first valid current hash
            for hash_data in current_hashes.values():
                if isinstance(hash_data, dict) and hash_data.get("hash") is not None:
                    sample_current_hash = hash_data.get("hash", "")
                    break
            
            # Only compare if we have valid hashes
            if sample_baseline_hash and sample_current_hash:
                # If baseline uses MD5 (32 chars) and current uses SHA256 (64 chars), we should create a new baseline
                if len(sample_baseline_hash) == 32 and len(sample_current_hash) == 64:
                    return True
        
        return False
    
    async def _create_initial_baseline(self, site_config: Any, current_state: Dict[str, Any]) -> Dict[str, Any]:
        """Create initial baseline when none exists."""
        # Create baseline data
        baseline_data = {
            "site_id": site_config.name,
            "site_name": site_config.name,
            "site_url": site_config.url,
            "baseline_date": datetime.now().strftime("%Y%m%d"),
            "created_at": datetime.now().isoformat(),
            "baseline_version": "2.0",
            "total_urls": current_state["total_urls"],
            "total_content_hashes": current_state["total_content_hashes"],
            
            # State data
            "urls": current_state["urls"],
            "content_hashes": current_state["content_hashes"],
            
            # Metadata
            "metadata": {
                "creation_method": "simplified_change_detector",
                "content_hash_algorithm": "sha256",
                "content_extraction_method": "main_content_only",
                "baseline_type": "initial"
            }
        }
        
        # Save baseline
        baseline_file = self.baseline_manager.save_baseline(site_config.name, baseline_data)
        
        # Log baseline event
        self.baseline_manager._log_baseline_event("baseline_created", site_config.name, {
            "file_path": baseline_file,
            "total_urls": current_state["total_urls"],
            "total_content_hashes": current_state["total_content_hashes"],
            "baseline_date": baseline_data["baseline_date"],
            "evolution_type": "initial_creation"
        })
        
        return {
            "site_id": site_config.name,
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
    
    async def _handle_changes_found(self, site_config: Any, baseline: Dict[str, Any], 
                                  current_state: Dict[str, Any], changes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Handle case when changes are detected."""
        print(f"🔄 Changes detected for {site_config.name}, updating baseline...")
        
        # Categorize changes
        new_pages = [c for c in changes if c["change_type"] == "new_page"]
        modified_pages = [c for c in changes if c["change_type"] == "modified_content"]
        deleted_pages = [c for c in changes if c["change_type"] == "deleted_page"]
        
        # Create new baseline by merging with current state
        new_baseline = self.baseline_manager.update_baseline_from_changes(
            site_config.name, baseline, current_state, changes
        )
        
        # Save the new baseline
        baseline_file = self.baseline_manager.save_baseline(site_config.name, new_baseline)
        
        # Save changes to dedicated changes directory
        changes_file = await self._save_changes(site_config.name, changes)
        
        # Log baseline event with detailed summary
        change_summary = f"{len(changes)} pages changed: {len(new_pages)} new pages, {len(modified_pages)} pages modified, {len(deleted_pages)} pages deleted"
        self.baseline_manager._log_baseline_event("baseline_updated", site_config.name, {
            "file_path": baseline_file,
            "changes_file": changes_file,
            "total_changes": len(changes),
            "new_pages": len(new_pages),
            "modified_pages": len(modified_pages),
            "deleted_pages": len(deleted_pages),
            "change_summary": change_summary,
            "evolution_type": "automatic_update"
        })
        
        print(f"✅ Baseline updated: {baseline_file}")
        print(f"📄 Changes saved: {changes_file}")
        print(f"📊 {change_summary}")
        
        return {
            "site_id": site_config.name,
            "site_name": site_config.name,
            "detection_time": datetime.now().isoformat(),
            "changes": changes,
            "summary": {
                "total_changes": len(changes),
                "new_pages": len(new_pages),
                "modified_pages": len(modified_pages),
                "deleted_pages": len(deleted_pages)
            },
            "metadata": {
                "message": change_summary,
                "baseline_updated": True,
                "baseline_file": baseline_file,
                "changes_file": changes_file
            },
            "baseline_updated": True,
            "baseline_file": baseline_file,
            "changes_file": changes_file
        }
    
    async def _handle_no_changes(self, site_config: Any, baseline: Dict[str, Any]) -> Dict[str, Any]:
        """Handle case when no changes are detected."""
        print(f"✅ No changes detected for {site_config.name}")
        
        # Log baseline validation event
        self.baseline_manager._log_baseline_event("baseline_validated", site_config.name, {
            "message": "Baseline validated - no changes detected",
            "baseline_date": baseline.get("baseline_date"),
            "total_urls": baseline.get("total_urls", 0),
            "total_content_hashes": baseline.get("total_content_hashes", 0),
            "evolution_type": "validation"
        })
        
        return {
            "site_id": site_config.name,
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
                "message": "Baseline validated - no changes detected",
                "baseline_updated": False
            },
            "baseline_updated": False,
            "baseline_file": None
        }
    
    async def _save_changes(self, site_name: str, changes: List[Dict[str, Any]]) -> str:
        """Save changes to dedicated changes directory."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{site_name}_{timestamp}_changes.json"
        filepath = self.changes_dir / filename
        
        changes_data = {
            "metadata": {
                "site_name": site_name,
                "detection_time": datetime.now().isoformat(),
                "total_changes": len(changes),
                "file_created": datetime.now().isoformat()
            },
            "changes": changes
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(changes_data, f, indent=2, ensure_ascii=False)
        
        return str(filepath) 