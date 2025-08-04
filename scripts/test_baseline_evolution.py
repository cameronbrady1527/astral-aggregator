#!/usr/bin/env python3
"""
Test Baseline Evolution System
Tests the complete baseline evolution functionality to ensure it works exactly as described.
"""

import asyncio
import json
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Add the parent directory to the path so we can import from app
sys.path.insert(0, str(Path(__file__).parent.parent))

# Use absolute imports
from app.crawler.change_detector import ChangeDetector
from app.utils.baseline_manager import BaselineManager
from app.utils.baseline_merger import BaselineMerger


class MockSiteConfig:
    """Mock site configuration for testing."""
    def __init__(self, name: str = "Test Site"):
        self.name = name
        self.url = "https://example.com/"
        self.sitemap_url = "https://example.com/sitemap.xml"
        self.verify_deleted_urls = True
        self.max_concurrent_checks = 5
        self.verification_timeout = 10
        self.detection_methods = ["sitemap", "content"]


class BaselineEvolutionTester:
    """Test the baseline evolution system end-to-end."""
    
    def __init__(self):
        self.baseline_manager = BaselineManager("test_baselines")
        self.merger = BaselineMerger()
        self.test_site_id = "test_site"
        
        # Clean up test baselines
        self._cleanup_test_baselines()
    
    def _cleanup_test_baselines(self):
        """Clean up any existing test baselines."""
        test_baseline_dir = Path("test_baselines")
        if test_baseline_dir.exists():
            for file in test_baseline_dir.glob(f"{self.test_site_id}_*_baseline.json"):
                file.unlink()
    
    def create_mock_baseline(self, urls: List[str], content_hashes: Dict[str, str]) -> Dict[str, Any]:
        """Create a mock baseline for testing."""
        baseline_data = {
            "site_id": self.test_site_id,
            "site_name": "Test Site",
            "site_url": "https://example.com/",
            "baseline_date": datetime.now().strftime("%Y%m%d"),
            "created_at": datetime.now().isoformat(),
            "baseline_version": "2.0",
            "total_urls": len(urls),
            "total_content_hashes": len(content_hashes),
            
            # Sitemap data
            "sitemap_state": {
                "detection_method": "sitemap",
                "sitemap_url": "https://example.com/sitemap.xml",
                "urls": urls,
                "total_urls": len(urls),
                "captured_at": datetime.now().isoformat(),
                "site_url": "https://example.com/"
            },
            
            # Content data
            "content_hashes": {
                url: {
                    "hash": content_hashes[url],
                    "content_length": 1000,
                    "status_code": 200,
                    "extracted_at": datetime.now().isoformat()
                }
                for url in content_hashes
            },
            
            # Metadata
            "metadata": {
                "creation_method": "test",
                "content_hash_algorithm": "sha256",
                "baseline_type": "test"
            }
        }
        
        return baseline_data
    
    def create_mock_current_state(self, urls: List[str], content_hashes: Dict[str, str]) -> Dict[str, Any]:
        """Create a mock current state for testing."""
        return {
            "sitemap_state": {
                "detection_method": "sitemap",
                "sitemap_url": "https://example.com/sitemap.xml",
                "urls": urls,
                "total_urls": len(urls),
                "captured_at": datetime.now().isoformat(),
                "site_url": "https://example.com/"
            },
            "content_hashes": {
                url: {
                    "hash": content_hashes[url],
                    "content_length": 1000,
                    "status_code": 200,
                    "extracted_at": datetime.now().isoformat()
                }
                for url in content_hashes
            }
        }
    
    def create_mock_changes(self, new_urls: List[str] = None, deleted_urls: List[str] = None, 
                          modified_urls: List[str] = None) -> List[Dict[str, Any]]:
        """Create mock changes for testing."""
        changes = []
        
        if new_urls:
            for url in new_urls:
                changes.append({
                    "url": url,
                    "change_type": "new",
                    "title": f"New page: {url}",
                    "detected_at": datetime.now().isoformat()
                })
        
        if deleted_urls:
            for url in deleted_urls:
                changes.append({
                    "url": url,
                    "change_type": "deleted",
                    "title": f"Removed page: {url}",
                    "detected_at": datetime.now().isoformat()
                })
        
        if modified_urls:
            for url in modified_urls:
                changes.append({
                    "url": url,
                    "change_type": "content_changed",
                    "title": f"Content changed: {url}",
                    "detected_at": datetime.now().isoformat()
                })
        
        return changes
    
    async def test_initial_baseline_creation(self):
        """Test initial baseline creation when no baseline exists."""
        print("🧪 Testing initial baseline creation...")
        
        # Create mock current state
        initial_urls = ["https://example.com/page1", "https://example.com/page2"]
        initial_hashes = {
            "https://example.com/page1": "hash1_initial",
            "https://example.com/page2": "hash2_initial"
        }
        current_state = self.create_mock_current_state(initial_urls, initial_hashes)
        
        # Create initial baseline
        initial_baseline = self.merger.create_initial_baseline(
            self.test_site_id, "Test Site", current_state
        )
        
        # Save baseline
        baseline_file = self.baseline_manager.save_baseline(self.test_site_id, initial_baseline)
        
        # Verify baseline
        assert initial_baseline["site_id"] == self.test_site_id
        assert initial_baseline["total_urls"] == 2
        assert initial_baseline["total_content_hashes"] == 2
        assert len(initial_baseline["sitemap_state"]["urls"]) == 2
        assert len(initial_baseline["content_hashes"]) == 2
        assert initial_baseline["evolution_type"] == "initial_creation"
        
        print("✅ Initial baseline creation test passed")
        return initial_baseline
    
    async def test_baseline_update_with_new_urls(self):
        """Test baseline update when new URLs are detected."""
        print("🧪 Testing baseline update with new URLs...")
        
        # Create initial baseline
        initial_urls = ["https://example.com/page1", "https://example.com/page2"]
        initial_hashes = {
            "https://example.com/page1": "hash1_initial",
            "https://example.com/page2": "hash2_initial"
        }
        initial_baseline = self.create_mock_baseline(initial_urls, initial_hashes)
        
        # Create current state with new URL
        current_urls = ["https://example.com/page1", "https://example.com/page2", "https://example.com/page3"]
        current_hashes = {
            "https://example.com/page1": "hash1_initial",  # Unchanged
            "https://example.com/page2": "hash2_initial",  # Unchanged
            "https://example.com/page3": "hash3_new"       # New
        }
        current_state = self.create_mock_current_state(current_urls, current_hashes)
        
        # Create changes
        changes = self.create_mock_changes(new_urls=["https://example.com/page3"])
        
        # Update baseline
        new_baseline = self.baseline_manager.update_baseline_from_changes(
            self.test_site_id, initial_baseline, current_state, changes
        )
        
        # Verify baseline evolution
        assert new_baseline["total_urls"] == 3
        assert new_baseline["total_content_hashes"] == 3
        assert len(new_baseline["sitemap_state"]["urls"]) == 3
        assert len(new_baseline["content_hashes"]) == 3
        
        # Verify unchanged URLs kept their hashes
        assert new_baseline["content_hashes"]["https://example.com/page1"]["hash"] == "hash1_initial"
        assert new_baseline["content_hashes"]["https://example.com/page2"]["hash"] == "hash2_initial"
        
        # Verify new URL added with new hash
        assert new_baseline["content_hashes"]["https://example.com/page3"]["hash"] == "hash3_new"
        
        # Verify evolution metadata
        assert new_baseline["evolution_type"] == "automatic_update"
        assert new_baseline["changes_applied"] == 1
        assert new_baseline["previous_baseline_date"] == initial_baseline["baseline_date"]
        
        print("✅ Baseline update with new URLs test passed")
        return new_baseline
    
    async def test_baseline_update_with_deleted_urls(self):
        """Test baseline update when URLs are deleted."""
        print("🧪 Testing baseline update with deleted URLs...")
        
        # Create initial baseline
        initial_urls = ["https://example.com/page1", "https://example.com/page2", "https://example.com/page3"]
        initial_hashes = {
            "https://example.com/page1": "hash1_initial",
            "https://example.com/page2": "hash2_initial",
            "https://example.com/page3": "hash3_initial"
        }
        initial_baseline = self.create_mock_baseline(initial_urls, initial_hashes)
        
        # Create current state with deleted URL
        current_urls = ["https://example.com/page1", "https://example.com/page2"]  # page3 deleted
        current_hashes = {
            "https://example.com/page1": "hash1_initial",  # Unchanged
            "https://example.com/page2": "hash2_initial"   # Unchanged
        }
        current_state = self.create_mock_current_state(current_urls, current_hashes)
        
        # Create changes
        changes = self.create_mock_changes(deleted_urls=["https://example.com/page3"])
        
        # Update baseline
        new_baseline = self.baseline_manager.update_baseline_from_changes(
            self.test_site_id, initial_baseline, current_state, changes
        )
        
        # Verify baseline evolution
        assert new_baseline["total_urls"] == 2
        assert new_baseline["total_content_hashes"] == 2
        assert len(new_baseline["sitemap_state"]["urls"]) == 2
        assert len(new_baseline["content_hashes"]) == 2
        
        # Verify deleted URL is not in new baseline
        assert "https://example.com/page3" not in new_baseline["content_hashes"]
        assert "https://example.com/page3" not in new_baseline["sitemap_state"]["urls"]
        
        # Verify remaining URLs kept their hashes
        assert new_baseline["content_hashes"]["https://example.com/page1"]["hash"] == "hash1_initial"
        assert new_baseline["content_hashes"]["https://example.com/page2"]["hash"] == "hash2_initial"
        
        print("✅ Baseline update with deleted URLs test passed")
        return new_baseline
    
    async def test_baseline_update_with_modified_content(self):
        """Test baseline update when content is modified."""
        print("🧪 Testing baseline update with modified content...")
        
        # Create initial baseline
        initial_urls = ["https://example.com/page1", "https://example.com/page2"]
        initial_hashes = {
            "https://example.com/page1": "hash1_initial",
            "https://example.com/page2": "hash2_initial"
        }
        initial_baseline = self.create_mock_baseline(initial_urls, initial_hashes)
        
        # Create current state with modified content
        current_urls = ["https://example.com/page1", "https://example.com/page2"]
        current_hashes = {
            "https://example.com/page1": "hash1_modified",  # Modified
            "https://example.com/page2": "hash2_initial"    # Unchanged
        }
        current_state = self.create_mock_current_state(current_urls, current_hashes)
        
        # Create changes
        changes = self.create_mock_changes(modified_urls=["https://example.com/page1"])
        
        # Update baseline
        new_baseline = self.baseline_manager.update_baseline_from_changes(
            self.test_site_id, initial_baseline, current_state, changes
        )
        
        # Verify baseline evolution
        assert new_baseline["total_urls"] == 2
        assert new_baseline["total_content_hashes"] == 2
        assert len(new_baseline["sitemap_state"]["urls"]) == 2
        assert len(new_baseline["content_hashes"]) == 2
        
        # Verify modified URL has updated hash
        assert new_baseline["content_hashes"]["https://example.com/page1"]["hash"] == "hash1_modified"
        
        # Verify unchanged URL kept its hash
        assert new_baseline["content_hashes"]["https://example.com/page2"]["hash"] == "hash2_initial"
        
        print("✅ Baseline update with modified content test passed")
        return new_baseline
    
    async def test_baseline_update_with_mixed_changes(self):
        """Test baseline update with mixed changes (new, deleted, modified)."""
        print("🧪 Testing baseline update with mixed changes...")
        
        # Create initial baseline
        initial_urls = ["https://example.com/page1", "https://example.com/page2", "https://example.com/page3"]
        initial_hashes = {
            "https://example.com/page1": "hash1_initial",
            "https://example.com/page2": "hash2_initial",
            "https://example.com/page3": "hash3_initial"
        }
        initial_baseline = self.create_mock_baseline(initial_urls, initial_hashes)
        
        # Create current state with mixed changes
        current_urls = ["https://example.com/page1", "https://example.com/page2", "https://example.com/page4"]  # page3 deleted, page4 added
        current_hashes = {
            "https://example.com/page1": "hash1_modified",  # Modified
            "https://example.com/page2": "hash2_initial",   # Unchanged
            "https://example.com/page4": "hash4_new"        # New
        }
        current_state = self.create_mock_current_state(current_urls, current_hashes)
        
        # Create changes
        changes = self.create_mock_changes(
            new_urls=["https://example.com/page4"],
            deleted_urls=["https://example.com/page3"],
            modified_urls=["https://example.com/page1"]
        )
        
        # Update baseline
        new_baseline = self.baseline_manager.update_baseline_from_changes(
            self.test_site_id, initial_baseline, current_state, changes
        )
        
        # Verify baseline evolution
        assert new_baseline["total_urls"] == 3
        assert new_baseline["total_content_hashes"] == 3
        assert len(new_baseline["sitemap_state"]["urls"]) == 3
        assert len(new_baseline["content_hashes"]) == 3
        
        # Verify deleted URL is not in new baseline
        assert "https://example.com/page3" not in new_baseline["content_hashes"]
        assert "https://example.com/page3" not in new_baseline["sitemap_state"]["urls"]
        
        # Verify modified URL has updated hash
        assert new_baseline["content_hashes"]["https://example.com/page1"]["hash"] == "hash1_modified"
        
        # Verify unchanged URL kept its hash
        assert new_baseline["content_hashes"]["https://example.com/page2"]["hash"] == "hash2_initial"
        
        # Verify new URL added with new hash
        assert new_baseline["content_hashes"]["https://example.com/page4"]["hash"] == "hash4_new"
        
        print("✅ Baseline update with mixed changes test passed")
        return new_baseline
    
    async def test_no_baseline_update_when_no_changes(self):
        """Test that baseline is not updated when no changes are detected."""
        print("🧪 Testing no baseline update when no changes...")
        
        # Create initial baseline
        initial_urls = ["https://example.com/page1", "https://example.com/page2"]
        initial_hashes = {
            "https://example.com/page1": "hash1_initial",
            "https://example.com/page2": "hash2_initial"
        }
        initial_baseline = self.create_mock_baseline(initial_urls, initial_hashes)
        
        # Create current state with no changes
        current_urls = ["https://example.com/page1", "https://example.com/page2"]
        current_hashes = {
            "https://example.com/page1": "hash1_initial",  # Unchanged
            "https://example.com/page2": "hash2_initial"   # Unchanged
        }
        current_state = self.create_mock_current_state(current_urls, current_hashes)
        
        # Create empty changes
        changes = []
        
        # Update baseline
        new_baseline = self.baseline_manager.update_baseline_from_changes(
            self.test_site_id, initial_baseline, current_state, changes
        )
        
        # Verify baseline evolution
        assert new_baseline["total_urls"] == 2
        assert new_baseline["total_content_hashes"] == 2
        assert len(new_baseline["sitemap_state"]["urls"]) == 2
        assert len(new_baseline["content_hashes"]) == 2
        
        # Verify all hashes remain the same
        assert new_baseline["content_hashes"]["https://example.com/page1"]["hash"] == "hash1_initial"
        assert new_baseline["content_hashes"]["https://example.com/page2"]["hash"] == "hash2_initial"
        
        # Verify evolution metadata
        assert new_baseline["evolution_type"] == "automatic_update"
        assert new_baseline["changes_applied"] == 0
        
        print("✅ No baseline update when no changes test passed")
        return new_baseline
    
    async def test_baseline_validation(self):
        """Test baseline validation functionality."""
        print("🧪 Testing baseline validation...")
        
        # Create a baseline
        initial_urls = ["https://example.com/page1", "https://example.com/page2"]
        initial_hashes = {
            "https://example.com/page1": "hash1_initial",
            "https://example.com/page2": "hash2_initial"
        }
        baseline = self.create_mock_baseline(initial_urls, initial_hashes)
        
        # Validate baseline
        validation_result = self.baseline_manager.validate_baseline(baseline)
        
        # Verify validation passes
        assert validation_result["is_valid"] == True
        assert len(validation_result["errors"]) == 0
        
        print("✅ Baseline validation test passed")
    
    async def run_all_tests(self):
        """Run all baseline evolution tests."""
        print("🚀 Starting Baseline Evolution System Tests")
        print("=" * 60)
        
        try:
            # Test 1: Initial baseline creation
            await self.test_initial_baseline_creation()
            
            # Test 2: Baseline update with new URLs
            await self.test_baseline_update_with_new_urls()
            
            # Test 3: Baseline update with deleted URLs
            await self.test_baseline_update_with_deleted_urls()
            
            # Test 4: Baseline update with modified content
            await self.test_baseline_update_with_modified_content()
            
            # Test 5: Baseline update with mixed changes
            await self.test_baseline_update_with_mixed_changes()
            
            # Test 6: No baseline update when no changes
            await self.test_no_baseline_update_when_no_changes()
            
            # Test 7: Baseline validation
            await self.test_baseline_validation()
            
            print("\n🎉 ALL TESTS PASSED!")
            print("✅ Baseline evolution system works exactly as described:")
            print("   - Creates initial baselines when none exist")
            print("   - Updates baselines when changes are detected")
            print("   - Keeps unchanged URLs with their original hashes")
            print("   - Adds new URLs with their current hashes")
            print("   - Updates modified URLs with new hashes")
            print("   - Removes deleted URLs from baseline")
            print("   - Maintains no duplication of URLs")
            print("   - Preserves all required metadata")
            
        except Exception as e:
            print(f"\n❌ TEST FAILED: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        finally:
            # Clean up test baselines
            self._cleanup_test_baselines()
        
        return True


async def main():
    """Main test function."""
    tester = BaselineEvolutionTester()
    success = await tester.run_all_tests()
    
    if success:
        print("\n✅ All baseline evolution tests completed successfully!")
        return 0
    else:
        print("\n❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 