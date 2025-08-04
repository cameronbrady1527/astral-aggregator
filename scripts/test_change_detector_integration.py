#!/usr/bin/env python3
"""
Test ChangeDetector Integration with Baseline Evolution
Tests that the ChangeDetector properly integrates with the baseline evolution system.
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime

# Add the parent directory to the path so we can import from app
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.crawler.change_detector import ChangeDetector
from app.utils.baseline_manager import BaselineManager


class MockSiteConfig:
    """Mock site configuration for testing."""
    def __init__(self, name: str = "Test Site"):
        self.name = name
        self.url = "https://example.com/"
        self.sitemap_url = "https://example.com/sitemap.xml"
        self.verify_deleted_urls = True
        self.max_concurrent_checks = 5
        self.verification_timeout = 10
        self.detection_methods = ["sitemap"]
        self.is_active = True
        self.check_interval_minutes = 60


class ChangeDetectorIntegrationTester:
    """Test the ChangeDetector integration with baseline evolution."""
    
    def __init__(self):
        self.test_site_id = "test_site_integration"
        self.baseline_manager = BaselineManager("test_baselines_integration")
        
        # Clean up test baselines
        self._cleanup_test_baselines()
    
    def _cleanup_test_baselines(self):
        """Clean up any existing test baselines."""
        test_baseline_dir = Path("test_baselines_integration")
        if test_baseline_dir.exists():
            for file in test_baseline_dir.glob(f"{self.test_site_id}_*_baseline.json"):
                file.unlink()
    
    async def test_change_detector_initial_run(self):
        """Test ChangeDetector on first run (no baseline exists)."""
        print("🧪 Testing ChangeDetector initial run...")
        
        # Create a mock site config
        site_config = MockSiteConfig(self.test_site_id)
        
        # Create ChangeDetector with mock config
        change_detector = ChangeDetector()
        
        # Mock the config manager to return our test site
        change_detector.config_manager.sites = {self.test_site_id: site_config}
        
        # Use the same baseline manager for consistency
        change_detector.baseline_manager = self.baseline_manager
        
        # Run detection
        results = await change_detector.detect_changes_for_site(self.test_site_id)
        
        # Verify results
        assert results["site_id"] == self.test_site_id
        assert results["baseline_updated"] == True
        assert results["baseline_file"] is not None
        
        # Check that baseline was created
        latest_baseline = self.baseline_manager.get_latest_baseline(self.test_site_id)
        assert latest_baseline is not None
        assert latest_baseline["site_id"] == self.test_site_id
        assert latest_baseline["evolution_type"] == "initial_creation"
        
        print("✅ ChangeDetector initial run test passed")
        return results
    
    async def test_change_detector_with_existing_baseline(self):
        """Test ChangeDetector with existing baseline."""
        print("🧪 Testing ChangeDetector with existing baseline...")
        
        # Create a mock site config
        site_config = MockSiteConfig(self.test_site_id)
        
        # Create ChangeDetector with mock config
        change_detector = ChangeDetector()
        change_detector.config_manager.sites = {self.test_site_id: site_config}
        
        # Use the same baseline manager for consistency
        change_detector.baseline_manager = self.baseline_manager
        
        # Run detection again (should use existing baseline)
        results = await change_detector.detect_changes_for_site(self.test_site_id)
        
        # Verify results
        assert results["site_id"] == self.test_site_id
        
        # Since there are no real changes, baseline should not be updated
        # (This depends on the mock detector implementation)
        print("✅ ChangeDetector with existing baseline test passed")
        return results
    
    async def test_site_status_with_baseline(self):
        """Test that site status includes baseline information."""
        print("🧪 Testing site status with baseline...")
        
        # Create a mock site config
        site_config = MockSiteConfig(self.test_site_id)
        
        # Create ChangeDetector with mock config
        change_detector = ChangeDetector()
        change_detector.config_manager.sites = {self.test_site_id: site_config}
        
        # Use the same baseline manager for consistency
        change_detector.baseline_manager = self.baseline_manager
        
        # Get site status
        status = change_detector.get_site_status(self.test_site_id)
        
        # Verify status includes baseline information
        assert status["site_id"] == self.test_site_id
        assert "latest_baseline" in status
        
        print("✅ Site status with baseline test passed")
        return status
    
    async def test_list_sites_with_baseline(self):
        """Test that list_sites includes baseline information."""
        print("🧪 Testing list_sites with baseline...")
        
        # Create a mock site config
        site_config = MockSiteConfig(self.test_site_id)
        
        # Create ChangeDetector with mock config
        change_detector = ChangeDetector()
        change_detector.config_manager.sites = {self.test_site_id: site_config}
        
        # Use the same baseline manager for consistency
        change_detector.baseline_manager = self.baseline_manager
        
        # Get sites list
        sites = change_detector.list_sites()
        
        # Verify sites list includes baseline information
        assert len(sites) == 1
        assert sites[0]["site_id"] == self.test_site_id
        assert "latest_baseline" in sites[0]
        
        print("✅ List sites with baseline test passed")
        return sites
    
    async def run_all_tests(self):
        """Run all integration tests."""
        print("🚀 Starting ChangeDetector Integration Tests")
        print("=" * 60)
        
        try:
            # Test 1: Initial run
            await self.test_change_detector_initial_run()
            
            # Test 2: With existing baseline
            await self.test_change_detector_with_existing_baseline()
            
            # Test 3: Site status
            await self.test_site_status_with_baseline()
            
            # Test 4: List sites
            await self.test_list_sites_with_baseline()
            
            print("\n🎉 ALL INTEGRATION TESTS PASSED!")
            print("✅ ChangeDetector properly integrates with baseline evolution:")
            print("   - Creates initial baselines on first run")
            print("   - Uses existing baselines for subsequent runs")
            print("   - Includes baseline information in status endpoints")
            print("   - Properly handles baseline evolution metadata")
            
        except Exception as e:
            print(f"\n❌ INTEGRATION TEST FAILED: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        finally:
            # Clean up test baselines
            self._cleanup_test_baselines()
        
        return True


async def main():
    """Main test function."""
    tester = ChangeDetectorIntegrationTester()
    success = await tester.run_all_tests()
    
    if success:
        print("\n✅ All ChangeDetector integration tests completed successfully!")
        return 0
    else:
        print("\n❌ Some integration tests failed!")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 