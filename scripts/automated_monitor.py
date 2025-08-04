#!/usr/bin/env python3
"""
Automated Change Monitor - Continuous monitoring using comprehensive baseline
This script provides automated change detection with scheduling and notifications.
"""

import asyncio
import json
import sys
import os
import time
import schedule
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import aiohttp
from bs4 import BeautifulSoup
import hashlib

# Add the app directory to the path
app_path = Path(__file__).parent.parent / "app"
sys.path.insert(0, str(app_path))

# Import from the crawler package
from app.crawler.sitemap_detector import SitemapDetector


class MockSiteConfig:
    """Mock site configuration for testing."""
    def __init__(self):
        self.name = "Judiciary UK"
        self.url = "https://www.judiciary.uk/"
        self.sitemap_url = "https://www.judiciary.uk/sitemap_index.xml"
        self.verify_deleted_urls = True
        self.max_concurrent_checks = 5
        self.verification_timeout = 10


class AutomatedMonitor:
    """Automated change monitoring with comprehensive baseline comparison."""
    
    def __init__(self, baseline_file: str, config: Dict[str, Any] = None):
        self.baseline_file = baseline_file
        self.config = config or self._get_default_config()
        self.site_config = MockSiteConfig()
        self.detector = SitemapDetector(self.site_config)
        self.session = None
        self.monitoring_active = False
        self.last_check_time = None
        self.total_checks = 0
        self.total_changes_detected = 0
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default monitoring configuration."""
        return {
            "check_interval_minutes": 60,  # Check every hour
            "max_urls_to_check": 50,  # Limit URLs to check per run
            "notification_enabled": True,
            "save_changes": True,
            "log_level": "INFO",
            "retry_on_failure": True,
            "max_retries": 3,
            "retry_delay_seconds": 30
        }
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def start_monitoring(self):
        """Start the automated monitoring process."""
        print("🚀 Starting automated change monitoring...")
        print(f"📁 Baseline: {self.baseline_file}")
        print(f"⏰ Check interval: {self.config['check_interval_minutes']} minutes")
        print(f"🔍 Max URLs per check: {self.config['max_urls_to_check']}")
        
        # Load baseline
        self.baseline_data = await self._load_baseline()
        if not self.baseline_data:
            print("❌ Failed to load baseline. Monitoring cannot start.")
            return False
        
        self.monitoring_active = True
        
        # Schedule the monitoring job
        schedule.every(self.config['check_interval_minutes']).minutes.do(
            lambda: asyncio.create_task(self._run_check())
        )
        
        # Run initial check
        await self._run_check()
        
        # Start the monitoring loop
        await self._monitoring_loop()
        
        return True
    
    async def _monitoring_loop(self):
        """Main monitoring loop."""
        print("🔄 Monitoring loop started. Press Ctrl+C to stop.")
        
        try:
            while self.monitoring_active:
                schedule.run_pending()
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n⏹️  Monitoring stopped by user")
            self.monitoring_active = False
    
    async def _run_check(self):
        """Run a single change detection check."""
        self.total_checks += 1
        self.last_check_time = datetime.now()
        
        print(f"\n🔍 Running check #{self.total_checks} at {self.last_check_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            changes = await self._detect_changes()
            
            if changes and changes['summary']['total_changes'] > 0:
                self.total_changes_detected += changes['summary']['total_changes']
                await self._handle_changes(changes)
            else:
                print("✅ No changes detected")
            
            # Save monitoring stats
            await self._save_monitoring_stats()
            
        except Exception as e:
            print(f"❌ Error during check: {e}")
            if self.config['retry_on_failure']:
                await self._retry_check()
    
    async def _detect_changes(self) -> Optional[Dict[str, Any]]:
        """Detect changes using the comprehensive baseline."""
        # Get current sitemap state
        print("   Fetching current sitemap state...")
        current_sitemap = await self.detector.get_current_state()
        
        print(f"   Current sitemap result: {len(current_sitemap.get('urls', []))} URLs")
        if 'error' in current_sitemap:
            print(f"   Error in sitemap: {current_sitemap['error']}")
        
        if not current_sitemap.get('urls'):
            print("❌ Warning: Current sitemap returned 0 URLs. Using baseline URLs.")
            current_sitemap['urls'] = self.baseline_data['sitemap_state']['urls']
        
        # Compare sitemap URLs
        baseline_urls = set(self.baseline_data['sitemap_state']['urls'])
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
        
        # Analyze changes (limited to config max)
        changes = {
            "check_time": datetime.now().isoformat(),
            "check_number": self.total_checks,
            "baseline_file": self.baseline_file,
            "summary": {
                "total_changes": 0,
                "new_pages": 0,
                "deleted_pages": 0,
                "modified_pages": 0
            },
            "changes": []
        }
        
        # Process new URLs
        if new_urls:
            check_new = list(new_urls)[:self.config['max_urls_to_check']]
            print(f"🔍 Analyzing {len(check_new)} new URLs...")
            new_changes = await self._analyze_new_urls(check_new)
            changes['changes'].extend(new_changes)
            changes['summary']['new_pages'] = len(new_changes)
        
        # Process deleted URLs
        if deleted_urls:
            check_deleted = list(deleted_urls)[:self.config['max_urls_to_check']]
            print(f"🔍 Analyzing {len(check_deleted)} deleted URLs...")
            deleted_changes = await self._analyze_deleted_urls(check_deleted)
            changes['changes'].extend(deleted_changes)
            changes['summary']['deleted_pages'] = len(deleted_changes)
        
        # Process modified URLs
        if common_urls:
            check_common = list(common_urls)[:self.config['max_urls_to_check']]
            print(f"🔍 Checking content changes for {len(check_common)} existing URLs...")
            modified_changes = await self._analyze_content_changes(check_common)
            changes['changes'].extend(modified_changes)
            changes['summary']['modified_pages'] = len(modified_changes)
        
        changes['summary']['total_changes'] = len(changes['changes'])
        return changes
    
    async def _load_baseline(self) -> Optional[Dict[str, Any]]:
        """Load baseline data from file."""
        try:
            with open(self.baseline_file, 'r', encoding='utf-8') as f:
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
        
        for url in urls:
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
                        "status_code": content_data.get('status_code')
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
                async with self.session.head(url, timeout=10) as response:
                    if response.status in [404, 410] or response.status >= 500:
                        change = {
                            "url": url,
                            "change_type": "deleted",
                            "detected_at": datetime.now().isoformat(),
                            "title": f"Deleted page: {url}",
                            "description": f"Page was in baseline but no longer exists (HTTP {response.status})",
                            "metadata": {"status_code": response.status}
                        }
                    else:
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
    
    async def _analyze_content_changes(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Analyze content changes for existing URLs."""
        changes = []
        
        for url in urls:
            try:
                current_content = await self._get_url_content(url)
                baseline_content = self.baseline_data['content_hashes'].get(url, {})
                
                if not current_content.get('hash') or not baseline_content.get('hash'):
                    continue
                
                if current_content['hash'] != baseline_content['hash']:
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
                            "new_content_length": current_content.get('content_length', 0)
                        }
                    }
                    changes.append(change)
                
            except Exception as e:
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
                    "status_code": response.status
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
    
    async def _handle_changes(self, changes: Dict[str, Any]):
        """Handle detected changes."""
        print(f"🚨 Changes detected! Total: {changes['summary']['total_changes']}")
        
        # Save changes if enabled
        if self.config['save_changes']:
            await self._save_changes(changes)
        
        # Send notifications if enabled
        if self.config['notification_enabled']:
            await self._send_notification(changes)
        
        # Print summary
        summary = changes['summary']
        print(f"📊 Change Summary:")
        print(f"   New pages: {summary['new_pages']}")
        print(f"   Deleted pages: {summary['deleted_pages']}")
        print(f"   Modified pages: {summary['modified_pages']}")
    
    async def _save_changes(self, changes: Dict[str, Any]):
        """Save changes to output file."""
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"automated_changes_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(changes, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Changes saved to: {output_file}")
    
    async def _send_notification(self, changes: Dict[str, Any]):
        """Send notification about changes (placeholder for future implementation)."""
        # This would typically send email, Slack, or other notifications
        print("📢 Notification: Changes detected on Judiciary UK website")
        print(f"   Total changes: {changes['summary']['total_changes']}")
        print(f"   Check time: {changes['check_time']}")
    
    async def _retry_check(self):
        """Retry the check after a delay."""
        for attempt in range(self.config['max_retries']):
            print(f"🔄 Retrying check in {self.config['retry_delay_seconds']} seconds (attempt {attempt + 1}/{self.config['max_retries']})")
            await asyncio.sleep(self.config['retry_delay_seconds'])
            
            try:
                await self._run_check()
                return
            except Exception as e:
                print(f"❌ Retry attempt {attempt + 1} failed: {e}")
        
        print("❌ All retry attempts failed")
    
    async def _save_monitoring_stats(self):
        """Save monitoring statistics."""
        stats = {
            "last_check_time": self.last_check_time.isoformat() if self.last_check_time else None,
            "total_checks": self.total_checks,
            "total_changes_detected": self.total_changes_detected,
            "monitoring_active": self.monitoring_active,
            "baseline_file": self.baseline_file
        }
        
        stats_file = Path("monitoring_stats.json")
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)


async def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python automated_monitor.py <baseline_file> [check_interval_minutes]")
        print("Example: python automated_monitor.py baselines/judiciary_uk_20250804_143420_comprehensive_baseline.json 60")
        return 1
    
    baseline_file = sys.argv[1]
    check_interval = int(sys.argv[2]) if len(sys.argv) > 2 else 60
    
    if not os.path.exists(baseline_file):
        print(f"❌ Baseline file not found: {baseline_file}")
        return 1
    
    # Configuration
    config = {
        "check_interval_minutes": check_interval,
        "max_urls_to_check": 50,
        "notification_enabled": True,
        "save_changes": True,
        "retry_on_failure": True,
        "max_retries": 3,
        "retry_delay_seconds": 30
    }
    
    print("🚀 Starting automated change monitoring...")
    
    async with AutomatedMonitor(baseline_file, config) as monitor:
        success = await monitor.start_monitoring()
        
        if success:
            print("✅ Monitoring completed successfully")
            return 0
        else:
            print("❌ Monitoring failed to start")
            return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 