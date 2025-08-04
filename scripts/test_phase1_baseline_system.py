#!/usr/bin/env python3
"""
Test Script for Phase 1: Baseline Management and Merger System
Tests the BaselineManager and BaselineMerger classes to ensure they work correctly.
"""

import sys
import os
import json
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))

from utils.baseline_manager import BaselineManager
from utils.baseline_merger import BaselineMerger


def create_test_data():
    """Create test data for baseline testing."""
    
    # Previous baseline data
    previous_baseline = {
        "site_id": "test_site",
        "site_name": "Test Site",
        "baseline_date": "20241201",
        "created_at": "2024-12-01T10:00:00",
        "sitemap_state": {
            "urls": [
                "https://example.com/page1",
                "https://example.com/page2", 
                "https://example.com/page3",
                "https://example.com/page4"
            ]
        },
        "content_hashes": {
            "https://example.com/page1": {"hash": "abc123", "content_length": 1000},
            "https://example.com/page2": {"hash": "def456", "content_length": 1500},
            "https://example.com/page3": {"hash": "ghi789", "content_length": 2000},
            "https://example.com/page4": {"hash": "jkl012", "content_length": 1200}
        },
        "total_urls": 4,
        "total_content_hashes": 4
    }
    
    # Current state data
    current_state = {
        "sitemap_state": {
            "urls": [
                "https://example.com/page1",
                "https://example.com/page2",
                "https://example.com/page3",
                "https://example.com/page5",  # New page
                "https://example.com/page6"   # New page
            ]
        },
        "content_hashes": {
            "https://example.com/page1": {"hash": "abc123", "content_length": 1000},  # Unchanged
            "https://example.com/page2": {"hash": "def999", "content_length": 1600},  # Modified
            "https://example.com/page3": {"hash": "ghi789", "content_length": 2000},  # Unchanged
            "https://example.com/page5": {"hash": "mno345", "content_length": 800},   # New
            "https://example.com/page6": {"hash": "pqr678", "content_length": 1100}   # New
        }
    }
    
    # Detected changes
    detected_changes = [
        {
            "url": "https://example.com/page4",
            "change_type": "deleted",
            "title": "Removed page: https://example.com/page4"
        },
        {
            "url": "https://example.com/page2", 
            "change_type": "modified",
            "title": "Content modified: https://example.com/page2"
        },
        {
            "url": "https://example.com/page5",
            "change_type": "new",
            "title": "New page: https://example.com/page5"
        },
        {
            "url": "https://example.com/page6",
            "change_type": "new", 
            "title": "New page: https://example.com/page6"
        }
    ]
    
    return previous_baseline, current_state, detected_changes


def test_baseline_merger():
    """Test the BaselineMerger class."""
    print("🧪 Testing BaselineMerger...")
    
    previous_baseline, current_state, detected_changes = create_test_data()
    
    merger = BaselineMerger()
    
    # Test merging
    new_baseline = merger.merge_baselines(previous_baseline, current_state, detected_changes)
    
    print(f"✅ Merge completed successfully")
    print(f"   Previous baseline URLs: {len(previous_baseline['content_hashes'])}")
    print(f"   New baseline URLs: {len(new_baseline['content_hashes'])}")
    print(f"   Changes applied: {new_baseline.get('changes_applied', 0)}")
    
    # Verify the merge logic
    expected_urls = {
        "https://example.com/page1",  # Unchanged
        "https://example.com/page2",  # Modified
        "https://example.com/page3",  # Unchanged
        "https://example.com/page5",  # New
        "https://example.com/page6"   # New
    }
    
    actual_urls = set(new_baseline['content_hashes'].keys())
    
    if expected_urls == actual_urls:
        print("✅ URL filtering correct - deleted URLs removed, new URLs added")
    else:
        print("❌ URL filtering incorrect")
        print(f"   Expected: {expected_urls}")
        print(f"   Actual: {actual_urls}")
        return False
    
    # Verify hash updates
    if new_baseline['content_hashes']["https://example.com/page2"]["hash"] == "def999":
        print("✅ Modified URL hash updated correctly")
    else:
        print("❌ Modified URL hash not updated")
        return False
    
    # Verify unchanged URLs kept same hash
    if new_baseline['content_hashes']["https://example.com/page1"]["hash"] == "abc123":
        print("✅ Unchanged URL hash preserved correctly")
    else:
        print("❌ Unchanged URL hash modified incorrectly")
        return False
    
    # Test validation
    validation_result = merger.validate_merge_result(previous_baseline, new_baseline, detected_changes)
    if validation_result["is_valid"]:
        print("✅ Merge validation passed")
    else:
        print("❌ Merge validation failed:")
        for error in validation_result["errors"]:
            print(f"   - {error}")
        return False
    
    return True


