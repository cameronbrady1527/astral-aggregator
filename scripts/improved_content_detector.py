#!/usr/bin/env python3
"""
Improved Content Detector with Better Error Handling
This version includes rate limiting, retry logic, and better error handling.
"""

import asyncio
import sys
import os
import json
import time
import hashlib
import aiohttp
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import random

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.crawler.content_detector import ContentDetector
from app.utils.config import ConfigManager

class ImprovedContentDetector(ContentDetector):
    """Improved content detector with better error handling and rate limiting."""
    
    def __init__(self, site_config: Any):
        super().__init__(site_config)
        self.rate_limit_delay = 0.5  # 500ms between requests
        self.max_retries = 3
        self.timeout = 30  # 30 seconds timeout
        self.max_concurrent = 5  # Max concurrent requests
        
    async def _fetch_content_hashes(self, urls: List[str]) -> Dict[str, str]:
        """Fetch content hashes with improved error handling and rate limiting."""
        content_hashes = {}
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def fetch_with_semaphore(url: str):
            async with semaphore:
                return await self._fetch_single_content_hash_with_retry(url)
        
        # Process URLs in batches to avoid overwhelming the server
        batch_size = 10
        for i in range(0, len(urls), batch_size):
            batch = urls[i:i + batch_size]
            print(f"📄 Processing batch {i//batch_size + 1}/{(len(urls) + batch_size - 1)//batch_size} ({len(batch)} URLs)")
            
            tasks = [fetch_with_semaphore(url) for url in batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for j, result in enumerate(results):
                if isinstance(result, tuple) and len(result) == 2:
                    url, content_hash = result
                    if content_hash:
                        content_hashes[url] = content_hash
                else:
                    print(f"⚠️ Failed to fetch {batch[j]}: {result}")
            
            # Rate limiting between batches
            if i + batch_size < len(urls):
                await asyncio.sleep(self.rate_limit_delay)
        
        return content_hashes
    
    async def _fetch_single_content_hash_with_retry(self, url: str) -> tuple[str, Optional[str]]:
        """Fetch content hash with retry logic."""
        for attempt in range(self.max_retries):
            try:
                timeout = aiohttp.ClientTimeout(total=self.timeout)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    # Add random delay to avoid being detected as a bot
                    await asyncio.sleep(random.uniform(0.1, 0.3))
                    
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.5',
                        'Accept-Encoding': 'gzip, deflate',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1',
                    }
                    
                    async with session.get(url, headers=headers, allow_redirects=True) as response:
                        if response.status == 200:
                            content = await response.text()
                            main_content = self._extract_main_content(content)
                            
                            if main_content:
                                content_hash = hashlib.md5(main_content.encode('utf-8')).hexdigest()
                                return url, content_hash
                            else:
                                return url, None
                        elif response.status == 404:
                            # Page not found - don't retry
                            return url, None
                        elif response.status in [429, 503]:
                            # Rate limited or service unavailable - wait and retry
                            wait_time = (attempt + 1) * 2
                            print(f"⏳ Rate limited for {url}, waiting {wait_time}s (attempt {attempt + 1})")
                            await asyncio.sleep(wait_time)
                            continue
                        else:
                            # Other HTTP errors - don't retry
                            return url, None
                            
            except asyncio.TimeoutError:
                if attempt < self.max_retries - 1:
                    wait_time = (attempt + 1) * 1
                    print(f"⏳ Timeout for {url}, retrying in {wait_time}s (attempt {attempt + 1})")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    return url, None
            except Exception as e:
                if attempt < self.max_retries - 1:
                    wait_time = (attempt + 1) * 1
                    print(f"⚠️ Error for {url}: {e}, retrying in {wait_time}s (attempt {attempt + 1})")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    return url, None
        
        return url, None

async def run_improved_content_detection():
    """Run improved content detection for both sites."""
    print("🚀 IMPROVED CONTENT DETECTION")
    print("=" * 50)
    
    config = ConfigManager()
    sites = ['judiciary_uk', 'waverley_gov']
    
    for site_id in sites:
        print(f"\n🔍 Processing {site_id}...")
        
        try:
            site_config = config.get_site(site_id)
            if not site_config:
                print(f"❌ Site {site_id} not found in configuration")
                continue
            
            # Create improved content detector
            detector = ImprovedContentDetector(site_config)
            
            # Get current state with improved error handling
            start_time = time.time()
            state = await detector.get_current_state()
            duration = time.time() - start_time
            
            # Save results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"improved_content_check_{site_id}_{timestamp}.json"
            
            result = {
                "site_id": site_id,
                "site_name": site_config.name,
                "timestamp": datetime.now().isoformat(),
                "duration_seconds": round(duration, 2),
                "state": state,
                "summary": {
                    "total_pages": state.get("total_pages", 0),
                    "urls_checked": len(state.get("urls_checked", [])),
                    "content_hashes": len(state.get("content_hashes", {}))
                }
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Completed {site_config.name}")
            print(f"   📄 Total pages: {result['summary']['total_pages']}")
            print(f"   🔗 URLs checked: {result['summary']['urls_checked']}")
            print(f"   🔍 Content hashes: {result['summary']['content_hashes']}")
            print(f"   ⏱️ Duration: {duration:.2f}s")
            print(f"   💾 Saved to: {output_file}")
            
        except Exception as e:
            print(f"❌ Error processing {site_id}: {e}")
    
    print(f"\n✅ Improved content detection completed")

if __name__ == "__main__":
    asyncio.run(run_improved_content_detection()) 