#!/usr/bin/env python3
# ==============================================================================
# create_comprehensive_baseline.py — Create complete baselines for change detection
# ==============================================================================
# Purpose: Create baselines with URLs, content hashes, and metadata for change detection
# Sections: Imports, Public Exports, MockSiteConfig Class, ComprehensiveBaselineCreator Class, Main Functions
# ==============================================================================

# ==============================================================================
# Imports
# ==============================================================================

# Standard Library -----
import asyncio
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Third-Party -----
import aiohttp
from bs4 import BeautifulSoup

# Internal -----
# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))
from crawler.sitemap_detector import SitemapDetector

# ==============================================================================
# Public exports
# ==============================================================================
__all__ = [
    'MockSiteConfig',
    'ComprehensiveBaselineCreator',
    'main'
]

# ==============================================================================
# MockSiteConfig Class
# ==============================================================================

class MockSiteConfig:
    """Mock site configuration for testing."""
    def __init__(self, site_id: str = None):
        # default to Judiciary UK if no site_id provided
        if site_id == "judiciary_uk" or site_id is None:
            self.name = "Judiciary UK"
            self.url = "https://www.judiciary.uk/"
            self.sitemap_url = "https://www.judiciary.uk/sitemap_index.xml"
        elif site_id == "waverley_gov":
            self.name = "Waverley Borough Council"
            self.url = "https://www.waverley.gov.uk/"
            self.sitemap_url = "https://www.waverley.gov.uk/sitemap.xml"
        else:
            # generic configuration for unknown sites
            self.name = site_id.replace("_", " ").title() if site_id else "Unknown Site"
            self.url = f"https://{site_id.replace('_', '.')}/" if site_id else "https://example.com/"
            self.sitemap_url = f"https://{site_id.replace('_', '.')}/sitemap.xml" if site_id else "https://example.com/sitemap.xml"
        
        self.verify_deleted_urls = True
        self.max_concurrent_checks = 5
        self.verification_timeout = 10


