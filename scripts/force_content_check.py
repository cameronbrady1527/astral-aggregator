#!/usr/bin/env python3
"""
Force content detection script to check for content changes that might be missed.
This script bypasses the interval check and forces content detection to run.
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

class ForceContentChecker:
    """Force content detection to check for missed changes."""
    
    def __init__(self):
        self.config = ConfigManager()
    
    async def force_content_check(self, site_id: str) -> Dict[str, Any]:
        """Force content detection for a specific site."""
        print(f"\n🔍 Force checking content for {site_id}...")
        
        try:
            # Get site configuration
            site_config = self.config.get_site(site_id)
            if not site_config:
                return {"error": f"Site {site_id} not found in configuration"}
            
            # Create content detector
            content_detector = ContentDetector(site_config)
            
            # Get current state
            print(f"📄 Fetching current content state for {site_config.name}...")
            current_state = await content_detector.get_current_state()
            
            # Look for previous state file
            previous_state = self._find_previous_state(site_config.name)
            
            if previous_state:
                print(f"🔄 Comparing with previous state from {previous_state.get('captured_at', 'unknown')}...")
                changes = await content_detector.detect_changes(previous_state)
                
                result = {
                    "site_id": site_id,
                    "site_name": site_config.name,
                    "timestamp": datetime.now().isoformat(),
                    "current_state": current_state,
                    "previous_state": previous_state,
                    "changes": changes.changes,
                    "summary": changes.summary,
                    "metadata": changes.metadata
                }
            else:
                print("⚠️ No previous state found - this is the first content check")
                result = {
                    "site_id": site_id,
                    "site_name": site_config.name,
                    "timestamp": datetime.now().isoformat(),
                    "current_state": current_state,
                    "previous_state": None,
                    "changes": [],
                    "summary": {"total_changes": 0, "new_pages": 0, "modified_pages": 0, "deleted_pages": 0},
                    "metadata": {"message": "First content check - no previous state to compare"}
                }
            
            return result
            
        except Exception as e:
            return {
                "site_id": site_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _find_previous_state(self, site_name: str) -> Dict[str, Any]:
        """Find the most recent previous state file for content detection."""
        output_dir = Path("output")
        if not output_dir.exists():
            return None
        
        # Look for state files with content detection
        state_files = []
        for date_dir in output_dir.iterdir():
            if date_dir.is_dir() and date_dir.name.startswith("2025"):
                for file in date_dir.glob(f"{site_name}_state_*"):
                    if "content" in file.name or "hybrid" in file.name:
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
        """Print the content check results."""
        if "error" in results:
            print(f"❌ Error: {results['error']}")
            return
        
        print(f"\n📊 CONTENT CHECK RESULTS FOR {results['site_name'].upper()}")
        print("=" * 60)
        
        changes = results.get('changes', [])
        summary = results.get('summary', {})
        
        print(f"📄 Pages checked: {results.get('current_state', {}).get('total_pages', 0)}")
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

async def main():
    """Main function to run force content checks."""
    print("🔍 FORCE CONTENT DETECTION CHECK")
    print("=" * 50)
    print("This script will force content detection for both sites to check for missed changes.")
    
    checker = ForceContentChecker()
    
    # Check both sites
    sites = ['judiciary_uk', 'waverley_gov']
    
    for site_id in sites:
        results = await checker.force_content_check(site_id)
        checker.print_results(results)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"force_content_check_{site_id}_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Results saved to: {filename}")
        print("-" * 50)

if __name__ == "__main__":
    asyncio.run(main()) 