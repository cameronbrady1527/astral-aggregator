#!/usr/bin/env python3
"""
Debug Sitemap Detector - Test the sitemap detector to see why it's returning 0 URLs
"""

import asyncio
import sys
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))

from crawler.sitemap_detector import SitemapDetector


class MockSiteConfig:
    """Mock site configuration for testing."""
    def __init__(self):
        self.name = "Judiciary UK"
        self.url = "https://www.judiciary.uk/"
        self.sitemap_url = "https://www.judiciary.uk/sitemap_index.xml"
        self.verify_deleted_urls = True
        self.max_concurrent_checks = 5
        self.verification_timeout = 10


async def debug_sitemap_detector():
    """Debug the sitemap detector step by step."""
    print("🔍 Debugging Sitemap Detector")
    print("=" * 50)
    
    site_config = MockSiteConfig()
    detector = SitemapDetector(site_config)
    
    print(f"📋 Site Config:")
    print(f"   Name: {site_config.name}")
    print(f"   URL: {site_config.url}")
    print(f"   Sitemap URL: {site_config.sitemap_url}")
    print(f"   Detector sitemap URL: {detector.sitemap_url}")
    
    print(f"\n🔍 Testing sitemap fetch...")
    
    try:
        # Test the core method directly
        print("   Calling _fetch_all_sitemap_urls...")
        urls, sitemap_info = await detector._fetch_all_sitemap_urls()
        
        print(f"✅ Success!")
        print(f"   URLs found: {len(urls)}")
        print(f"   Sitemap info: {sitemap_info}")
        
        if urls:
            print(f"   First 5 URLs:")
            for i, url in enumerate(urls[:5]):
                print(f"     {i+1}. {url}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n🔍 Testing get_current_state...")
    
    try:
        state = await detector.get_current_state()
        print(f"✅ Success!")
        print(f"   State keys: {list(state.keys())}")
        print(f"   URLs in state: {len(state.get('urls', []))}")
        print(f"   Total URLs: {state.get('total_urls', 0)}")
        
        if 'error' in state:
            print(f"   Error in state: {state['error']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Main function."""
    await debug_sitemap_detector()


if __name__ == "__main__":
    asyncio.run(main()) 