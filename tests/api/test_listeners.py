# ==============================================================================
# test_listeners.py — API Tests for Listeners Router
# ==============================================================================
# Purpose: Test the listeners API endpoints for change detection
# ==============================================================================

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
import json

from app.main import app


class TestListenersEndpoints:
    """Test the listeners API endpoints."""
    
    def test_listeners_root_endpoint(self, client):
        """Test the listeners root endpoint."""
        response = client.get("/api/listeners/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        assert "Website Change Detection API" in data["message"]
        assert "description" in data
        assert "endpoints" in data
        assert "available_sites" in data
    
    def test_listeners_root_with_initialization_state(self, client):
        """Test listeners root endpoint when system is initializing."""
        with patch('app.routers.listeners.get_change_detector', return_value=None):
            response = client.get("/api/listeners/")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["status"] == "initializing"
            assert "System is starting up" in data["note"]
    
    def test_listeners_endpoints_structure(self, client):
        """Test that listeners root shows all available endpoints."""
        response = client.get("/api/listeners/")
        data = response.json()
        
        endpoints = data["endpoints"]
        
        # Should list all available endpoints
        expected_endpoints = [
            "trigger_site",
            "trigger_all", 
            "status",
            "sites",
            "site_status",
            "site_changes",
            "all_changes",
            "analytics",
            "site_analytics",
            "realtime",
            "history"
        ]
        
        for endpoint in expected_endpoints:
            assert endpoint in endpoints
    
    def test_trigger_site_info_endpoint(self, client):
        """Test the trigger site info endpoint."""
        response = client.get("/api/listeners/trigger/test_site")
        
        assert response.status_code == 404  # Site doesn't exist in test config
        data = response.json()
        
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    def test_trigger_info_endpoint(self, client):
        """Test the general trigger info endpoint."""
        response = client.get("/api/listeners/trigger")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        assert "trigger" in data["message"].lower()
        assert "endpoints" in data
        assert "available_sites" in data
    
    @patch('app.routers.listeners.get_change_detector')
    def test_trigger_site_detection_success(self, mock_get_detector, client):
        """Test successful site detection trigger."""
        # Mock the change detector
        mock_detector = MagicMock()
        mock_detector.detect_changes_for_site = AsyncMock(return_value={
            "status": "success",
            "changes_found": 2,
            "site_id": "test_site"
        })
        mock_get_detector.return_value = mock_detector
        
        response = client.post("/api/listeners/trigger/test_site")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert data["status"] == "started"
        assert "message" in data
        assert "started" in data["message"].lower()
        
        # Verify the detector was called
        mock_detector.detect_changes_for_site.assert_called_once_with("test_site")
    
    @patch('app.routers.listeners.get_change_detector')
    def test_trigger_site_detection_failure(self, mock_get_detector, client):
        """Test site detection trigger when detector fails."""
        # Mock the change detector to raise an exception
        mock_detector = MagicMock()
        mock_detector.detect_changes_for_site = AsyncMock(side_effect=Exception("Test error"))
        mock_get_detector.return_value = mock_detector
        
        response = client.post("/api/listeners/trigger/test_site")
        
        assert response.status_code == 200  # The endpoint returns 200 even on error
        data = response.json()
        
        assert "status" in data
        assert data["status"] == "started"  # The endpoint starts the process even if it fails later
    
    @patch('app.routers.listeners.get_change_detector')
    def test_trigger_all_sites_detection(self, mock_get_detector, client):
        """Test triggering detection for all sites."""
        # Mock the change detector
        mock_detector = MagicMock()
        mock_detector.detect_changes_for_all_sites = AsyncMock(return_value={
            "status": "success",
            "sites_processed": 3,
            "total_changes": 5
        })
        mock_get_detector.return_value = mock_detector
        
        response = client.post("/api/listeners/trigger/all")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert data["status"] == "started"
        assert "message" in data
        assert "started" in data["message"].lower()
        
        # The endpoint starts the process asynchronously, so we can't verify the call immediately
        # The test passes if we get a 200 response with "started" status
    
    def test_system_status_endpoint(self, client):
        """Test the system status endpoint."""
        response = client.get("/api/listeners/status")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert "active_sites" in data
        assert "total_sites" in data
        assert "sites" in data
    
    def test_list_sites_endpoint(self, client):
        """Test the list sites endpoint."""
        response = client.get("/api/listeners/sites")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return a list
        assert isinstance(data, list)
        
        # Each site should have required fields
        if len(data) > 0:
            site = data[0]
            assert "site_id" in site
            assert "name" in site
            assert "url" in site
            assert "is_active" in site
    
    def test_get_site_status_endpoint(self, client):
        """Test getting status for a specific site."""
        response = client.get("/api/listeners/sites/test_site")
        
        assert response.status_code == 404  # Site doesn't exist in test config
        data = response.json()
        
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    def test_get_site_status_nonexistent(self, client):
        """Test getting status for a non-existent site."""
        response = client.get("/api/listeners/sites/nonexistent_site")
        
        assert response.status_code == 404
        data = response.json()
        
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    def test_get_site_changes_endpoint(self, client):
        """Test getting changes for a specific site."""
        response = client.get("/api/listeners/changes/test_site")
        
        assert response.status_code == 404  # Site doesn't exist in test config
        data = response.json()
        
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    def test_get_site_changes_with_limit(self, client):
        """Test getting site changes with limit parameter."""
        response = client.get("/api/listeners/changes/test_site?limit=5")
        
        assert response.status_code == 404  # Site doesn't exist in test config
        data = response.json()
        
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    def test_get_all_changes_endpoint(self, client):
        """Test getting all changes across all sites."""
        response = client.get("/api/listeners/changes")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "recent_changes" in data
        assert "total_sites" in data
        assert isinstance(data["recent_changes"], list)
    
    def test_get_all_changes_with_limit(self, client):
        """Test getting all changes with limit parameter."""
        response = client.get("/api/listeners/changes?limit=10")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "recent_changes" in data
        assert len(data["recent_changes"]) <= 10
    
    def test_get_system_analytics_endpoint(self, client):
        """Test getting system analytics."""
        response = client.get("/api/listeners/analytics")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "analytics" in data
        assert "status" in data
        assert "overview" in data["analytics"]
    
    def test_get_site_analytics_endpoint(self, client):
        """Test getting analytics for a specific site."""
        response = client.get("/api/listeners/analytics/test_site")
        
        assert response.status_code == 404  # Site doesn't exist in test config
        data = response.json()
        
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    def test_get_realtime_status_endpoint(self, client):
        """Test getting realtime status."""
        response = client.get("/api/listeners/realtime")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert "timestamp" in data
        assert "sites" in data
    
    def test_get_detection_progress_endpoint(self, client):
        """Test getting detection progress."""
        response = client.get("/api/listeners/progress")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert "detection_status" in data
        assert "current_site" in data["detection_status"]
    
    def test_get_historical_data_endpoint(self, client):
        """Test getting historical data."""
        response = client.get("/api/listeners/history")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "history" in data
        assert "status" in data
        assert "period_days" in data["history"]
    
    def test_get_historical_data_with_days_parameter(self, client):
        """Test getting historical data with days parameter."""
        response = client.get("/api/listeners/history?days=14")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "history" in data
        assert "period_days" in data["history"]
        assert data["history"]["period_days"] == 14
    
    def test_invalid_limit_parameter(self, client):
        """Test that invalid limit parameters are handled properly."""
        # Test limit too high
        response = client.get("/api/listeners/changes?limit=1000")
        assert response.status_code == 422  # Validation error
        
        # Test limit too low
        response = client.get("/api/listeners/changes?limit=0")
        assert response.status_code == 422  # Validation error
    
    def test_invalid_days_parameter(self, client):
        """Test that invalid days parameters are handled properly."""
        # Test days too high
        response = client.get("/api/listeners/history?days=100")
        assert response.status_code == 422  # Validation error
        
        # Test days too low
        response = client.get("/api/listeners/history?days=0")
        assert response.status_code == 422  # Validation error
    
    def test_endpoint_method_not_allowed(self, client):
        """Test that wrong HTTP methods return 405."""
        # Test GET on POST-only endpoint
        response = client.get("/api/listeners/trigger/test_site")
        assert response.status_code == 404  # Site doesn't exist in test config
        
        # Test POST on GET-only endpoint
        response = client.post("/api/listeners/status")
        assert response.status_code == 405
    
    def test_endpoint_response_headers(self, client):
        """Test that endpoints return proper headers."""
        response = client.get("/api/listeners/status")
        
        assert response.status_code == 200
        assert "content-type" in response.headers
        assert "application/json" in response.headers["content-type"]
    
    def test_concurrent_requests_to_listeners(self, client):
        """Test that listeners endpoints handle concurrent requests."""
        import threading
        import time
        
        results = []
        errors = []
        
        def make_request():
            try:
                response = client.get("/api/listeners/status")
                results.append(response.status_code)
            except Exception as e:
                errors.append(str(e))
        
        # Make multiple concurrent requests
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        assert len(errors) == 0
        assert len(results) == 3
        assert all(status == 200 for status in results) 