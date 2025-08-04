#!/usr/bin/env python3
"""
Test script to verify URL verification fix for sitemap detector.
This script tests the specific case where pages are marked as deleted
but actually still exist.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))

from crawler.sitemap_detector import SitemapDetector
from utils.config import ConfigManager


class MockSiteConfig:
    """Mock site configuration for testing."""
    def __init__(self):
        self.name = "Judiciary UK"
        self.url = "https://www.judiciary.uk/"
        self.sitemap_url = "https://www.judiciary.uk/sitemap_index.xml"
        self.verify_deleted_urls = True
        self.max_concurrent_checks = 3
        self.verification_timeout = 10


async def test_url_verification():
    """Test the URL verification functionality."""
    print("🧪 Testing URL verification fix...")
    
    # Create mock site config
    site_config = MockSiteConfig()
    detector = SitemapDetector(site_config)
    
    # Test URLs that were incorrectly marked as deleted
    test_urls = [
        "https://www.judiciary.uk/appointments-and-retirements/appointment-as-a-judge-of-the-first-tier-tribunal-immigration-and-asylum-chamber-lodato/",
        "https://www.judiciary.uk/appointments-and-retirements/district-judge-appointment-cassidy/",
        "https://www.judiciary.uk/appointments-and-retirements/district-judge-appointment-preston/"
    ]
    
    print(f"🔍 Testing {len(test_urls)} URLs that were incorrectly marked as deleted...")
    
    # Test the verification method directly
    verified_deleted = await detector._verify_deleted_urls(set(test_urls))
    
    print(f"✅ Results:")
    print(f"   URLs tested: {len(test_urls)}")
    print(f"   Actually deleted: {len(verified_deleted)}")
    print(f"   Still exist: {len(test_urls) - len(verified_deleted)}")
    
    for url in test_urls:
        status = "❌ DELETED" if url in verified_deleted else "✅ EXISTS"
        print(f"   {status}: {url}")
    
    # Verify that none of these URLs should be marked as deleted
    if len(verified_deleted) == 0:
        print("🎉 SUCCESS: All URLs correctly identified as still existing!")
        return True
    else:
        print("⚠️  WARNING: Some URLs are still being marked as deleted")
        return False


async def test_with_previous_state():
    """Test the full change detection with a mock previous state."""
    print("\n🧪 Testing full change detection with verification...")
    
    site_config = MockSiteConfig()
    detector = SitemapDetector(site_config)
    
    # Create a mock previous state with the URLs that were incorrectly marked as deleted
    previous_state = {
        "urls": [
            "https://www.judiciary.uk/appointments-and-retirements/appointment-as-a-judge-of-the-first-tier-tribunal-immigration-and-asylum-chamber-lodato/",
            "https://www.judiciary.uk/appointments-and-retirements/district-judge-appointment-cassidy/",
            "https://www.judiciary.uk/appointments-and-retirements/district-judge-appointment-preston/",
            "https://www.judiciary.uk/some-actual-page-that-exists/"
        ]
    }
    
    print("🔍 Running change detection with verification enabled...")
    result = await detector.detect_changes(previous_state)
    
    print(f"✅ Change detection results:")
    print(f"   Total changes: {len(result.changes)}")
    print(f"   New pages: {result.metadata.get('new_urls', 0)}")
    print(f"   Deleted pages: {result.metadata.get('deleted_urls', 0)}")
    print(f"   Unverified deleted: {result.metadata.get('unverified_deleted_urls', 0)}")
    
    # Check if any of our test URLs are still marked as deleted
    test_urls = [
        "https://www.judiciary.uk/appointments-and-retirements/appointment-as-a-judge-of-the-first-tier-tribunal-immigration-and-asylum-chamber-lodato/",
        "https://www.judiciary.uk/appointments-and-retirements/district-judge-appointment-cassidy/",
        "https://www.judiciary.uk/appointments-and-retirements/district-judge-appointment-preston/"
    ]
    
    deleted_urls = [change["url"] for change in result.changes if change["change_type"] == "deleted"]
    
    incorrectly_marked = [url for url in test_urls if url in deleted_urls]
    
    if not incorrectly_marked:
        print("🎉 SUCCESS: No URLs incorrectly marked as deleted!")
        return True
    else:
        print(f"⚠️  WARNING: {len(incorrectly_marked)} URLs still incorrectly marked as deleted:")
        for url in incorrectly_marked:
            print(f"   ❌ {url}")
        return False


async def main():
    """Main test function."""
    print("🚀 Starting URL verification tests...")
    
    # Test 1: Direct URL verification
    test1_passed = await test_url_verification()
    
    # Test 2: Full change detection
    test2_passed = await test_with_previous_state()
    
    print(f"\n📊 Test Results:")
    print(f"   URL Verification: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"   Change Detection: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print("🎉 All tests passed! The URL verification fix is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please review the implementation.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 