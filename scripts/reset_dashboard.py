#!/usr/bin/env python3
"""
Reset Dashboard Script
=====================

This script resets the dashboard to starting values by:
1. Deleting all baseline files
2. Clearing baseline events
3. Resetting the system to a clean state

Usage:
    python scripts/reset_dashboard.py
"""

import os
import shutil
import json
from pathlib import Path
from datetime import datetime

def reset_dashboard():
    """Reset the dashboard to starting values."""
    
    print("🔄 Resetting Dashboard to Starting Values...")
    print("=" * 50)
    
    # Get the project root directory
    project_root = Path(__file__).parent.parent
    baselines_dir = project_root / "baselines"
    output_dir = project_root / "output"
    cache_dir = project_root / "cache"
    
    # 1. Delete all baseline files
    print("\n🗑️  Deleting baseline files...")
    if baselines_dir.exists():
        baseline_files = list(baselines_dir.glob("*_baseline.json"))
        baseline_events_file = baselines_dir / "baseline_events.json"
        
        deleted_count = 0
        for baseline_file in baseline_files:
            try:
                baseline_file.unlink()
                deleted_count += 1
                print(f"   ✅ Deleted: {baseline_file.name}")
            except Exception as e:
                print(f"   ❌ Error deleting {baseline_file.name}: {e}")
        
        # Delete baseline events file
        if baseline_events_file.exists():
            try:
                baseline_events_file.unlink()
                print(f"   ✅ Deleted: baseline_events.json")
            except Exception as e:
                print(f"   ❌ Error deleting baseline_events.json: {e}")
        
        print(f"   📊 Total baseline files deleted: {deleted_count}")
    else:
        print("   ℹ️  No baselines directory found")
    
    # 2. Clear output directories (optional - uncomment if you want to clear all output)
    print("\n🗂️  Clearing output directories...")
    if output_dir.exists():
        output_subdirs = [d for d in output_dir.iterdir() if d.is_dir()]
        cleared_count = 0
        for subdir in output_subdirs:
            try:
                shutil.rmtree(subdir)
                cleared_count += 1
                print(f"   ✅ Cleared: {subdir.name}")
            except Exception as e:
                print(f"   ❌ Error clearing {subdir.name}: {e}")
        print(f"   📊 Total output directories cleared: {cleared_count}")
    else:
        print("   ℹ️  No output directory found")
    
    # 3. Clear cache (optional)
    print("\n🧹 Clearing cache...")
    if cache_dir.exists():
        cache_subdirs = [d for d in cache_dir.iterdir() if d.is_dir()]
        cleared_count = 0
        for subdir in cache_subdirs:
            try:
                shutil.rmtree(subdir)
                cleared_count += 1
                print(f"   ✅ Cleared cache: {subdir.name}")
            except Exception as e:
                print(f"   ❌ Error clearing cache {subdir.name}: {e}")
        print(f"   📊 Total cache directories cleared: {cleared_count}")
    else:
        print("   ℹ️  No cache directory found")
    
    # 4. Create fresh baseline events file with empty structure
    print("\n📝 Creating fresh baseline events file...")
    if baselines_dir.exists():
        baseline_events_file = baselines_dir / "baseline_events.json"
        empty_events = []
        try:
            with open(baseline_events_file, 'w', encoding='utf-8') as f:
                json.dump(empty_events, f, indent=2, ensure_ascii=False)
            print("   ✅ Created fresh baseline_events.json")
        except Exception as e:
            print(f"   ❌ Error creating baseline_events.json: {e}")
    
    # 5. Create a reset marker file
    reset_marker = project_root / "RESET_MARKER.txt"
    try:
        with open(reset_marker, 'w', encoding='utf-8') as f:
            f.write(f"Dashboard reset completed at: {datetime.now().isoformat()}\n")
            f.write("All baseline files and output data have been cleared.\n")
            f.write("The system is now in a clean starting state.\n")
        print(f"   ✅ Created reset marker: {reset_marker.name}")
    except Exception as e:
        print(f"   ❌ Error creating reset marker: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Dashboard Reset Complete!")
    print("\n📋 Summary:")
    print("   • All baseline files deleted")
    print("   • Output directories cleared")
    print("   • Cache cleared")
    print("   • Fresh baseline events file created")
    print("   • Reset marker file created")
    print("\n🚀 The system is now ready to start fresh!")
    print("   You can now run the application and see how it builds up from nothing.")
    print("\n💡 Next steps:")
    print("   1. Start the application: python -m app.main")
    print("   2. Visit the dashboard: http://localhost:8000/dashboard")
    print("   3. Trigger site detection to see the system in action")

if __name__ == "__main__":
    reset_dashboard() 