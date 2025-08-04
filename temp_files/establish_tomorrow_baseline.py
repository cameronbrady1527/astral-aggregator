#!/usr/bin/env python3
"""
Establish Tomorrow's Baseline
This script creates a baseline for tomorrow's date to ensure proper daily comparison.
"""

import asyncio
import sys
import os
import json
from datetime import datetime, timedelta
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scripts.daily_baseline_system import DailyBaselineSystem

async def establish_tomorrow_baseline():
    """Establish baseline for tomorrow's date."""
    print("📊 ESTABLISHING TOMORROW'S BASELINE")
    print("=" * 50)
    
    system = DailyBaselineSystem()
    
    # Get tomorrow's date
    tomorrow = datetime.now() + timedelta(days=1)
    tomorrow_date = tomorrow.strftime("%Y%m%d")
    
    print(f"📅 Creating baseline for: {tomorrow_date}")
    
    sites = ['judiciary_uk', 'waverley_gov']
    
    for site_id in sites:
        print(f"\n🔍 Processing {site_id}...")
        
        try:
            # Get site configuration
            site_config = system.config.get_site(site_id)
            if not site_config:
                print(f"❌ Site {site_id} not found in configuration")
                continue
            
            # Create baseline path for tomorrow
            baseline_path = system.get_baseline_path(site_id, tomorrow_date)
            
            if baseline_path.exists():
                print(f"⚠️ Baseline already exists for {tomorrow_date}")
                continue
            
            # Create content detector and get comprehensive state
            print(f"📄 Fetching comprehensive content state for {site_config.name}...")
            from app.crawler.content_detector import ContentDetector
            content_detector = ContentDetector(site_config)
            content_state = await content_detector.get_current_state()
            
            # Create sitemap detector and get sitemap state
            print(f"📋 Fetching sitemap state for {site_config.name}...")
            from app.crawler.sitemap_detector import SitemapDetector
            sitemap_detector = SitemapDetector(site_config)
            sitemap_state = await sitemap_detector.get_current_state()
            
            # Create comprehensive baseline
            baseline = {
                "site_id": site_id,
                "site_name": site_config.name,
                "baseline_date": tomorrow_date,
                "timestamp": datetime.now().isoformat(),
                "content_state": content_state,
                "sitemap_state": sitemap_state,
                "summary": {
                    "total_pages": content_state.get("total_pages", 0),
                    "sitemap_urls": len(sitemap_state.get("urls", [])),
                    "content_hashes": len(content_state.get("content_hashes", {}))
                }
            }
            
            # Save baseline
            with open(baseline_path, 'w', encoding='utf-8') as f:
                json.dump(baseline, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Tomorrow's baseline saved to: {baseline_path}")
            print(f"📊 Summary: {baseline['summary']}")
            
        except Exception as e:
            print(f"❌ Error processing {site_id}: {e}")
    
    print(f"\n✅ Tomorrow's baseline establishment completed")

if __name__ == "__main__":
    asyncio.run(establish_tomorrow_baseline()) 