#!/usr/bin/env python3
"""
Test baseline update functionality for the aggregator.
"""

import asyncio
import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add the app directory to the path
app_path = str(Path(__file__).parent.parent / "app")
sys.path.insert(0, app_path)

# Import after adding to path
from crawler.change_detector import ChangeDetector
from utils.baseline_manager import BaselineManager

async def test_baseline_update():
    """Test baseline update functionality."""
    print("🔧 Testing baseline update functionality...")
    
    try:
        # Initialize change detector
        detector = ChangeDetector()
        baseline_manager = BaselineManager()
        
        # Get list of sites
        sites = detector.list_sites()
        if not sites:
            print("❌ No sites configured")
            return False
        
        print(f"✅ Found {len(sites)} configured sites")
        
        # Test with the first active site
        active_sites = [site for site in sites if site.get('is_active', True)]
        if not active_sites:
            print("❌ No active sites found")
            return False
        
        test_site = active_sites[0]
        site_id = test_site['site_id']
        site_name = test_site['name']
        
        print(f"🔄 Testing with site: {site_name} ({site_id})")
        
        # Get current baseline
        current_baseline = baseline_manager.get_latest_baseline(site_name)
        if current_baseline:
            print(f"✅ Found existing baseline: {current_baseline.get('baseline_date')}")
            print(f"   URLs: {current_baseline.get('total_urls', 0)}")
            print(f"   Content hashes: {len(current_baseline.get('content_hashes', {}))}")
        else:
            print("ℹ️ No existing baseline found - will create initial baseline")
        
        # Get baseline events
        events = baseline_manager.get_baseline_events(site_name, limit=5)
        if events:
            print(f"📊 Recent baseline events: {len(events)}")
            for event in events[-3:]:  # Show last 3 events
                event_type = event.get('event_type', 'unknown')
                timestamp = event.get('timestamp', 'unknown')
                print(f"   {event_type}: {timestamp}")
        else:
            print("ℹ️ No baseline events found")
        
        # Test change detection (this will trigger baseline update if changes are found)
        print(f"🔄 Running change detection for {site_name}...")
        
        # Get site configuration
        site_config = detector.config_manager.get_site(site_id)
        if not site_config:
            print(f"❌ Site configuration not found for {site_id}")
            return False
        
        # Run detection for the first method
        if site_config.detection_methods:
            method = site_config.detection_methods[0]
            print(f"🔄 Testing method: {method}")
            
            try:
                result = await detector._run_detection_method(site_config, method)
                
                print(f"✅ Detection completed")
                print(f"   Changes found: {len(result.get('changes', []))}")
                print(f"   Baseline updated: {result.get('baseline_updated', False)}")
                
                if result.get('baseline_updated'):
                    baseline_file = result.get('baseline_file')
                    print(f"   New baseline file: {baseline_file}")
                    
                    # Check if the new baseline was actually created
                    if baseline_file and Path(baseline_file).exists():
                        print("✅ New baseline file created successfully")
                        
                        # Load and verify the new baseline
                        with open(baseline_file, 'r') as f:
                            new_baseline = json.load(f)
                        
                        print(f"   New baseline info:")
                        print(f"     Date: {new_baseline.get('baseline_date')}")
                        print(f"     URLs: {new_baseline.get('total_urls', 0)}")
                        print(f"     Content hashes: {len(new_baseline.get('content_hashes', {}))}")
                        
                        # Check for evolution info
                        evolution = new_baseline.get('baseline_evolution', {})
                        if evolution:
                            print(f"     Evolution type: {evolution.get('evolution_type')}")
                            print(f"     Changes applied: {evolution.get('changes_applied', 0)}")
                        
                        return True
                    else:
                        print("❌ New baseline file not found")
                        return False
                else:
                    print("ℹ️ No changes detected - baseline not updated")
                    return True
                    
            except Exception as e:
                print(f"❌ Error during detection: {e}")
                return False
        else:
            print("❌ No detection methods configured")
            return False
            
    except Exception as e:
        print(f"❌ Error testing baseline update: {e}")
        return False

async def test_baseline_events():
    """Test baseline event logging."""
    print("\n🔄 Testing baseline event logging...")
    
    try:
        baseline_manager = BaselineManager()
        
        # Get all sites
        sites = baseline_manager.list_baselines()
        if not sites:
            print("ℹ️ No sites with baselines found")
            return True
        
        print(f"✅ Found {len(sites)} sites with baselines")
        
        # Test event retrieval for each site
        for site_id in list(sites.keys())[:3]:  # Test first 3 sites
            events = baseline_manager.get_baseline_events(site_id, limit=5)
            print(f"📊 {site_id}: {len(events)} recent events")
            
            for event in events[-2:]:  # Show last 2 events
                event_type = event.get('event_type', 'unknown')
                timestamp = event.get('timestamp', 'unknown')
                details = event.get('details', {})
                
                if event_type == 'baseline_updated':
                    changes = details.get('changes_applied', 0)
                    print(f"   {event_type}: {changes} changes at {timestamp}")
                elif event_type == 'baseline_created':
                    urls = details.get('total_urls', 0)
                    print(f"   {event_type}: {urls} URLs at {timestamp}")
                else:
                    print(f"   {event_type}: {timestamp}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing baseline events: {e}")
        return False

async def main():
    """Main test function."""
    print("🚀 Starting baseline update test...")
    
    # Test baseline update functionality
    baseline_ok = await test_baseline_update()
    
    # Test baseline events
    events_ok = await test_baseline_events()
    
    print("\n📊 Test Results:")
    print(f"   Baseline Update: {'✅ PASS' if baseline_ok else '❌ FAIL'}")
    print(f"   Baseline Events: {'✅ PASS' if events_ok else '❌ FAIL'}")
    
    if baseline_ok and events_ok:
        print("\n✅ All baseline functionality tests passed!")
        print("   Baseline updates should now work correctly when changes are detected.")
    else:
        print("\n🔧 Issues found with baseline functionality.")
        print("   Check the logs above for specific errors.")

if __name__ == "__main__":
    asyncio.run(main()) 