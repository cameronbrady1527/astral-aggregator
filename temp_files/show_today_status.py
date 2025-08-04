#!/usr/bin/env python3
"""
Show Today's Baseline Status
Displays current baseline information and comparison results.
"""

import json
from pathlib import Path
from datetime import datetime

def show_today_status():
    """Show today's baseline status."""
    print("📊 TODAY'S BASELINE STATUS")
    print("=" * 50)
    
    # Get today's date
    today = datetime.now().strftime("%Y%m%d")
    print(f"📅 Date: {today}")
    
    # Check baselines
    baseline_dir = Path("baselines")
    if baseline_dir.exists():
        baseline_files = list(baseline_dir.glob(f"*_{today}_baseline.json"))
        print(f"\n📁 Baselines found: {len(baseline_files)}")
        
        for baseline_file in baseline_files:
            try:
                with open(baseline_file, 'r', encoding='utf-8') as f:
                    baseline = json.load(f)
                
                site_name = baseline.get('site_name', 'Unknown')
                total_pages = baseline.get('summary', {}).get('total_pages', 0)
                sitemap_urls = baseline.get('summary', {}).get('sitemap_urls', 0)
                content_hashes = baseline.get('summary', {}).get('content_hashes', 0)
                
                print(f"\n🔍 {site_name}:")
                print(f"   📄 Total pages: {total_pages}")
                print(f"   📋 Sitemap URLs: {sitemap_urls}")
                print(f"   🔍 Content hashes: {content_hashes}")
                
            except Exception as e:
                print(f"❌ Error reading {baseline_file}: {e}")
    
    # Check comparison results
    comparison_dir = Path("comparison_results")
    if comparison_dir.exists():
        comparison_files = list(comparison_dir.glob(f"daily_comparison_*_{today}_*.json"))
        print(f"\n🔄 Comparison results found: {len(comparison_files)}")
        
        for comparison_file in comparison_files:
            try:
                with open(comparison_file, 'r', encoding='utf-8') as f:
                    comparison = json.load(f)
                
                site_name = comparison.get('site_name', 'Unknown')
                message = comparison.get('message', 'No message')
                total_changes = comparison.get('summary', {}).get('total_changes', 0)
                new_pages = comparison.get('summary', {}).get('new_pages', 0)
                modified_pages = comparison.get('summary', {}).get('modified_pages', 0)
                
                print(f"\n🔄 {site_name} Comparison:")
                print(f"   💬 Status: {message}")
                print(f"   🔄 Total changes: {total_changes}")
                print(f"   🆕 New pages: {new_pages}")
                print(f"   ✏️ Modified pages: {modified_pages}")
                
            except Exception as e:
                print(f"❌ Error reading {comparison_file}: {e}")
    
    print(f"\n✅ Today's baseline status check completed")

if __name__ == "__main__":
    show_today_status() 