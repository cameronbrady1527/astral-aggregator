#!/usr/bin/env python3
"""
Script to display change detection results in a readable format.
"""

import asyncio
import sys
import os
import json
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.crawler.change_detector import ChangeDetector

def display_changes_from_file(filepath: str):
    """Display changes from a JSON file in a readable format."""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        changes_data = data.get("changes", {})
        methods = changes_data.get("methods", {})
        
        for method_name, method_data in methods.items():
            print(f"\n🔍 {method_name.upper()} DETECTION RESULTS")
            print("=" * 60)
            
            if "error" in method_data:
                print(f"❌ Error: {method_data['error']}")
                continue
            
            summary = method_data.get("summary", {})
            print(f"📊 Summary:")
            print(f"   Total changes: {summary.get('total_changes', 0)}")
            print(f"   New pages: {summary.get('new_pages', 0)}")
            print(f"   Modified pages: {summary.get('modified_pages', 0)}")
            print(f"   Deleted pages: {summary.get('deleted_pages', 0)}")
            
            changes = method_data.get("changes", [])
            if changes:
                print(f"\n📋 Detailed Changes:")
                
                # Group by change type
                new_pages = [c for c in changes if c.get("change_type") == "new"]
                deleted_pages = [c for c in changes if c.get("change_type") == "deleted"]
                modified_pages = [c for c in changes if c.get("change_type") == "modified"]
                
                if new_pages:
                    print(f"\n🆕 NEW PAGES ({len(new_pages)}):")
                    for i, change in enumerate(new_pages[:10], 1):  # Show first 10
                        url = change.get("url", "")
                        print(f"   {i}. {url}")
                    if len(new_pages) > 10:
                        print(f"   ... and {len(new_pages) - 10} more")
                
                if deleted_pages:
                    print(f"\n🗑️  DELETED PAGES ({len(deleted_pages)}):")
                    for i, change in enumerate(deleted_pages[:10], 1):  # Show first 10
                        url = change.get("url", "")
                        print(f"   {i}. {url}")
                    if len(deleted_pages) > 10:
                        print(f"   ... and {len(deleted_pages) - 10} more")
                
                if modified_pages:
                    print(f"\n✏️  MODIFIED PAGES ({len(modified_pages)}):")
                    for i, change in enumerate(modified_pages[:10], 1):  # Show first 10
                        url = change.get("url", "")
                        print(f"   {i}. {url}")
                    if len(modified_pages) > 10:
                        print(f"   ... and {len(modified_pages) - 10} more")
            else:
                print("✅ No changes detected")
            
            # Show metadata
            metadata = method_data.get("metadata", {})
            if metadata:
                print(f"\n📈 Metadata:")
                for key, value in metadata.items():
                    print(f"   {key}: {value}")
    
    except Exception as e:
        print(f"❌ Error reading file: {e}")

def find_latest_change_file(site_name: str):
    """Find the latest change detection file for a site."""
    output_dir = Path("output")
    change_files = []
    
    for run_folder in output_dir.iterdir():
        if run_folder.is_dir():
            pattern = f"{site_name}_*.json"
            files = list(run_folder.glob(pattern))
            # Filter out state files (only want change files)
            change_files.extend([f for f in files if "state_" not in f.name])
    
    if not change_files:
        return None
    
    # Get the most recent file
    latest_file = max(change_files, key=lambda x: x.stat().st_mtime)
    return str(latest_file)

async def run_live_detection(site_id: str):
    """Run live change detection and display results."""
    print(f"🔍 Running live change detection for {site_id}...")
    
    detector = ChangeDetector()
    result = await detector.detect_changes_for_site(site_id)
    
    # Display the results
    site_name = result.get("site_name", site_id)
    print(f"\n📋 RESULTS FOR {site_name.upper()}")
    print("=" * 60)
    
    methods = result.get("methods", {})
    for method_name, method_data in methods.items():
        print(f"\n🔍 {method_name.upper()} DETECTION RESULTS")
        print("-" * 40)
        
        if "error" in method_data:
            print(f"❌ Error: {method_data['error']}")
            continue
        
        summary = method_data.get("summary", {})
        print(f"📊 Summary:")
        print(f"   Total changes: {summary.get('total_changes', 0)}")
        print(f"   New pages: {summary.get('new_pages', 0)}")
        print(f"   Modified pages: {summary.get('modified_pages', 0)}")
        print(f"   Deleted pages: {summary.get('deleted_pages', 0)}")
        
        changes = method_data.get("changes", [])
        if changes:
            print(f"\n📋 Sample Changes (first 5):")
            for i, change in enumerate(changes[:5], 1):
                change_type = change.get("change_type", "unknown")
                url = change.get("url", "")
                print(f"   {i}. [{change_type.upper()}] {url}")
            
            if len(changes) > 5:
                print(f"   ... and {len(changes) - 5} more changes")

def main():
    """Main function to show changes."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python show_changes.py <site_id>                    # Run live detection")
        print("  python show_changes.py <site_id> --latest           # Show latest results from file")
        print("  python show_changes.py <site_id> --file <filepath>  # Show results from specific file")
        print("\nAvailable sites: judiciary_uk, waverley_gov")
        return
    
    site_id = sys.argv[1]
    
    if "--latest" in sys.argv:
        # Show latest results from file
        site_name_map = {
            "judiciary_uk": "Judiciary UK",
            "waverley_gov": "Waverley Borough Council"
        }
        site_name = site_name_map.get(site_id, site_id)
        
        latest_file = find_latest_change_file(site_name)
        if latest_file:
            print(f"📁 Latest change file: {latest_file}")
            display_changes_from_file(latest_file)
        else:
            print(f"❌ No change files found for {site_name}")
    
    elif "--file" in sys.argv:
        # Show results from specific file
        try:
            file_index = sys.argv.index("--file")
            filepath = sys.argv[file_index + 1]
            display_changes_from_file(filepath)
        except (IndexError, ValueError):
            print("❌ Please provide a filepath after --file")
    
    else:
        # Run live detection
        asyncio.run(run_live_detection(site_id))

if __name__ == "__main__":
    main() 