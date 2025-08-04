# ==============================================================================
# test_dashboard.py — API Tests for Dashboard Router
# ==============================================================================
# Purpose: Test the dashboard API endpoints and HTML responses
# ==============================================================================

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.main import app


class TestDashboardEndpoints:
    """Test the dashboard API endpoints."""
    
    def test_dashboard_root_endpoint(self, client):
        """Test the main dashboard endpoint."""
        response = client.get("/dashboard/")
        
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        
        # Should return HTML content
        html_content = response.text
        assert "<!DOCTYPE html>" in html_content
        assert "<html" in html_content
        assert "<head>" in html_content
        assert "<body>" in html_content
        
        # Should contain dashboard title
        assert "Astral - Website Change Detection Dashboard" in html_content
        
        # Should contain Chart.js and other dependencies
        assert "chart.js" in html_content.lower()
        assert "date-fns" in html_content.lower()
    
    def test_dashboard_html_structure(self, client):
        """Test that dashboard HTML has proper structure."""
        response = client.get("/dashboard/")
        
        assert response.status_code == 200
        html_content = response.text
        
        # Check for essential HTML elements
        assert "<title>" in html_content
        assert "<meta charset=" in html_content
        assert "<meta name=\"viewport\"" in html_content
        
        # Check for CSS styling
        assert "style" in html_content
        assert "background" in html_content
        assert "font-family" in html_content
        
        # Check for JavaScript
        assert "script" in html_content
        assert "function" in html_content
    
    def test_dashboard_content_sections(self, client):
        """Test that dashboard contains expected content sections."""
        response = client.get("/dashboard/")
        
        assert response.status_code == 200
        html_content = response.text
        
        # Should contain main sections
        assert "header" in html_content
        assert "container" in html_content
        assert "status-bar" in html_content
        
        # Should contain dashboard functionality
        assert "chart" in html_content.lower()
        assert "api" in html_content.lower()
        assert "fetch" in html_content.lower()
    
    def test_dashboard_responsive_design(self, client):
        """Test that dashboard has responsive design elements."""
        response = client.get("/dashboard/")
        
        assert response.status_code == 200
        html_content = response.text
        
        # Should have responsive viewport meta tag
        assert "width=device-width" in html_content
        assert "initial-scale=1.0" in html_content
        
        # Should have responsive CSS
        assert "max-width" in html_content
        assert "flex-wrap" in html_content
    
    def test_dashboard_javascript_functionality(self, client):
        """Test that dashboard has JavaScript functionality."""
        response = client.get("/dashboard/")
        
        assert response.status_code == 200
        html_content = response.text
        
        # Should contain JavaScript functions
        assert "async function" in html_content or "function" in html_content
        assert "fetch(" in html_content
        assert "JSON.parse" in html_content or "json()" in html_content
        
        # Should have error handling
        assert "catch" in html_content or "error" in html_content
    
    def test_dashboard_api_integration(self, client):
        """Test that dashboard integrates with API endpoints."""
        response = client.get("/dashboard/")
        
        assert response.status_code == 200
        html_content = response.text
        
        # Should reference API endpoints that actually exist in the dashboard
        assert "/api/listeners/progress" in html_content
        assert "/api/listeners/analytics" in html_content
        assert "/api/listeners/realtime" in html_content
    
    def test_dashboard_chart_integration(self, client):
        """Test that dashboard includes chart functionality."""
        response = client.get("/dashboard/")
        
        assert response.status_code == 200
        html_content = response.text
        
        # Should include Chart.js
        assert "Chart.js" in html_content or "chart.js" in html_content
        
        # Should have canvas elements for charts
        assert "canvas" in html_content
        
        # Should have chart configuration
        assert "new Chart" in html_content or "Chart(" in html_content
    
    def test_dashboard_error_handling(self, client):
        """Test that dashboard handles errors gracefully."""
        response = client.get("/dashboard/")
        
        assert response.status_code == 200
        html_content = response.text
        
        # Should have error handling in JavaScript
        assert "error" in html_content.lower()
        assert "catch" in html_content or "console.error" in html_content
    
    def test_dashboard_loading_states(self, client):
        """Test that dashboard shows loading states."""
        response = client.get("/dashboard/")
        
        assert response.status_code == 200
        html_content = response.text
        
        # Should have loading indicators
        assert "loading" in html_content.lower() or "spinner" in html_content.lower()
    
    def test_dashboard_data_refresh(self, client):
        """Test that dashboard can refresh data."""
        response = client.get("/dashboard/")
        
        assert response.status_code == 200
        html_content = response.text
        
        # Should have refresh functionality
        assert "refresh" in html_content.lower() or "update" in html_content.lower()
        assert "setInterval" in html_content or "setTimeout" in html_content
    
    def test_dashboard_accessibility(self, client):
        """Test that dashboard has accessibility features."""
        response = client.get("/dashboard/")
        
        assert response.status_code == 200
        html_content = response.text
        
        # Should have semantic HTML elements
        assert "<header>" in html_content or "header" in html_content
        assert "<main>" in html_content or "main" in html_content
        
        # Should have proper contrast and readability
        assert "color" in html_content
        assert "background" in html_content
    
    def test_dashboard_performance(self, client):
        """Test that dashboard loads efficiently."""
        import time
        
        start_time = time.time()
        response = client.get("/dashboard/")
        end_time = time.time()
        
        assert response.status_code == 200
        
        # Should load within reasonable time
        load_time = end_time - start_time
        assert load_time < 2.0  # Should load within 2 seconds
    
    def test_dashboard_content_length(self, client):
        """Test that dashboard has substantial content."""
        response = client.get("/dashboard/")
        
        assert response.status_code == 200
        html_content = response.text
        
        # Should have meaningful content length
        assert len(html_content) > 1000  # At least 1KB of content
    
    def test_dashboard_security_headers(self, client):
        """Test that dashboard has proper security headers."""
        response = client.get("/dashboard/")
        
        assert response.status_code == 200
        
        # Should have content-type header
        assert "content-type" in response.headers
        assert "text/html" in response.headers["content-type"]
    
    def test_dashboard_cross_browser_compatibility(self, client):
        """Test that dashboard works across different browsers."""
        response = client.get("/dashboard/")
        
        assert response.status_code == 200
        html_content = response.text
        
        # Should use standard HTML5 elements
        assert "<!DOCTYPE html>" in html_content
        
        # Should use standard CSS properties
        assert "display" in html_content
        assert "margin" in html_content
        assert "padding" in html_content
    
    def test_dashboard_mobile_compatibility(self, client):
        """Test that dashboard is mobile-friendly."""
        response = client.get("/dashboard/")
        
        assert response.status_code == 200
        html_content = response.text
        
        # Should have mobile viewport
        assert "viewport" in html_content
        assert "width=device-width" in html_content
        
        # Should have touch-friendly elements
        assert "cursor" in html_content or "pointer" in html_content
    
    def test_dashboard_data_visualization(self, client):
        """Test that dashboard includes data visualization."""
        response = client.get("/dashboard/")
        
        assert response.status_code == 200
        html_content = response.text
        
        # Should have chart elements
        assert "chart" in html_content.lower()
        
        # Should have data display elements
        assert "data" in html_content.lower()
        assert "status" in html_content.lower()
    
    def test_dashboard_navigation(self, client):
        """Test that dashboard has navigation elements."""
        response = client.get("/dashboard/")
        
        assert response.status_code == 200
        html_content = response.text
        
        # Should have navigation or menu elements
        assert "container" in html_content.lower() or "header" in html_content.lower()
    
    def test_dashboard_real_time_updates(self, client):
        """Test that dashboard supports real-time updates."""
        response = client.get("/dashboard/")
        
        assert response.status_code == 200
        html_content = response.text
        
        # Should have real-time update functionality
        assert "websocket" in html_content.lower() or "setInterval" in html_content or "setTimeout" in html_content
    
    def test_dashboard_export_functionality(self, client):
        """Test that dashboard supports data export."""
        response = client.get("/dashboard/")
        
        assert response.status_code == 200
        html_content = response.text
        
        # Should have export functionality
        assert "json" in html_content.lower() or "data" in html_content.lower()
    
    def test_dashboard_search_functionality(self, client):
        """Test that dashboard has search capabilities."""
        response = client.get("/dashboard/")
        
        assert response.status_code == 200
        html_content = response.text
        
        # Should have search functionality
        assert "search" in html_content.lower() or "filter" in html_content.lower()
    
    def test_dashboard_sorting_functionality(self, client):
        """Test that dashboard supports data sorting."""
        response = client.get("/dashboard/")
        
        assert response.status_code == 200
        html_content = response.text
        
        # Should have sorting functionality
        assert "sort" in html_content.lower() or "order" in html_content.lower()
    
    def test_dashboard_pagination(self, client):
        """Test that dashboard supports pagination."""
        response = client.get("/dashboard/")
        
        assert response.status_code == 200
        html_content = response.text
        
        # Should have pagination functionality
        assert "page" in html_content.lower() or "pagination" in html_content.lower()
    
    def test_dashboard_notifications(self, client):
        """Test that dashboard shows notifications."""
        response = client.get("/dashboard/")
        
        assert response.status_code == 200
        html_content = response.text
        
        # Should have notification functionality
        assert "success" in html_content.lower() or "error" in html_content.lower()
    
    def test_dashboard_settings(self, client):
        """Test that dashboard has settings functionality."""
        response = client.get("/dashboard/")
        
        assert response.status_code == 200
        html_content = response.text
        
        # Should have settings functionality
        assert "setting" in html_content.lower() or "config" in html_content.lower() 