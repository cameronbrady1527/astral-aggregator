#!/usr/bin/env python3
"""
Comprehensive content detection script that checks ALL pages.
This script provides a complete baseline for daily comparison.
"""

import asyncio
import sys
import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.crawler.content_detector import ContentDetector
from app.utils.config import ConfigManager

class ComprehensiveContentChecker:
    """Comprehensive content detection for all pages."""
    
    def __init__(self):
        self.config = ConfigManager()
    
    async def comprehensive_content_check(self, site_id: str) -> Dict[str, Any]:
        """Run comprehensive content detection for a specific site."""
        print(f"\n🔍 Running COMPREHENSIVE content check for {site_id}...")
        
        try:
            # Get site configuration
            site_config = self.config.get_site(site_id)
            if not site_config:
                return {"error": f"Site {site_id} not found in configuration"}
            
            # Create content detector
            content_detector = ContentDetector(site_config)
            
            # Get current state (now checking ALL pages)
            print(f"📄 Fetching content state for ALL pages on {site_config.name}...")
            start_time = time.time()
            current_state = await content_detector.get_current_state()
            duration = time.time() - start_time
            
            # Look for previous state file
            previous_state = self._find_previous_state(site_config.name)
            
            if previous_state:
                print(f"🔄 Comparing with previous state from {previous_state.get('captured_at', 'unknown')}...")
                changes = await content_detector.detect_changes(previous_state)
                
                result = {
                    "site_id": site_id,
                    "site_name": site_config.name,
                    "timestamp": datetime.now().isoformat(),
                    "duration": duration,
                    "current_state": current_state,
                    "previous_state": previous_state,
                    "changes": changes.changes,
                    "summary": changes.summary,
                    "metadata": changes.metadata
                }
            else:
                print("⚠️ No previous state found - this is the first comprehensive content check")
                result = {
                    "site_id": site_id,
                    "site_name": site_config.name,
                    "timestamp": datetime.now().isoformat(),
                    "duration": duration,
                    "current_state": current_state,
                    "previous_state": None,
                    "changes": [],
                    "summary": {"total_changes": 0, "new_pages": 0, "modified_pages": 0, "deleted_pages": 0},
                    "metadata": {"message": "First comprehensive content check - established baseline"}
                }
            
            return result
            
        except Exception as e:
            return {
                "site_id": site_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _find_previous_state(self, site_name: str) -> Dict[str, Any]:
        """Find the most recent previous comprehensive state file."""
        output_dir = Path("output")
        if not output_dir.exists():
            return None
        
        # Look for comprehensive state files
        state_files = []
        for date_dir in output_dir.iterdir():
            if date_dir.is_dir() and date_dir.name.startswith("2025"):
                for file in date_dir.glob(f"{site_name}_state_*"):
                    if "comprehensive" in file.name or "hybrid" in file.name:
                        state_files.append(file)
        
        if not state_files:
            return None
        
        # Get the most recent file
        latest_file = max(state_files, key=lambda f: f.stat().st_mtime)
        
        try:
            with open(latest_file, 'r', encoding='utf-8') as f:
                state_data = json.load(f)
                return state_data
        except Exception as e:
            print(f"⚠️ Error reading state file {latest_file}: {e}")
            return None
    
    def print_results(self, results: Dict[str, Any]):
        """Print the comprehensive content check results."""
        if "error" in results:
            print(f"❌ Error: {results['error']}")
            return
        
        print(f"\n📊 COMPREHENSIVE CONTENT CHECK RESULTS FOR {results['site_name'].upper()}")
        print("=" * 70)
        
        current_state = results.get('current_state', {})
        changes = results.get('changes', [])
        summary = results.get('summary', {})
        
        print(f"⏱️  Duration: {results.get('duration', 0):.2f}s")
        print(f"📄 Total pages checked: {current_state.get('total_pages', 0)}")
        print(f"🔄 Total changes: {summary.get('total_changes', 0)}")
        print(f"🆕 New pages: {summary.get('new_pages', 0)}")
        print(f"✏️ Modified pages: {summary.get('modified_pages', 0)}")
        print(f"🗑️ Deleted pages: {summary.get('deleted_pages', 0)}")
        
        if changes:
            print(f"\n📝 DETAILED CHANGES:")
            for i, change in enumerate(changes, 1):
                print(f"  {i}. {change.get('change_type', 'unknown')}: {change.get('url', 'unknown')}")
                if change.get('title'):
                    print(f"     Title: {change['title']}")
                if change.get('description'):
                    print(f"     Description: {change['description']}")
        else:
            print(f"\n✅ No content changes detected")
        
        metadata = results.get('metadata', {})
        if metadata.get('message'):
            print(f"\n💡 Note: {metadata['message']}")
        
        # Show some URLs that were checked
        urls_checked = current_state.get('urls_checked', [])
        if urls_checked:
            print(f"\n🔍 SAMPLE URLs CHECKED (showing first 5):")
            for i, url in enumerate(urls_checked[:5], 1):
                print(f"  {i}. {url}")
            if len(urls_checked) > 5:
                print(f"  ... and {len(urls_checked) - 5} more pages")

async def main():
    """Main function to run comprehensive content checks."""
    print("🔍 COMPREHENSIVE CONTENT DETECTION")
    print("=" * 50)
    print("This script will check ALL pages for content changes.")
    print("This provides a complete baseline for daily comparison.")
    
    checker = ComprehensiveContentChecker()
    
    # Check both sites
    sites = ['judiciary_uk', 'waverley_gov']
    
    for site_id in sites:
        results = await checker.comprehensive_content_check(site_id)
        checker.print_results(results)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"comprehensive_content_check_{site_id}_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Results saved to: {filename}")
        print("-" * 50)

if __name__ == "__main__":
    asyncio.run(main()) 