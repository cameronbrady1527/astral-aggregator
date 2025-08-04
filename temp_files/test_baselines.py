#!/usr/bin/env python3
"""Simple test to check baseline files."""

import json
from pathlib import Path

def test_baselines():
    """Test baseline files."""
    print("🔍 Testing baseline files...")
    
    baseline_dir = Path("baselines")
    if not baseline_dir.exists():
        print("❌ Baselines directory not found")
        return
    
    baseline_files = list(baseline_dir.glob("*_baseline.json"))
    print(f"📁 Found {len(baseline_files)} baseline files:")
    
    total_size = 0
    for baseline_file in baseline_files:
        file_size = baseline_file.stat().st_size
        file_size_mb = file_size / (1024 * 1024)
        total_size += file_size
        
        print(f"  📄 {baseline_file.name}: {file_size_mb:.2f} MB")
        
        # Try to load the baseline
        try:
            with open(baseline_file, 'r', encoding='utf-8') as f:
                baseline = json.load(f)
            
            print(f"    Site: {baseline.get('site_name', 'Unknown')}")
            print(f"    Date: {baseline.get('baseline_date', 'Unknown')}")
            print(f"    Pages: {baseline.get('summary', {}).get('total_pages', 0)}")
            
        except Exception as e:
            print(f"    ❌ Error loading: {e}")
    
    total_size_mb = total_size / (1024 * 1024)
    print(f"\n💾 Total size: {total_size_mb:.2f} MB")

if __name__ == "__main__":
    test_baselines() 