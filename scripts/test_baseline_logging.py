#!/usr/bin/env python3
"""
Test Baseline Logging - Demonstrate the new baseline logging functionality
This script tests the enhanced logging and dashboard integration for baseline events.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))

from utils.baseline_manager import BaselineManager
from utils.baseline_merger import BaselineMerger


class MockSiteConfig:
    """Mock site configuration for testing."""
    def __init__(self):
        self.name = "Test Site"
        self.url = "https://test.example.com/"
        self.sitemap_url = "https://test.example.com/sitemap.xml"


async def test_baseline_logging():
    """Test the baseline logging functionality."""
    print("🧪 Testing Baseline Logging Functionality")
    print("=" * 60)
    
    # Initialize baseline manager
    manager = BaselineManager("test_baselines")
    
    # Test 1: Create initial baseline
    print("\n📋 Test 1: Creating Initial Baseline")
    print("-" * 40)
    
    initial_baseline = {
        "site_id": "test_site",
        "site_name": "Test Site",
        "baseline_date": "20241201",
        "created_at": "2024-12-01T10:00:00",
        "evolution_type": "initial_creation",
        "total_urls": 5,
        "total_content_hashes": 5,
        "sitemap_state": {
            "urls": [
                "https://test.example.com/page1",
                "https://test.example.com/page2",
                "https://test.example.com/page3",
                "https://test.example.com/page4",
                "https://test.example.com/page5"
            ]
        },
        "content_hashes": {
            "https://test.example.com/page1": {"hash": "abc123", "content_length": 100},
            "https://test.example.com/page2": {"hash": "def456", "content_length": 150},
            "https://test.example.com/page3": {"hash": "ghi789", "content_length": 200},
            "https://test.example.com/page4": {"hash": "jkl012", "content_length": 120},
            "https://test.example.com/page5": {"hash": "mno345", "content_length": 180}
        }
    }
    
    try:
        baseline_file = manager.save_baseline("test_site", initial_baseline)
        print(f"✅ Initial baseline created: {baseline_file}")
    except Exception as e:
        print(f"❌ Failed to create initial baseline: {e}")
        return
    
    # Test 2: Update baseline with changes
    print("\n🔄 Test 2: Updating Baseline with Changes")
    print("-" * 40)
    
    current_state = {
        "sitemap_state": {
            "urls": [
                "https://test.example.com/page1",
                "https://test.example.com/page2",
                "https://test.example.com/page3",
                "https://test.example.com/page6",  # New page
                "https://test.example.com/page7"   # New page
            ]
        },
        "content_hashes": {
            "https://test.example.com/page1": {"hash": "abc123", "content_length": 100},  # Unchanged
            "https://test.example.com/page2": {"hash": "def999", "content_length": 250},  # Modified
            "https://test.example.com/page3": {"hash": "ghi789", "content_length": 200},  # Unchanged
            "https://test.example.com/page6": {"hash": "pqr678", "content_length": 300},  # New
            "https://test.example.com/page7": {"hash": "stu901", "content_length": 350}   # New
        }
    }
    
    detected_changes = [
        {
            "url": "https://test.example.com/page2",
            "change_type": "content_changed",
            "title": "Content modified: https://test.example.com/page2"
        },
        {
            "url": "https://test.example.com/page4",
            "change_type": "deleted",
            "title": "Removed page: https://test.example.com/page4"
        },
        {
            "url": "https://test.example.com/page5",
            "change_type": "deleted",
            "title": "Removed page: https://test.example.com/page5"
        },
        {
            "url": "https://test.example.com/page6",
            "change_type": "new",
            "title": "New page: https://test.example.com/page6"
        },
        {
            "url": "https://test.example.com/page7",
            "change_type": "new",
            "title": "New page: https://test.example.com/page7"
        }
    ]
    
    try:
        new_baseline = manager.update_baseline_from_changes(
            "test_site", initial_baseline, current_state, detected_changes
        )
        
        updated_baseline_file = manager.save_baseline("test_site", new_baseline)
        print(f"✅ Baseline updated: {updated_baseline_file}")
        
        # Test validation
        merger = BaselineMerger()
        validation_result = merger.validate_merge_result(
            initial_baseline, new_baseline, detected_changes
        )
        
        manager._log_baseline_event("baseline_validation", "test_site", {
            "is_valid": validation_result["is_valid"],
            "errors": validation_result.get("errors", []),
            "warnings": validation_result.get("warnings", []),
            "baseline_file": updated_baseline_file
        })
        
    except Exception as e:
        print(f"❌ Failed to update baseline: {e}")
        return
    
    # Test 3: Simulate baseline error
    print("\n❌ Test 3: Simulating Baseline Error")
    print("-" * 40)
    
    manager._log_baseline_event("baseline_error", "test_site", {
        "error": "Simulated error for testing purposes",
        "operation": "test_error_simulation"
    })
    
    # Test 4: Display baseline events
    print("\n📊 Test 4: Displaying Baseline Events")
    print("-" * 40)
    
    events = manager.get_baseline_events("test_site", limit=10)
    
    if events:
        print(f"Found {len(events)} baseline events:")
        for i, event in enumerate(events, 1):
            print(f"\n{i}. {event['event_type'].upper()} - {event['site_id']}")
            print(f"   Time: {event['timestamp']}")
            print(f"   Details: {event['details']}")
    else:
        print("No baseline events found")
    
    # Test 5: Dashboard API simulation
    print("\n🌐 Test 5: Dashboard API Simulation")
    print("-" * 40)
    
    # Simulate what the dashboard would receive
    dashboard_data = {
        "status": "success",
        "baseline_events": events,
        "total_events": len(events),
        "site_id": "test_site",
        "limit": 10
    }
    
    print("Dashboard API Response:")
    print(f"Status: {dashboard_data['status']}")
    print(f"Total Events: {dashboard_data['total_events']}")
    print(f"Site ID: {dashboard_data['site_id']}")
    
    print("\n🎉 Baseline Logging Test Completed Successfully!")
    print("\n💡 What you should see:")
    print("   ✅ Terminal logs with emoji indicators")
    print("   ✅ Structured event data for dashboard")
    print("   ✅ Different event types (created, updated, error, validation)")
    print("   ✅ Detailed information for each event")
    
    print("\n🚀 Next Steps:")
    print("   1. Check the terminal output for formatted logs")
    print("   2. Visit the dashboard to see baseline events")
    print("   3. Trigger a real detection to see live logging")
    print("   4. Monitor baseline evolution in real-time")


if __name__ == "__main__":
    # Clean up test directory
    test_dir = Path("test_baselines")
    if test_dir.exists():
        import shutil
        shutil.rmtree(test_dir)
    
    # Run the test
    asyncio.run(test_baseline_logging())
    
    # Clean up after test
    if test_dir.exists():
        import shutil
        shutil.rmtree(test_dir)
        print(f"\n🧹 Cleaned up test directory: {test_dir}") 