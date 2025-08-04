# ==============================================================================
# test_baseline_manager.py — Tests for BaselineManager
# ==============================================================================
# Purpose: Test baseline management functionality including creation, updating, and retrieval
# Sections: Imports, Test Classes
# ==============================================================================

# ==============================================================================
# Imports
# ==============================================================================

# Standard Library -----
import pytest
import tempfile
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import patch, MagicMock

# Internal -----
from app.utils.baseline_manager import BaselineManager


class TestBaselineManager:
    """Test cases for BaselineManager class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.baseline_dir = Path(self.temp_dir) / "baselines"
        self.baseline_dir.mkdir(exist_ok=True)
        self.manager = BaselineManager(str(self.baseline_dir))
        
        # Sample baseline data
        self.sample_baseline = {
            "site_id": "test_site",
            "site_name": "Test Site",
            "site_url": "https://test.example.com/",
            "baseline_date": "20240101",
            "created_at": "2024-01-01T00:00:00",
            "baseline_version": "2.0",
            "total_urls": 4,
            "total_content_hashes": 4,
            "sitemap_state": {
                "urls": [
                    "https://test.example.com/page1",
                    "https://test.example.com/page2",
                    "https://test.example.com/page3",
                    "https://test.example.com/page4"
                ]
            },
            "content_hashes": {
                "https://test.example.com/page1": {"hash": "abc123", "content_length": 100},
                "https://test.example.com/page2": {"hash": "def456", "content_length": 200},
                "https://test.example.com/page3": {"hash": "ghi789", "content_length": 300},
                "https://test.example.com/page4": {"hash": "jkl012", "content_length": 400}
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
    
    def test_initialization(self):
        """Test BaselineManager initialization."""
        assert self.manager.baseline_dir == self.baseline_dir
        assert self.baseline_dir.exists()
    
    def test_save_baseline(self):
        """Test saving a baseline to file."""
        site_id = "test_site"
        baseline_file = self.manager.save_baseline(site_id, self.sample_baseline)
        
        assert Path(baseline_file).exists()
        assert site_id in baseline_file
        
        # Verify file content
        with open(baseline_file, 'r') as f:
            saved_data = json.load(f)
        
        assert saved_data["site_id"] == site_id
        assert saved_data["site_name"] == "Test Site"
        assert saved_data["total_urls"] == 4
    
    def test_get_latest_baseline_exists(self):
        """Test getting the latest baseline when it exists."""
        # Save multiple baselines
        site_id = "test_site"
        baseline1 = self.sample_baseline.copy()
        baseline1["baseline_date"] = "20240101"
        baseline1["created_at"] = "2024-01-01T00:00:00"
        
        baseline2 = self.sample_baseline.copy()
        baseline2["baseline_date"] = "20240102"
        baseline2["created_at"] = "2024-01-02T00:00:00"
        
        self.manager.save_baseline(site_id, baseline1)
        self.manager.save_baseline(site_id, baseline2)
        
        # Get latest baseline
        latest = self.manager.get_latest_baseline(site_id)
        
        assert latest is not None
        assert latest["baseline_date"] == "20240102"
        assert latest["created_at"] == "2024-01-02T00:00:00"
    
    def test_get_latest_baseline_not_exists(self):
        """Test getting the latest baseline when none exists."""
        latest = self.manager.get_latest_baseline("nonexistent_site")
        assert latest is None
    
    def test_list_baselines(self):
        """Test listing all baselines for a site."""
        site_id = "test_site"
        
        # Save multiple baselines
        for i in range(3):
            baseline = self.sample_baseline.copy()
            baseline["baseline_date"] = f"2024010{i+1}"
            baseline["created_at"] = f"2024-01-0{i+1}T00:00:00"
            self.manager.save_baseline(site_id, baseline)
        
        baselines = self.manager.list_baselines(site_id)
        
        assert len(baselines) == 3
        assert all("2024010" in date for date in baselines)
    
    def test_list_baselines_empty(self):
        """Test listing baselines when none exist."""
        baselines = self.manager.list_baselines("nonexistent_site")
        assert len(baselines) == 0
    
    def test_cleanup_old_baselines(self):
        """Test cleaning up old baselines based on count."""
        site_id = "test_site"
        
        # Create multiple baselines with different dates
        baselines = []
        for i in range(7):  # Create 7 baselines
            baseline = self.sample_baseline.copy()
            baseline["baseline_date"] = f"2024010{i+1}"  # 20240101, 20240102, etc.
            baseline["created_at"] = f"2024-01-0{i+1}T00:00:00"
            baselines.append(baseline)
        
        # Save all baselines
        for baseline in baselines:
            self.manager.save_baseline(site_id, baseline)
        
        # Verify we have 7 baselines
        initial_baselines = self.manager.list_baselines(site_id)
        assert len(initial_baselines) == 7
        
        # Clean up, keeping only the 3 most recent baselines
        result = self.manager.cleanup_old_baselines(site_id, max_baselines_per_site=3)
        
        assert result["total_files_deleted"] == 4  # Should delete 4 oldest files
        assert result["kept_baselines"] == 3  # Should keep 3 most recent
        
        # Verify only 3 baselines remain
        remaining_baselines = self.manager.list_baselines(site_id)
        assert len(remaining_baselines) == 3
        
        # Verify the most recent dates are kept (20240105, 20240106, 20240107)
        remaining_dates = [date for date in remaining_baselines]
        assert "20240105" in remaining_dates[0] or "20240106" in remaining_dates[0] or "20240107" in remaining_dates[0]
        assert "20240105" in remaining_dates[1] or "20240106" in remaining_dates[1] or "20240107" in remaining_dates[1]
        assert "20240105" in remaining_dates[2] or "20240106" in remaining_dates[2] or "20240107" in remaining_dates[2]
    
    def test_baseline_validation_valid(self):
        """Test baseline validation with valid data."""
        is_valid = self.manager.validate_baseline(self.sample_baseline)
        assert is_valid is True
    
    def test_baseline_validation_invalid(self):
        """Test baseline validation with invalid data."""
        invalid_baseline = self.sample_baseline.copy()
        del invalid_baseline["site_id"]  # Missing required field
        
        is_valid = self.manager.validate_baseline(invalid_baseline)
        assert is_valid is False
    
    def test_baseline_validation_missing_content_hashes(self):
        """Test baseline validation with missing content hashes."""
        invalid_baseline = self.sample_baseline.copy()
        del invalid_baseline["content_hashes"]
        
        is_valid = self.manager.validate_baseline(invalid_baseline)
        assert is_valid is False
    
    def test_get_baseline_info(self):
        """Test getting detailed information about a baseline."""
        site_id = "test_site"
        baseline_file = self.manager.save_baseline(site_id, self.sample_baseline)
        
        info = self.manager.get_baseline_info(site_id, "20240101")
        
        assert info["site_id"] == site_id
        assert info["date"] == "20240101"
        assert info["file_path"] == baseline_file
        assert info["file_size_mb"] > 0
        assert info["baseline_info"]["site_name"] == "Test Site"
    
    def test_get_baseline_info_not_found(self):
        """Test getting info for non-existent baseline."""
        info = self.manager.get_baseline_info("test_site", "nonexistent")
        
        assert "error" in info
        assert "not found" in info["error"]
    
    def test_get_storage_stats(self):
        """Test getting storage statistics."""
        site_id = "test_site"
        
        # Save multiple baselines
        for i in range(2):
            baseline = self.sample_baseline.copy()
            baseline["baseline_date"] = f"2024010{i+1}"
            self.manager.save_baseline(site_id, baseline)
        
        stats = self.manager.get_storage_stats()
        
        assert stats["total_files"] == 2
        assert stats["total_size_mb"] > 0
        assert site_id in stats["site_stats"]
        assert stats["site_stats"][site_id]["count"] == 2
    
    def test_baseline_file_naming(self):
        """Test that baseline files are named correctly."""
        site_id = "test_site"
        baseline_file = self.manager.save_baseline(site_id, self.sample_baseline)
        
        filename = Path(baseline_file).name
        assert filename.startswith(f"{site_id}_")
        assert filename.endswith("_baseline.json")
        assert len(filename.split("_")) >= 3  # site_id, timestamp, baseline.json
    
    def test_concurrent_baseline_access(self):
        """Test concurrent access to baseline files."""
        import threading
        import time
        
        site_id = "test_site"
        results = []
        
        def save_baseline():
            baseline = self.sample_baseline.copy()
            baseline["baseline_date"] = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = self.manager.save_baseline(site_id, baseline)
            results.append(file_path)
        
        # Create multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=save_baseline)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all baselines were saved
        assert len(results) == 5
        assert len(set(results)) == 5  # All unique files
        
        # Verify all files exist
        for file_path in results:
            assert Path(file_path).exists()
    
    def test_baseline_metadata_consistency(self):
        """Test that baseline metadata is consistent."""
        site_id = "test_site"
        baseline_file = self.manager.save_baseline(site_id, self.sample_baseline)
        
        # Read the saved baseline
        with open(baseline_file, 'r') as f:
            saved_baseline = json.load(f)
        
        # Verify metadata consistency
        assert saved_baseline["total_urls"] == len(saved_baseline["sitemap_state"]["urls"])
        assert saved_baseline["total_content_hashes"] == len(saved_baseline["content_hashes"])
        assert saved_baseline["site_id"] == site_id
        assert "baseline_date" in saved_baseline
        assert "created_at" in saved_baseline
    
    def test_error_handling_invalid_json(self):
        """Test error handling when reading invalid JSON files."""
        # Create an invalid JSON file
        invalid_file = self.baseline_dir / "test_site_invalid_baseline.json"
        with open(invalid_file, 'w') as f:
            f.write("invalid json content")
        
        # Should handle gracefully
        latest = self.manager.get_latest_baseline("test_site")
        # Should not crash and should return None or handle gracefully
        assert latest is None or isinstance(latest, dict)
    
    def test_baseline_versioning(self):
        """Test baseline versioning functionality."""
        site_id = "test_site"
        
        # Save baseline with version
        baseline = self.sample_baseline.copy()
        baseline["baseline_version"] = "2.1"
        baseline_file = self.manager.save_baseline(site_id, baseline)
        
        # Verify version is saved
        with open(baseline_file, 'r') as f:
            saved_baseline = json.load(f)
        
        assert saved_baseline["baseline_version"] == "2.1"
    
    def test_baseline_compression(self):
        """Test baseline compression functionality if implemented."""
        # This test would verify compression works if implemented
        # For now, just test that the system works without compression
        site_id = "test_site"
        baseline_file = self.manager.save_baseline(site_id, self.sample_baseline)
        
        # Verify file was saved successfully
        assert Path(baseline_file).exists()
        
        # Verify file can be read back
        latest = self.manager.get_latest_baseline(site_id)
        assert latest is not None
        assert latest["site_id"] == site_id 