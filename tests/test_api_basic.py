"""
Simple API Tests for LatentLens

This module contains basic tests for all FastAPI endpoints to verify
they return correct HTTP status codes and response formats.

Author: LatentLens Team
License: MIT
"""

import pytest
from fastapi.testclient import TestClient
import time

from src.main import application_instance


@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(application_instance)


class TestBasicEndpoints:
    """Basic tests for API endpoints functionality."""
    
    def test_health_check(self, client):
        """Test that health check endpoint works."""
        response = client.get("/health")
        
        assert response.status_code == 200
        json_response = response.json()
        assert "status" in json_response
        assert json_response["status"] == "ok"
    
    def test_user_recommendations_endpoint_exists(self, client):
        """Test that user recommendations endpoint exists and accepts requests."""
        response = client.get("/recommend/123")
        
        # Should not return 404 (endpoint doesn't exist)
        assert response.status_code != 404
        
        # Should return either 200 (success) or 500 (internal error)
        # but not validation errors for valid input
        assert response.status_code in [200, 500]
    
    def test_hybrid_recommendations_endpoint_exists(self, client):
        """Test that hybrid recommendations endpoint exists."""
        response = client.get("/recommend/hybrid/123")
        
        assert response.status_code != 404
        assert response.status_code in [200, 500]
    
    def test_popular_movies_endpoint_exists(self, client):
        """Test that popular movies endpoint exists."""
        response = client.get("/movies/popular")
        
        assert response.status_code != 404
        assert response.status_code in [200, 500]
    
    def test_cold_start_endpoint_exists(self, client):
        """Test that cold start endpoint exists."""
        response = client.get("/recommend/cold-start/999999")
        
        assert response.status_code != 404
        assert response.status_code in [200, 500]
    
    def test_similar_movies_endpoint_exists(self, client):
        """Test that similar movies endpoint exists."""
        response = client.get("/movies/similar?movie_title=Toy Story (1995)")
        
        assert response.status_code != 404
        assert response.status_code in [200, 500]
    
    def test_new_movies_endpoint_exists(self, client):
        """Test that new movies endpoint exists."""
        response = client.get("/movies/new")
        
        assert response.status_code != 404
        assert response.status_code in [200, 500]


class TestInputValidation:
    """Test input validation for API endpoints."""
    
    def test_invalid_user_id_validation(self, client):
        """Test that invalid user IDs are rejected."""
        # Test negative user ID
        response = client.get("/recommend/0")
        assert response.status_code == 422  # Validation error
        
        # Test non-numeric user ID
        response = client.get("/recommend/abc")
        assert response.status_code == 422  # Validation error
    
    def test_invalid_limit_validation(self, client):
        """Test that invalid limits are rejected."""
        # Test limit too small
        response = client.get("/recommend/123?limit=0")
        assert response.status_code == 422  # Validation error
        
        # Test limit too large
        response = client.get("/recommend/123?limit=100")
        assert response.status_code == 422  # Validation error
        
        # Test non-numeric limit
        response = client.get("/recommend/123?limit=abc")
        assert response.status_code == 422  # Validation error
    
    def test_valid_parameters_accepted(self, client):
        """Test that valid parameters are accepted."""
        # Valid user ID and limit
        response = client.get("/recommend/123?limit=5")
        
        # Should not be a validation error
        assert response.status_code != 422
        
        # Should be either success or internal error
        assert response.status_code in [200, 500]