def test_baseline_manager():
    """Test the BaselineManager class."""
    print("\n🧪 Testing BaselineManager...")
    
    # Create temporary baseline directory
    test_baseline_dir = "test_baselines"
    manager = BaselineManager(test_baseline_dir)
    
    previous_baseline, current_state, detected_changes = create_test_data()
    
    # Test saving baseline
    try:
        baseline_file = manager.save_baseline("test_site", previous_baseline)
        print(f"✅ Baseline saved: {baseline_file}")
    except Exception as e:
        print(f"❌ Failed to save baseline: {e}")
        return False
    
    # Test loading baseline
    loaded_baseline = manager.get_latest_baseline("test_site")
    if loaded_baseline and loaded_baseline["site_id"] == "test_site":
        print("✅ Baseline loaded correctly")
    else:
        print("❌ Failed to load baseline")
        return False
    
    # Test baseline update
    try:
        new_baseline = manager.update_baseline_from_changes(
            "test_site", previous_baseline, current_state, detected_changes
        )
        print("✅ Baseline update completed")
        
        # Add a small delay to ensure different timestamps
        import time
        time.sleep(1)
        
        # Save the updated baseline
        updated_file = manager.save_baseline("test_site", new_baseline)
        print(f"✅ Updated baseline saved: {updated_file}")
        
    except Exception as e:
        print(f"❌ Failed to update baseline: {e}")
        return False
    
    # Test baseline validation
    validation_result = manager.validate_baseline(new_baseline)
    if validation_result["is_valid"]:
        print("✅ Baseline validation passed")
    else:
        print("❌ Baseline validation failed:")
        for error in validation_result["errors"]:
            print(f"   - {error}")
        return False
    
    # Test listing baselines
    baselines = manager.list_baselines("test_site")
    if "test_site" in baselines and len(baselines["test_site"]) >= 1:
        print(f"✅ Baseline listing works: {len(baselines['test_site'])} baselines found")
    else:
        print("❌ Baseline listing failed")
        print(f"   Available baselines: {baselines}")
        return False
    
    # Cleanup
    import shutil
    import time
    try:
        if os.path.exists(test_baseline_dir):
            # Give files a moment to be released
            time.sleep(0.1)
            shutil.rmtree(test_baseline_dir)
            print("✅ Test cleanup completed")
    except Exception as e:
        print(f"⚠️  Cleanup warning: {e}")
        # Try to remove individual files
        try:
            for file in os.listdir(test_baseline_dir):
                os.remove(os.path.join(test_baseline_dir, file))
            os.rmdir(test_baseline_dir)
            print("✅ Test cleanup completed (alternative method)")
        except:
            print("⚠️  Could not clean up test directory - manual cleanup may be needed")
    
    return True


def test_initial_baseline_creation():
    """Test initial baseline creation."""
    print("\n🧪 Testing Initial Baseline Creation...")
    
    merger = BaselineMerger()
    current_state = {
        "sitemap_state": {
            "urls": ["https://example.com/page1", "https://example.com/page2"]
        },
        "content_hashes": {
            "https://example.com/page1": {"hash": "abc123", "content_length": 1000},
            "https://example.com/page2": {"hash": "def456", "content_length": 1500}
        }
    }
    
    initial_baseline = merger.create_initial_baseline("test_site", "Test Site", current_state)
    
    if (initial_baseline["site_id"] == "test_site" and 
        initial_baseline["evolution_type"] == "initial_creation" and
        len(initial_baseline["content_hashes"]) == 2):
        print("✅ Initial baseline creation successful")
        return True
    else:
        print("❌ Initial baseline creation failed")
        return False


def main():
    """Run all tests."""
    print("🚀 Starting Phase 1 Baseline System Tests")
    print("=" * 50)
    
    tests = [
        ("BaselineMerger", test_baseline_merger),
        ("BaselineManager", test_baseline_manager),
        ("Initial Baseline Creation", test_initial_baseline_creation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} test...")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} test PASSED")
            else:
                print(f"❌ {test_name} test FAILED")
        except Exception as e:
            print(f"❌ {test_name} test ERROR: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Phase 1 tests passed! Baseline system is ready.")
        return 0
    else:
        print("⚠️  Some tests failed. Please review the implementation.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 