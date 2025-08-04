#!/usr/bin/env python3
"""
Daily Baseline System for Comprehensive Change Detection
This system establishes daily baselines and provides proper change comparison.
"""

import asyncio
import sys
import os
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.crawler.content_detector import ContentDetector
from app.crawler.sitemap_detector import SitemapDetector
from app.utils.config import ConfigManager

class DailyBaselineSystem:
    """Daily baseline system for comprehensive change detection."""
    
    def __init__(self):
        self.config = ConfigManager()
        self.baseline_dir = Path("baselines")
        self.baseline_dir.mkdir(exist_ok=True)
    
    def get_baseline_path(self, site_id: str, date: str) -> Path:
        """Get the path for a specific site's baseline on a specific date."""
        return self.baseline_dir / f"{site_id}_{date}_baseline.json"
    
    def get_latest_baseline_path(self, site_id: str) -> Optional[Path]:
        """Get the path to the latest baseline for a site."""
        pattern = f"{site_id}_*_baseline.json"
        baseline_files = list(self.baseline_dir.glob(pattern))
        
        if not baseline_files:
            return None
        
        # Sort by modification time and get the latest
        latest_file = max(baseline_files, key=lambda f: f.stat().st_mtime)
        return latest_file
    
    def get_previous_baseline_path(self, site_id: str, current_date: str) -> Optional[Path]:
        """Get the path to the previous day's baseline."""
        current_dt = datetime.strptime(current_date, "%Y%m%d")
        previous_dt = current_dt - timedelta(days=1)
        previous_date = previous_dt.strftime("%Y%m%d")
        
        previous_path = self.get_baseline_path(site_id, previous_date)
        return previous_path if previous_path.exists() else None
    
    async def establish_daily_baseline(self, site_id: str) -> Dict[str, Any]:
        """Establish a comprehensive baseline for a site."""
        print(f"\n📊 Establishing daily baseline for {site_id}...")
        
        try:
            # Get site configuration
            site_config = self.config.get_site(site_id)
            if not site_config:
                return {"error": f"Site {site_id} not found in configuration"}
            
            # Get current date
            current_date = datetime.now().strftime("%Y%m%d")
            baseline_path = self.get_baseline_path(site_id, current_date)
            
            # Check if baseline already exists for today
            if baseline_path.exists():
                print(f"⚠️ Baseline already exists for {current_date}, loading existing...")
                with open(baseline_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            # Create content detector and get comprehensive state
            print(f"📄 Fetching comprehensive content state for {site_config.name}...")
            content_detector = ContentDetector(site_config)
            start_time = time.time()
            content_state = await content_detector.get_current_state()
            content_duration = time.time() - start_time
            
            # Create sitemap detector and get sitemap state
            print(f"📋 Fetching sitemap state for {site_config.name}...")
            sitemap_detector = SitemapDetector(site_config)
            start_time = time.time()
            sitemap_state = await sitemap_detector.get_current_state()
            sitemap_duration = time.time() - start_time
            
            # Create comprehensive baseline
            baseline = {
                "site_id": site_id,
                "site_name": site_config.name,
                "baseline_date": current_date,
                "timestamp": datetime.now().isoformat(),
                "content_state": content_state,
                "sitemap_state": sitemap_state,
                "performance": {
                    "content_duration": content_duration,
                    "sitemap_duration": sitemap_duration,
                    "total_duration": content_duration + sitemap_duration
                },
                "summary": {
                    "total_pages": content_state.get("total_pages", 0),
                    "sitemap_urls": len(sitemap_state.get("urls", [])),
                    "content_hashes": len(content_state.get("content_hashes", {}))
                }
            }
            
            # Save baseline
            with open(baseline_path, 'w', encoding='utf-8') as f:
                json.dump(baseline, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Baseline saved to: {baseline_path}")
            return baseline
            
        except Exception as e:
            return {
                "site_id": site_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def compare_with_previous_baseline(self, site_id: str) -> Dict[str, Any]:
        """Compare current baseline with previous day's baseline."""
        print(f"\n🔄 Comparing {site_id} with previous baseline...")
        
        try:
            # Get current date and baseline
            current_date = datetime.now().strftime("%Y%m%d")
            current_baseline_path = self.get_baseline_path(site_id, current_date)
            
            if not current_baseline_path.exists():
                return {"error": f"No current baseline found for {current_date}"}
            
            # Load current baseline
            with open(current_baseline_path, 'r', encoding='utf-8') as f:
                current_baseline = json.load(f)
            
            # Get previous baseline
            previous_baseline_path = self.get_previous_baseline_path(site_id, current_date)
            
            if not previous_baseline_path:
                return {
                    "site_id": site_id,
                    "message": "No previous baseline found - this is the first baseline",
                    "current_baseline": current_baseline,
                    "changes": [],
                    "summary": {
                        "total_changes": 0,
                        "new_pages": 0,
                        "modified_pages": 0,
                        "deleted_pages": 0
                    }
                }
            
            # Load previous baseline
            with open(previous_baseline_path, 'r', encoding='utf-8') as f:
                previous_baseline = json.load(f)
            
            # Compare content states
            current_content_hashes = current_baseline["content_state"].get("content_hashes", {})
            previous_content_hashes = previous_baseline["content_state"].get("content_hashes", {})
            
            # Find changes
            changes = []
            new_pages = 0
            modified_pages = 0
            deleted_pages = 0
            
            # Find new pages
            new_urls = set(current_content_hashes.keys()) - set(previous_content_hashes.keys())
            for url in new_urls:
                changes.append({
                    "change_type": "new_page",
                    "url": url,
                    "title": f"New page: {url}",
                    "description": "Page not present in previous baseline"
                })
                new_pages += 1
            
            # Find modified pages
            for url, current_hash in current_content_hashes.items():
                if url in previous_content_hashes:
                    previous_hash = previous_content_hashes[url]
                    if current_hash != previous_hash:
                        changes.append({
                            "change_type": "content_modified",
                            "url": url,
                            "title": f"Content modified: {url}",
                            "description": f"Content hash changed from {previous_hash[:8]} to {current_hash[:8]}"
                        })
                        modified_pages += 1
            
            # Find deleted pages
            deleted_urls = set(previous_content_hashes.keys()) - set(current_content_hashes.keys())
            for url in deleted_urls:
                changes.append({
                    "change_type": "page_deleted",
                    "url": url,
                    "title": f"Page deleted: {url}",
                    "description": "Page present in previous baseline but not in current"
                })
                deleted_pages += 1
            
            # Compare sitemap changes
            current_sitemap_urls = set(current_baseline["sitemap_state"].get("urls", []))
            previous_sitemap_urls = set(previous_baseline["sitemap_state"].get("urls", []))
            
            new_sitemap_urls = current_sitemap_urls - previous_sitemap_urls
            deleted_sitemap_urls = previous_sitemap_urls - current_sitemap_urls
            
            for url in new_sitemap_urls:
                changes.append({
                    "change_type": "sitemap_new",
                    "url": url,
                    "title": f"New in sitemap: {url}",
                    "description": "URL added to sitemap"
                })
            
            for url in deleted_sitemap_urls:
                changes.append({
                    "change_type": "sitemap_deleted",
                    "url": url,
                    "title": f"Removed from sitemap: {url}",
                    "description": "URL removed from sitemap"
                })
            
            comparison_result = {
                "site_id": site_id,
                "site_name": current_baseline["site_name"],
                "comparison_date": current_date,
                "previous_baseline_date": previous_baseline["baseline_date"],
                "timestamp": datetime.now().isoformat(),
                "current_baseline": current_baseline,
                "previous_baseline": previous_baseline,
                "changes": changes,
                "summary": {
                    "total_changes": len(changes),
                    "new_pages": new_pages,
                    "modified_pages": modified_pages,
                    "deleted_pages": deleted_pages,
                    "new_sitemap_urls": len(new_sitemap_urls),
                    "deleted_sitemap_urls": len(deleted_sitemap_urls)
                }
            }
            
            return comparison_result
            
        except Exception as e:
            return {
                "site_id": site_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def print_baseline_info(self, baseline: Dict[str, Any]):
        """Print baseline information."""
        if "error" in baseline:
            print(f"❌ Error: {baseline['error']}")
            return
        
        print(f"\n📊 BASELINE INFO FOR {baseline['site_name'].upper()}")
        print("=" * 60)
        print(f"📅 Date: {baseline['baseline_date']}")
        print(f"⏰ Timestamp: {baseline['timestamp']}")
        print(f"📄 Total pages: {baseline['summary']['total_pages']}")
        print(f"📋 Sitemap URLs: {baseline['summary']['sitemap_urls']}")
        print(f"🔍 Content hashes: {baseline['summary']['content_hashes']}")
        print(f"⏱️  Content duration: {baseline['performance']['content_duration']:.2f}s")
        print(f"⏱️  Sitemap duration: {baseline['performance']['sitemap_duration']:.2f}s")
        print(f"⏱️  Total duration: {baseline['performance']['total_duration']:.2f}s")
    
    def print_comparison_results(self, comparison: Dict[str, Any]):
        """Print comparison results."""
        if "error" in comparison:
            print(f"❌ Error: {comparison['error']}")
            return
        
        if "message" in comparison:
            print(f"💡 {comparison['message']}")
            return
        
        print(f"\n🔄 COMPARISON RESULTS FOR {comparison['site_name'].upper()}")
        print("=" * 60)
        print(f"📅 Current date: {comparison['comparison_date']}")
        print(f"📅 Previous baseline: {comparison['previous_baseline_date']}")
        print(f"🔄 Total changes: {comparison['summary']['total_changes']}")
        print(f"🆕 New pages: {comparison['summary']['new_pages']}")
        print(f"✏️ Modified pages: {comparison['summary']['modified_pages']}")
        print(f"🗑️ Deleted pages: {comparison['summary']['deleted_pages']}")
        print(f"📋 New sitemap URLs: {comparison['summary']['new_sitemap_urls']}")
        print(f"📋 Deleted sitemap URLs: {comparison['summary']['deleted_sitemap_urls']}")
        
        if comparison['changes']:
            print(f"\n📝 DETAILED CHANGES:")
            for i, change in enumerate(comparison['changes'][:20], 1):  # Show first 20
                print(f"  {i}. {change['change_type']}: {change['url']}")
                if change.get('description'):
                    print(f"     {change['description']}")
            
            if len(comparison['changes']) > 20:
                print(f"  ... and {len(comparison['changes']) - 20} more changes")
        else:
            print(f"\n✅ No changes detected")

async def main():
    """Main function to run daily baseline system."""
    print("📊 DAILY BASELINE SYSTEM")
    print("=" * 50)
    print("This system establishes daily baselines and compares changes.")
    
    system = DailyBaselineSystem()
    
    # Check both sites
    sites = ['judiciary_uk', 'waverley_gov']
    
    for site_id in sites:
        # Establish baseline
        baseline = await system.establish_daily_baseline(site_id)
        system.print_baseline_info(baseline)
        
        # Compare with previous baseline
        comparison = await system.compare_with_previous_baseline(site_id)
        system.print_comparison_results(comparison)
        
        # Save comparison results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        comparison_filename = f"daily_comparison_{site_id}_{timestamp}.json"
        
        with open(comparison_filename, 'w', encoding='utf-8') as f:
            json.dump(comparison, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Comparison results saved to: {comparison_filename}")
        print("-" * 50)

if __name__ == "__main__":
    asyncio.run(main()) 