#!/usr/bin/env python3
"""
Baseline Management Script
Manages baseline retention, cleanup, and provides baseline information.
"""

import sys
import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.utils.config import ConfigManager

class BaselineManager:
    """Manages baseline files and retention policies."""
    
    def __init__(self):
        self.config = ConfigManager()
        self.baseline_dir = Path("baselines")
        self.baseline_dir.mkdir(exist_ok=True)
    
    def list_baselines(self, site_id: str = None) -> Dict[str, List[str]]:
        """List all available baselines."""
        baselines = {}
        
        for baseline_file in self.baseline_dir.glob("*_baseline.json"):
            filename = baseline_file.name
            parts = filename.replace("_baseline.json", "").split("_")
            
            if len(parts) >= 2:
                file_site_id = parts[0]
                date = parts[1]
                
                if site_id is None or file_site_id == site_id:
                    if file_site_id not in baselines:
                        baselines[file_site_id] = []
                    baselines[file_site_id].append(date)
        
        # Sort dates for each site
        for site in baselines:
            baselines[site].sort()
        
        return baselines
    
    def get_baseline_info(self, site_id: str, date: str) -> Dict[str, Any]:
        """Get information about a specific baseline."""
        baseline_path = self.baseline_dir / f"{site_id}_{date}_baseline.json"
        
        if not baseline_path.exists():
            return {"error": f"Baseline not found: {baseline_path}"}
        
        try:
            with open(baseline_path, 'r', encoding='utf-8') as f:
                baseline = json.load(f)
            
            file_size = baseline_path.stat().st_size
            file_size_mb = file_size / (1024 * 1024)
            
            return {
                "site_id": site_id,
                "date": date,
                "file_path": str(baseline_path),
                "file_size_mb": round(file_size_mb, 2),
                "baseline_info": baseline
            }
        except Exception as e:
            return {"error": f"Error reading baseline: {e}"}
    
    def cleanup_old_baselines(self, days_to_keep: int = 30) -> Dict[str, Any]:
        """Clean up baselines older than specified days."""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        cutoff_date_str = cutoff_date.strftime("%Y%m%d")
        
        deleted_files = []
        total_size_freed = 0
        
        for baseline_file in self.baseline_dir.glob("*_baseline.json"):
            filename = baseline_file.name
            parts = filename.replace("_baseline.json", "").split("_")
            
            if len(parts) >= 2:
                date_str = parts[1]
                
                try:
                    file_date = datetime.strptime(date_str, "%Y%m%d")
                    if file_date < cutoff_date:
                        file_size = baseline_file.stat().st_size
                        baseline_file.unlink()
                        deleted_files.append(filename)
                        total_size_freed += file_size
                except ValueError:
                    # Skip files with invalid date format
                    continue
        
        return {
            "deleted_files": deleted_files,
            "total_files_deleted": len(deleted_files),
            "total_size_freed_mb": round(total_size_freed / (1024 * 1024), 2),
            "cutoff_date": cutoff_date_str
        }
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics for baselines."""
        total_files = 0
        total_size = 0
        site_stats = {}
        
        for baseline_file in self.baseline_dir.glob("*_baseline.json"):
            filename = baseline_file.name
            parts = filename.replace("_baseline.json", "").split("_")
            
            if len(parts) >= 2:
                site_id = parts[0]
                file_size = baseline_file.stat().st_size
                
                total_files += 1
                total_size += file_size
                
                if site_id not in site_stats:
                    site_stats[site_id] = {"count": 0, "size": 0}
                
                site_stats[site_id]["count"] += 1
                site_stats[site_id]["size"] += file_size
        
        # Convert to MB and add to stats
        for site in site_stats:
            site_stats[site]["size_mb"] = round(site_stats[site]["size"] / (1024 * 1024), 2)
        
        return {
            "total_files": total_files,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "site_stats": site_stats
        }
    
    def print_baseline_list(self, baselines: Dict[str, List[str]]):
        """Print baseline list in a formatted way."""
        print("\n📊 AVAILABLE BASELINES")
        print("=" * 50)
        
        if not baselines:
            print("No baselines found.")
            return
        
        for site_id, dates in baselines.items():
            print(f"\n🔍 {site_id.upper()}:")
            print(f"   Total baselines: {len(dates)}")
            print(f"   Date range: {dates[0]} to {dates[-1]}")
            print(f"   Recent baselines:")
            for date in dates[-5:]:  # Show last 5
                print(f"     - {date}")
    
    def print_storage_stats(self, stats: Dict[str, Any]):
        """Print storage statistics."""
        print("\n💾 STORAGE STATISTICS")
        print("=" * 50)
        print(f"Total files: {stats['total_files']}")
        print(f"Total size: {stats['total_size_mb']} MB")
        
        if stats['site_stats']:
            print("\nPer-site breakdown:")
            for site_id, site_stat in stats['site_stats'].items():
                print(f"  {site_id}: {site_stat['count']} files, {site_stat['size_mb']} MB")

def main():
    """Main function for baseline management."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Manage baseline files")
    parser.add_argument("--list", action="store_true", help="List all baselines")
    parser.add_argument("--site", type=str, help="Filter by site ID")
    parser.add_argument("--info", type=str, help="Get info for specific baseline (format: site_id_YYYYMMDD)")
    parser.add_argument("--cleanup", type=int, metavar="DAYS", help="Clean up baselines older than DAYS")
    parser.add_argument("--stats", action="store_true", help="Show storage statistics")
    
    args = parser.parse_args()
    
    manager = BaselineManager()
    
    if args.list:
        baselines = manager.list_baselines(args.site)
        manager.print_baseline_list(baselines)
    
    elif args.info:
        if "_" not in args.info:
            print("Error: Please specify baseline in format: site_id_YYYYMMDD")
            return
        
        site_id, date = args.info.split("_", 1)
        info = manager.get_baseline_info(site_id, date)
        
        if "error" in info:
            print(f"❌ {info['error']}")
        else:
            print(f"\n📊 BASELINE INFO: {args.info}")
            print("=" * 50)
            print(f"File: {info['file_path']}")
            print(f"Size: {info['file_size_mb']} MB")
            print(f"Site: {info['baseline_info']['site_name']}")
            print(f"Date: {info['baseline_info']['baseline_date']}")
            print(f"Total pages: {info['baseline_info']['summary']['total_pages']}")
    
    elif args.cleanup is not None:
        print(f"🧹 Cleaning up baselines older than {args.cleanup} days...")
        result = manager.cleanup_old_baselines(args.cleanup)
        
        print(f"Deleted {result['total_files_deleted']} files")
        print(f"Freed {result['total_size_freed_mb']} MB")
        print(f"Cutoff date: {result['cutoff_date']}")
        
        if result['deleted_files']:
            print("\nDeleted files:")
            for filename in result['deleted_files'][:10]:  # Show first 10
                print(f"  - {filename}")
            if len(result['deleted_files']) > 10:
                print(f"  ... and {len(result['deleted_files']) - 10} more")
    
    elif args.stats:
        stats = manager.get_storage_stats()
        manager.print_storage_stats(stats)
    
    else:
        # Default: show stats and list
        print("📊 BASELINE MANAGEMENT")
        print("=" * 50)
        
        stats = manager.get_storage_stats()
        manager.print_storage_stats(stats)
        
        baselines = manager.list_baselines()
        manager.print_baseline_list(baselines)
        
        print("\n💡 Usage:")
        print("  python scripts/manage_baselines.py --list")
        print("  python scripts/manage_baselines.py --info judiciary_uk_20250804")
        print("  python scripts/manage_baselines.py --cleanup 30")
        print("  python scripts/manage_baselines.py --stats")

if __name__ == "__main__":
    main() 