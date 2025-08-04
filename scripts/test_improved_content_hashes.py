#!/usr/bin/env python3
"""
Test Improved Content Hashes Script
==================================

This script tests the improved content hash fetching with better error reporting
and consistent data structure.
"""

import asyncio
import sys
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.crawler.change_detector import ChangeDetector
from app.utils.config import ConfigManager

async def test_improved_content_hashes():
    """Test improved content hash fetching."""
    
    print("🧪 Testing Improved Content Hash Fetching")
    print("=" * 60)
    
    try:
        # Create change detector
        change_detector = ChangeDetector()
        
        # Test with Waverley (smaller site for faster testing)
        site_id = "waverley_gov"
        site_config = change_detector.config_manager.get_site(site_id)
        
        if not site_config:
            print("❌ Waverley site not found in configuration")
            return
        
        print(f"📋 Testing site: {site_config.name}")
        print(f"🔗 URL: {site_config.url}")
        print(f"🗺️ Sitemap: {site_config.sitemap_url}")
        print(f"🔍 Methods: {site_config.detection_methods}")
        
        # Check content detector configuration
        max_pages = getattr(site_config, 'max_content_pages', 10)
        print(f"📄 Max content pages: {max_pages}")
        
        # Clear existing baseline for fresh test
        baseline_manager = change_detector.baseline_manager
        existing_baseline = baseline_manager.get_latest_baseline(site_config.name)
        
        if existing_baseline:
            print(f"⚠️ Found existing baseline, will create new one for testing")
            # Delete the existing baseline file
            import glob
            import os
            baseline_files = glob.glob(f"baselines/{site_config.name}_*_baseline.json")
            for file in baseline_files:
                try:
                    os.remove(file)
                    print(f"   🗑️ Deleted: {file}")
                except Exception as e:
                    print(f"   ❌ Error deleting {file}: {e}")
        
        print("\n🚀 Running detection with improved content hash fetching...")
        
        # Run detection
        result = await change_detector.detect_changes_for_site(site_id)
        
        print("\n📊 Detection Results:")
        print(f"   Site: {result['site_name']}")
        print(f"   Detection Time: {result['detection_time']}")
        print(f"   Methods Used: {list(result['methods'].keys())}")
        
        # Check baseline creation
        if result.get('baseline_updated'):
            print(f"   ✅ Baseline Updated: {result.get('baseline_file')}")
            
            # Get the new baseline
            new_baseline = baseline_manager.get_latest_baseline(site_config.name)
            if new_baseline:
                print(f"   📊 Total URLs: {new_baseline.get('total_urls', 0)}")
                print(f"   🔗 Content Hashes: {new_baseline.get('total_content_hashes', 0)}")
                
                # Check if content hashes were actually fetched with new structure
                content_hashes = new_baseline.get('content_hashes', {})
                if content_hashes:
                    print(f"   ✅ Content hashes fetched successfully!")
                    
                    # Check structure of content hashes
                    sample_hash = next(iter(content_hashes.values()))
                    print(f"   📝 Sample hash structure: {type(sample_hash)}")
                    
                    if isinstance(sample_hash, dict):
                        print(f"   📋 Hash keys: {list(sample_hash.keys())}")
                        print(f"   🔑 Hash value: {sample_hash.get('hash', 'N/A')[:20]}...")
                        print(f"   📅 Fetched at: {sample_hash.get('fetched_at', 'N/A')}")
                        print(f"   ✅ Status: {sample_hash.get('status', 'N/A')}")
                    else:
                        print(f"   ⚠️ Old format detected: {sample_hash[:20]}...")
                    
                    # Count successful vs failed
                    successful = sum(1 for h in content_hashes.values() 
                                   if isinstance(h, dict) and h.get('status') == 'success')
                    print(f"   📈 Successful hashes: {successful}")
                    print(f"   📉 Failed hashes: {len(content_hashes) - successful}")
                else:
                    print(f"   ❌ No content hashes found in baseline")
            else:
                print(f"   ❌ Could not retrieve new baseline")
        else:
            print(f"   ℹ️ No baseline update needed")
        
        # Check baseline events
        events = baseline_manager.get_baseline_events(site_config.name, limit=5)
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
    asyncio.run(test_improved_content_hashes()) 