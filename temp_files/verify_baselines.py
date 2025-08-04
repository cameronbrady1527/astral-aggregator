#!/usr/bin/env python3
"""Verify baseline files are valid and contain expected data."""

import json
from pathlib import Path

def verify_baselines():
    """Verify baseline files."""
    print("🔍 VERIFYING BASELINE FILES")
    print("=" * 50)
    
    baseline_dir = Path("baselines")
    if not baseline_dir.exists():
        print("❌ Baselines directory not found")
        return False
    
    baseline_files = list(baseline_dir.glob("*_baseline.json"))
    print(f"📁 Found {len(baseline_files)} baseline files")
    
    all_valid = True
    
    for baseline_file in baseline_files:
        print(f"\n📄 Checking: {baseline_file.name}")
        
        try:
            # Check file size
            file_size = baseline_file.stat().st_size
            file_size_mb = file_size / (1024 * 1024)
            print(f"   Size: {file_size_mb:.2f} MB")
            
            # Try to load JSON
            with open(baseline_file, 'r', encoding='utf-8') as f:
                baseline = json.load(f)
            
            # Verify required fields
            required_fields = ['site_id', 'site_name', 'baseline_date', 'content_state', 'sitemap_state', 'summary']
            missing_fields = [field for field in required_fields if field not in baseline]
            
            if missing_fields:
                print(f"   ❌ Missing required fields: {missing_fields}")
                all_valid = False
            else:
                print(f"   ✅ Valid JSON structure")
                print(f"   Site: {baseline['site_name']}")
                print(f"   Date: {baseline['baseline_date']}")
                print(f"   Total pages: {baseline['summary']['total_pages']}")
                print(f"   Sitemap URLs: {baseline['summary']['sitemap_urls']}")
                print(f"   Content hashes: {baseline['summary']['content_hashes']}")
                
                # Check if content state has the expected structure
                content_state = baseline['content_state']
                if 'content_hashes' in content_state and isinstance(content_state['content_hashes'], dict):
                    print(f"   Content hashes count: {len(content_state['content_hashes'])}")
                else:
                    print(f"   ⚠️ Content state structure may be incomplete")
                
                # Check if sitemap state has the expected structure
                sitemap_state = baseline['sitemap_state']
                if 'urls' in sitemap_state and isinstance(sitemap_state['urls'], list):
                    print(f"   Sitemap URLs count: {len(sitemap_state['urls'])}")
                else:
                    print(f"   ⚠️ Sitemap state structure may be incomplete")
            
        except json.JSONDecodeError as e:
            print(f"   ❌ Invalid JSON: {e}")
            all_valid = False
        except Exception as e:
            print(f"   ❌ Error reading file: {e}")
            all_valid = False
    
    print(f"\n{'✅' if all_valid else '❌'} BASELINE VERIFICATION {'PASSED' if all_valid else 'FAILED'}")
    return all_valid

if __name__ == "__main__":
    verify_baselines() 