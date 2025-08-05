# ==============================================================================
# test_baseline_evolution_integration.py — Integration Tests for Baseline Evolution
# ==============================================================================
# Purpose: Test the complete baseline evolution workflow end-to-end
# Sections: Imports, Test Classes
# ==============================================================================

# ==============================================================================
# Imports
# ==============================================================================

# Standard Library -----
import pytest
import tempfile
import json
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import patch, MagicMock, AsyncMock

# Internal -----
from app.crawler.change_detector import ChangeDetector
from app.crawler.sitemap_detector import SitemapDetector
from app.crawler.content_detector import ContentDetector
from app.utils.baseline_manager import BaselineManager
from app.utils.baseline_merger import BaselineMerger
from app.utils.json_writer import ChangeDetectionWriter


class TestBaselineEvolutionWorkflow:
    """Integration tests for the complete baseline evolution workflow."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.baseline_dir = Path(self.temp_dir) / "baselines"
        self.output_dir = Path(self.temp_dir) / "output"
        self.baseline_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        
        # Create managers
        self.baseline_manager = BaselineManager(str(self.baseline_dir))
        self.baseline_merger = BaselineMerger()
        self.json_writer = ChangeDetectionWriter(str(self.output_dir))
        
        # Sample site configuration
        self.site_config = MagicMock()
        self.site_config.name = "Test Site"
        self.site_config.url = "https://test.example.com/"
        self.site_config.sitemap_url = "https://test.example.com/sitemap.xml"
        self.site_config.detection_methods = ["sitemap", "content"]
        
        # Initial baseline data
        self.initial_baseline = {
            "site_id": "test_site",
            "site_name": "Test Site",
            "site_url": "https://test.example.com/",
            "baseline_date": "20240101",
            "created_at": "2024-01-01T00:00:00",
            "baseline_version": "2.0",
            "total_urls": 3,
            "total_content_hashes": 3,
            "sitemap_state": {
                "urls": [
                    "https://test.example.com/page1",
                    "https://test.example.com/page2",
                    "https://test.example.com/page3"
                ]
            },
            "content_hashes": {
                "https://test.example.com/page1": {"hash": "abc123", "content_length": 100},
                "https://test.example.com/page2": {"hash": "def456", "content_length": 200},
                "https://test.example.com/page3": {"hash": "ghi789", "content_length": 300}
            },
            "metadata": {
                "creation_method": "test",
                "content_hash_algorithm": "sha256"
            }
        }
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @pytest.mark.asyncio
    async def test_first_detection_creates_baseline(self):
        """Test that first detection creates initial baseline."""
        site_id = "test_site"
        
        # Mock current state for first detection
        current_state = {
            "detection_method": "sitemap",
            "sitemap_url": "https://test.example.com/sitemap.xml",
            "urls": [
                "https://test.example.com/page1",
                "https://test.example.com/page2",
                "https://test.example.com/page3"
            ],
            "total_urls": 3,
            "captured_at": datetime.now().isoformat()
        }
        
        # Mock detector
        detector = MagicMock()
        detector.get_current_state = AsyncMock(return_value=current_state)
        detector.detect_changes = AsyncMock(return_value=MagicMock(
            changes=[],
            summary={"total_changes": 0},
            metadata={"message": "First run - establishing baseline"}
        ))
        
        # Simulate first detection (no previous baseline)
        previous_baseline = None
        
        # This should create a new baseline
        if previous_baseline is None:
            new_baseline = self.baseline_merger.create_initial_baseline(
                site_id, current_state, self.site_config
            )
            baseline_file = self.baseline_manager.save_baseline(site_id, new_baseline)
        
        # Verify baseline was created
        assert Path(baseline_file).exists()
        
        # Verify baseline content
        with open(baseline_file, 'r') as f:
            saved_baseline = json.load(f)
        
        assert saved_baseline["site_id"] == site_id
        assert saved_baseline["total_urls"] == 3
        assert len(saved_baseline["sitemap_state"]["urls"]) == 3
        assert "baseline_date" in saved_baseline
        assert "created_at" in saved_baseline
    
    @pytest.mark.asyncio
    async def test_baseline_evolution_with_new_urls(self):
        """Test baseline evolution when new URLs are detected."""
        site_id = "test_site"
        
        # Save initial baseline
        self.baseline_manager.save_baseline(site_id, self.initial_baseline)
        
        # Simulate current state with new URLs
        current_state = {
            "detection_method": "sitemap",
            "sitemap_url": "https://test.example.com/sitemap.xml",
            "urls": [
                "https://test.example.com/page1",
                "https://test.example.com/page2", 
                "https://test.example.com/page3",
                "https://test.example.com/page4",  # New URL
                "https://test.example.com/page5"   # New URL
            ],
            "total_urls": 5,
            "captured_at": datetime.now().isoformat()
        }
        
        # Simulate detected changes
        detected_changes = [
            {
                "url": "https://test.example.com/page4",
                "change_type": "new",
                "title": "New page: https://test.example.com/page4"
            },
            {
                "url": "https://test.example.com/page5", 
                "change_type": "new",
                "title": "New page: https://test.example.com/page5"
            }
        ]
        
        # Get previous baseline
        previous_baseline = self.baseline_manager.get_latest_baseline(site_id)
        
        # Update baseline with changes
        new_baseline = self.baseline_merger.merge_baselines(
            previous_baseline, current_state, detected_changes
        )
        
        # Save new baseline
        baseline_file = self.baseline_manager.save_baseline(site_id, new_baseline)
        
        # Verify baseline evolution
        assert Path(baseline_file).exists()
        
        with open(baseline_file, 'r') as f:
            updated_baseline = json.load(f)
        
        # Should have 5 URLs now (3 original + 2 new)
        assert updated_baseline["total_urls"] == 5
        assert len(updated_baseline["sitemap_state"]["urls"]) == 5
        
        # Should include new URLs
        assert "https://test.example.com/page4" in updated_baseline["sitemap_state"]["urls"]
        assert "https://test.example.com/page5" in updated_baseline["sitemap_state"]["urls"]
        
        # Should preserve original URLs
        assert "https://test.example.com/page1" in updated_baseline["sitemap_state"]["urls"]
        assert "https://test.example.com/page2" in updated_baseline["sitemap_state"]["urls"]
        assert "https://test.example.com/page3" in updated_baseline["sitemap_state"]["urls"]
        
        # Should have updated metadata
        assert updated_baseline["baseline_date"] != self.initial_baseline["baseline_date"]
        assert "updated_at" in updated_baseline
        assert updated_baseline["changes_applied"] == 2
    
    @pytest.mark.asyncio
    async def test_baseline_evolution_with_deleted_urls(self):
        """Test baseline evolution when URLs are deleted."""
        site_id = "test_site"
        
        # Save initial baseline
        self.baseline_manager.save_baseline(site_id, self.initial_baseline)
        
        # Simulate current state with deleted URLs
        current_state = {
            "detection_method": "sitemap",
            "sitemap_url": "https://test.example.com/sitemap.xml",
            "urls": [
                "https://test.example.com/page1",
                "https://test.example.com/page2"
                # page3 is deleted
            ],
            "total_urls": 2,
            "captured_at": datetime.now().isoformat()
        }
        
        # Simulate detected changes
        detected_changes = [
            {
                "url": "https://test.example.com/page3",
                "change_type": "deleted",
                "title": "Removed page: https://test.example.com/page3"
            }
        ]
        
        # Get previous baseline
        previous_baseline = self.baseline_manager.get_latest_baseline(site_id)
        
        # Update baseline with changes
        new_baseline = self.baseline_merger.merge_baselines(
            previous_baseline, current_state, detected_changes
        )
        
        # Save new baseline
        baseline_file = self.baseline_manager.save_baseline(site_id, new_baseline)
        
        # Verify baseline evolution
        with open(baseline_file, 'r') as f:
            updated_baseline = json.load(f)
        
        # Should have 2 URLs now (3 original - 1 deleted)
        assert updated_baseline["total_urls"] == 2
        assert len(updated_baseline["sitemap_state"]["urls"]) == 2
        
        # Should NOT include deleted URL
        assert "https://test.example.com/page3" not in updated_baseline["sitemap_state"]["urls"]
        
        # Should preserve remaining URLs
        assert "https://test.example.com/page1" in updated_baseline["sitemap_state"]["urls"]
        assert "https://test.example.com/page2" in updated_baseline["sitemap_state"]["urls"]
        
        # Should have updated metadata
        assert updated_baseline["changes_applied"] == 1
    
    @pytest.mark.asyncio
    async def test_baseline_evolution_with_modified_content(self):
        """Test baseline evolution when content is modified."""
        site_id = "test_site"
        
        # Save initial baseline
        self.baseline_manager.save_baseline(site_id, self.initial_baseline)
        
        # Simulate current state with modified content
        current_state = {
            "detection_method": "content",
            "content_hashes": {
                "https://test.example.com/page1": {"hash": "abc123", "content_length": 100},  # Unchanged
                "https://test.example.com/page2": {"hash": "def999", "content_length": 250},  # Modified
                "https://test.example.com/page3": {"hash": "ghi789", "content_length": 300}   # Unchanged
            },
            "captured_at": datetime.now().isoformat()
        }
        
        # Simulate detected changes
        detected_changes = [
            {
                "url": "https://test.example.com/page2",
                "change_type": "content_changed",
                "title": "Content changed: https://test.example.com/page2"
            }
        ]
        
        # Get previous baseline
        previous_baseline = self.baseline_manager.get_latest_baseline(site_id)
        
        # Update baseline with changes
        new_baseline = self.baseline_merger.merge_baselines(
            previous_baseline, current_state, detected_changes
        )
        
        # Save new baseline
        baseline_file = self.baseline_manager.save_baseline(site_id, new_baseline)
        
        # Verify baseline evolution
        with open(baseline_file, 'r') as f:
            updated_baseline = json.load(f)
        
        # Should have updated content hash for modified page
        assert updated_baseline["content_hashes"]["https://test.example.com/page2"]["hash"] == "def999"
        assert updated_baseline["content_hashes"]["https://test.example.com/page2"]["content_length"] == 250
        
        # Should preserve unchanged content hashes
        assert updated_baseline["content_hashes"]["https://test.example.com/page1"]["hash"] == "abc123"
        assert updated_baseline["content_hashes"]["https://test.example.com/page3"]["hash"] == "ghi789"
        
        # Should have updated metadata
        assert updated_baseline["changes_applied"] == 1
    
    @pytest.mark.asyncio
    async def test_baseline_evolution_mixed_changes(self):
        """Test baseline evolution with mixed changes (new, deleted, modified)."""
        site_id = "test_site"
        
        # Save initial baseline
        self.baseline_manager.save_baseline(site_id, self.initial_baseline)
        
        # Simulate current state with mixed changes
        current_state = {
            "detection_method": "hybrid",
            "sitemap_url": "https://test.example.com/sitemap.xml",
            "urls": [
                "https://test.example.com/page1",
                "https://test.example.com/page2",
                "https://test.example.com/page4",  # New URL
                "https://test.example.com/page5"   # New URL
                # page3 is deleted
            ],
            "content_hashes": {
                "https://test.example.com/page1": {"hash": "abc123", "content_length": 100},  # Unchanged
                "https://test.example.com/page2": {"hash": "def999", "content_length": 250},  # Modified
                "https://test.example.com/page4": {"hash": "mno345", "content_length": 500},  # New
                "https://test.example.com/page5": {"hash": "pqr678", "content_length": 600}   # New
            },
            "total_urls": 4,
            "captured_at": datetime.now().isoformat()
        }
        
        # Simulate detected changes
        detected_changes = [
            {
                "url": "https://test.example.com/page3",
                "change_type": "deleted",
                "title": "Removed page: https://test.example.com/page3"
            },
            {
                "url": "https://test.example.com/page4",
                "change_type": "new",
                "title": "New page: https://test.example.com/page4"
            },
            {
                "url": "https://test.example.com/page5",
                "change_type": "new", 
                "title": "New page: https://test.example.com/page5"
            },
            {
                "url": "https://test.example.com/page2",
                "change_type": "content_changed",
                "title": "Content changed: https://test.example.com/page2"
            }
        ]
        
        # Get previous baseline
        previous_baseline = self.baseline_manager.get_latest_baseline(site_id)
        
        # Update baseline with changes
        new_baseline = self.baseline_merger.merge_baselines(
            previous_baseline, current_state, detected_changes
        )
        
        # Save new baseline
        baseline_file = self.baseline_manager.save_baseline(site_id, new_baseline)
        
        # Verify baseline evolution
        with open(baseline_file, 'r') as f:
            updated_baseline = json.load(f)
        
        # Should have 4 URLs (3 original - 1 deleted + 2 new)
        assert updated_baseline["total_urls"] == 4
        assert len(updated_baseline["sitemap_state"]["urls"]) == 4
        
        # Should include new URLs
        assert "https://test.example.com/page4" in updated_baseline["sitemap_state"]["urls"]
        assert "https://test.example.com/page5" in updated_baseline["sitemap_state"]["urls"]
        
        # Should NOT include deleted URL
        assert "https://test.example.com/page3" not in updated_baseline["sitemap_state"]["urls"]
        
        # Should preserve remaining URLs
        assert "https://test.example.com/page1" in updated_baseline["sitemap_state"]["urls"]
        assert "https://test.example.com/page2" in updated_baseline["sitemap_state"]["urls"]
        
        # Should have updated content hashes
        assert updated_baseline["content_hashes"]["https://test.example.com/page2"]["hash"] == "def999"
        assert updated_baseline["content_hashes"]["https://test.example.com/page4"]["hash"] == "mno345"
        assert updated_baseline["content_hashes"]["https://test.example.com/page5"]["hash"] == "pqr678"
        
        # Should preserve unchanged content hash
        assert updated_baseline["content_hashes"]["https://test.example.com/page1"]["hash"] == "abc123"
        
        # Should have updated metadata
        assert updated_baseline["changes_applied"] == 4
    
    @pytest.mark.asyncio
    async def test_baseline_evolution_no_changes(self):
        """Test baseline evolution when no changes are detected."""
        site_id = "test_site"
        
        # Save initial baseline
        self.baseline_manager.save_baseline(site_id, self.initial_baseline)
        
        # Simulate current state with no changes
        current_state = {
            "detection_method": "sitemap",
            "sitemap_url": "https://test.example.com/sitemap.xml",
            "urls": [
                "https://test.example.com/page1",
                "https://test.example.com/page2",
                "https://test.example.com/page3"
            ],
            "total_urls": 3,
            "captured_at": datetime.now().isoformat()
        }
        
        # No changes detected
        detected_changes = []
        
        # Get previous baseline
        previous_baseline = self.baseline_manager.get_latest_baseline(site_id)
        
        # Update baseline with changes (should be no-op)
        new_baseline = self.baseline_merger.merge_baselines(
            previous_baseline, current_state, detected_changes
        )
        
        # Save new baseline
        baseline_file = self.baseline_manager.save_baseline(site_id, new_baseline)
        
        # Verify baseline evolution
        with open(baseline_file, 'r') as f:
            updated_baseline = json.load(f)
        
        # Should have same number of URLs
        assert updated_baseline["total_urls"] == 3
        assert len(updated_baseline["sitemap_state"]["urls"]) == 3
        
        # Should preserve all URLs
        assert "https://test.example.com/page1" in updated_baseline["sitemap_state"]["urls"]
        assert "https://test.example.com/page2" in updated_baseline["sitemap_state"]["urls"]
        assert "https://test.example.com/page3" in updated_baseline["sitemap_state"]["urls"]
        
        # Should have updated metadata
        assert updated_baseline["changes_applied"] == 0
    
    @pytest.mark.asyncio
    async def test_multiple_baseline_evolutions(self):
        """Test multiple consecutive baseline evolutions."""
        site_id = "test_site"
        
        # Start with initial baseline
        self.baseline_manager.save_baseline(site_id, self.initial_baseline)
        
        # Evolution 1: Add new URL
        current_state_1 = {
            "detection_method": "sitemap",
            "urls": [
                "https://test.example.com/page1",
                "https://test.example.com/page2",
                "https://test.example.com/page3",
                "https://test.example.com/page4"  # New
            ],
            "total_urls": 4
        }
        
        changes_1 = [
            {
                "url": "https://test.example.com/page4",
                "change_type": "new",
                "title": "New page: https://test.example.com/page4"
            }
        ]
        
        previous_baseline = self.baseline_manager.get_latest_baseline(site_id)
        new_baseline_1 = self.baseline_merger.merge_baselines(
            previous_baseline, current_state_1, changes_1
        )
        self.baseline_manager.save_baseline(site_id, new_baseline_1)
        
        # Evolution 2: Delete URL and modify content
        current_state_2 = {
            "detection_method": "hybrid",
            "urls": [
                "https://test.example.com/page1",
                "https://test.example.com/page2",
                "https://test.example.com/page4"  # page3 deleted
            ],
            "content_hashes": {
                "https://test.example.com/page1": {"hash": "abc123", "content_length": 100},
                "https://test.example.com/page2": {"hash": "def999", "content_length": 250},  # Modified
                "https://test.example.com/page4": {"hash": "mno345", "content_length": 500}
            },
            "total_urls": 3
        }
        
        changes_2 = [
            {
                "url": "https://test.example.com/page3",
                "change_type": "deleted",
                "title": "Removed page: https://test.example.com/page3"
            },
            {
                "url": "https://test.example.com/page2",
                "change_type": "content_changed",
                "title": "Content changed: https://test.example.com/page2"
            }
        ]
        
        previous_baseline = self.baseline_manager.get_latest_baseline(site_id)
        new_baseline_2 = self.baseline_merger.merge_baselines(
            previous_baseline, current_state_2, changes_2
        )
        self.baseline_manager.save_baseline(site_id, new_baseline_2)
        
        # Verify final state
        final_baseline = self.baseline_manager.get_latest_baseline(site_id)
        
        assert final_baseline["total_urls"] == 3
        assert len(final_baseline["sitemap_state"]["urls"]) == 3
        
        # Should have page1, page2, page4 (page3 deleted)
        assert "https://test.example.com/page1" in final_baseline["sitemap_state"]["urls"]
        assert "https://test.example.com/page2" in final_baseline["sitemap_state"]["urls"]
        assert "https://test.example.com/page4" in final_baseline["sitemap_state"]["urls"]
        assert "https://test.example.com/page3" not in final_baseline["sitemap_state"]["urls"]
        
        # Should have updated content hash for page2
        assert final_baseline["content_hashes"]["https://test.example.com/page2"]["hash"] == "def999"
        
        # Should preserve unchanged content hash for page1
        assert final_baseline["content_hashes"]["https://test.example.com/page1"]["hash"] == "abc123"
    
    @pytest.mark.asyncio
    async def test_baseline_evolution_with_output_generation(self):
        """Test that baseline evolution works with output generation."""
        site_id = "test_site"
        
        # Save initial baseline
        self.baseline_manager.save_baseline(site_id, self.initial_baseline)
        
        # Simulate detection with changes
        current_state = {
            "detection_method": "sitemap",
            "urls": [
                "https://test.example.com/page1",
                "https://test.example.com/page2",
                "https://test.example.com/page4"  # New URL
            ],
            "total_urls": 3
        }
        
        detected_changes = [
            {
                "url": "https://test.example.com/page3",
                "change_type": "deleted",
                "title": "Removed page: https://test.example.com/page3"
            },
            {
                "url": "https://test.example.com/page4",
                "change_type": "new",
                "title": "New page: https://test.example.com/page4"
            }
        ]
        
        # Update baseline
        previous_baseline = self.baseline_manager.get_latest_baseline(site_id)
        new_baseline = self.baseline_merger.merge_baselines(
            previous_baseline, current_state, detected_changes
        )
        baseline_file = self.baseline_manager.save_baseline(site_id, new_baseline)
        
        # Generate output file
        output_data = {
            "site_id": site_id,
            "site_name": "Test Site",
            "detection_time": datetime.now().isoformat(),
            "changes": detected_changes,
            "summary": {
                "total_changes": 2,
                "new_pages": 1,
                "deleted_pages": 1
            },
            "baseline_updated": True,
            "new_baseline_file": baseline_file
        }
        
        output_file = self.json_writer.write_changes("Test Site", output_data)
        
        # Verify both baseline and output were created
        assert Path(baseline_file).exists()
        assert Path(output_file).exists()
        
        # Verify output content
        with open(output_file, 'r') as f:
            output_content = json.load(f)
        
        assert output_content["changes"]["site_id"] == site_id
        assert output_content["changes"]["baseline_updated"] is True
        assert output_content["changes"]["new_baseline_file"] == baseline_file
        assert len(output_content["changes"]["changes"]) == 2
    
    @pytest.mark.asyncio
    async def test_baseline_evolution_error_handling(self):
        """Test error handling during baseline evolution."""
        site_id = "test_site"
        
        # Save initial baseline
        self.baseline_manager.save_baseline(site_id, self.initial_baseline)
        
        # Simulate corrupted current state
        corrupted_state = {
            "detection_method": "sitemap",
            "urls": None,  # Corrupted data
            "total_urls": 3
        }
        
        detected_changes = [
            {
                "url": "https://test.example.com/page4",
                "change_type": "new",
                "title": "New page: https://test.example.com/page4"
            }
        ]
        
        # This should handle the error gracefully
        previous_baseline = self.baseline_manager.get_latest_baseline(site_id)
        
        try:
            new_baseline = self.baseline_merger.merge_baselines(
                previous_baseline, corrupted_state, detected_changes
            )
            # If it doesn't raise an exception, it should handle the error gracefully
            assert new_baseline is not None
        except Exception as e:
            # If it raises an exception, it should be a specific type
            assert "corrupted" in str(e).lower() or "invalid" in str(e).lower()
    
    @pytest.mark.asyncio
    async def test_baseline_evolution_performance(self):
        """Test baseline evolution performance with large datasets."""
        site_id = "test_site"
        
        # Create large initial baseline
        large_baseline = self.initial_baseline.copy()
        large_baseline["sitemap_state"]["urls"] = [
            f"https://test.example.com/page{i}" for i in range(1000)
        ]
        large_baseline["content_hashes"] = {
            f"https://test.example.com/page{i}": {
                "hash": f"hash{i:08d}",
                "content_length": 100 + i
            } for i in range(1000)
        }
        large_baseline["total_urls"] = 1000
        large_baseline["total_content_hashes"] = 1000
        
        self.baseline_manager.save_baseline(site_id, large_baseline)
        
        # Simulate large current state with changes
        current_state = {
            "detection_method": "sitemap",
            "urls": [
                f"https://test.example.com/page{i}" for i in range(1000, 1100)  # 100 new URLs
            ] + [
                f"https://test.example.com/page{i}" for i in range(100, 900)  # 800 existing URLs
            ],
            "total_urls": 900
        }
        
        # Simulate 100 new URLs and 100 deleted URLs
        detected_changes = [
            {
                "url": f"https://test.example.com/page{i}",
                "change_type": "new",
                "title": f"New page: https://test.example.com/page{i}"
            } for i in range(1000, 1100)
        ] + [
            {
                "url": f"https://test.example.com/page{i}",
                "change_type": "deleted",
                "title": f"Removed page: https://test.example.com/page{i}"
            } for i in range(900, 1000)
        ]
        
        # Measure performance
        import time
        start_time = time.time()
        
        previous_baseline = self.baseline_manager.get_latest_baseline(site_id)
        new_baseline = self.baseline_merger.merge_baselines(
            previous_baseline, current_state, detected_changes
        )
        baseline_file = self.baseline_manager.save_baseline(site_id, new_baseline)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Verify performance is reasonable (should complete within 5 seconds)
        assert processing_time < 5.0
        
        # Verify result
        with open(baseline_file, 'r') as f:
            updated_baseline = json.load(f)
        
        assert updated_baseline["total_urls"] == 900
        assert len(updated_baseline["sitemap_state"]["urls"]) == 900
        assert updated_baseline["changes_applied"] == 200 