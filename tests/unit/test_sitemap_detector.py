# ==============================================================================
# test_sitemap_detector.py — Unit Tests for Sitemap-based Change Detection
# ==============================================================================
# Purpose: Test SitemapDetector class functionality
# ==============================================================================

import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from aioresponses import aioresponses
from app.crawler.sitemap_detector import SitemapDetector
from app.utils.config import SiteConfig


class TestSitemapDetector:
    """Test cases for SitemapDetector class."""
    
    @pytest.fixture
    def site_config(self):
        """Create a test site configuration."""
        return SiteConfig(
            name='Test Site',
            url='https://example.com',
            sitemap_url='https://example.com/sitemap.xml'
        )
    
    @pytest.fixture
    def detector(self, site_config):
        """Create a SitemapDetector instance."""
        return SitemapDetector(site_config)
    
    def test_sitemap_detector_initialization(self, detector, site_config):
        """Test SitemapDetector initialization."""
        assert detector.site_config == site_config
        assert detector.site_name == 'Test Site'
        assert detector.site_url == 'https://example.com'
        assert detector.sitemap_url == 'https://example.com/sitemap.xml'
    
    def test_guess_sitemap_url(self, site_config):
        """Test sitemap URL guessing when not provided."""
        site_config.sitemap_url = None
        detector = SitemapDetector(site_config)
        
        assert detector.sitemap_url == 'https://example.com/sitemap.xml'
    
    @pytest.mark.asyncio
    async def test_get_current_state_success(self, detector):
        """Test successful current state retrieval."""
        mock_urls = ['https://example.com/page1', 'https://example.com/page2']
        mock_sitemap_info = {'type': 'single_sitemap', 'total_urls': 2}
        
        with patch.object(detector, '_fetch_all_sitemap_urls', return_value=(mock_urls, mock_sitemap_info)):
            state = await detector.get_current_state()
            
            assert state['detection_method'] == 'sitemap'
            assert state['sitemap_url'] == 'https://example.com/sitemap.xml'
            assert state['urls'] == mock_urls
            assert state['total_urls'] == 2
            assert state['sitemap_info'] == mock_sitemap_info
            assert 'captured_at' in state
            assert state['site_url'] == 'https://example.com'
    
    @pytest.mark.asyncio
    async def test_get_current_state_error(self, detector):
        """Test current state retrieval with error."""
        with patch.object(detector, '_fetch_all_sitemap_urls', side_effect=Exception('Network error')):
            state = await detector.get_current_state()
            
            assert state['detection_method'] == 'sitemap'
            assert state['sitemap_url'] == 'https://example.com/sitemap.xml'
            assert state['urls'] == []
            assert state['total_urls'] == 0
            assert state['error'] == 'Network error'
            assert 'captured_at' in state
    
    @pytest.mark.asyncio
    async def test_detect_changes_first_run(self, detector):
        """Test change detection on first run (no previous state)."""
        mock_urls = ['https://example.com/page1', 'https://example.com/page2']
        mock_sitemap_info = {'type': 'single_sitemap', 'total_urls': 2}
        
        with patch.object(detector, '_fetch_all_sitemap_urls', return_value=(mock_urls, mock_sitemap_info)):
            result = await detector.detect_changes()
            
            assert result.detection_method == 'sitemap'
            assert result.site_name == 'Test Site'
            assert len(result.changes) == 0
            assert result.metadata['message'] == 'First run - no previous state to compare'
            assert result.metadata['current_urls'] == 2
    
    @pytest.mark.asyncio
    async def test_detect_changes_new_urls(self, detector):
        """Test change detection with new URLs."""
        previous_state = {
            'urls': ['https://example.com/page1'],
            'total_urls': 1
        }
        
        current_urls = ['https://example.com/page1', 'https://example.com/page2']
        mock_sitemap_info = {'type': 'single_sitemap', 'total_urls': 2}
        
        with patch.object(detector, '_fetch_all_sitemap_urls', return_value=(current_urls, mock_sitemap_info)):
            result = await detector.detect_changes(previous_state)
            
            assert result.detection_method == 'sitemap'
            assert result.site_name == 'Test Site'
            assert len(result.changes) == 1
            assert result.changes[0]['change_type'] == 'new'
            assert result.changes[0]['url'] == 'https://example.com/page2'
            assert result.metadata['new_urls'] == 1
            assert result.metadata['deleted_urls'] == 0
    
    @pytest.mark.asyncio
    async def test_detect_changes_deleted_urls(self, detector):
        """Test change detection with deleted URLs."""
        previous_state = {
            'urls': ['https://example.com/page1', 'https://example.com/page2'],
            'total_urls': 2
        }
        
        current_urls = ['https://example.com/page1']
        mock_sitemap_info = {'type': 'single_sitemap', 'total_urls': 1}
        
        with patch.object(detector, '_fetch_all_sitemap_urls', return_value=(current_urls, mock_sitemap_info)):
            result = await detector.detect_changes(previous_state)
            
            assert result.detection_method == 'sitemap'
            assert result.site_name == 'Test Site'
            assert len(result.changes) == 1
            assert result.changes[0]['change_type'] == 'deleted'
            assert result.changes[0]['url'] == 'https://example.com/page2'
            assert result.metadata['new_urls'] == 0
            assert result.metadata['deleted_urls'] == 1
    
    @pytest.mark.asyncio
    async def test_detect_changes_no_changes(self, detector):
        """Test change detection with no changes."""
        previous_state = {
            'urls': ['https://example.com/page1', 'https://example.com/page2'],
            'total_urls': 2
        }
        
        current_urls = ['https://example.com/page1', 'https://example.com/page2']
        mock_sitemap_info = {'type': 'single_sitemap', 'total_urls': 2}
        
        with patch.object(detector, '_fetch_all_sitemap_urls', return_value=(current_urls, mock_sitemap_info)):
            result = await detector.detect_changes(previous_state)
            
            assert result.detection_method == 'sitemap'
            assert result.site_name == 'Test Site'
            assert len(result.changes) == 0
            assert result.metadata['new_urls'] == 0
            assert result.metadata['deleted_urls'] == 0
    
    @pytest.mark.asyncio
    async def test_detect_changes_error(self, detector):
        """Test change detection with error."""
        with patch.object(detector, '_fetch_all_sitemap_urls', side_effect=Exception('Network error')):
            result = await detector.detect_changes()
            
            assert result.detection_method == 'sitemap'
            assert result.site_name == 'Test Site'
            assert len(result.changes) == 0
            assert 'error' in result.metadata
            assert result.metadata['error'] == 'Network error'
    
    @pytest.mark.asyncio
    async def test_fetch_all_sitemap_urls_single_sitemap(self, detector):
        """Test fetching URLs from a single sitemap."""
        sitemap_content = '''<?xml version="1.0" encoding="UTF-8"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <url>
                <loc>https://example.com/page1</loc>
            </url>
            <url>
                <loc>https://example.com/page2</loc>
            </url>
        </urlset>'''
        
        with aioresponses() as m:
            m.get('https://example.com/sitemap.xml', status=200, body=sitemap_content)
            
            urls, sitemap_info = await detector._fetch_all_sitemap_urls()
            
            assert urls == ['https://example.com/page1', 'https://example.com/page2']
            assert sitemap_info['type'] == 'single_sitemap'
            assert sitemap_info['total_urls'] == 2
    
    @pytest.mark.asyncio
    async def test_fetch_all_sitemap_urls_sitemap_index(self, detector):
        """Test fetching URLs from a sitemap index."""
        index_content = '''<?xml version="1.0" encoding="UTF-8"?>
        <sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <sitemap>
                <loc>https://example.com/sitemap1.xml</loc>
            </sitemap>
            <sitemap>
                <loc>https://example.com/sitemap2.xml</loc>
            </sitemap>
        </sitemapindex>'''
        
        sitemap1_content = '''<?xml version="1.0" encoding="UTF-8"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <url>
                <loc>https://example.com/page1</loc>
            </url>
        </urlset>'''
        
        sitemap2_content = '''<?xml version="1.0" encoding="UTF-8"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <url>
                <loc>https://example.com/page2</loc>
            </url>
        </urlset>'''
        
        with aioresponses() as m:
            m.get('https://example.com/sitemap.xml', status=200, body=index_content)
            m.get('https://example.com/sitemap1.xml', status=200, body=sitemap1_content)
            m.get('https://example.com/sitemap2.xml', status=200, body=sitemap2_content)
            
            urls, sitemap_info = await detector._fetch_all_sitemap_urls()
            
            assert set(urls) == {'https://example.com/page1', 'https://example.com/page2'}
            assert sitemap_info['type'] == 'sitemap_index'
            assert sitemap_info['total_urls'] == 2
            assert sitemap_info['total_sitemaps'] == 2
    
    @pytest.mark.asyncio
    async def test_fetch_all_sitemap_urls_http_error(self, detector):
        """Test fetching URLs with HTTP error."""
        with aioresponses() as m:
            m.get('https://example.com/sitemap.xml', status=404)
            
            with pytest.raises(Exception, match='Failed to fetch sitemap: 404'):
                await detector._fetch_all_sitemap_urls()
    
    @pytest.mark.asyncio
    async def test_fetch_all_sitemap_urls_network_error(self, detector):
        """Test fetching URLs with network error."""
        with aioresponses() as m:
            m.get('https://example.com/sitemap.xml', exception=Exception('Network error'))
            
            with pytest.raises(Exception, match='Network error'):
                await detector._fetch_all_sitemap_urls()
    
    def test_is_sitemap_index_true(self, detector):
        """Test sitemap index detection with valid index."""
        index_content = '''<?xml version="1.0" encoding="UTF-8"?>
        <sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <sitemap>
                <loc>https://example.com/sitemap1.xml</loc>
            </sitemap>
        </sitemapindex>'''
        
        assert detector._is_sitemap_index(index_content) is True
    
    def test_is_sitemap_index_false(self, detector):
        """Test sitemap index detection with regular sitemap."""
        sitemap_content = '''<?xml version="1.0" encoding="UTF-8"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <url>
                <loc>https://example.com/page1</loc>
            </url>
        </urlset>'''
        
        assert detector._is_sitemap_index(sitemap_content) is False
    
    def test_is_sitemap_index_invalid_xml(self, detector):
        """Test sitemap index detection with invalid XML."""
        invalid_content = 'invalid xml content'
        
        assert detector._is_sitemap_index(invalid_content) is False
    
    def test_parse_sitemap_index(self, detector):
        """Test parsing sitemap index XML."""
        index_content = '''<?xml version="1.0" encoding="UTF-8"?>
        <sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <sitemap>
                <loc>https://example.com/sitemap1.xml</loc>
            </sitemap>
            <sitemap>
                <loc>https://example.com/sitemap2.xml</loc>
            </sitemap>
        </sitemapindex>'''
        
        sitemap_urls = detector._parse_sitemap_index(index_content)
        
        assert sitemap_urls == [
            'https://example.com/sitemap1.xml',
            'https://example.com/sitemap2.xml'
        ]
    
    def test_parse_sitemap_index_invalid_xml(self, detector):
        """Test parsing invalid sitemap index XML."""
        invalid_content = 'invalid xml content'
        
        with pytest.raises(Exception, match='Failed to parse sitemap index XML'):
            detector._parse_sitemap_index(invalid_content)
    
    def test_parse_sitemap(self, detector):
        """Test parsing regular sitemap XML."""
        sitemap_content = '''<?xml version="1.0" encoding="UTF-8"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <url>
                <loc>https://example.com/page1</loc>
            </url>
            <url>
                <loc>https://example.com/page2</loc>
            </url>
        </urlset>'''
        
        urls = detector._parse_sitemap(sitemap_content)
        
        assert urls == ['https://example.com/page1', 'https://example.com/page2']
    
    def test_parse_sitemap_invalid_xml(self, detector):
        """Test parsing invalid sitemap XML."""
        invalid_content = 'invalid xml content'
        
        with pytest.raises(Exception, match='Failed to parse sitemap XML'):
            detector._parse_sitemap(invalid_content)
    
    def test_extract_last_modified(self, detector):
        """Test extracting last modified date from sitemap."""
        sitemap_content = '''<?xml version="1.0" encoding="UTF-8"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <lastmod>2023-01-01T00:00:00Z</lastmod>
            <url>
                <loc>https://example.com/page1</loc>
            </url>
        </urlset>'''
        
        last_modified = detector._extract_last_modified(sitemap_content)
        
        assert last_modified == '2023-01-01T00:00:00Z'
    
    def test_extract_last_modified_not_found(self, detector):
        """Test extracting last modified date when not present."""
        sitemap_content = '''<?xml version="1.0" encoding="UTF-8"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <url>
                <loc>https://example.com/page1</loc>
            </url>
        </urlset>'''
        
        last_modified = detector._extract_last_modified(sitemap_content)
        
        assert last_modified is None 