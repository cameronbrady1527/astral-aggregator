#!/usr/bin/env python3
"""
Test Content Hashes Script
==========================

This script tests the content hash fetching functionality for initial baselines.
"""

import asyncio
import sys
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.crawler.change_detector import ChangeDetector
from app.utils.config import ConfigManager

async def test_content_hashes():
    """Test content hash fetching for initial baselines."""
    
    print("🧪 Testing Content Hash Fetching for Initial Baselines")
    print("=" * 60)
    
    try:
        # Create change detector
        change_detector = ChangeDetector()
        
        # Get Waverley site config
        config_manager = change_detector.config_manager
        waverley_config = config_manager.get_site("waverley_gov")
        
        if not waverley_config:
            print("❌ Waverley site not found in configuration")
            return
        
        print(f"📋 Testing site: {waverley_config.name}")
        print(f"🔗 URL: {waverley_config.url}")
        print(f"🗺️ Sitemap: {waverley_config.sitemap_url}")
        print(f"🔍 Methods: {waverley_config.detection_methods}")
        print()
        
        # Clear any existing baseline for this test
        baseline_manager = change_detector.baseline_manager
        existing_baseline = baseline_manager.get_latest_baseline(waverley_config.name)
        
        if existing_baseline:
            print(f"⚠️ Found existing baseline, will test with current system")
        else:
            print(f"✅ No existing baseline found, will create initial baseline")
        
        print("\n🚀 Running detection for Waverley site...")
        
        # Run detection
        result = await change_detector.detect_changes_for_site("waverley_gov")
        
        print("\n📊 Detection Results:")
        print(f"   Site: {result['site_name']}")
        print(f"   Detection Time: {result['detection_time']}")
        print(f"   Methods Used: {list(result['methods'].keys())}")
        
        # Check baseline creation
        if result.get('baseline_updated'):
            print(f"   ✅ Baseline Updated: {result.get('baseline_file')}")
            
            # Get the new baseline
            new_baseline = baseline_manager.get_latest_baseline(waverley_config.name)
            if new_baseline:
                print(f"   📊 Total URLs: {new_baseline.get('total_urls', 0)}")
                print(f"   🔗 Content Hashes: {new_baseline.get('total_content_hashes', 0)}")
                
                # Check if content hashes were actually fetched
                content_hashes = new_baseline.get('content_hashes', {})
                if content_hashes:
                    print(f"   ✅ Content hashes fetched successfully!")
                    print(f"   📝 Sample hashes:")
                    for i, (url, hash_data) in enumerate(list(content_hashes.items())[:3]):
                        print(f"      {i+1}. {url[:50]}... -> {hash_data.get('hash', 'N/A')[:20]}...")
                else:
                    print(f"   ❌ No content hashes found in baseline")
            else:
                print(f"   ❌ Could not retrieve new baseline")
        else:
            print(f"   ℹ️ No baseline update needed")
        
        # Check baseline events
        events = baseline_manager.get_baseline_events(waverley_config.name, limit=5)
        print(f"\n📋 Baseline Events ({len(events)}):")
        for event in events:
            print(f"   📅 {event['timestamp']} - {event['event_type']} - {event['site_id']}")
            details = event['details']
            if 'total_content_hashes' in details:
                print(f"      Content Hashes: {details['total_content_hashes']}")
        
        print("\n✅ Test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_content_hashes()) 