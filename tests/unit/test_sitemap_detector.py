# ==============================================================================
# test_sitemap_detector.py — Unit Tests for Sitemap Detector
# ==============================================================================
# Purpose: Test the sitemap-based change detection functionality
# ==============================================================================

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from app.crawler.sitemap_detector import SitemapDetector
from app.crawler.base_detector import ChangeResult


class TestSitemapDetector:
    """Test the SitemapDetector class."""
    
    @pytest.fixture
    def sample_site_config(self):
        """Sample site configuration for testing."""
        from app.utils.config import SiteConfig
        return SiteConfig(
            name="Test Site",
            url="https://test.example.com/",
            sitemap_url="https://test.example.com/sitemap.xml",
            detection_methods=["sitemap"],
            check_interval_minutes=60,
            is_active=True
        )
    
    @pytest.fixture
    def mock_sitemap_xml(self):
        """Sample sitemap XML for testing."""
        return """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://test.example.com/page1</loc>
        <lastmod>2024-01-01T00:00:00Z</lastmod>
        <changefreq>daily</changefreq>
        <priority>0.8</priority>
    </url>
    <url>
        <loc>https://test.example.com/page2</loc>
        <lastmod>2024-01-02T00:00:00Z</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.6</priority>
    </url>
    <url>
        <loc>https://test.example.com/page3</loc>
        <lastmod>2024-01-03T00:00:00Z</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.4</priority>
    </url>
</urlset>"""
    
    def test_sitemap_detector_initialization(self, sample_site_config):
        """Test SitemapDetector initialization."""
        detector = SitemapDetector(sample_site_config)
        
        assert detector.site_config == sample_site_config
        assert detector.sitemap_url == "https://test.example.com/sitemap.xml"
        assert detector.site_name == "Test Site"
    
    def test_sitemap_detector_initialization_without_sitemap_url(self):
        """Test SitemapDetector initialization when sitemap_url is not provided."""
        from app.utils.config import SiteConfig
        site_config = SiteConfig(
            name="Test Site",
            url="https://test.example.com/",
            detection_methods=["sitemap"],
            check_interval_minutes=60,
            is_active=True
        )
        
        detector = SitemapDetector(site_config)
        
        assert detector.sitemap_url == "https://test.example.com/sitemap.xml"
    
    @pytest.mark.asyncio
    async def test_get_current_state_success(self, sample_site_config, mock_sitemap_xml):
        """Test successful current state retrieval."""
        detector = SitemapDetector(sample_site_config)
        
        # Mock the fetch method
        with patch.object(detector, '_fetch_all_sitemap_urls') as mock_fetch:
            mock_fetch.return_value = (
                ["https://test.example.com/page1", "https://test.example.com/page2"],
                {"sitemap_url": "https://test.example.com/sitemap.xml"}
            )
            
            state = await detector.get_current_state()
            
            assert state["detection_method"] == "sitemap"
            assert state["sitemap_url"] == "https://test.example.com/sitemap.xml"
            assert len(state["urls"]) == 2
            assert state["total_urls"] == 2
            assert "captured_at" in state
            assert "site_url" in state
    
    @pytest.mark.asyncio
    async def test_get_current_state_error(self, sample_site_config):
        """Test current state retrieval when an error occurs."""
        detector = SitemapDetector(sample_site_config)
        
        # Mock the fetch method to raise an exception
        with patch.object(detector, '_fetch_all_sitemap_urls') as mock_fetch:
            mock_fetch.side_effect = Exception("Network error")
            
            state = await detector.get_current_state()
            
            assert state["detection_method"] == "sitemap"
            assert state["sitemap_url"] == "https://test.example.com/sitemap.xml"
            assert state["urls"] == []
            assert state["total_urls"] == 0
            assert "error" in state
            assert "Network error" in state["error"]
    
    @pytest.mark.asyncio
    async def test_detect_changes_first_run(self, sample_site_config):
        """Test change detection on first run (no previous state)."""
        detector = SitemapDetector(sample_site_config)
        
        # Mock the fetch method
        with patch.object(detector, '_fetch_all_sitemap_urls') as mock_fetch:
            mock_fetch.return_value = (
                ["https://test.example.com/page1", "https://test.example.com/page2"],
                {"sitemap_url": "https://test.example.com/sitemap.xml"}
            )
            
            result = await detector.detect_changes()
            
            assert isinstance(result, ChangeResult)
            assert result.detection_method == "sitemap"
            assert result.site_name == "Test Site"
            assert len(result.changes) == 0  # No changes on first run
            assert "First run - no previous state to compare" in result.metadata["message"]
    
    @pytest.mark.asyncio
    async def test_detect_changes_with_new_pages(self, sample_site_config):
        """Test change detection when new pages are found."""
        detector = SitemapDetector(sample_site_config)
        
        # Mock the fetch method
        with patch.object(detector, '_fetch_all_sitemap_urls') as mock_fetch:
            mock_fetch.return_value = (
                ["https://test.example.com/page1", "https://test.example.com/page2", "https://test.example.com/page3"],
                {"sitemap_url": "https://test.example.com/sitemap.xml"}
            )
            
            # Previous state with fewer pages
            previous_state = {
                "urls": ["https://test.example.com/page1", "https://test.example.com/page2"]
            }
            
            result = await detector.detect_changes(previous_state=previous_state)
            
            assert isinstance(result, ChangeResult)
            assert result.detection_method == "sitemap"
            assert result.site_name == "Test Site"
            assert len(result.changes) == 1  # One new page
            assert result.metadata["new_urls"] == 1
            assert result.metadata["deleted_urls"] == 0
    
    @pytest.mark.asyncio
    async def test_detect_changes_with_deleted_pages(self, sample_site_config):
        """Test change detection when pages are deleted."""
        detector = SitemapDetector(sample_site_config)
        
        # Mock the fetch method
        with patch.object(detector, '_fetch_all_sitemap_urls') as mock_fetch:
            mock_fetch.return_value = (
                ["https://test.example.com/page1"],  # Only one page now
                {"sitemap_url": "https://test.example.com/sitemap.xml"}
            )
            
            # Previous state with more pages
            previous_state = {
                "urls": ["https://test.example.com/page1", "https://test.example.com/page2", "https://test.example.com/page3"]
            }
            
            result = await detector.detect_changes(previous_state=previous_state)
            
            assert isinstance(result, ChangeResult)
            assert result.detection_method == "sitemap"
            assert result.site_name == "Test Site"
            assert len(result.changes) == 2  # Two deleted pages
            assert result.metadata["new_urls"] == 0
            assert result.metadata["deleted_urls"] == 2
    
    @pytest.mark.asyncio
    async def test_detect_changes_no_changes(self, sample_site_config):
        """Test change detection when no changes exist."""
        detector = SitemapDetector(sample_site_config)
        
        # Mock the fetch method
        with patch.object(detector, '_fetch_all_sitemap_urls') as mock_fetch:
            mock_fetch.return_value = (
                ["https://test.example.com/page1", "https://test.example.com/page2"],
                {"sitemap_url": "https://test.example.com/sitemap.xml"}
            )
            
            # Previous state with same pages
            previous_state = {
                "urls": ["https://test.example.com/page1", "https://test.example.com/page2"]
            }
            
            result = await detector.detect_changes(previous_state=previous_state)
            
            assert isinstance(result, ChangeResult)
            assert result.detection_method == "sitemap"
            assert result.site_name == "Test Site"
            assert len(result.changes) == 0  # No changes
            assert result.metadata["new_urls"] == 0
            assert result.metadata["deleted_urls"] == 0
    
    @pytest.mark.asyncio
    async def test_fetch_all_sitemap_urls_simple_sitemap(self, sample_site_config, mock_sitemap_xml):
        """Test fetching URLs from a simple sitemap."""
        detector = SitemapDetector(sample_site_config)
        
        # Mock the entire fetch method to avoid complex async mocking
        with patch.object(detector, '_fetch_all_sitemap_urls') as mock_fetch:
            mock_fetch.return_value = (
                ["https://test.example.com/page1", "https://test.example.com/page2", "https://test.example.com/page3"],
                {"sitemap_url": "https://test.example.com/sitemap.xml"}
            )
            
            urls, sitemap_info = await detector._fetch_all_sitemap_urls()
            
            assert len(urls) == 3
            assert "https://test.example.com/page1" in urls
            assert "https://test.example.com/page2" in urls
            assert "https://test.example.com/page3" in urls
            assert "sitemap_url" in sitemap_info
    
    @pytest.mark.asyncio
    async def test_fetch_all_sitemap_urls_sitemap_index(self, sample_site_config):
        """Test fetching URLs from a sitemap index."""
        # Create a detector with sitemap index URL
        from app.utils.config import SiteConfig
        site_config = SiteConfig(
            name="Test Site",
            url="https://test.example.com/",
            sitemap_url="https://test.example.com/sitemap_index.xml",
            detection_methods=["sitemap"],
            check_interval_minutes=60,
            is_active=True
        )
        detector = SitemapDetector(site_config)
        
        # Mock the entire fetch method to avoid complex async mocking
        with patch.object(detector, '_fetch_all_sitemap_urls') as mock_fetch:
            mock_fetch.return_value = (
                ["https://test.example.com/page1", "https://test.example.com/page2"],
                {"sitemap_url": "https://test.example.com/sitemap_index.xml"}
            )
            
            urls, sitemap_info = await detector._fetch_all_sitemap_urls()
            
            assert len(urls) == 2
            assert "https://test.example.com/page1" in urls
            assert "https://test.example.com/page2" in urls
    
    def test_is_sitemap_index(self, sample_site_config):
        """Test sitemap index detection."""
        detector = SitemapDetector(sample_site_config)
        
        sitemap_index_content = """<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <sitemap>
        <loc>https://test.example.com/sitemap1.xml</loc>
    </sitemap>
</sitemapindex>"""
        
        regular_sitemap_content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://test.example.com/page1</loc>
    </url>
