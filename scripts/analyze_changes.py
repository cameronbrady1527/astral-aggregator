#!/usr/bin/env python3
"""
Change Analysis Tool - Analyze and verify detected changes
This tool helps understand what changes were detected and verify their validity.
"""

import asyncio
import json
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import aiohttp

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


class ChangeAnalyzer:
    """Analyze and verify detected changes."""
    
    def __init__(self, site_config: MockSiteConfig):
        self.site_config = site_config
        self.detector = SitemapDetector(site_config)
    
    async def analyze_changes_file(self, changes_file: str) -> Dict[str, Any]:
        """Analyze a changes output file."""
        print(f"📊 Analyzing changes file: {changes_file}")
        
        with open(changes_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract changes
        changes = data.get('changes', {}).get('methods', {}).get('hybrid', {}).get('changes', [])
        summary = data.get('changes', {}).get('methods', {}).get('hybrid', {}).get('summary', {})
        
        print(f"📈 Summary from file:")
        print(f"   Total changes: {summary.get('total_changes', 0)}")
        print(f"   New pages: {summary.get('new_pages', 0)}")
        print(f"   Modified pages: {summary.get('modified_pages', 0)}")
        print(f"   Deleted pages: {summary.get('deleted_pages', 0)}")
        
        # Categorize changes
        new_urls = [c['url'] for c in changes if c['change_type'] == 'new']
        deleted_urls = [c['url'] for c in changes if c['change_type'] == 'deleted']
        modified_urls = [c['url'] for c in changes if c['change_type'] == 'modified']
        
        return {
            'new_urls': new_urls,
            'deleted_urls': deleted_urls,
            'modified_urls': modified_urls,
            'summary': summary
        }
    
    async def verify_new_pages(self, urls: List[str]) -> Dict[str, Any]:
        """Verify that new pages actually exist."""
        print(f"\n🔍 Verifying {len(urls)} new pages...")
        
        results = {
            'exist': [],
            'not_found': [],
            'errors': []
        }
        
        # Check first 10 URLs to avoid overwhelming the server
        check_urls = urls[:10]
        
        async with aiohttp.ClientSession() as session:
            for url in check_urls:
                try:
                    async with session.head(url, timeout=10, allow_redirects=False) as response:
                        if response.status == 200:
                            results['exist'].append(url)
                        else:
                            results['not_found'].append(f"{url} (Status: {response.status})")
                except Exception as e:
                    results['errors'].append(f"{url} (Error: {str(e)})")
        
        print(f"✅ Results:")
        print(f"   Exist: {len(results['exist'])}")
        print(f"   Not found: {len(results['not_found'])}")
        print(f"   Errors: {len(results['errors'])}")
        
        if results['exist']:
            print(f"   ✅ Sample existing pages:")
            for url in results['exist'][:3]:
                print(f"      - {url}")
        
        if results['not_found']:
            print(f"   ❌ Sample not found pages:")
            for url in results['not_found'][:3]:
                print(f"      - {url}")
        
        return results
    
    async def verify_deleted_pages(self, urls: List[str]) -> Dict[str, Any]:
        """Verify that deleted pages are actually deleted."""
        print(f"\n🔍 Verifying {len(urls)} deleted pages...")
        
        results = {
            'actually_deleted': [],
            'still_exist': [],
            'errors': []
        }
        
        async with aiohttp.ClientSession() as session:
            for url in urls:
                try:
                    async with session.head(url, timeout=10, allow_redirects=False) as response:
                        if response.status in [404, 410] or response.status >= 500:
                            results['actually_deleted'].append(f"{url} (Status: {response.status})")
                        else:
                            results['still_exist'].append(f"{url} (Status: {response.status})")
                except Exception as e:
                    results['errors'].append(f"{url} (Error: {str(e)})")
        
        print(f"✅ Results:")
        print(f"   Actually deleted: {len(results['actually_deleted'])}")
        print(f"   Still exist: {len(results['still_exist'])}")
        print(f"   Errors: {len(results['errors'])}")
        
        if results['still_exist']:
            print(f"   ⚠️  Pages still existing (false positives):")
            for url in results['still_exist']:
                print(f"      - {url}")
        
        return results
    
    async def get_current_sitemap_state(self) -> Dict[str, Any]:
        """Get the current sitemap state for comparison."""
        print(f"\n📋 Getting current sitemap state...")
        
        try:
            current_state = await self.detector.get_current_state()
            print(f"✅ Current sitemap has {current_state.get('total_urls', 0)} URLs")
            return current_state
        except Exception as e:
            print(f"❌ Error getting current state: {e}")
            return {}
    
    async def compare_with_baseline(self, baseline_file: str) -> Dict[str, Any]:
        """Compare current state with a baseline file."""
        print(f"\n📊 Comparing with baseline: {baseline_file}")
        
        try:
            with open(baseline_file, 'r', encoding='utf-8') as f:
                baseline_data = json.load(f)
            
            baseline_urls = set(baseline_data.get('urls', []))
            print(f"📋 Baseline has {len(baseline_urls)} URLs")
            
            # Get current state
            current_state = await self.detector.get_current_state()
            current_urls = set(current_state.get('urls', []))
            print(f"📋 Current sitemap has {len(current_urls)} URLs")
            
            # Calculate differences
            new_urls = current_urls - baseline_urls
            removed_urls = baseline_urls - current_urls
            
            print(f"📈 Comparison results:")
            print(f"   New URLs: {len(new_urls)}")
            print(f"   Removed URLs: {len(removed_urls)}")
            
            if new_urls:
                print(f"   📝 Sample new URLs:")
                for url in list(new_urls)[:5]:
                    print(f"      - {url}")
            
            if removed_urls:
                print(f"   🗑️  Sample removed URLs:")
                for url in list(removed_urls)[:5]:
                    print(f"      - {url}")
            
            return {
                'new_urls': list(new_urls),
                'removed_urls': list(removed_urls),
                'baseline_count': len(baseline_urls),
                'current_count': len(current_urls)
            }
            
        except Exception as e:
            print(f"❌ Error comparing with baseline: {e}")
            return {}


async def main():
    """Main analysis function."""
    if len(sys.argv) < 2:
        print("Usage: python analyze_changes.py <changes_file> [baseline_file]")
        print("Example: python analyze_changes.py output/20250804_135115/Judiciary\\ UK_20250804_135149.json")
        return 1
    
    changes_file = sys.argv[1]
    baseline_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(changes_file):
        print(f"❌ Changes file not found: {changes_file}")
        return 1
    
    print("🚀 Starting change analysis...")
    
    # Initialize analyzer
    site_config = MockSiteConfig()
    analyzer = ChangeAnalyzer(site_config)
    
    # Analyze changes file
    analysis = await analyzer.analyze_changes_file(changes_file)
    
    # Verify new pages
    if analysis['new_urls']:
        await analyzer.verify_new_pages(analysis['new_urls'])
    
    # Verify deleted pages
    if analysis['deleted_urls']:
        await analyzer.verify_deleted_pages(analysis['deleted_urls'])
    
    # Compare with baseline if provided
    if baseline_file and os.path.exists(baseline_file):
        await analyzer.compare_with_baseline(baseline_file)
    elif baseline_file:
        print(f"\n⚠️  Baseline file not found: {baseline_file}")
    
    # Get current sitemap state
    await analyzer.get_current_sitemap_state()
    
    print(f"\n📊 Analysis complete!")
    print(f"💡 Tips:")
    print(f"   - New pages should return HTTP 200")
    print(f"   - Deleted pages should return HTTP 404/410")
    print(f"   - Check if changes are recent or from delayed sitemap updates")
    print(f"   - Verify if the baseline comparison makes sense")
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 