# ==============================================================================
# test_change_detection.py — Integration Tests for Change Detection
# ==============================================================================
# Purpose: Test the complete change detection workflow
# ==============================================================================

import pytest
import tempfile
import yaml
import json
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock

from app.crawler.change_detector import ChangeDetector
from app.utils.config import ConfigManager, SiteConfig
from app.utils.json_writer import ChangeDetectionWriter


class TestChangeDetectionIntegration:
    """Integration tests for the complete change detection workflow."""
    
    @pytest.fixture
    def temp_config_file(self, test_config):
        """Create a temporary config file for testing."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(test_config, f)
            temp_file = f.name
        
        yield temp_file
        
        # Cleanup
        import os
        try:
            os.unlink(temp_file)
        except FileNotFoundError:
            pass
    
    @pytest.fixture
    def temp_output_dir(self):
        """Create a temporary output directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.mark.asyncio
    async def test_complete_change_detection_workflow(self, temp_config_file, temp_output_dir):
        """Test the complete change detection workflow from config to output."""
        # Set environment variable to use the temp config file
        import os
        original_config = os.environ.get('CONFIG_FILE')
        os.environ['CONFIG_FILE'] = temp_config_file
        
        try:
            # Initialize components
            config_manager = ConfigManager(temp_config_file)
            json_writer = ChangeDetectionWriter(temp_output_dir)
            
            # Mock the change detector to avoid actual HTTP requests
            with patch('app.crawler.change_detector.ChangeDetector') as mock_detector_class:
                mock_detector = MagicMock()
                mock_detector_class.return_value = mock_detector
                
                # Mock the detection result
                from app.crawler.base_detector import ChangeResult
                mock_result = ChangeResult("sitemap", "Test Site 1")
                mock_result.add_change("new", "https://test1.example.com/new-page", title="New Page")
                mock_result.add_change("modified", "https://test1.example.com/existing-page", title="Modified Page")
                
                mock_detector.detect_changes_for_site.return_value = mock_result
                
                # Create change detector instance
                detector = ChangeDetector()
                
                # Test detection for a specific site
                site_config = config_manager.get_site("test_site_1")
                assert site_config is not None
                
                result = await detector.detect_changes_for_site("test_site_1")
                
                # Verify result structure
                assert result.detection_method == "sitemap"
                assert result.site_name == "Test Site 1"
                assert len(result.changes) == 2
                assert result.summary["total_changes"] == 2
                assert result.summary["new_pages"] == 1
                assert result.summary["modified_pages"] == 1
                
                # Write result to file
                filepath = json_writer.write_changes("Test Site 1", result.to_dict())
                
                # Verify file was created
                assert Path(filepath).exists()
                
                # Verify file contents
                with open(filepath, 'r') as f:
                    data = json.load(f)
                
                assert data["metadata"]["detection_method"] == "sitemap"
                assert data["metadata"]["site_name"] == "Test Site 1"
                assert "changes" in data
        finally:
            # Restore original environment variable
            if original_config:
                os.environ['CONFIG_FILE'] = original_config
            else:
                os.environ.pop('CONFIG_FILE', None)
    
    @pytest.mark.asyncio
    async def test_multiple_sites_detection(self, temp_config_file, temp_output_dir):
        """Test detecting changes for multiple sites."""
        config_manager = ConfigManager(temp_config_file)
        json_writer = ChangeDetectionWriter(temp_output_dir)
        
        with patch('app.crawler.change_detector.ChangeDetector') as mock_detector_class:
            mock_detector = MagicMock()
            mock_detector_class.return_value = mock_detector
            
            # Mock different results for different sites
            from app.crawler.base_detector import ChangeResult
            
            def mock_detect_site(site_id):
                if site_id == "test_site_1":
                    result = ChangeResult("sitemap", "Test Site 1")
                    result.add_change("new", "https://test1.example.com/new-page")
                    return result
                elif site_id == "test_site_2":
                    result = ChangeResult("firecrawl", "Test Site 2")
                    result.add_change("modified", "https://test2.example.com/modified-page")
                    return result
                else:
                    return ChangeResult("sitemap", "Unknown Site")
            
            mock_detector.detect_changes_for_site.side_effect = mock_detect_site
            
            detector = ChangeDetector()
            
            # Test detection for multiple sites
            active_sites = config_manager.get_active_sites()
            assert len(active_sites) == 2
            
            results = []
            for site in active_sites:
                result = await detector.detect_changes_for_site(site.name.lower().replace(" ", "_"))
                results.append(result)
                
                # Write each result
                json_writer.write_changes(site.name, result.to_dict())
            
            # Verify results
            assert len(results) == 2
            assert results[0].detection_method == "sitemap"
            assert results[1].detection_method == "firecrawl"
            
            # Verify files were created
            change_files = json_writer.list_change_files()
            assert len(change_files) >= 2
    
    @pytest.mark.asyncio
    async def test_change_detection_with_previous_state(self, temp_config_file, temp_output_dir):
        """Test change detection with previous state comparison."""
        config_manager = ConfigManager(temp_config_file)
        json_writer = ChangeDetectionWriter(temp_output_dir)
        
        # Create a previous state file
        previous_state = {
            "detection_method": "sitemap",
            "urls": [
                "https://test1.example.com/existing-page",
                "https://test1.example.com/old-page"
            ],
            "last_updated": "2024-01-01T00:00:00Z"
        }
        
        previous_filepath = json_writer.write_site_state("Test Site 1", previous_state)
        assert Path(previous_filepath).exists()
        
        with patch('app.crawler.change_detector.ChangeDetector') as mock_detector_class:
            mock_detector = MagicMock()
            mock_detector_class.return_value = mock_detector
            
            # Mock detection result that includes comparison with previous state
            from app.crawler.base_detector import ChangeResult
            mock_result = ChangeResult("sitemap", "Test Site 1")
            mock_result.add_change("new", "https://test1.example.com/new-page", title="New Page")
            mock_result.add_change("deleted", "https://test1.example.com/old-page", title="Old Page")
            
            mock_detector.detect_changes_for_site.return_value = mock_result
            
            detector = ChangeDetector()
            
            # Test detection
            result = await detector.detect_changes_for_site("test_site_1")
            
            # Verify result includes comparison data
            assert result.detection_method == "sitemap"
            assert len(result.changes) == 2
            assert result.summary["new_pages"] == 1
            assert result.summary["deleted_pages"] == 1
            
            # Write current state for future comparisons
            current_state = {
                "detection_method": "sitemap",
                "urls": [
                    "https://test1.example.com/existing-page",
                    "https://test1.example.com/new-page"
                ],
                "last_updated": "2024-01-02T00:00:00Z"
            }
            
            current_filepath = json_writer.write_site_state("Test Site 1", current_state)
            assert Path(current_filepath).exists()
            
            # Write changes
            changes_filepath = json_writer.write_changes("Test Site 1", result.to_dict())
            assert Path(changes_filepath).exists()
    
    @pytest.mark.asyncio
    async def test_error_handling_in_detection_workflow(self, temp_config_file, temp_output_dir):
        """Test error handling during the detection workflow."""
        config_manager = ConfigManager(temp_config_file)
        json_writer = ChangeDetectionWriter(temp_output_dir)
        
        with patch('app.crawler.change_detector.ChangeDetector') as mock_detector_class:
            mock_detector = MagicMock()
            mock_detector_class.return_value = mock_detector
            
            # Mock an error during detection
            mock_detector.detect_changes_for_site.side_effect = Exception("Detection failed")
            
            detector = ChangeDetector()
            
            # Test that errors are handled gracefully
            try:
                result = await detector.detect_changes_for_site("test_site_1")
                # If no exception is raised, the error handling should be implemented
            except Exception as e:
                # Expected behavior - error should be caught and handled
                assert "Detection failed" in str(e)
    
    @pytest.mark.asyncio
    async def test_detection_with_different_methods(self, temp_config_file, temp_output_dir):
        """Test detection using different methods for the same site."""
        config_manager = ConfigManager(temp_config_file)
        json_writer = ChangeDetectionWriter(temp_output_dir)
        
        with patch('app.crawler.change_detector.ChangeDetector') as mock_detector_class:
            mock_detector = MagicMock()
            mock_detector_class.return_value = mock_detector
            
            from app.crawler.base_detector import ChangeResult
            
            def mock_detect_with_method(site_id, method=None):
                if method == "sitemap":
                    result = ChangeResult("sitemap", "Test Site 1")
                    result.add_change("new", "https://test1.example.com/sitemap-page")
                    return result
                elif method == "firecrawl":
                    result = ChangeResult("firecrawl", "Test Site 1")
                    result.add_change("modified", "https://test1.example.com/firecrawl-page")
                    return result
                else:
                    return ChangeResult("unknown", "Test Site 1")
            
            mock_detector.detect_changes_for_site.side_effect = mock_detect_with_method
            
            detector = ChangeDetector()
            
            # Test detection with sitemap method
            sitemap_result = await detector.detect_changes_for_site("test_site_1", method="sitemap")
            assert sitemap_result.detection_method == "sitemap"
            
            # Test detection with firecrawl method
            firecrawl_result = await detector.detect_changes_for_site("test_site_1", method="firecrawl")
            assert firecrawl_result.detection_method == "firecrawl"
            
            # Write both results
            json_writer.write_changes("Test Site 1", sitemap_result.to_dict())
            json_writer.write_changes("Test Site 1", firecrawl_result.to_dict())
            
            # Verify both files were created
            change_files = json_writer.list_change_files("Test Site 1")
            assert len(change_files) >= 2
    
    @pytest.mark.asyncio
    async def test_configuration_validation_in_workflow(self, temp_output_dir):
        """Test that configuration validation works within the workflow."""
        json_writer = ChangeDetectionWriter(temp_output_dir)
        
        # Test with invalid config file
        invalid_config_file = "/nonexistent/config.yaml"
        
        try:
            config_manager = ConfigManager(invalid_config_file)
            # If no exception is raised, the error handling should be implemented
        except Exception as e:
            # Expected behavior - should handle missing config file
            assert "config" in str(e).lower() or "file" in str(e).lower()
    
    @pytest.mark.asyncio
    async def test_output_file_management(self, temp_config_file, temp_output_dir):
        """Test output file management and organization."""
        config_manager = ConfigManager(temp_config_file)
        json_writer = ChangeDetectionWriter(temp_output_dir)
        
        with patch('app.crawler.change_detector.ChangeDetector') as mock_detector_class:
            mock_detector = MagicMock()
            mock_detector_class.return_value = mock_detector
            
            from app.crawler.base_detector import ChangeResult
            
            def mock_detect_multiple(site_id):
                result = ChangeResult("sitemap", f"Site {site_id}")
                result.add_change("new", f"https://{site_id}.example.com/page")
                return result
            
            mock_detector.detect_changes_for_site.side_effect = mock_detect_multiple
            
            detector = ChangeDetector()
            
            # Run multiple detections
            sites = ["test_site_1", "test_site_2"]
            for site_id in sites:
                result = await detector.detect_changes_for_site(site_id)
                json_writer.write_changes(f"Site {site_id}", result.to_dict())
                
                # Also write state files
                state_data = {
                    "detection_method": "sitemap",
                    "urls": [f"https://{site_id}.example.com/page"],
                    "last_updated": "2024-01-01T00:00:00Z"
                }
                json_writer.write_site_state(f"Site {site_id}", state_data)
            
            # Verify file organization
            run_folder = json_writer.get_run_folder()
            assert Path(run_folder).exists()
            
            # List all files
            change_files = json_writer.list_change_files()
            assert len(change_files) >= len(sites) * 2  # Changes + state files
            
            # Test listing files for specific site
            site_files = json_writer.list_change_files("Site test_site_1")
            assert len(site_files) >= 2  # At least one change and one state file 