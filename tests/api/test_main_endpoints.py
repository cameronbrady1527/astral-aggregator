# ==============================================================================
# test_main_endpoints.py — API Tests for Main Application Endpoints
# ==============================================================================
# Purpose: Test the main FastAPI application endpoints
# ==============================================================================

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.main import app


class TestMainEndpoints:
    """Test the main application endpoints."""
    
    def test_root_endpoint(self, client):
        """Test the root endpoint."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert "service" in data
        assert data["service"] == "astral-api"
        assert "version" in data
        assert "message" in data
        assert "endpoints" in data
        assert "initialized" in data
        assert "routers_loaded" in data
    
    def test_health_endpoint(self, client):
        """Test the health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert data["status"] in ["healthy", "initializing"]
        assert "service" in data
        assert data["service"] == "astral-api"
        assert "version" in data
        assert "initialized" in data
        assert "routers_loaded" in data
    
    def test_ping_endpoint(self, client):
        """Test the ping endpoint."""
        response = client.get("/ping")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "pong" in data
        assert data["pong"] == "ok"
        assert "status" in data
        assert data["status"] == "healthy"
    
    def test_test_endpoint(self, client):
        """Test the test endpoint."""
        response = client.get("/test")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        assert data["message"] == "Astral API is working!"
        assert "timestamp" in data
        assert "status" in data
        assert data["status"] == "success"
        assert "initialized" in data
        assert "routers_loaded" in data
    
    def test_debug_endpoint(self, client):
        """Test the debug endpoint."""
        response = client.get("/debug")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert data["status"] == "debug"
        assert "app_initialized" in data
        assert "routers_loaded" in data
        assert "environment" in data
        assert "available_modules" in data
        
        # Check environment information
        env = data["environment"]
        assert "python_version" in env
        assert "platform" in env
        assert "current_directory" in env
        assert "pythonpath" in env
        assert "port" in env
        assert "railway_environment" in env
        assert "railway_public_domain" in env
        assert "config_file" in env
        
        # Check available modules
        modules = data["available_modules"]
        assert "fastapi" in modules
        assert "uvicorn" in modules
        assert isinstance(modules["fastapi"], bool)
        assert isinstance(modules["uvicorn"], bool)
    
    def test_api_docs_endpoint(self, client):
        """Test that API documentation is accessible."""
        response = client.get("/docs")
        
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "Swagger UI" in response.text or "FastAPI" in response.text
    
    def test_openapi_schema_endpoint(self, client):
        """Test that OpenAPI schema is accessible."""
        response = client.get("/openapi.json")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data
        assert data["info"]["title"] == "Astral API"
        assert "Website Change Detection System" in data["info"]["description"]
    
    def test_endpoint_headers(self, client):
        """Test that endpoints return proper headers."""
        response = client.get("/health")
        
        assert response.status_code == 200
        assert "content-type" in response.headers
        assert "application/json" in response.headers["content-type"]
    
    def test_cors_headers(self, client):
        """Test CORS headers if configured."""
        response = client.options("/health")
        
        # Should not fail even if CORS is not configured
        assert response.status_code in [200, 405, 404]
    
    def test_404_endpoint(self, client):
        """Test that non-existent endpoints return 404."""
        response = client.get("/nonexistent")
        
        assert response.status_code == 404
    
    def test_method_not_allowed(self, client):
        """Test that wrong HTTP methods return 405."""
        response = client.post("/health")
        
        assert response.status_code == 405
    
    def test_root_endpoint_with_initialization_state(self, client):
        """Test root endpoint reflects initialization state."""
        response = client.get("/")
        data = response.json()
        
        # Should have initialization flags
        assert "initialized" in data
        assert "routers_loaded" in data
        
        # These should be boolean values
        assert isinstance(data["initialized"], bool)
        assert isinstance(data["routers_loaded"], bool)
    
    def test_health_endpoint_status_values(self, client):
        """Test health endpoint returns valid status values."""
        response = client.get("/health")
        data = response.json()
        
        # Status should be one of the expected values
        assert data["status"] in ["healthy", "initializing"]
        
        # Version should be a string
        assert isinstance(data["version"], str)
        assert len(data["version"]) > 0
    
    def test_debug_endpoint_module_detection(self, client):
        """Test debug endpoint correctly detects available modules."""
        response = client.get("/debug")
        data = response.json()
        
        modules = data["available_modules"]
        
        # Should detect FastAPI (since we're using it)
        assert modules["fastapi"] is True
        
        # Should have boolean values for all module checks
        for module_name, is_available in modules.items():
            assert isinstance(is_available, bool)
    
    def test_endpoint_response_structure(self, client):
        """Test that all endpoints return consistent response structure."""
        endpoints = ["/", "/health", "/ping", "/test"]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 200
            
            data = response.json()
            assert isinstance(data, dict)
            
            # All responses should have at least a status or message
            assert any(key in data for key in ["status", "message", "pong"])
    
    def test_debug_endpoint_environment_variables(self, client):
        """Test debug endpoint shows environment variable information."""
        response = client.get("/debug")
        data = response.json()
        
        env = data["environment"]
        
        # Should show environment variable status
        assert "pythonpath" in env
        assert "port" in env
        assert "railway_environment" in env
        assert "railway_public_domain" in env
        assert "config_file" in env
        
        # Values should be strings (either actual values or "NOT SET")
        for key, value in env.items():
            assert isinstance(value, str)
    
    def test_concurrent_requests(self, client):
        """Test that endpoints handle concurrent requests properly."""
        import threading
        import time
        
        results = []
        errors = []
        
        def make_request():
            try:
                response = client.get("/health")
                results.append(response.status_code)
            except Exception as e:
                errors.append(str(e))
        
        # Make multiple concurrent requests
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        assert len(errors) == 0
        assert len(results) == 5
        assert all(status == 200 for status in results)
    
    def test_endpoint_performance(self, client):
        """Test that endpoints respond within reasonable time."""
        import time
        
        endpoints = ["/", "/health", "/ping", "/test"]
        
        for endpoint in endpoints:
            start_time = time.time()
            response = client.get(endpoint)
            end_time = time.time()
            
            assert response.status_code == 200
            response_time = end_time - start_time
            
            # Should respond within 1 second
            assert response_time < 1.0
    
    def test_debug_endpoint_system_info(self, client):
        """Test debug endpoint provides useful system information."""
        response = client.get("/debug")
        data = response.json()
        
        env = data["environment"]
        
        # Should provide Python version
        assert "python_version" in env
        assert "3." in env["python_version"]  # Should be Python 3.x
        
        # Should provide platform information
        assert "platform" in env
        assert len(env["platform"]) > 0
        
        # Should provide current directory
        assert "current_directory" in env
        assert len(env["current_directory"]) > 0 