#!/usr/bin/env python3
"""
Check if content-detected pages are actually in the sitemap.
This script helps understand the relationship between sitemap and content detection.
"""

import asyncio
import sys
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.crawler.sitemap_detector import SitemapDetector
from app.crawler.content_detector import ContentDetector
from app.utils.config import ConfigManager

class SitemapContentChecker:
    """Check overlap between sitemap and content detection."""
    
    def __init__(self):
        self.config = ConfigManager()
    
    async def check_overlap(self, site_id: str) -> Dict[str, Any]:
        """Check if content-detected pages are in the sitemap."""
        print(f"\n🔍 Checking sitemap-content overlap for {site_id}...")
        
        try:
            # Get site configuration
            site_config = self.config.get_site(site_id)
            if not site_config:
                return {"error": f"Site {site_id} not found in configuration"}
            
            # Get current sitemap URLs
            print(f"📋 Fetching current sitemap for {site_config.name}...")
            sitemap_detector = SitemapDetector(site_config)
            sitemap_state = await sitemap_detector.get_current_state()
            sitemap_urls = set(sitemap_state.get("urls", []))
            
            # Get current content URLs
            print(f"📄 Fetching current content state for {site_config.name}...")
            content_detector = ContentDetector(site_config)
            content_state = await content_detector.get_current_state()
            content_urls = set(content_state.get("content_hashes", {}).keys())
            
            # Find overlap
            overlap_urls = sitemap_urls.intersection(content_urls)
            sitemap_only = sitemap_urls - content_urls
            content_only = content_urls - sitemap_urls
            
            result = {
                "site_id": site_id,
                "site_name": site_config.name,
                "timestamp": datetime.now().isoformat(),
                "sitemap_urls_count": len(sitemap_urls),
                "content_urls_count": len(content_urls),
                "overlap_count": len(overlap_urls),
                "sitemap_only_count": len(sitemap_only),
                "content_only_count": len(content_only),
                "overlap_urls": list(overlap_urls),
                "sitemap_only_urls": list(sitemap_only),
                "content_only_urls": list(content_only),
                "sitemap_urls": list(sitemap_urls),
                "content_urls": list(content_urls)
            }
            
            return result
            
        except Exception as e:
            return {
                "site_id": site_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def print_results(self, results: Dict[str, Any]):
        """Print the overlap analysis results."""
        if "error" in results:
            print(f"❌ Error: {results['error']}")
            return
        
        print(f"\n📊 SITEMAP-CONTENT OVERLAP ANALYSIS FOR {results['site_name'].upper()}")
        print("=" * 70)
        
        print(f"📋 Sitemap URLs: {results['sitemap_urls_count']}")
        print(f"📄 Content URLs: {results['content_urls_count']}")
        print(f"🔄 Overlap: {results['overlap_count']}")
        print(f"📋 Sitemap only: {results['sitemap_only_count']}")
        print(f"📄 Content only: {results['content_only_count']}")
        
        if results['content_only_urls']:
            print(f"\n🔍 CONTENT-ONLY URLs (not in sitemap):")
            for i, url in enumerate(results['content_only_urls'][:10], 1):  # Show first 10
                print(f"  {i}. {url}")
            if len(results['content_only_urls']) > 10:
                print(f"  ... and {len(results['content_only_urls']) - 10} more")
        
        if results['sitemap_only_urls']:
            print(f"\n📋 SITEMAP-ONLY URLs (not in content check):")
            for i, url in enumerate(results['sitemap_only_urls'][:10], 1):  # Show first 10
                print(f"  {i}. {url}")
            if len(results['sitemap_only_urls']) > 10:
                print(f"  ... and {len(results['sitemap_only_urls']) - 10} more")
        
        # Check if the "new_content" pages from our force check are in sitemap
        print(f"\n🔍 ANALYZING 'NEW_CONTENT' PAGES:")
        new_content_urls = [
            "https://www.judiciary.uk/speech-by-the-master-of-the-rolls-london-international-dispute-week-2022/",
            "https://www.judiciary.uk/sharing-best-practice-in-the-commercial-courts-at-the-3rd-full-meeting-of-sifocc/",
            "https://www.judiciary.uk/new-memorandum-published-detailing-the-response-of-the-worlds-commercial-courts-to-covid-19/",
            "https://www.judiciary.uk/news-and-updates/",
            "https://www.judiciary.uk/speech-by-the-lord-chief-justice-opening-of-the-newcastle-civil-family-courts-and-tribunals-centre/",
            "https://www.judiciary.uk/lord-chief-justice-officially-opens-civil-and-family-courts-and-tribunal-centre-in-newcastle/",
            "https://www.judiciary.uk/speech-by-mr-justice-foxton-grays-inn-and-city-of-london-law-society-joint-annual-lecture/",
            "https://www.judiciary.uk/health-education-and-social-chamber-president-and-chief-medical-member-to-speak-at-the-international-congress-of-the-royal-college-of-psychiatrists/",
            "https://www.judiciary.uk/announcement-vice-president-of-the-court-of-appeal-criminal-division/",
            "https://www.judiciary.uk/commonwealth-commercial-courts-establishing-the-new-normal/"
        ]
        
        if results['site_id'] == 'judiciary_uk':
            for url in new_content_urls:
                in_sitemap = url in results['sitemap_urls']
                in_content = url in results['content_urls']
                status = "✅ Both" if in_sitemap and in_content else "📋 Sitemap only" if in_sitemap else "📄 Content only" if in_content else "❌ Neither"
                print(f"  {url}")
                print(f"    Status: {status}")

async def main():
    """Main function to run overlap checks."""
    print("🔍 SITEMAP-CONTENT OVERLAP ANALYSIS")
    print("=" * 50)
    print("This script will check if content-detected pages are actually in the sitemap.")
    
    checker = SitemapContentChecker()
    
    # Check both sites
    sites = ['judiciary_uk', 'waverley_gov']
    
    for site_id in sites:
        results = await checker.check_overlap(site_id)
        checker.print_results(results)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"sitemap_content_overlap_{site_id}_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Results saved to: {filename}")
        print("-" * 50)

if __name__ == "__main__":
    asyncio.run(main()) 