#!/usr/bin/env python3
"""
Investigate Content Hashes Script
================================

This script investigates the content hash fetching issues to understand
why the numbers don't add up between URLs and content hashes.
"""

import asyncio
import sys
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.crawler.content_detector import ContentDetector
from app.crawler.hybrid_detector import HybridDetector
from app.utils.config import ConfigManager

async def investigate_content_hashes():
    """Investigate content hash fetching issues."""
    
    print("🔍 Investigating Content Hash Fetching Issues")
    print("=" * 60)
    
    try:
        # Create config manager
        config_manager = ConfigManager()
        
        # Test both sites
        sites_to_test = ["waverley_gov", "judiciary_uk"]
        
        for site_id in sites_to_test:
            print(f"\n📋 Testing site: {site_id}")
            print("-" * 40)
            
            site_config = config_manager.get_site(site_id)
            if not site_config:
                print(f"❌ Site {site_id} not found in configuration")
                continue
            
            print(f"🔗 URL: {site_config.url}")
            print(f"🗺️ Sitemap: {site_config.sitemap_url}")
            print(f"🔍 Methods: {site_config.detection_methods}")
            
            # Check content detector configuration
            max_pages = getattr(site_config, 'max_content_pages', 10)
            print(f"📄 Max content pages: {max_pages}")
            
            # Test content detector directly
            print(f"\n🧪 Testing Content Detector directly...")
            content_detector = ContentDetector(site_config)
            
            # Get sitemap URLs
            sitemap_urls = await content_detector._get_sitemap_urls()
            print(f"📊 Total URLs in sitemap: {len(sitemap_urls)}")
            
            # Check how many URLs would be processed
            if max_pages > 0:
                urls_to_check = sitemap_urls[:max_pages]
                print(f"🔍 URLs that will be checked: {len(urls_to_check)}")
            else:
                urls_to_check = sitemap_urls
                print(f"🔍 All URLs will be checked: {len(urls_to_check)}")
            
            # Test fetching content hashes for first few URLs
            print(f"\n🔍 Testing content hash fetching for first 5 URLs...")
            test_urls = urls_to_check[:5]
            
            content_hashes = await content_detector._fetch_content_hashes(test_urls)
            print(f"✅ Successfully fetched content hashes: {len(content_hashes)}")
            
            # Show details for each URL
            for url in test_urls:
                if url in content_hashes:
                    hash_data = content_hashes[url]
                    if isinstance(hash_data, dict):
                        hash_value = hash_data.get('hash', 'N/A')
                    else:
                        hash_value = str(hash_data)
                    print(f"   ✅ {url[:60]}... -> {hash_value[:20]}...")
                else:
                    print(f"   ❌ {url[:60]}... -> FAILED")
            
            # Test hybrid detector
            print(f"\n🧪 Testing Hybrid Detector...")
            hybrid_detector = HybridDetector(site_config)
            
            # Check if content detection should run
            should_run = hybrid_detector._should_run_content_check()
            print(f"🔍 Should run content check: {should_run}")
            
            # Get current state
            current_state = await hybrid_detector.get_current_state()
            
            sitemap_state = current_state.get("sitemap_state", {})
            content_state = current_state.get("content_state", {})
            
            print(f"📊 Sitemap URLs: {len(sitemap_state.get('urls', []))}")
            
            if content_state:
                content_hashes = content_state.get("content_hashes", {})
                print(f"🔗 Content hashes: {len(content_hashes)}")
                
                # Check if content hashes have the expected structure
                if content_hashes:
                    sample_hash = next(iter(content_hashes.values()))
                    print(f"📝 Sample hash structure: {type(sample_hash)}")
                    if isinstance(sample_hash, dict):
                        print(f"   Keys: {list(sample_hash.keys())}")
                    else:
                        print(f"   Value: {sample_hash[:50]}...")
            else:
                print(f"❌ No content state (content detection not run)")
            
            print("\n" + "="*60)
        
        print("\n✅ Investigation completed!")
        
    except Exception as e:
        print(f"❌ Investigation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(investigate_content_hashes()) 