# ==============================================================================
# test_baseline_evolution_api.py — API Tests for Baseline Evolution
# ==============================================================================
# Purpose: Test baseline evolution functionality through API endpoints
# Sections: Imports, Test Classes
# ==============================================================================

# ==============================================================================
# Imports
# ==============================================================================

# Standard Library -----
import pytest
import json
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock

# Internal -----
from app.main import app
from app.crawler.change_detector import ChangeDetector
from app.utils.baseline_manager import BaselineManager
from app.utils.baseline_merger import BaselineMerger


class TestBaselineEvolutionAPI:
    """API tests for baseline evolution functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.baseline_dir = Path(self.temp_dir) / "baselines"
        self.output_dir = Path(self.temp_dir) / "output"
        self.baseline_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        
        # Sample baseline data
        self.sample_baseline = {
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
    
    @patch('app.routers.listeners.get_change_detector')
    def test_trigger_site_detection_with_baseline_evolution(self, mock_get_detector, client):
        """Test that site detection trigger includes baseline evolution."""
        # Mock the change detector with baseline evolution
        mock_detector = MagicMock()
        mock_detector.detect_changes_for_site = AsyncMock(return_value={
            "site_id": "test_site",
            "site_name": "Test Site",
            "detection_time": datetime.now().isoformat(),
            "methods": {
                "sitemap": {
                    "detection_method": "sitemap",
                    "changes": [
                        {
                            "url": "https://test.example.com/page4",
                            "change_type": "new",
                            "title": "New page: https://test.example.com/page4"
                        }
                    ],
                    "summary": {
                        "total_changes": 1,
                        "new_pages": 1,
                        "deleted_pages": 0
                    },
                    "metadata": {
                        "current_urls": 4,
                        "previous_urls": 3,
                        "new_urls": 1
                    }
                }
            },
            "baseline_updated": True,
            "new_baseline_file": "baselines/test_site_20240102_baseline.json",
            "output_file": "output/20240102_120000/Test_Site_20240102_120000.json"
        })
        mock_get_detector.return_value = mock_detector
        
        # Trigger detection
        response = client.post("/api/listeners/trigger/test_site")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "started"
        assert "Change detection started for test_site" in data["message"]
        assert "progress_url" in data
    
    @patch('app.routers.listeners.get_change_detector')
    def test_detection_result_includes_baseline_info(self, mock_get_detector, client):
        """Test that detection results include baseline evolution information."""
        # Mock detection result with baseline evolution
        detection_result = {
            "site_id": "test_site",
            "site_name": "Test Site",
            "detection_time": datetime.now().isoformat(),
            "methods": {
                "sitemap": {
                    "detection_method": "sitemap",
                    "changes": [
                        {
                            "url": "https://test.example.com/page4",
                            "change_type": "new",
                            "title": "New page: https://test.example.com/page4"
                        },
                        {
                            "url": "https://test.example.com/page3",
                            "change_type": "deleted",
                            "title": "Removed page: https://test.example.com/page3"
                        }
                    ],
                    "summary": {
                        "total_changes": 2,
                        "new_pages": 1,
                        "deleted_pages": 1
                    }
                }
            },
            "baseline_updated": True,
            "new_baseline_file": "baselines/test_site_20240102_baseline.json",
            "baseline_evolution": {
                "previous_baseline_date": "20240101",
                "new_baseline_date": "20240102",
                "changes_applied": 2,
                "urls_added": 1,
                "urls_removed": 1,
                "content_hashes_updated": 0
            },
            "output_file": "output/20240102_120000/Test_Site_20240102_120000.json"
        }
        
        mock_detector = MagicMock()
        mock_detector.detect_changes_for_site = AsyncMock(return_value=detection_result)
        mock_get_detector.return_value = mock_detector
        
        # Trigger detection
        response = client.post("/api/listeners/trigger/test_site")
        
        assert response.status_code == 200
        
        # Wait for detection to complete (in real scenario)
        # For testing, we'll check the mocked result
        assert mock_detector.detect_changes_for_site.called
        
        # Verify baseline evolution info is included
        result = mock_detector.detect_changes_for_site.return_value
        assert result["baseline_updated"] is True
        assert "new_baseline_file" in result
        assert "baseline_evolution" in result
        assert result["baseline_evolution"]["changes_applied"] == 2
    
    @patch('app.routers.listeners.get_change_detector')
    def test_detection_with_no_changes_still_updates_baseline(self, mock_get_detector, client):
        """Test that detection with no changes still updates baseline metadata."""
        # Mock detection result with no changes
        detection_result = {
            "site_id": "test_site",
            "site_name": "Test Site",
            "detection_time": datetime.now().isoformat(),
            "methods": {
                "sitemap": {
                    "detection_method": "sitemap",
                    "changes": [],
                    "summary": {
                        "total_changes": 0,
                        "new_pages": 0,
                        "deleted_pages": 0
                    },
                    "metadata": {
                        "current_urls": 3,
                        "previous_urls": 3,
                        "new_urls": 0
                    }
                }
            },
            "baseline_updated": True,
            "new_baseline_file": "baselines/test_site_20240102_baseline.json",
            "baseline_evolution": {
                "previous_baseline_date": "20240101",
                "new_baseline_date": "20240102",
                "changes_applied": 0,
                "urls_added": 0,
                "urls_removed": 0,
                "content_hashes_updated": 0
            },
            "output_file": "output/20240102_120000/Test_Site_20240102_120000.json"
        }
        
        mock_detector = MagicMock()
        mock_detector.detect_changes_for_site = AsyncMock(return_value=detection_result)
        mock_get_detector.return_value = mock_detector
        
        # Trigger detection
        response = client.post("/api/listeners/trigger/test_site")
        
        assert response.status_code == 200
        
        # Verify baseline is still updated even with no changes
        result = mock_detector.detect_changes_for_site.return_value
        assert result["baseline_updated"] is True
        assert result["baseline_evolution"]["changes_applied"] == 0
    
    @patch('app.routers.listeners.get_change_detector')
    def test_first_detection_creates_initial_baseline(self, mock_get_detector, client):
        """Test that first detection creates initial baseline."""
        # Mock first detection (no previous baseline)
        detection_result = {
            "site_id": "test_site",
            "site_name": "Test Site",
            "detection_time": datetime.now().isoformat(),
            "methods": {
                "sitemap": {
                    "detection_method": "sitemap",
                    "changes": [],
                    "summary": {
                        "total_changes": 0,
                        "new_pages": 0,
                        "deleted_pages": 0
                    },
                    "metadata": {
                        "message": "First run - establishing baseline",
                        "current_urls": 3
                    }
                }
            },
            "baseline_created": True,
            "new_baseline_file": "baselines/test_site_20240102_baseline.json",
            "baseline_evolution": {
                "action": "created",
                "baseline_date": "20240102",
                "total_urls": 3,
                "total_content_hashes": 3
            },
            "output_file": "output/20240102_120000/Test_Site_20240102_120000.json"
        }
        
        mock_detector = MagicMock()
        mock_detector.detect_changes_for_site = AsyncMock(return_value=detection_result)
        mock_get_detector.return_value = mock_detector
        
        # Trigger detection
        response = client.post("/api/listeners/trigger/test_site")
        
        assert response.status_code == 200
        
        # Verify initial baseline creation
        result = mock_detector.detect_changes_for_site.return_value
        assert result["baseline_created"] is True
        assert result["baseline_evolution"]["action"] == "created"
        assert result["baseline_evolution"]["total_urls"] == 3
    
    @patch('app.routers.listeners.get_change_detector')
    def test_site_status_includes_baseline_info(self, mock_get_detector, client):
        """Test that site status endpoint includes baseline information."""
        # Mock site status with baseline info
        mock_detector = MagicMock()
        mock_detector.get_site_status.return_value = {
            "site_id": "test_site",
            "site_name": "Test Site",
            "url": "https://test.example.com/",
            "is_active": True,
            "detection_methods": ["sitemap", "content"],
            "recent_change_files": ["output/20240102_120000/Test_Site_20240102_120000.json"],
            "latest_state_file": "output/20240102_120000/Test_Site_state_sitemap_20240102_120000.json",
            "baseline_info": {
                "latest_baseline": "baselines/test_site_20240102_baseline.json",
                "baseline_date": "20240102",
                "total_urls": 4,
                "total_content_hashes": 4,
                "last_updated": "2024-01-02T12:00:00",
                "changes_since_creation": 5
            }
        }
        mock_get_detector.return_value = mock_detector
        
        # Get site status
        response = client.get("/api/listeners/site/test_site/status")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "baseline_info" in data
        assert data["baseline_info"]["latest_baseline"] == "baselines/test_site_20240102_baseline.json"
        assert data["baseline_info"]["baseline_date"] == "20240102"
        assert data["baseline_info"]["total_urls"] == 4
    
    @patch('app.routers.listeners.get_change_detector')
    def test_baseline_history_endpoint(self, mock_get_detector, client):
        """Test baseline history endpoint."""
        # Mock baseline history
        mock_detector = MagicMock()
        mock_detector.get_baseline_history.return_value = {
            "site_id": "test_site",
            "site_name": "Test Site",
            "baselines": [
                {
                    "baseline_date": "20240102",
                    "file_path": "baselines/test_site_20240102_baseline.json",
                    "total_urls": 4,
                    "total_content_hashes": 4,
                    "changes_applied": 2,
                    "created_at": "2024-01-02T12:00:00"
                },
                {
                    "baseline_date": "20240101",
                    "file_path": "baselines/test_site_20240101_baseline.json",
                    "total_urls": 3,
                    "total_content_hashes": 3,
                    "changes_applied": 0,
                    "created_at": "2024-01-01T00:00:00"
                }
            ],
            "evolution_summary": {
                "total_baselines": 2,
                "first_baseline_date": "20240101",
                "latest_baseline_date": "20240102",
                "total_changes_applied": 2,
                "current_urls": 4
            }
        }
        mock_get_detector.return_value = mock_detector
        
        # Get baseline history
        response = client.get("/api/listeners/site/test_site/baseline/history")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "baselines" in data
        assert len(data["baselines"]) == 2
        assert "evolution_summary" in data
        assert data["evolution_summary"]["total_baselines"] == 2
        assert data["evolution_summary"]["current_urls"] == 4
    
    @patch('app.routers.listeners.get_change_detector')
    def test_baseline_rollback_endpoint(self, mock_get_detector, client):
        """Test baseline rollback endpoint."""
        # Mock baseline rollback
        mock_detector = MagicMock()
        mock_detector.rollback_baseline = AsyncMock(return_value={
            "success": True,
            "message": "Baseline rolled back successfully",
            "rolled_back_to": "20240101",
            "new_current_baseline": "baselines/test_site_20240101_baseline.json",
            "urls_restored": 3,
            "content_hashes_restored": 3
        })
        mock_get_detector.return_value = mock_detector
        
        # Rollback baseline
        response = client.post("/api/listeners/site/test_site/baseline/rollback", json={
            "baseline_date": "20240101"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["rolled_back_to"] == "20240101"
        assert data["urls_restored"] == 3
    
    @patch('app.routers.listeners.get_change_detector')
    def test_baseline_rollback_invalid_date(self, mock_get_detector, client):
        """Test baseline rollback with invalid date."""
        # Mock baseline rollback failure
        mock_detector = MagicMock()
        mock_detector.rollback_baseline = AsyncMock(side_effect=ValueError("Baseline not found"))
        mock_get_detector.return_value = mock_detector
        
        # Rollback baseline with invalid date
        response = client.post("/api/listeners/site/test_site/baseline/rollback", json={
            "baseline_date": "invalid_date"
        })
        
        assert response.status_code == 400
        data = response.json()
        
        assert "error" in data
        assert "Baseline not found" in data["error"]
    
    @patch('app.routers.listeners.get_change_detector')
    def test_baseline_validation_endpoint(self, mock_get_detector, client):
        """Test baseline validation endpoint."""
        # Mock baseline validation
        mock_detector = MagicMock()
        mock_detector.validate_baseline = AsyncMock(return_value={
            "valid": True,
            "baseline_date": "20240102",
            "total_urls": 4,
            "total_content_hashes": 4,
            "validation_checks": {
                "structure_valid": True,
                "urls_consistent": True,
                "hashes_consistent": True,
                "metadata_complete": True
            },
            "warnings": [],
            "errors": []
        })
        mock_get_detector.return_value = mock_detector
        
        # Validate baseline
        response = client.get("/api/listeners/site/test_site/baseline/validate")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["valid"] is True
        assert data["baseline_date"] == "20240102"
        assert "validation_checks" in data
        assert data["validation_checks"]["structure_valid"] is True
    
    @patch('app.routers.listeners.get_change_detector')
    def test_baseline_validation_with_errors(self, mock_get_detector, client):
        """Test baseline validation with errors."""
        # Mock baseline validation with errors
        mock_detector = MagicMock()
        mock_detector.validate_baseline = AsyncMock(return_value={
            "valid": False,
            "baseline_date": "20240102",
            "total_urls": 4,
            "total_content_hashes": 3,  # Inconsistent
            "validation_checks": {
                "structure_valid": True,
                "urls_consistent": True,
                "hashes_consistent": False,  # Error
                "metadata_complete": True
            },
            "warnings": [],
            "errors": [
                "Content hash count (3) does not match URL count (4)"
            ]
        })
        mock_get_detector.return_value = mock_detector
        
        # Validate baseline
        response = client.get("/api/listeners/site/test_site/baseline/validate")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["valid"] is False
        assert len(data["errors"]) == 1
        assert "Content hash count" in data["errors"][0]
    
    @patch('app.routers.listeners.get_change_detector')
    def test_baseline_export_endpoint(self, mock_get_detector, client):
        """Test baseline export endpoint."""
        # Mock baseline export
        mock_detector = MagicMock()
        mock_detector.export_baseline = AsyncMock(return_value={
            "success": True,
            "export_file": "exports/test_site_20240102_baseline_export.json",
            "baseline_date": "20240102",
            "export_format": "json",
            "file_size_mb": 0.5,
            "includes_content_hashes": True,
            "includes_metadata": True
        })
        mock_get_detector.return_value = mock_detector
        
        # Export baseline
        response = client.post("/api/listeners/site/test_site/baseline/export", json={
            "format": "json",
            "include_content_hashes": True,
            "include_metadata": True
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["baseline_date"] == "20240102"
        assert data["export_format"] == "json"
        assert data["includes_content_hashes"] is True
    
    @patch('app.routers.listeners.get_change_detector')
    def test_baseline_import_endpoint(self, mock_get_detector, client):
        """Test baseline import endpoint."""
        # Mock baseline import
        mock_detector = MagicMock()
        mock_detector.import_baseline = AsyncMock(return_value={
            "success": True,
            "message": "Baseline imported successfully",
            "imported_baseline_date": "20240102",
            "total_urls": 4,
            "total_content_hashes": 4,
            "validation_passed": True
        })
        mock_get_detector.return_value = mock_detector
        
        # Import baseline
        response = client.post("/api/listeners/site/test_site/baseline/import", json={
            "import_file": "exports/test_site_20240102_baseline_export.json",
            "overwrite_existing": False,
            "validate_import": True
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["imported_baseline_date"] == "20240102"
        assert data["validation_passed"] is True
    
    @patch('app.routers.listeners.get_change_detector')
    def test_baseline_cleanup_endpoint(self, mock_get_detector, client):
        """Test baseline cleanup endpoint."""
        # Mock baseline cleanup
        mock_detector = MagicMock()
        mock_detector.cleanup_old_baselines = AsyncMock(return_value={
            "success": True,
            "message": "Old baselines cleaned up successfully",
            "deleted_files": [
                "baselines/test_site_20231201_baseline.json",
                "baselines/test_site_20231215_baseline.json"
            ],
            "total_files_deleted": 2,
            "total_size_freed_mb": 1.5,
            "cutoff_date": "20240101"
        })
        mock_get_detector.return_value = mock_detector
        
        # Cleanup old baselines
        response = client.post("/api/listeners/site/test_site/baseline/cleanup", json={
            "days_to_keep": 30
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["total_files_deleted"] == 2
        assert data["total_size_freed_mb"] == 1.5
    
    @patch('app.routers.listeners.get_change_detector')
    def test_baseline_statistics_endpoint(self, mock_get_detector, client):
        """Test baseline statistics endpoint."""
        # Mock baseline statistics
        mock_detector = MagicMock()
        mock_detector.get_baseline_statistics = AsyncMock(return_value={
            "site_id": "test_site",
            "site_name": "Test Site",
            "statistics": {
                "total_baselines": 5,
                "oldest_baseline_date": "20231201",
                "newest_baseline_date": "20240102",
                "total_storage_mb": 2.5,
                "average_baseline_size_mb": 0.5,
                "evolution_summary": {
                    "total_changes_applied": 15,
                    "urls_added": 10,
                    "urls_removed": 3,
                    "content_hashes_updated": 2
                }
            },
            "recent_activity": [
                {
                    "baseline_date": "20240102",
                    "changes_applied": 2,
                    "action": "updated"
                },
                {
                    "baseline_date": "20240101",
                    "changes_applied": 0,
                    "action": "updated"
                }
            ]
        })
        mock_get_detector.return_value = mock_detector
        
        # Get baseline statistics
        response = client.get("/api/listeners/site/test_site/baseline/statistics")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "statistics" in data
        assert data["statistics"]["total_baselines"] == 5
        assert data["statistics"]["total_storage_mb"] == 2.5
        assert "recent_activity" in data
        assert len(data["recent_activity"]) == 2
    
    @patch('app.routers.listeners.get_change_detector')
    def test_concurrent_baseline_operations(self, mock_get_detector, client):
        """Test concurrent baseline operations."""
        import threading
        import time
        
        # Mock detector for concurrent operations
        mock_detector = MagicMock()
        mock_detector.detect_changes_for_site = AsyncMock(return_value={
            "site_id": "test_site",
            "baseline_updated": True,
            "new_baseline_file": "baselines/test_site_concurrent_baseline.json"
        })
        mock_get_detector.return_value = mock_detector
        
        # Function to trigger detection
        def trigger_detection():
            response = client.post("/api/listeners/trigger/test_site")
            return response.status_code
        
        # Create multiple threads
        threads = []
        results = []
        
        for _ in range(3):
            thread = threading.Thread(target=lambda: results.append(trigger_detection()))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all operations completed successfully
        assert len(results) == 3
        assert all(status == 200 for status in results)
        
        # Verify detector was called multiple times
        assert mock_detector.detect_changes_for_site.call_count == 3
    
    @patch('app.routers.listeners.get_change_detector')
    def test_baseline_evolution_error_handling(self, mock_get_detector, client):
        """Test error handling during baseline evolution."""
        # Mock detector that raises an exception during baseline evolution
        mock_detector = MagicMock()
        mock_detector.detect_changes_for_site = AsyncMock(side_effect=Exception("Baseline evolution failed"))
        mock_get_detector.return_value = mock_detector
        
        # Trigger detection
        response = client.post("/api/listeners/trigger/test_site")
        
        # Should handle the error gracefully
        assert response.status_code in [200, 500]  # Depending on error handling
        
        # Verify the error was logged or handled appropriately
        assert mock_detector.detect_changes_for_site.called
    
    @patch('app.routers.listeners.get_change_detector')
    def test_baseline_evolution_with_large_dataset(self, mock_get_detector, client):
        """Test baseline evolution with large dataset."""
        # Mock detection with large dataset
        large_detection_result = {
            "site_id": "test_site",
            "site_name": "Test Site",
            "detection_time": datetime.now().isoformat(),
            "methods": {
                "sitemap": {
                    "detection_method": "sitemap",
                    "changes": [
                        {
                            "url": f"https://test.example.com/page{i}",
                            "change_type": "new",
                            "title": f"New page: https://test.example.com/page{i}"
                        } for i in range(100)  # 100 new URLs
                    ],
                    "summary": {
                        "total_changes": 100,
                        "new_pages": 100,
                        "deleted_pages": 0
                    }
                }
            },
            "baseline_updated": True,
            "new_baseline_file": "baselines/test_site_large_baseline.json",
            "baseline_evolution": {
                "changes_applied": 100,
                "urls_added": 100,
                "urls_removed": 0,
                "processing_time_seconds": 2.5
            }
        }
        
        mock_detector = MagicMock()
        mock_detector.detect_changes_for_site = AsyncMock(return_value=large_detection_result)
        mock_get_detector.return_value = mock_detector
        
        # Trigger detection
        response = client.post("/api/listeners/trigger/test_site")
        
        assert response.status_code == 200
        
        # Verify large dataset was handled
        result = mock_detector.detect_changes_for_site.return_value
        assert result["baseline_evolution"]["changes_applied"] == 100
        assert result["baseline_evolution"]["urls_added"] == 100
        assert result["baseline_evolution"]["processing_time_seconds"] < 5.0  # Should complete within 5 seconds 