class TestColdStartScenarios:
    """Test cold start scenarios with non-existent users."""
    
    def test_new_user_cold_start_popular(self, client):
        """Test cold start with popular strategy for new user."""
        # Use a very high user ID that likely doesn't exist
        non_existent_user = 999999999
        
        response = client.get(f"/recommend/cold-start/{non_existent_user}?strategy=popular&limit=5")
        
        # Should handle cold start gracefully
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            json_response = response.json()
            # Should have some structure
            assert isinstance(json_response, dict)
    
    def test_new_user_cold_start_trending(self, client):
        """Test cold start with trending strategy for new user."""
        non_existent_user = 888888888
        
        response = client.get(f"/recommend/cold-start/{non_existent_user}?strategy=trending&limit=3")
        
        assert response.status_code in [200, 500]
    
    def test_new_user_cold_start_diverse(self, client):
        """Test cold start with diverse strategy for new user."""
        non_existent_user = 777777777
        
        response = client.get(f"/recommend/cold-start/{non_existent_user}?strategy=diverse&limit=10")
        
        assert response.status_code in [200, 500]
    
    def test_cold_start_invalid_strategy(self, client):
        """Test that invalid strategies are handled properly."""
        response = client.get("/recommend/cold-start/123?strategy=invalid_strategy")
        
        # Should either reject with validation error or handle gracefully
        assert response.status_code in [200, 422, 500]


class TestResponseFormats:
    """Test that successful responses have expected formats."""
    
    def test_health_response_format(self, client):
        """Test health endpoint response format."""
        response = client.get("/health")
        
        assert response.status_code == 200
        json_response = response.json()
        
        assert isinstance(json_response, dict)
        assert "status" in json_response
        assert json_response["status"] == "ok"
    
    def test_recommendation_response_format(self, client):
        """Test that successful recommendation responses have expected format."""
        response = client.get("/recommend/123?limit=3")
        
        if response.status_code == 200:
            json_response = response.json()
            
            # Should be a dictionary
            assert isinstance(json_response, dict)
            
            # Should have some basic structure
            # (exact structure may vary based on implementation)
            assert len(json_response) > 0
    
    def test_popular_movies_response_format(self, client):
        """Test that popular movies response has expected format."""
        response = client.get("/movies/popular?limit=5")
        
        if response.status_code == 200:
            json_response = response.json()
            
            # Should have some structure
            assert json_response is not None


class TestPerformance:
    """Basic performance tests for API endpoints."""
    
    def test_health_check_performance(self, client):
        """Test that health check responds quickly."""
        start_time = time.time()
        response = client.get("/health")
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 1.0  # Should respond in less than 1 second
    
    def test_recommendation_reasonable_performance(self, client):
        """Test that recommendations respond in reasonable time."""
        start_time = time.time()
        response = client.get("/recommend/123?limit=5")
        end_time = time.time()
        
        response_time = end_time - start_time
        
        # Should respond in less than 30 seconds for small requests
        assert response_time < 30.0
        
        # Should not be a validation error for valid input
        assert response.status_code != 422


class TestAPIDocumentation:
    """Test that API documentation is accessible."""
    
    def test_openapi_schema_accessible(self, client):
        """Test that OpenAPI schema is accessible."""
        response = client.get("/openapi.json")
        
        assert response.status_code == 200
        
        json_response = response.json()
        assert "openapi" in json_response
        assert "info" in json_response
        assert "paths" in json_response
    
    def test_docs_page_accessible(self, client):
        """Test that Swagger UI docs page is accessible."""
        response = client.get("/docs")
        
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "").lower()
    
    def test_redoc_page_accessible(self, client):
        """Test that ReDoc documentation page is accessible."""
        response = client.get("/redoc")
        
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "").lower()


class TestErrorHandling:
    """Test error handling scenarios."""
    
    def test_invalid_endpoint_returns_404(self, client):
        """Test that invalid endpoints return 404."""
        response = client.get("/invalid/endpoint/path")
        
        assert response.status_code == 404
    
    def test_invalid_http_method(self, client):
        """Test that invalid HTTP methods are handled."""
        response = client.post("/health")
        
        assert response.status_code == 405  # Method not allowed
    
    def test_missing_required_parameters(self, client):
        """Test handling of missing required parameters."""
        # Test missing movie_title for similar movies
        response = client.get("/movies/similar")
        
        # Should return validation error for missing required parameter
        assert response.status_code == 422


if __name__ == "__main__":
    pytest.main([__file__])
