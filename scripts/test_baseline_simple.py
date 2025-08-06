#!/usr/bin/env python3
"""
Simple baseline test script.
"""

import os
import sys
import json
from pathlib import Path

# Add the app directory to the path
app_path = str(Path(__file__).parent.parent / "app")
sys.path.insert(0, app_path)

def test_baseline_events():
    """Test baseline event logging."""
    print("🔧 Testing baseline event logging...")
    
    # Check if baseline events file exists
    events_file = Path("baselines/baseline_events.json")
    if events_file.exists():
        print(f"✅ Baseline events file exists: {events_file}")
        
        # Read and display recent events
        try:
            with open(events_file, 'r') as f:
                events = json.load(f)
            
            print(f"📊 Found {len(events)} baseline events")
            
            # Show recent events
            recent_events = events[-5:] if len(events) > 5 else events
            for event in recent_events:
                print(f"   - {event.get('timestamp', 'N/A')}: {event.get('event_type', 'N/A')} for {event.get('site_id', 'N/A')}")
                
        except Exception as e:
            print(f"❌ Error reading events file: {e}")
    else:
        print(f"⚠️ No baseline events file found: {events_file}")
        print("   This is normal if no baselines have been updated yet")

def test_baseline_files():
    """Test baseline file structure."""
    print("\n🔧 Testing baseline file structure...")
    
    baselines_dir = Path("baselines")
    if baselines_dir.exists():
        print(f"✅ Baselines directory exists: {baselines_dir}")
        
        # List baseline files
        baseline_files = list(baselines_dir.glob("*.json"))
        print(f"📊 Found {len(baseline_files)} baseline files")
        
        for file in baseline_files[:5]:  # Show first 5
            print(f"   - {file.name}")
            
        if len(baseline_files) > 5:
            print(f"   ... and {len(baseline_files) - 5} more")
    else:
        print(f"⚠️ No baselines directory found: {baselines_dir}")

def main():
    """Main test function."""
    print("🚀 Starting simple baseline test...")
    
    test_baseline_events()
    test_baseline_files()
    
    print("\n📊 Test Results:")
    print("   Baseline Events: ✅ CHECKED")
    print("   Baseline Files: ✅ CHECKED")
    
    print("\n💡 To test baseline updates:")
    print("1. Run your change detection system")
    print("2. Check for new baseline events in baselines/baseline_events.json")
    print("3. Verify new baseline files are created in baselines/")

if __name__ == "__main__":
    main() 