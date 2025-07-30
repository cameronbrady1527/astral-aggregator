# ==============================================================================
# conftest.py — Pytest Configuration and Shared Fixtures
# ==============================================================================
# Purpose: Define shared fixtures and configuration for all tests
# ==============================================================================

import pytest
import asyncio
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, AsyncMock
from typing import Dict, Any

# Test configuration
@pytest.fixture(scope="session")
def test_config():
    """Test configuration settings."""
    return {
        "test_sites": {
            "test_site_1": {
                "name": "Test Site 1",
                "url": "https://test1.example.com/",
                "sitemap_url": "https://test1.example.com/sitemap.xml",
                "detection_methods": ["sitemap"],
                "check_interval_minutes": 60,
                "is_active": True
            },
            "test_site_2": {
                "name": "Test Site 2", 
                "url": "https://test2.example.com/",
                "sitemap_url": "https://test2.example.com/sitemap_index.xml",
                "detection_methods": ["sitemap"],
                "check_interval_minutes": 120,
                "is_active": True
            }
        },
        "firecrawl": {
            "api_key": "test-api-key",
            "base_url": "https://api.firecrawl.dev"
        },
        "system": {
            "output_directory": "test_output",
            "log_level": "DEBUG",
            "max_retries": 2,
            "timeout_seconds": 10
        }
    }

@pytest.fixture
def temp_output_dir():
    """Create a temporary output directory for tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

@pytest.fixture
def mock_sitemap_xml():
    """Sample sitemap XML for testing."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://example.com/page1</loc>
        <lastmod>2024-01-01T00:00:00Z</lastmod>
        <changefreq>daily</changefreq>
        <priority>0.8</priority>
    </url>
    <url>
        <loc>https://example.com/page2</loc>
        <lastmod>2024-01-02T00:00:00Z</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.6</priority>
    </url>
    <url>
        <loc>https://example.com/page3</loc>
        <lastmod>2024-01-03T00:00:00Z</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.4</priority>
    </url>
</urlset>"""

@pytest.fixture
def mock_sitemap_index_xml():
    """Sample sitemap index XML for testing."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <sitemap>
        <loc>https://example.com/sitemap1.xml</loc>
        <lastmod>2024-01-01T00:00:00Z</lastmod>
    </sitemap>
    <sitemap>
        <loc>https://example.com/sitemap2.xml</loc>
        <lastmod>2024-01-02T00:00:00Z</lastmod>
    </sitemap>
</sitemapindex>"""

@pytest.fixture
def mock_aiohttp_session():
    """Mock aiohttp session for testing."""
    session = AsyncMock()
    session.get = AsyncMock()
    session.close = AsyncMock()
    return session

@pytest.fixture
def mock_firecrawl_app():
    """Mock Firecrawl app for testing."""
    app = AsyncMock()
    app.crawl = AsyncMock()
    return app

# Async test utilities
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# Test data fixtures
@pytest.fixture
def sample_site_config():
    """Sample site configuration for testing."""
    return {
        "name": "Test Site",
        "url": "https://test.example.com/",
        "sitemap_url": "https://test.example.com/sitemap.xml",
        "detection_methods": ["sitemap"],
        "check_interval_minutes": 60,
        "is_active": True
    }

@pytest.fixture
def sample_change_result():
    """Sample change detection result for testing."""
    return {
        "changes": [
            {
                "change_type": "new",
                "url": "https://example.com/new-page",
                "title": "New Page",
                "detected_at": "2024-01-01T00:00:00Z"
            }
        ],
        "metadata": {
            "total_changes": 1,
            "detection_method": "sitemap",
            "site_name": "Test Site"
        }
    } 