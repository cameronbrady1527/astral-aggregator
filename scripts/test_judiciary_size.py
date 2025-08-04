#!/usr/bin/env python3
"""
Quick script to check Judiciary UK sitemap size and estimate processing time.
"""

import asyncio
import sys
import os
import re
from datetime import datetime

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.crawler.content_detector import ContentDetector


class JudiciaryConfig(object):
    def __init__(self):
        self.name = 'Judiciary UK'
        self.url = 'https://www.judiciary.uk/'
        self.sitemap_url = 'https://www.judiciary.uk/sitemap_index.xml'
        self.max_concurrent_requests = 30
        self.connection_pool_size = 60
        self.batch_size = 200
        self.ultra_fast_timeout = 12
        self.adaptive_rate_limiting = True
        self.min_concurrent_requests = 5
        self.success_rate_threshold = 0.98
        self.rate_adjustment_factor = 0.7
        self.rate_increase_factor = 1.05
        self.progressive_ramping = True
        self.ramp_start_concurrency = 3
        self.ramp_target_concurrency = 30
        self.ramp_batch_size = 15
        self.content_selectors = ['main', 'article', '.content', '#content', '.main-content']
        self.exclude_selectors = ['nav', 'footer', '.sidebar', '.ads', '.comments', '.header', '.menu']
        self.max_content_pages = 0
        self.content_timeout = 10


async def check_judiciary_size():
    """Check Judiciary UK sitemap size and estimate processing time."""
    print("🔍 Checking Judiciary UK sitemap size...")
    
    config = JudiciaryConfig()
    detector = ContentDetector(config)
    detector.sitemap_url = config.sitemap_url
    detector.site_url = config.url
    
    try:
        # Get sitemap index URLs first
        sitemap_urls = await detector._get_sitemap_urls()
        print(f"📋 Found {len(sitemap_urls)} sitemap files in index")
        
        # Now fetch all individual page URLs from each sitemap
        all_page_urls = []
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            for i, sitemap_url in enumerate(sitemap_urls):
                print(f"   Checking sitemap {i+1}/{len(sitemap_urls)}: {sitemap_url}")
                try:
                    async with session.get(sitemap_url) as response:
                        if response.status == 200:
                            content = await response.text()
                            # Extract page URLs from this sitemap
                            page_urls = re.findall(r'<loc>(.*?)</loc>', content)
                            # Filter out non-page URLs (like images, etc.)
                            page_urls = [url for url in page_urls if not url.endswith(('.jpg', '.png', '.gif', '.pdf', '.xml'))]
                            all_page_urls.extend(page_urls)
                            print(f"     Found {len(page_urls)} pages in this sitemap")
                        else:
                            print(f"     Failed to fetch sitemap: {response.status}")
                except Exception as e:
                    print(f"     Error fetching sitemap: {e}")
        
        # Remove duplicates
        unique_urls = list(set(all_page_urls))
        total_urls = len(unique_urls)
        
        print(f"\n📊 Judiciary UK Statistics:")
        print(f"   Sitemap files: {len(sitemap_urls)}")
        print(f"   Total page URLs found: {total_urls:,}")
        
        # Estimate processing time based on Waverley performance
        # From our tests: ~5.1 URLs/second for 100 URLs
        # Conservative estimate: 4 URLs/second for large sites
        estimated_seconds = total_urls / 4
        estimated_minutes = estimated_seconds / 60
        estimated_hours = estimated_minutes / 60
        
        print(f"\n⏱️  Estimated Processing Time:")
        print(f"   Speed: ~4 URLs/second (conservative estimate)")
        print(f"   Total time: {estimated_seconds:.0f} seconds")
        print(f"   Total time: {estimated_minutes:.1f} minutes")
        print(f"   Total time: {estimated_hours:.2f} hours")
        
        # Show some sample URLs
        print(f"\n📝 Sample URLs (first 5):")
        for i, url in enumerate(unique_urls[:5]):
            print(f"   {i+1}. {url}")
        
        if total_urls > 5:
            print(f"   ... and {total_urls - 5:,} more URLs")
        
        return total_urls, estimated_seconds
        
    except Exception as e:
        print(f"❌ Error checking Judiciary UK: {e}")
        return 0, 0
    finally:
        await detector.close()


if __name__ == "__main__":
    try:
        total_urls, estimated_time = asyncio.run(check_judiciary_size())
        if total_urls > 0:
            print(f"\n✅ Judiciary UK has {total_urls:,} URLs")
            print(f"⏰ Estimated processing time: {estimated_time/60:.1f} minutes")
        else:
            print("❌ Could not determine Judiciary UK size")
    except Exception as e:
        print(f"❌ Script failed: {e}")
        sys.exit(1) 