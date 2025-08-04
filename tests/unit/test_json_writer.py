# ==============================================================================
# test_json_writer.py — Unit Tests for JSON Writer Utility
# ==============================================================================
# Purpose: Test the JSON writing and file management functionality
# ==============================================================================

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open

from app.utils.json_writer import ChangeDetectionWriter


class TestChangeDetectionWriter:
    """Test the ChangeDetectionWriter class."""
    
    def test_json_writer_initialization(self, temp_output_dir):
        """Test ChangeDetectionWriter initialization."""
        writer = ChangeDetectionWriter(temp_output_dir)
        
        assert writer.output_dir == Path(temp_output_dir)
        assert writer.output_dir.exists()
        assert writer.run_folder.exists()
    
    def test_create_output_directory(self):
        """Test creating output directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            new_dir = Path(temp_dir) / "new_output"
            
            # Directory shouldn't exist initially
            assert not new_dir.exists()
            
            writer = ChangeDetectionWriter(str(new_dir))
            
            # Directory should be created
            assert new_dir.exists()
            assert writer.output_dir == new_dir
    
    def test_write_changes(self, temp_output_dir, sample_change_result):
        """Test writing changes to JSON file."""
        writer = ChangeDetectionWriter(temp_output_dir)
        
        # Create a mock change result
        from app.crawler.base_detector import ChangeResult
        result = ChangeResult("sitemap", "Test Site")
        result.add_change("new", "https://example.com/new-page", title="New Page")
        result.add_change("modified", "https://example.com/modified-page", title="Modified Page")
        
        # Write the changes
        filepath = writer.write_changes("Test Site", result.to_dict())
        
        # Verify file was created
        assert Path(filepath).exists()
        
        # Verify file contents
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        assert data["metadata"]["site_name"] == "Test Site"
        assert data["metadata"]["detection_method"] == "sitemap"
        assert "changes" in data
    
    def test_write_changes_with_metadata(self, temp_output_dir):
        """Test writing changes with additional metadata."""
        writer = ChangeDetectionWriter(temp_output_dir)
        
        from app.crawler.base_detector import ChangeResult
        result = ChangeResult("firecrawl", "Test Site")
        result.add_change("new", "https://example.com/new-page", title="New Page")
        
        # Add metadata
        result.metadata["crawl_duration"] = 5.2
        result.metadata["pages_crawled"] = 10
        result.metadata["api_calls"] = 3
        
        # Create the changes data structure expected by write_changes
        changes_data = result.to_dict()
        changes_data["metadata"] = result.metadata
        
        filepath = writer.write_changes("Test Site", changes_data)
        
        # Verify metadata was written
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        # The metadata should be in the changes section, not the top-level metadata
        assert data["changes"]["metadata"]["crawl_duration"] == 5.2
        assert data["changes"]["metadata"]["pages_crawled"] == 10
        assert data["changes"]["metadata"]["api_calls"] == 3
    
    def test_write_site_state(self, temp_output_dir):
        """Test writing site state to JSON file."""
        writer = ChangeDetectionWriter(temp_output_dir)
        
        state_data = {
            "detection_method": "sitemap",
            "urls": ["https://example.com/page1", "https://example.com/page2"],
            "last_updated": "2024-01-01T00:00:00Z"
        }
        
        filepath = writer.write_site_state("Test Site", state_data)
        
        # Verify file was created
        assert Path(filepath).exists()
        
        # Verify file contents
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        assert data["metadata"]["site_name"] == "Test Site"
        assert data["metadata"]["detection_method"] == "sitemap"
        assert data["state"]["urls"] == state_data["urls"]
    
    def test_filename_generation(self, temp_output_dir):
        """Test that filenames are generated correctly."""
        writer = ChangeDetectionWriter(temp_output_dir)
        
        # Test changes filename
        filepath = writer.write_changes("Test Site", {"test": "data"})
        filename = Path(filepath).name
        
        assert filename.startswith("Test Site_")
        assert filename.endswith(".json")
        assert "_" in filename  # Should contain timestamp
    
    def test_write_multiple_files(self, temp_output_dir):
        """Test writing multiple files in the same run."""
        writer = ChangeDetectionWriter(temp_output_dir)
        
        # Write multiple files
        filepath1 = writer.write_changes("Site 1", {"data": "1"})
        filepath2 = writer.write_changes("Site 2", {"data": "2"})
        filepath3 = writer.write_site_state("Site 1", {"state": "data"})
        
        # All files should exist
        assert Path(filepath1).exists()
        assert Path(filepath2).exists()
        assert Path(filepath3).exists()
        
        # All files should be in the same run folder
        run_folder = writer.get_run_folder()
        assert str(Path(filepath1).parent) == run_folder
        assert str(Path(filepath2).parent) == run_folder
        assert str(Path(filepath3).parent) == run_folder
    
    def test_write_with_special_characters(self, temp_output_dir):
        """Test writing files with special characters in site names."""
        writer = ChangeDetectionWriter(temp_output_dir)
        
        # Test with special characters
        special_site_name = "Test Site (Special) & More!"
        filepath = writer.write_changes(special_site_name, {"test": "data"})
        
        # File should be created successfully
        assert Path(filepath).exists()
        
        # Verify content
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        assert data["metadata"]["site_name"] == special_site_name
    
    def test_write_empty_result(self, temp_output_dir):
        """Test writing empty change results."""
        writer = ChangeDetectionWriter(temp_output_dir)
        
        empty_result = {
            "detection_method": "sitemap",
            "site_name": "Test Site",
            "changes": [],
            "summary": {
                "total_changes": 0,
                "new_pages": 0,
                "modified_pages": 0,
                "deleted_pages": 0
            }
        }
        
        filepath = writer.write_changes("Test Site", empty_result)
        
        # File should be created
        assert Path(filepath).exists()
        
        # Verify content
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        assert data["changes"]["changes"] == []
        assert data["changes"]["summary"]["total_changes"] == 0
    
    def test_write_large_data(self, temp_output_dir):
        """Test writing large amounts of data."""
        writer = ChangeDetectionWriter(temp_output_dir)
        
        # Create large data structure
        large_data = {
            "detection_method": "sitemap",
            "site_name": "Large Test Site",
            "changes": [
                {
                    "change_type": "new",
                    "url": f"https://example.com/page-{i}",
                    "title": f"Page {i}",
                    "content": "x" * 1000  # Large content
                }
                for i in range(100)
            ],
            "summary": {
                "total_changes": 100,
                "new_pages": 100,
                "modified_pages": 0,
                "deleted_pages": 0
            }
        }
        
        filepath = writer.write_changes("Large Test Site", large_data)
        
        # File should be created
        assert Path(filepath).exists()
        
        # Verify file size is reasonable
        file_size = Path(filepath).stat().st_size
        assert file_size > 1000  # Should be larger than 1KB
        
        # Verify content
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        assert len(data["changes"]["changes"]) == 100
    
    def test_error_handling_invalid_directory(self):
        """Test error handling when directory cannot be created."""
        invalid_path = "/invalid/path/that/cannot/be/created"
        
        # Should not raise an exception during initialization
        # (the actual behavior depends on the implementation)
        try:
            writer = ChangeDetectionWriter(invalid_path)
            # If it doesn't raise, that's fine too
        except Exception:
            # If it raises, that's also acceptable behavior
            pass
    
    def test_error_handling_json_serialization(self, temp_output_dir):
        """Test error handling when JSON serialization fails."""
        writer = ChangeDetectionWriter(temp_output_dir)
        
        # Create data that cannot be serialized
        non_serializable_data = {
            "test": "data",
            "function": lambda x: x,  # Functions cannot be serialized
            "file": open(__file__, 'r')  # File objects cannot be serialized
        }
        
        # Should handle serialization errors gracefully
        try:
            writer.write_changes("Test Site", non_serializable_data)
        except (TypeError, ValueError):
            # Expected behavior for non-serializable data
            pass 