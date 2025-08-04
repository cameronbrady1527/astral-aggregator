# ==============================================================================
# conftest.py — Pytest Configuration and Shared Fixtures
# ==============================================================================
# Purpose: Define shared fixtures and configuration for all tests
# ==============================================================================

import pytest
import asyncio
import tempfile
import os
import json
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any, List
from fastapi.testclient import TestClient
from fastapi import FastAPI

# Import the main app
from app.main import app

# Test configuration
@pytest.fixture(scope="session")
def test_config():
    """Test configuration settings."""
    return {
        "sites": {
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
                "detection_methods": ["sitemap", "firecrawl"],
                "check_interval_minutes": 120,
                "is_active": True
            },
            "test_site_3": {
                "name": "Test Site 3",
                "url": "https://test3.example.com/",
                "sitemap_url": "https://test3.example.com/sitemap.xml",
                "detection_methods": ["firecrawl"],
                "check_interval_minutes": 180,
                "is_active": False
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
def temp_config_file(test_config):
    """Create a temporary config file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        import yaml
        yaml.dump(test_config, f)
        temp_file = f.name
    
    yield temp_file
    
    # Cleanup
    os.unlink(temp_file)

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

@pytest.fixture
def mock_firecrawl_response():
    """Mock Firecrawl API response."""
    return {
        "status": "success",
        "data": [
            {
                "url": "https://example.com/page1",
                "title": "Page 1",
                "content": "This is page 1 content",
                "lastModified": "2024-01-01T00:00:00Z"
            },
            {
                "url": "https://example.com/page2", 
                "title": "Page 2",
                "content": "This is page 2 content",
                "lastModified": "2024-01-02T00:00:00Z"
            }
        ]
    }

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
        "detection_method": "sitemap",
        "site_name": "Test Site",
        "detection_time": "2024-01-01T00:00:00Z",
        "changes": [
            {
                "change_type": "new",
                "url": "https://example.com/new-page",
                "title": "New Page",
                "detected_at": "2024-01-01T00:00:00Z"
            },
            {
                "change_type": "modified",
                "url": "https://example.com/existing-page",
                "title": "Modified Page",
                "detected_at": "2024-01-01T00:00:00Z"
            }
        ],
        "summary": {
            "total_changes": 2,
            "new_pages": 1,
            "modified_pages": 1,
            "deleted_pages": 0
        },
        "metadata": {}
    }

@pytest.fixture
def mock_previous_state():
    """Mock previous state for change detection testing."""
    return {
        "pages": {
            "https://example.com/page1": {
                "title": "Page 1",
                "last_modified": "2024-01-01T00:00:00Z",
                "content_hash": "abc123"
            },
            "https://example.com/page2": {
                "title": "Page 2", 
                "last_modified": "2024-01-02T00:00:00Z",
                "content_hash": "def456"
            }
        },
        "last_updated": "2024-01-02T00:00:00Z"
    }

@pytest.fixture
def mock_current_state():
    """Mock current state for change detection testing."""
    return {
        "pages": {
            "https://example.com/page1": {
                "title": "Page 1 Updated",
                "last_modified": "2024-01-03T00:00:00Z",
                "content_hash": "xyz789"
            },
            "https://example.com/page2": {
                "title": "Page 2",
                "last_modified": "2024-01-02T00:00:00Z", 
                "content_hash": "def456"
            },
            "https://example.com/page3": {
                "title": "New Page 3",
                "last_modified": "2024-01-03T00:00:00Z",
                "content_hash": "new123"
            }
        },
        "last_updated": "2024-01-03T00:00:00Z"
    }

# FastAPI test client
@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    # Ensure routers are loaded for tests
    try:
        from app.routers import listeners, dashboard
        app.include_router(listeners.router)
        app.include_router(dashboard.router)
    except Exception:
        # Routers might already be included
        pass
    
    return TestClient(app)

# Async test utilities
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# Environment setup
@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment variables."""
    # Set test environment variables
    os.environ["TESTING"] = "true"
    os.environ["CONFIG_FILE"] = "test_config.yaml"
    
    yield
    
    # Cleanup
    if "TESTING" in os.environ:
        del os.environ["TESTING"]
    if "CONFIG_FILE" in os.environ:
        del os.environ["CONFIG_FILE"] 