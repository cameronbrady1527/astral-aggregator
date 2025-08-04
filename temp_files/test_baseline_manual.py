#!/usr/bin/env python3
"""Manual test of baseline system."""

import asyncio
import sys
import os
import json
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.utils.config import ConfigManager

async def test_baseline_manual():
    """Test baseline system manually."""
    print("🔍 MANUAL BASELINE TEST")
    print("=" * 50)
    
    try:
        # Test config loading
        print("1. Testing config loading...")
        config = ConfigManager()
        judiciary = config.get_site('judiciary_uk')
        waverley = config.get_site('waverley_gov')
        
        if judiciary:
            print(f"   ✅ Judiciary config loaded: {judiciary.name}")
            print(f"   max_content_pages: {getattr(judiciary, 'max_content_pages', 'NOT SET')}")
        else:
            print("   ❌ Judiciary config failed")
            
        if waverley:
            print(f"   ✅ Waverley config loaded: {waverley.name}")
            print(f"   max_content_pages: {getattr(waverley, 'max_content_pages', 'NOT SET')}")
        else:
            print("   ❌ Waverley config failed")
        
        # Test baseline directory
        print("\n2. Testing baseline directory...")
        baseline_dir = Path("baselines")
        if baseline_dir.exists():
            print(f"   ✅ Baseline directory exists: {baseline_dir}")
            baseline_files = list(baseline_dir.glob("*_baseline.json"))
            print(f"   Found {len(baseline_files)} baseline files")
            for f in baseline_files:
                size_mb = f.stat().st_size / (1024 * 1024)
                print(f"     - {f.name}: {size_mb:.2f} MB")
        else:
            print("   ❌ Baseline directory not found")
        
        # Test reading a baseline file
        print("\n3. Testing baseline file reading...")
        waverley_baseline = baseline_dir / "waverley_gov_20250804_baseline.json"
        if waverley_baseline.exists():
            try:
                with open(waverley_baseline, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"   ✅ Waverley baseline loaded successfully")
                print(f"   Site: {data.get('site_name', 'Unknown')}")
                print(f"   Date: {data.get('baseline_date', 'Unknown')}")
                print(f"   Total pages: {data.get('summary', {}).get('total_pages', 0)}")
            except Exception as e:
                print(f"   ❌ Error reading Waverley baseline: {e}")
        else:
            print("   ❌ Waverley baseline file not found")
        
        print("\n✅ Manual test completed")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_baseline_manual()) 