#!/usr/bin/env python3
"""
Fix Baseline Script - Create a proper baseline for change detection
This script fixes corrupted baseline files and creates a fresh baseline.
"""

import asyncio
import json
import sys
import os
from pathlib import Path
from datetime import datetime

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))

from crawler.sitemap_detector import SitemapDetector


class MockSiteConfig:
    """Mock site configuration for testing."""
    def __init__(self):
        self.name = "Judiciary UK"
        self.url = "https://www.judiciary.uk/"
        self.sitemap_url = "https://www.judiciary.uk/sitemap_index.xml"
        self.verify_deleted_urls = True
        self.max_concurrent_checks = 5
        self.verification_timeout = 10


async def fix_baseline(site_id: str = "judiciary_uk"):
    """Fix the baseline for a given site."""
    print(f"🔧 Fixing baseline for {site_id}...")
    
    # Initialize detector
    site_config = MockSiteConfig()
    detector = SitemapDetector(site_config)
    
    # Get current state
    print("📋 Fetching current sitemap state...")
    current_state = await detector.get_current_state()
    
    if not current_state.get('urls'):
        print("❌ Failed to fetch current state")
        return False
    
    print(f"✅ Current sitemap has {len(current_state['urls'])} URLs")
    
    # Create baseline filename
    baseline_dir = Path("baselines")
    baseline_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d")
    baseline_file = baseline_dir / f"{site_id}_{timestamp}_baseline.json"
    
    # Save baseline
    print(f"💾 Saving baseline to {baseline_file}...")
    
    baseline_data = {
        "site_id": site_id,
        "site_name": site_config.name,
        "baseline_date": timestamp,
        "captured_at": datetime.now().isoformat(),
        **current_state
    }
    
    with open(baseline_file, 'w', encoding='utf-8') as f:
        json.dump(baseline_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Baseline saved successfully!")
    print(f"📊 Baseline contains {len(current_state['urls'])} URLs")
    
    # Verify the baseline
    print("🔍 Verifying baseline...")
    with open(baseline_file, 'r', encoding='utf-8') as f:
        saved_data = json.load(f)
    
    if len(saved_data.get('urls', [])) == len(current_state['urls']):
        print("✅ Baseline verification successful!")
        return True
    else:
        print("❌ Baseline verification failed!")
        return False


async def analyze_baseline(baseline_file: str):
    """Analyze an existing baseline file."""
    print(f"📊 Analyzing baseline: {baseline_file}")
    
    try:
        with open(baseline_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        urls = data.get('urls', [])
        print(f"📋 Baseline contains {len(urls)} URLs")
        print(f"📅 Created: {data.get('captured_at', 'Unknown')}")
        print(f"🏷️  Site: {data.get('site_name', 'Unknown')}")
        
        if urls:
            print(f"📝 Sample URLs:")
            for url in urls[:5]:
                print(f"   - {url}")
        else:
            print("⚠️  Baseline is empty (corrupted)")
            
    except Exception as e:
        print(f"❌ Error analyzing baseline: {e}")


async def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python fix_baseline.py <command> [options]")
        print("Commands:")
        print("  fix <site_id>     - Fix baseline for a site")
        print("  analyze <file>    - Analyze an existing baseline")
        print("Examples:")
        print("  python fix_baseline.py fix judiciary_uk")
        print("  python fix_baseline.py analyze baselines/judiciary_uk_20250804_baseline.json")
        return 1
    
    command = sys.argv[1]
    
    if command == "fix":
        site_id = sys.argv[2] if len(sys.argv) > 2 else "judiciary_uk"
        success = await fix_baseline(site_id)
        return 0 if success else 1
        
    elif command == "analyze":
        if len(sys.argv) < 3:
            print("❌ Please provide a baseline file to analyze")
            return 1
        
        baseline_file = sys.argv[2]
        await analyze_baseline(baseline_file)
        return 0
        
    else:
        print(f"❌ Unknown command: {command}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 