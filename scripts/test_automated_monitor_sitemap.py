#!/usr/bin/env python3
"""
Test Automated Monitor Sitemap - Test the sitemap detector within the automated monitor context
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


async def test_with_session():
    """Test sitemap detector within a session context (like automated monitor)."""
    print("🔍 Testing sitemap detector within session context...")
    
    import aiohttp
    
    async with aiohttp.ClientSession() as session:
        print("   Session created")
        
        site_config = MockSiteConfig()
        detector = SitemapDetector(site_config)
        
        print("   Calling get_current_state...")
        try:
            state = await detector.get_current_state()
            print(f"✅ Success!")
            print(f"   URLs found: {len(state.get('urls', []))}")
            print(f"   Total URLs: {state.get('total_urls', 0)}")
            
            if 'error' in state:
                print(f"   Error: {state['error']}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()


async def test_without_session():
    """Test sitemap detector without session context."""
    print("🔍 Testing sitemap detector without session context...")
    
    site_config = MockSiteConfig()
    detector = SitemapDetector(site_config)
    
    print("   Calling get_current_state...")
    try:
        state = await detector.get_current_state()
        print(f"✅ Success!")
        print(f"   URLs found: {len(state.get('urls', []))}")
        print(f"   Total URLs: {state.get('total_urls', 0)}")
        
        if 'error' in state:
            print(f"   Error: {state['error']}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Main function."""
    print("🚀 Testing Sitemap Detector in Different Contexts")
    print("=" * 60)
    
    await test_without_session()
    print()
    await test_with_session()


if __name__ == "__main__":
    asyncio.run(main()) 