# ==============================================================================
# test_base_detector.py — Unit Tests for Base Detector Classes
# ==============================================================================
# Purpose: Test the base detector classes and change result functionality
# ==============================================================================

import pytest
from datetime import datetime
from unittest.mock import Mock

from app.crawler.base_detector import ChangeResult, BaseDetector
from app.utils.config import SiteConfig


class TestChangeResult:
    """Test the ChangeResult class."""
    
    def test_change_result_initialization(self):
        """Test ChangeResult initialization."""
        result = ChangeResult("sitemap", "Test Site")
        
        assert result.detection_method == "sitemap"
        assert result.site_name == "Test Site"
        assert result.changes == []
        assert result.summary["total_changes"] == 0
        assert result.summary["new_pages"] == 0
        assert result.summary["modified_pages"] == 0
        assert result.summary["deleted_pages"] == 0
        assert result.metadata == {}
    
    def test_add_change_new_page(self):
        """Test adding a new page change."""
        result = ChangeResult("sitemap", "Test Site")
        
        result.add_change("new", "https://example.com/new-page", title="New Page")
        
        assert len(result.changes) == 1
        assert result.changes[0]["change_type"] == "new"
        assert result.changes[0]["url"] == "https://example.com/new-page"
        assert result.changes[0]["title"] == "New Page"
        assert result.summary["total_changes"] == 1
        assert result.summary["new_pages"] == 1
        assert result.summary["modified_pages"] == 0
        assert result.summary["deleted_pages"] == 0
    
    def test_add_change_modified_page(self):
        """Test adding a modified page change."""
        result = ChangeResult("sitemap", "Test Site")
        
        result.add_change("modified", "https://example.com/modified-page", title="Modified Page")
        
        assert len(result.changes) == 1
        assert result.changes[0]["change_type"] == "modified"
        assert result.changes[0]["url"] == "https://example.com/modified-page"
        assert result.changes[0]["title"] == "Modified Page"
        assert result.summary["total_changes"] == 1
        assert result.summary["new_pages"] == 0
        assert result.summary["modified_pages"] == 1
        assert result.summary["deleted_pages"] == 0
    
    def test_add_change_deleted_page(self):
        """Test adding a deleted page change."""
        result = ChangeResult("sitemap", "Test Site")
        
        result.add_change("deleted", "https://example.com/deleted-page", title="Deleted Page")
        
        assert len(result.changes) == 1
        assert result.changes[0]["change_type"] == "deleted"
        assert result.changes[0]["url"] == "https://example.com/deleted-page"
        assert result.changes[0]["title"] == "Deleted Page"
        assert result.summary["total_changes"] == 1
        assert result.summary["new_pages"] == 0
        assert result.summary["modified_pages"] == 0
        assert result.summary["deleted_pages"] == 1
    
    def test_add_multiple_changes(self):
        """Test adding multiple changes and verifying summary."""
        result = ChangeResult("sitemap", "Test Site")
        
        result.add_change("new", "https://example.com/new-page", title="New Page")
        result.add_change("modified", "https://example.com/modified-page", title="Modified Page")
        result.add_change("deleted", "https://example.com/deleted-page", title="Deleted Page")
        result.add_change("new", "https://example.com/another-new-page", title="Another New Page")
        
        assert len(result.changes) == 4
        assert result.summary["total_changes"] == 4
        assert result.summary["new_pages"] == 2
        assert result.summary["modified_pages"] == 1
        assert result.summary["deleted_pages"] == 1
    
    def test_add_change_with_additional_kwargs(self):
        """Test adding a change with additional keyword arguments."""
        result = ChangeResult("sitemap", "Test Site")
        
        result.add_change(
            "modified", 
            "https://example.com/page", 
            title="Page Title",
            content_hash="abc123",
            last_modified="2024-01-01T00:00:00Z",
            custom_field="custom_value"
        )
        
        assert len(result.changes) == 1
        change = result.changes[0]
        assert change["change_type"] == "modified"
        assert change["url"] == "https://example.com/page"
        assert change["title"] == "Page Title"
        assert change["content_hash"] == "abc123"
        assert change["last_modified"] == "2024-01-01T00:00:00Z"
        assert change["custom_field"] == "custom_value"
    
    def test_to_dict(self):
        """Test converting ChangeResult to dictionary."""
        result = ChangeResult("firecrawl", "Test Site")
        result.add_change("new", "https://example.com/new-page", title="New Page")
        result.metadata["crawl_duration"] = 5.2
        result.metadata["pages_crawled"] = 10
        
        result_dict = result.to_dict()
        
        assert result_dict["detection_method"] == "firecrawl"
        assert result_dict["site_name"] == "Test Site"
        assert len(result_dict["changes"]) == 1
        assert result_dict["changes"][0]["change_type"] == "new"
        assert result_dict["changes"][0]["url"] == "https://example.com/new-page"
        assert result_dict["summary"]["total_changes"] == 1
        assert result_dict["summary"]["new_pages"] == 1
        assert result_dict["metadata"]["crawl_duration"] == 5.2
        assert result_dict["metadata"]["pages_crawled"] == 10
        assert "detection_time" in result_dict


class TestBaseDetector:
    """Test the BaseDetector abstract class."""
    
    def test_base_detector_initialization(self):
        """Test BaseDetector initialization with site config."""
        site_config = SiteConfig(
            name="Test Site",
            url="https://test.example.com/",
            sitemap_url="https://test.example.com/sitemap.xml"
        )
        
        # Create a concrete implementation for testing
        class TestDetector(BaseDetector):
            async def detect_changes(self, previous_state=None):
                return self.create_result()
            
            async def get_current_state(self):
                return {"pages": {}}
        
        detector = TestDetector(site_config)
        
        assert detector.site_config == site_config
        assert detector.site_name == "Test Site"
        assert detector.site_url == "https://test.example.com/"
    
    def test_create_result(self):
        """Test creating a ChangeResult instance."""
        site_config = SiteConfig(
            name="Test Site",
            url="https://test.example.com/"
        )
        
        class TestDetector(BaseDetector):
            async def detect_changes(self, previous_state=None):
                return self.create_result()
            
            async def get_current_state(self):
                return {"pages": {}}
        
        detector = TestDetector(site_config)
        result = detector.create_result()
        
        assert isinstance(result, ChangeResult)
        assert result.detection_method == "test"
        assert result.site_name == "Test Site"
    
    def test_base_detector_abstract_methods(self):
        """Test that BaseDetector cannot be instantiated directly."""
        site_config = SiteConfig(
            name="Test Site",
            url="https://test.example.com/"
        )
        
        # Should raise TypeError when trying to instantiate abstract class
        with pytest.raises(TypeError):
            BaseDetector(site_config)
    
    def test_detector_with_custom_site_config_attributes(self):
        """Test BaseDetector with site config that has custom attributes."""
        site_config = SiteConfig(
            name="Test Site",
            url="https://test.example.com/",
            custom_attribute="custom_value",
            another_attribute=123
        )
        
        class TestDetector(BaseDetector):
            async def detect_changes(self, previous_state=None):
                return self.create_result()
            
            async def get_current_state(self):
                return {"pages": {}}
        
        detector = TestDetector(site_config)
        
        # Custom attributes should be accessible
        assert hasattr(detector.site_config, 'custom_attribute')
        assert detector.site_config.custom_attribute == "custom_value"
        assert hasattr(detector.site_config, 'another_attribute')
        assert detector.site_config.another_attribute == 123 