#!/usr/bin/env python3
"""Check baseline file structure and identify issues."""

import json
import sys
from pathlib import Path

def check_baseline_structure():
    """Check baseline file structure."""
    print("🔍 CHECKING BASELINE STRUCTURE")
    print("=" * 50)
    
    baseline_dir = Path("baselines")
    if not baseline_dir.exists():
        print("❌ Baselines directory not found")
        return
    
    baseline_files = list(baseline_dir.glob("*_baseline.json"))
    print(f"📁 Found {len(baseline_files)} baseline files")
    
    for baseline_file in baseline_files:
        print(f"\n📄 Analyzing: {baseline_file.name}")
        
        try:
            # Get file size
            file_size = baseline_file.stat().st_size
            file_size_mb = file_size / (1024 * 1024)
            print(f"   Size: {file_size_mb:.2f} MB")
            
            # Try to load the file
            with open(baseline_file, 'r', encoding='utf-8') as f:
                data = f.read()
                print(f"   Raw data length: {len(data)} characters")
                
                # Try to parse JSON
                baseline = json.loads(data)
                print(f"   ✅ JSON parsed successfully")
                
                # Check structure
                print(f"   Site ID: {baseline.get('site_id', 'MISSING')}")
                print(f"   Site Name: {baseline.get('site_name', 'MISSING')}")
                print(f"   Date: {baseline.get('baseline_date', 'MISSING')}")
                
                # Check content state
                content_state = baseline.get('content_state', {})
                print(f"   Content state keys: {list(content_state.keys())}")
                
                if 'content_hashes' in content_state:
                    content_hashes = content_state['content_hashes']
                    if isinstance(content_hashes, dict):
                        print(f"   Content hashes count: {len(content_hashes)}")
                    else:
                        print(f"   ⚠️ Content hashes is not a dict: {type(content_hashes)}")
                
                # Check sitemap state
                sitemap_state = baseline.get('sitemap_state', {})
                print(f"   Sitemap state keys: {list(sitemap_state.keys())}")
                
                if 'urls' in sitemap_state:
                    urls = sitemap_state['urls']
                    if isinstance(urls, list):
                        print(f"   Sitemap URLs count: {len(urls)}")
                    else:
                        print(f"   ⚠️ URLs is not a list: {type(urls)}")
                
                # Check summary
                summary = baseline.get('summary', {})
                print(f"   Summary: {summary}")
                
        except json.JSONDecodeError as e:
            print(f"   ❌ JSON decode error: {e}")
            print(f"   Error position: line {e.lineno}, column {e.colno}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            print(f"   Error type: {type(e)}")

if __name__ == "__main__":
    check_baseline_structure() 