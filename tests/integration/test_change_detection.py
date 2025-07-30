# ==============================================================================
# test_change_detection.py — Integration Tests for Change Detection System
# ==============================================================================
# Purpose: Test the complete change detection workflow
# ==============================================================================

import pytest
import asyncio
import tempfile
import yaml
from unittest.mock import patch, MagicMock, AsyncMock
from pathlib import Path

from app.crawler.change_detector import ChangeDetector
from app.utils.config import SiteConfig


class TestChangeDetectionIntegration:
    """Integration tests for the change detection system."""
    
    @pytest.fixture
    def temp_config_file(self):
        """Create a temporary configuration file for testing."""
        config_data = {
            'sites': {
                'test_site_1': {
                    'name': 'Test Site 1',
                    'url': 'https://test1.example.com/',
                    'sitemap_url': 'https://test1.example.com/sitemap.xml',
                    'detection_methods': ['sitemap'],
                    'check_interval_minutes': 1440,
                    'is_active': True
                },
                'test_site_2': {
                    'name': 'Test Site 2',
                    'url': 'https://test2.example.com/',
                    'sitemap_url': 'https://test2.example.com/sitemap.xml',
                    'detection_methods': ['sitemap'],
                    'check_interval_minutes': 1440,
                    'is_active': True
                }
            },
            'firecrawl': {
                'api_key': 'test_key',
                'base_url': 'https://api.firecrawl.dev'
            },
            'system': {
                'output_directory': 'output',
                'log_level': 'INFO',
                'max_retries': 3,
                'timeout_seconds': 30
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            yield f.name
        
        # Cleanup
        Path(f.name).unlink(missing_ok=True)
    
    @pytest.fixture
    def mock_sitemap_responses(self):
        """Mock sitemap responses for testing."""
        return {
            'https://test1.example.com/sitemap.xml': '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://test1.example.com/page1</loc>
        <lastmod>2024-01-01T00:00:00Z</lastmod>
    </url>
    <url>
        <loc>https://test1.example.com/page2</loc>
        <lastmod>2024-01-01T00:00:00Z</lastmod>
    </url>
</urlset>''',
            'https://test2.example.com/sitemap.xml': '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://test2.example.com/page1</loc>
        <lastmod>2024-01-01T00:00:00Z</lastmod>
    </url>
</urlset>'''
        }
    
    @pytest.mark.integration
    def test_change_detector_initialization(self, temp_config_file):
        """Test ChangeDetector initialization."""
        detector = ChangeDetector(temp_config_file)
        assert detector is not None
        assert hasattr(detector, 'config_manager')
        assert len(detector.config_manager.sites) == 2
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_detect_changes_for_site(self, temp_config_file, mock_sitemap_responses):
        """Test change detection for a single site."""
        with patch('aiohttp.ClientSession.get') as mock_get:
            # Mock successful responses
            mock_response = MagicMock()
            mock_response.status = 200
            
            async def mock_text():
                return mock_sitemap_responses["https://test1.example.com/sitemap.xml"]
            
            mock_response.text = mock_text
            
            mock_get.return_value.__aenter__.return_value = mock_response
            
            detector = ChangeDetector(temp_config_file)
            results = await detector.detect_changes_for_site("test_site_1")
            
            assert results is not None
            assert "methods" in results
            assert "sitemap" in results["methods"]
            assert results["methods"]["sitemap"]["detection_method"] == "sitemap"
            assert results["methods"]["sitemap"]["site_name"] == "Test Site 1"
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_detect_changes_for_all_sites(self, temp_config_file, mock_sitemap_responses):
        """Test change detection for all sites."""
        with patch('aiohttp.ClientSession.get') as mock_get:
            # Mock successful responses for both sites
            mock_response = MagicMock()
            mock_response.status = 200
            
            async def mock_text():
                # Return different content based on URL
                if "test1.example.com" in str(mock_get.call_args):
                    return mock_sitemap_responses["https://test1.example.com/sitemap.xml"]
                else:
                    return mock_sitemap_responses["https://test2.example.com/sitemap.xml"]
            
            mock_response.text = mock_text
            mock_get.return_value.__aenter__.return_value = mock_response
            
            detector = ChangeDetector(temp_config_file)
            results = await detector.detect_changes_for_all_sites()
            
            assert results is not None
            assert "sites" in results
            assert "test_site_1" in results["sites"]
            assert "test_site_2" in results["sites"]
            assert len(results["sites"]) == 2
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_change_detection_with_previous_state(self, temp_config_file, mock_sitemap_responses):
        """Test change detection when previous state exists."""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status = 200
            
            async def mock_text():
                return mock_sitemap_responses["https://test1.example.com/sitemap.xml"]
            
            mock_response.text = mock_text
            mock_get.return_value.__aenter__.return_value = mock_response
            
            detector = ChangeDetector(temp_config_file)
            
            # First run to establish baseline
            results1 = await detector.detect_changes_for_site("test_site_1")
            
            # Second run should detect no changes since it's the same content
            results2 = await detector.detect_changes_for_site("test_site_1")
            
            assert results1 is not None
            assert results2 is not None
            assert "methods" in results1
            assert "methods" in results2
            assert "sitemap" in results1["methods"]
            assert "sitemap" in results2["methods"]
    
    @pytest.mark.integration
    def test_error_handling_invalid_site(self, temp_config_file):
        """Test error handling for invalid site."""
        detector = ChangeDetector(temp_config_file)
        
        # get_site_status returns an error dictionary for invalid sites
        status = detector.get_site_status("invalid_site")
        assert "error" in status
        assert status["error"] == "Site 'invalid_site' not found"
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_error_handling_network_failure(self, temp_config_file):
        """Test error handling for network failures."""
        with patch('aiohttp.ClientSession.get') as mock_get:
            # Mock network failure
            mock_get.side_effect = Exception("Network error")
            
            detector = ChangeDetector(temp_config_file)
            results = await detector.detect_changes_for_site("test_site_1")
            
            assert results is not None
            assert "methods" in results
            assert "sitemap" in results["methods"]
            assert "error" in results["methods"]["sitemap"]["metadata"]
            assert results["methods"]["sitemap"]["metadata"]["error"] == "Network error"
    
    @pytest.mark.integration
    def test_list_sites(self, temp_config_file):
        """Test listing all sites."""
        detector = ChangeDetector(temp_config_file)
        sites = detector.list_sites()
        
        assert len(sites) == 2
        site_ids = [site["site_id"] for site in sites]
        assert "test_site_1" in site_ids
        assert "test_site_2" in site_ids
        
        site1 = next(site for site in sites if site["site_id"] == "test_site_1")
        site2 = next(site for site in sites if site["site_id"] == "test_site_2")
        assert site1["name"] == "Test Site 1"
        assert site2["name"] == "Test Site 2"
    
    @pytest.mark.integration
    def test_get_site_status(self, temp_config_file):
        """Test getting status for a specific site."""
        detector = ChangeDetector(temp_config_file)
        status = detector.get_site_status("test_site_1")
        
        assert status is not None
        assert status["site_id"] == "test_site_1"
        assert status["site_name"] == "Test Site 1"
        assert status["url"] == "https://test1.example.com/"
        assert status["is_active"] is True
    
    @pytest.mark.integration
    def test_get_site_status_invalid(self, temp_config_file):
        """Test getting status for an invalid site."""
        detector = ChangeDetector(temp_config_file)
        status = detector.get_site_status("invalid_site")
        
        assert "error" in status
        assert status["error"] == "Site 'invalid_site' not found" 