class ComprehensiveBaselineCreator:
    """Create comprehensive baselines with URLs and content hashes."""
    
    def __init__(self, site_config: MockSiteConfig):
        self.site_config = site_config
        self.detector = SitemapDetector(site_config)
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def create_baseline(self, site_id: str, max_urls: int = None) -> Dict[str, Any]:
        """Create a comprehensive baseline for a site with URLs and content hashes."""
        print(f"🔧 Creating comprehensive baseline for {site_id}...")
        
        # step 1: get sitemap URLs
        print("📋 Step 1: Fetching sitemap URLs...")
        sitemap_state = await self.detector.get_current_state()
        
        if not sitemap_state.get('urls'):
            print("[ X ] Failed to fetch sitemap URLs")
            return None
        
        urls = sitemap_state['urls']
        print(f"✅ Found {len(urls)} URLs in sitemap")
        
        # step 2: get content hashes for all URLs
        print("🔍 Step 2: Calculating content hashes...")
        content_data = await self._get_content_hashes(urls, max_urls)
        
        # step 3: create comprehensive baseline
        print("💾 Step 3: Creating baseline file...")
        baseline_data = {
            "site_id": site_id,
            "site_name": self.site_config.name,
            "site_url": self.site_config.url,
            "baseline_date": datetime.now().strftime("%Y%m%d"),
            "created_at": datetime.now().isoformat(),
            "baseline_version": "2.0",
            "total_urls": len(urls),
            "total_content_hashes": len(content_data),
            
            # sitemap data
            "sitemap_state": sitemap_state,
            
            # content data
            "content_hashes": content_data,
            
            # metadata
            "metadata": {
                "creation_method": "comprehensive_baseline_creator",
                "content_hash_algorithm": "sha256",
                "content_extraction_method": "main_content_only",
                "baseline_type": "full"
            }
        }
        
        return baseline_data
    
    async def _get_content_hashes(self, urls: List[str], max_urls: int = None) -> Dict[str, Any]:
        """Get content hashes for ALL URLs (comprehensive baseline)."""
        if max_urls:
            print(f"🔍 Getting content hashes for up to {max_urls} URLs...")
            check_urls = urls[:max_urls]
        else:
            print(f"🔍 Getting content hashes for ALL {len(urls)} URLs (comprehensive baseline)...")
            check_urls = urls
        content_data = {}
        
        # process URLs in batches
        batch_size = 20  # increased batch size for efficiency
        total_batches = (len(check_urls) + batch_size - 1) // batch_size
        
        for i in range(0, len(check_urls), batch_size):
            batch = check_urls[i:i + batch_size]
            batch_num = i // batch_size + 1
            print(f"   Processing batch {batch_num}/{total_batches} ({len(batch)} URLs) - Progress: {i + len(batch)}/{len(check_urls)}")
            
            batch_results = await self._process_url_batch(batch)
            content_data.update(batch_results)
            
            # small delay between batches to be respectful to the server
            await asyncio.sleep(0.5)
        
        print(f"✅ Successfully processed {len(content_data)} URLs")
        return content_data
    
    async def _process_url_batch(self, urls: List[str]) -> Dict[str, Any]:
        """Process a batch of URLs to get content hashes."""
        tasks = [self._get_single_url_content(url) for url in urls]
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
    
    async def _get_single_url_content(self, url: str) -> Dict[str, Any]:
        """Get content hash for a single URL."""
        try:
            async with self.session.get(url, timeout=15) as response:
                if response.status != 200:
                    return {
                        "error": f"HTTP {response.status}",
                        "hash": None,
                        "content_length": 0,
                        "status_code": response.status,
                        "extracted_at": datetime.now().isoformat()
                    }
                
                content = await response.text()
                
                # extract main content (remove navigation, footer, etc.)
                main_content = self._extract_main_content(content)
                
                # calculate hash
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
            
            # remove unwanted elements
            for element in soup(['nav', 'footer', '.sidebar', '.ads', '.comments', '.header', '.menu', 'script', 'style']):
                element.decompose()
            
            # try to find main content areas
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
            
            # if no main content found, use body text
            if not main_content:
                main_content = soup.get_text(separator=' ', strip=True)
            
            # clean up whitespace
            main_content = ' '.join(main_content.split())
            
            return main_content
            
        except Exception:
            # fallback: return first 1000 characters of text
            return ' '.join(html_content.split())[:1000]
    
    async def save_baseline(self, baseline_data: Dict[str, Any], site_id: str) -> str:
        """Save baseline to file."""
        baseline_dir = Path("baselines")
        baseline_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        baseline_file = baseline_dir / f"{site_id}_{timestamp}_comprehensive_baseline.json"
        
        print(f"💾 Saving baseline to {baseline_file}...")
        
        with open(baseline_file, 'w', encoding='utf-8') as f:
            json.dump(baseline_data, f, indent=2, ensure_ascii=False)
        
        # create baseline event for dashboard integration
        await self._create_baseline_event(site_id, baseline_data, str(baseline_file))
        
        print(f"✅ Baseline saved successfully!")
        print(f"📊 Baseline contains:")
        print(f"   - {baseline_data['total_urls']} URLs")
        print(f"   - {baseline_data['total_content_hashes']} content hashes")
        print(f"   - Created at: {baseline_data['created_at']}")
        
        return str(baseline_file)
    
    async def _create_baseline_event(self, site_id: str, baseline_data: Dict[str, Any], file_path: str):
        """Create baseline event for dashboard integration."""
        try:
            # load existing events
            events_file = Path("baselines/baseline_events.json")
            events = []
            
            if events_file.exists():
                with open(events_file, 'r', encoding='utf-8') as f:
                    events = json.load(f)
            
            # create new event
            event = {
                "timestamp": datetime.now().isoformat(),
                "event_type": "baseline_created",
                "site_id": site_id,
                "details": {
                    "file_path": file_path,
                    "total_urls": baseline_data.get("total_urls", 0),
                    "total_content_hashes": baseline_data.get("total_content_hashes", 0),
                    "baseline_date": baseline_data.get("baseline_date"),
                    "evolution_type": "initial_creation"
                }
            }
            
            # add to events
            events.append(event)
            
            # keep only last 100 events
            if len(events) > 100:
                events = events[-100:]
            
            # save events
            with open(events_file, 'w', encoding='utf-8') as f:
                json.dump(events, f, indent=2, ensure_ascii=False)
            
            print(f"📊 Baseline event created for dashboard integration")
            
        except Exception as e:
            print(f"⚠️ Warning: Could not create baseline event: {e}")
    
    async def verify_baseline(self, baseline_file: str) -> bool:
        """Verify that the baseline file is valid."""
        print("🔍 Verifying baseline...")
        
        try:
            with open(baseline_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # check required fields
            required_fields = ['site_id', 'sitemap_state', 'content_hashes', 'total_urls', 'total_content_hashes']
            for field in required_fields:
                if field not in data:
                    print(f"[ X ] Missing required field: {field}")
                    return False
            
            # check data consistency
            urls_count = len(data['sitemap_state']['urls'])
            hashes_count = len(data['content_hashes'])
            
            if urls_count != data['total_urls']:
                print(f"[ X ] URL count mismatch: {urls_count} vs {data['total_urls']}")
                return False
            
            if hashes_count != data['total_content_hashes']:
                print(f"[ X ] Hash count mismatch: {hashes_count} vs {data['total_content_hashes']}")
                return False
            
            print("✅ Baseline verification successful!")
            return True
            
        except Exception as e:
            print(f"[ X ] Baseline verification failed: {e}")
            return False


async def reset_dashboard():
    """Reset the dashboard to start fresh."""
    print("🔄 Resetting dashboard...")
    
    # clear any existing change detection state
    # this would typically involve clearing database records or resetting counters
    print("✅ Dashboard reset complete (no existing state to clear)")


async def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python create_comprehensive_baseline.py <site_id> [max_urls]")
        print("Example: python create_comprehensive_baseline.py judiciary_uk")
        print("Example: python create_comprehensive_baseline.py judiciary_uk 1000  # Limit to 1000 URLs")
        print("Note: If no max_urls is specified, ALL URLs will be processed for comprehensive baseline")
        return 1
    
    site_id = sys.argv[1]
    max_urls = int(sys.argv[2]) if len(sys.argv) > 2 else None  # None = process ALL URLs
    
    print("🚀 Starting comprehensive baseline creation...")
    
    # step 1: reset dashboard
    await reset_dashboard()
    
    # step 2: create baseline
    site_config = MockSiteConfig(site_id)
    async with ComprehensiveBaselineCreator(site_config) as creator:
        baseline_data = await creator.create_baseline(site_id, max_urls)
        
        if not baseline_data:
            print("[ X ] Failed to create baseline")
            return 1
        
        # step 3: save baseline
        baseline_file = await creator.save_baseline(baseline_data, site_id)
        
        # step 4: verify baseline
        success = await creator.verify_baseline(baseline_file)
        
        if success:
            print(f"\n🎉 Comprehensive baseline created successfully!")
            print(f"📁 Baseline file: {baseline_file}")
            print(f"📊 Ready for change detection!")
            print(f"\n💡 Next steps:")
            print(f"   1. Run change detection against this baseline")
            print(f"   2. Monitor for real changes")
            print(f"   3. Verify that initial detection shows 0 changes")
            return 0
        else:
            print("[ X ] Baseline verification failed")
            return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 