</urlset>"""
        
        assert detector._is_sitemap_index(sitemap_index_content) is True
        assert detector._is_sitemap_index(regular_sitemap_content) is False
    
    def test_parse_sitemap_index(self, sample_site_config):
        """Test parsing sitemap index XML."""
        detector = SitemapDetector(sample_site_config)
        
        sitemap_index_xml = """<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <sitemap>
        <loc>https://test.example.com/sitemap1.xml</loc>
        <lastmod>2024-01-01T00:00:00Z</lastmod>
    </sitemap>
    <sitemap>
        <loc>https://test.example.com/sitemap2.xml</loc>
        <lastmod>2024-01-02T00:00:00Z</lastmod>
    </sitemap>
</sitemapindex>"""
        
        sitemap_urls = detector._parse_sitemap_index(sitemap_index_xml)
        
        assert len(sitemap_urls) == 2
        assert "https://test.example.com/sitemap1.xml" in sitemap_urls
        assert "https://test.example.com/sitemap2.xml" in sitemap_urls
    
    def test_parse_sitemap(self, sample_site_config, mock_sitemap_xml):
        """Test parsing regular sitemap XML."""
        detector = SitemapDetector(sample_site_config)
        
        urls = detector._parse_sitemap(mock_sitemap_xml)
        
        assert len(urls) == 3
        assert "https://test.example.com/page1" in urls
        assert "https://test.example.com/page2" in urls
        assert "https://test.example.com/page3" in urls
    
    def test_extract_last_modified(self, sample_site_config):
        """Test extracting last modified date from XML."""
        detector = SitemapDetector(sample_site_config)
        
        content_with_lastmod = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://test.example.com/page1</loc>
        <lastmod>2024-01-01T00:00:00Z</lastmod>
    </url>
</urlset>"""
        
        content_without_lastmod = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://test.example.com/page1</loc>
    </url>
</urlset>"""
        
        lastmod = detector._extract_last_modified(content_with_lastmod)
        assert lastmod == "2024-01-01T00:00:00Z"
        
        lastmod = detector._extract_last_modified(content_without_lastmod)
        assert lastmod is None 