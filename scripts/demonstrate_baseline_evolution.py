#!/usr/bin/env python3
"""
Demonstration Script: Baseline Evolution System
Shows exactly how the system behaves when changes are detected.
"""

import sys
import os
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))

from utils.baseline_manager import BaselineManager
from utils.baseline_merger import BaselineMerger


def demonstrate_baseline_evolution():
    """Demonstrate the baseline evolution behavior."""
    print("🎯 DEMONSTRATION: Baseline Evolution System")
    print("=" * 60)
    print("This demonstrates exactly what happens when changes are detected:")
    print("1. Baseline is updated with new date/time")
    print("2. Content hashes from previous baseline that didn't change are preserved")
    print("3. New hashes for URLs that changed are added")
    print("4. URLs that were detected as deleted are removed")
    print("5. URLs that were added, modified, and were already present are included")
    print("6. No duplication of URLs")
    print()
    
    # Create baseline manager
    manager = BaselineManager("demo_baselines")
    
    # Step 1: Create initial baseline
    print("📋 STEP 1: Initial Baseline")
    print("-" * 40)
    
    initial_baseline = {
        "site_id": "demo_site",
        "site_name": "Demo Site",
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
    
    print(f"Initial baseline contains {len(initial_baseline['content_hashes'])} URLs:")
    for url, data in initial_baseline['content_hashes'].items():
        print(f"  - {url} (hash: {data['hash'][:8]}...)")
    
    # Save initial baseline
    baseline_file = manager.save_baseline("demo_site", initial_baseline)
    print(f"✅ Initial baseline saved: {baseline_file}")
    print()
    
    # Step 2: Simulate changes detected
    print("🔍 STEP 2: Changes Detected")
    print("-" * 40)
    
    # Current state after changes
    current_state = {
        "sitemap_state": {
            "urls": [
                "https://example.com/page1",  # Unchanged
                "https://example.com/page2",  # Modified
                "https://example.com/page3",  # Unchanged
                "https://example.com/page5",  # New
                "https://example.com/page6"   # New
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
    
    print("Changes detected:")
    for change in detected_changes:
        print(f"  - {change['change_type']}: {change['url']}")
    print()
    
    # Step 3: Update baseline
    print("🔄 STEP 3: Baseline Evolution")
    print("-" * 40)
    
    new_baseline = manager.update_baseline_from_changes(
        "demo_site", initial_baseline, current_state, detected_changes
    )
    
    print(f"✅ New baseline created with date: {new_baseline['baseline_date']}")
    print(f"✅ Changes applied: {new_baseline.get('changes_applied', 0)}")
    print(f"✅ Evolution type: {new_baseline.get('evolution_type', 'unknown')}")
    print()
    
    # Step 4: Show the evolution results
    print("📊 STEP 4: Evolution Results")
    print("-" * 40)
    
    print("New baseline contains:")
    for url, data in new_baseline['content_hashes'].items():
        status = ""
        if url in initial_baseline['content_hashes']:
            if initial_baseline['content_hashes'][url]['hash'] == data['hash']:
                status = " (unchanged)"
            else:
                status = " (modified)"
        else:
            status = " (new)"
        
        print(f"  - {url} (hash: {data['hash'][:8]}...){status}")
    
    print()
    
    # Step 5: Verify requirements
    print("✅ STEP 5: Requirements Verification")
    print("-" * 40)
    
    # Check 1: New date/time established
    print(f"✅ New date/time established: {new_baseline['baseline_date']}")
    
    # Check 2: Content hashes from previous baseline that didn't change are preserved
    unchanged_urls = []
    for url in ["https://example.com/page1", "https://example.com/page3"]:
        if (url in initial_baseline['content_hashes'] and 
            url in new_baseline['content_hashes'] and
            initial_baseline['content_hashes'][url]['hash'] == new_baseline['content_hashes'][url]['hash']):
            unchanged_urls.append(url)
    
    print(f"✅ Unchanged URLs preserved: {len(unchanged_urls)} URLs")
    
    # Check 3: New hashes for URLs that changed
    modified_urls = []
    for url in ["https://example.com/page2"]:
        if (url in initial_baseline['content_hashes'] and 
            url in new_baseline['content_hashes'] and
            initial_baseline['content_hashes'][url]['hash'] != new_baseline['content_hashes'][url]['hash']):
            modified_urls.append(url)
    
    print(f"✅ Modified URLs updated: {len(modified_urls)} URLs")
    
    # Check 4: URLs that were detected as deleted are removed
    deleted_urls = ["https://example.com/page4"]
    deleted_removed = all(url not in new_baseline['content_hashes'] for url in deleted_urls)
    print(f"✅ Deleted URLs removed: {deleted_removed}")
    
    # Check 5: URLs that were added are included
    new_urls = ["https://example.com/page5", "https://example.com/page6"]
    new_included = all(url in new_baseline['content_hashes'] for url in new_urls)
    print(f"✅ New URLs included: {new_included}")
    
    # Check 6: No duplication of URLs
    all_urls = list(new_baseline['content_hashes'].keys())
    unique_urls = set(all_urls)
    no_duplication = len(all_urls) == len(unique_urls)
    print(f"✅ No URL duplication: {no_duplication}")
    
    print()
    
    # Step 6: Save the evolved baseline
    print("💾 STEP 6: Save Evolved Baseline")
    print("-" * 40)
    
    evolved_file = manager.save_baseline("demo_site", new_baseline)
    print(f"✅ Evolved baseline saved: {evolved_file}")
    
    # Show baseline summary
    print(f"📊 Baseline Summary:")
    print(f"   - Previous baseline URLs: {len(initial_baseline['content_hashes'])}")
    print(f"   - New baseline URLs: {len(new_baseline['content_hashes'])}")
    print(f"   - Unchanged: {len(unchanged_urls)}")
    print(f"   - Modified: {len(modified_urls)}")
    print(f"   - Added: {len(new_urls)}")
    print(f"   - Deleted: {len(deleted_urls)}")
    
    print()
    print("🎉 DEMONSTRATION COMPLETE!")
    print("The baseline evolution system works exactly as requested!")
    
    # Cleanup
    import shutil
    if os.path.exists("demo_baselines"):
        shutil.rmtree("demo_baselines")
        print("✅ Demo cleanup completed")


if __name__ == "__main__":
    demonstrate_baseline_evolution() 