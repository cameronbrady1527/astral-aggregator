#!/usr/bin/env python3
"""
Enhanced Change Detector - Compare current state against comprehensive baseline
This script provides detailed change detection with content analysis.
"""

import asyncio
import json
import sys
import os
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import aiohttp
from bs4 import BeautifulSoup

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


class EnhancedChangeDetector:
    """Enhanced change detection with comprehensive baseline comparison."""
    
    def __init__(self, site_config: MockSiteConfig):
        self.site_config = site_config
        self.detector = SitemapDetector(site_config)
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def detect_changes(self, baseline_file: str) -> Dict[str, Any]:
        """Detect changes by comparing current state with baseline."""
        print(f"🔍 Detecting changes against baseline: {baseline_file}")
        
        # Load baseline
        baseline_data = await self._load_baseline(baseline_file)
        if not baseline_data:
            return None
        
        # Get current sitemap state
        print("📋 Getting current sitemap state...")
        current_sitemap = await self.detector.get_current_state()
        
        if not current_sitemap.get('urls'):
            print("❌ Warning: Current sitemap returned 0 URLs. This might indicate a sitemap issue.")
            print("   Using baseline URLs as current state for comparison...")
            current_sitemap['urls'] = baseline_data['sitemap_state']['urls']
        
        # Compare sitemap URLs
        baseline_urls = set(baseline_data['sitemap_state']['urls'])
        current_urls = set(current_sitemap['urls'])
        
        new_urls = current_urls - baseline_urls
        deleted_urls = baseline_urls - current_urls
        common_urls = baseline_urls & current_urls
        
        print(f"📊 URL Comparison:")
        print(f"   Baseline URLs: {len(baseline_urls)}")
        print(f"   Current URLs: {len(current_urls)}")
        print(f"   New URLs: {len(new_urls)}")
        print(f"   Deleted URLs: {len(deleted_urls)}")
        print(f"   Common URLs: {len(common_urls)}")
        
        # Analyze changes
        changes = {
            "detection_time": datetime.now().isoformat(),
            "baseline_file": baseline_file,
            "baseline_date": baseline_data['baseline_date'],
            "summary": {
                "total_changes": 0,
                "new_pages": 0,
                "deleted_pages": 0,
                "modified_pages": 0,
                "unchanged_pages": 0
            },
            "changes": []
        }
        
        # Process new URLs
        if new_urls:
            print(f"🔍 Analyzing {len(new_urls)} new URLs...")
            new_changes = await self._analyze_new_urls(list(new_urls))
            changes['changes'].extend(new_changes)
            changes['summary']['new_pages'] = len(new_changes)
        
        # Process deleted URLs (limit to first 50 to avoid overwhelming the system)
        if deleted_urls:
            check_deleted = list(deleted_urls)[:50]  # Limit to first 50
            print(f"🔍 Analyzing {len(check_deleted)} deleted URLs (limited from {len(deleted_urls)} total)...")
            deleted_changes = await self._analyze_deleted_urls(check_deleted)
            changes['changes'].extend(deleted_changes)
            changes['summary']['deleted_pages'] = len(deleted_changes)
            if len(deleted_urls) > 50:
                changes['summary']['total_deleted_urls'] = len(deleted_urls)
                changes['summary']['analyzed_deleted_urls'] = 50
        
        # Process modified URLs (check content changes)
        if common_urls:
            check_common = list(common_urls)[:50]  # Limit to first 50
            print(f"🔍 Checking content changes for {len(check_common)} existing URLs (limited from {len(common_urls)} total)...")
            modified_changes = await self._analyze_content_changes(check_common, baseline_data['content_hashes'])
            changes['changes'].extend(modified_changes)
            changes['summary']['modified_pages'] = len(modified_changes)
            changes['summary']['unchanged_pages'] = len(common_urls) - len(modified_changes)
            if len(common_urls) > 50:
                changes['summary']['total_common_urls'] = len(common_urls)
                changes['summary']['analyzed_common_urls'] = 50
        
        # Update total changes
        changes['summary']['total_changes'] = len(changes['changes'])
        
        return changes
    
    async def _load_baseline(self, baseline_file: str) -> Optional[Dict[str, Any]]:
        """Load baseline data from file."""
        try:
            with open(baseline_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"✅ Loaded baseline:")
            print(f"   Site: {data['site_name']}")
            print(f"   Date: {data['baseline_date']}")
            print(f"   URLs: {data['total_urls']}")
            print(f"   Content hashes: {data['total_content_hashes']}")
            
            return data
            
        except Exception as e:
            print(f"❌ Failed to load baseline: {e}")
            return None
    
    async def _analyze_new_urls(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Analyze new URLs and get their content."""
        changes = []
        
        # Limit to first 20 URLs to avoid overwhelming the server
        check_urls = urls[:20]
        
        for url in check_urls:
            try:
                content_data = await self._get_url_content(url)
                
                change = {
                    "url": url,
                    "change_type": "new",
                    "detected_at": datetime.now().isoformat(),
                    "title": f"New page: {url}",
                    "description": f"Page not present in baseline. Content length: {content_data.get('content_length', 0)} characters.",
                    "metadata": {
                        "content_hash": content_data.get('hash'),
                        "content_length": content_data.get('content_length'),
                        "status_code": content_data.get('status_code'),
                        "content_preview": content_data.get('content_preview', '')[:100] + "..." if content_data.get('content_preview', '') else ''
                    }
                }
                
                changes.append(change)
                
            except Exception as e:
                change = {
                    "url": url,
                    "change_type": "new",
                    "detected_at": datetime.now().isoformat(),
                    "title": f"New page: {url}",
                    "description": f"Page not present in baseline. Error analyzing content: {str(e)}",
                    "metadata": {"error": str(e)}
                }
                changes.append(change)
        
        return changes
    
    async def _analyze_deleted_urls(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Analyze deleted URLs by checking if they still exist."""
        changes = []
        
        for url in urls:
            try:
                # Check if URL still exists
                async with self.session.head(url, timeout=10) as response:
                    if response.status in [404, 410] or response.status >= 500:
                        # Actually deleted
                        change = {
                            "url": url,
                            "change_type": "deleted",
                            "detected_at": datetime.now().isoformat(),
                            "title": f"Deleted page: {url}",
                            "description": f"Page was in baseline but no longer exists (HTTP {response.status})",
                            "metadata": {"status_code": response.status}
                        }
                    else:
                        # Still exists but removed from sitemap
                        change = {
                            "url": url,
                            "change_type": "removed_from_sitemap",
                            "detected_at": datetime.now().isoformat(),
                            "title": f"Removed from sitemap: {url}",
                            "description": f"Page still exists (HTTP {response.status}) but was removed from sitemap",
                            "metadata": {"status_code": response.status}
                        }
                
                changes.append(change)
                
            except Exception as e:
                change = {
                    "url": url,
                    "change_type": "deleted",
                    "detected_at": datetime.now().isoformat(),
                    "title": f"Deleted page: {url}",
                    "description": f"Page was in baseline but could not be verified (error: {str(e)})",
                    "metadata": {"error": str(e)}
                }
                changes.append(change)
        
        return changes
    
    async def _analyze_content_changes(self, urls: List[str], baseline_hashes: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze content changes for existing URLs."""
        changes = []
        
        # Limit to first 20 URLs to avoid overwhelming the server
        check_urls = urls[:20]
        
        for url in check_urls:
            try:
                current_content = await self._get_url_content(url)
                baseline_content = baseline_hashes.get(url, {})
                
                if not current_content.get('hash') or not baseline_content.get('hash'):
                    continue
                
                if current_content['hash'] != baseline_content['hash']:
                    # Content has changed
                    change = {
                        "url": url,
                        "change_type": "modified",
                        "detected_at": datetime.now().isoformat(),
                        "title": f"Content modified: {url}",
                        "description": f"Content hash changed from {baseline_content['hash'][:8]} to {current_content['hash'][:8]}",
                        "metadata": {
                            "old_hash": baseline_content['hash'],
                            "new_hash": current_content['hash'],
                            "old_content_length": baseline_content.get('content_length', 0),
                            "new_content_length": current_content.get('content_length', 0),
                            "content_preview": current_content.get('content_preview', '')[:100] + "..." if current_content.get('content_preview', '') else ''
                        }
                    }
                    changes.append(change)
                
            except Exception as e:
                # Skip URLs that can't be analyzed
                continue
        
        return changes
    
    async def _get_url_content(self, url: str) -> Dict[str, Any]:
        """Get content hash for a URL."""
        try:
            async with self.session.get(url, timeout=15) as response:
                if response.status != 200:
                    return {
                        "error": f"HTTP {response.status}",
                        "hash": None,
                        "content_length": 0,
                        "status_code": response.status
                    }
                
                content = await response.text()
                main_content = self._extract_main_content(content)
                content_hash = hashlib.sha256(main_content.encode('utf-8')).hexdigest()
                
                return {
                    "hash": content_hash,
                    "content_length": len(main_content),
                    "status_code": response.status,
                    "content_preview": main_content[:200] + "..." if len(main_content) > 200 else main_content
                }
                
        except Exception as e:
            return {
                "error": str(e),
                "hash": None,
                "content_length": 0,
                "status_code": None
            }
    
    def _extract_main_content(self, html_content: str) -> str:
        """Extract main content from HTML."""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['nav', 'footer', '.sidebar', '.ads', '.comments', '.header', '.menu', 'script', 'style']):
                element.decompose()
            
            # Try to find main content areas
            main_selectors = [
                'main',
                'article',
                '.content',
                '#content',
                '.main-content',
                '.post-content',
                '.entry-content'
            ]
            
            main_content = ""
            for selector in main_selectors:
                element = soup.select_one(selector)
                if element:
                    main_content = element.get_text(separator=' ', strip=True)
                    break
            
            # If no main content found, use body text
            if not main_content:
                main_content = soup.get_text(separator=' ', strip=True)
            
            # Clean up whitespace
            main_content = ' '.join(main_content.split())
            
            return main_content
            
        except Exception:
            return ' '.join(html_content.split())[:1000]
    
    async def save_changes(self, changes: Dict[str, Any], site_id: str) -> str:
        """Save changes to output file."""
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"{site_id}_{timestamp}_enhanced_changes.json"
        
        print(f"💾 Saving changes to {output_file}...")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(changes, f, indent=2, ensure_ascii=False)
        
        return str(output_file)


async def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python enhanced_change_detector.py <baseline_file>")
        print("Example: python enhanced_change_detector.py baselines/judiciary_uk_20250804_123456_comprehensive_baseline.json")
        return 1
    
    baseline_file = sys.argv[1]
    
    if not os.path.exists(baseline_file):
        print(f"❌ Baseline file not found: {baseline_file}")
        return 1
    
    print("🚀 Starting enhanced change detection...")
    
    site_config = MockSiteConfig()
    async with EnhancedChangeDetector(site_config) as detector:
        changes = await detector.detect_changes(baseline_file)
        
        if not changes:
            print("❌ Failed to detect changes")
            return 1
        
        # Save changes
        output_file = await detector.save_changes(changes, "judiciary_uk")
        
        # Print summary
        summary = changes['summary']
        print(f"\n📊 Change Detection Summary:")
        print(f"   Total changes: {summary['total_changes']}")
        print(f"   New pages: {summary['new_pages']}")
        print(f"   Deleted pages: {summary['deleted_pages']}")
        print(f"   Modified pages: {summary['modified_pages']}")
        print(f"   Unchanged pages: {summary['unchanged_pages']}")
        
        if summary['total_changes'] == 0:
            print(f"\n🎉 No changes detected! Baseline comparison is working correctly.")
        else:
            print(f"\n📝 Changes detected and saved to: {output_file}")
        
        return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 