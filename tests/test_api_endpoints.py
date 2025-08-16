"""
Unit Tests for FastAPI Endpoints

This module contains tests for the FastAPI endpoints in the main application,
including health checks and recommendation endpoints.

Author: LatentLens Team
License: MIT
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from src.main import application_instance


@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(application_instance)


class TestHealthEndpoint:
    """Test suite for the health check endpoint."""
    
    def test_health_check_success(self, client):
        """Test that health check returns successful response."""
        response = client.get("/health")
        
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
    
    def test_health_check_response_format(self, client):
        """Test that health check response has correct format."""
        response = client.get("/health")
        
        json_response = response.json()
        assert isinstance(json_response, dict)
        assert "status" in json_response
        assert json_response["status"] == "ok"


class TestRecommendationEndpoints:
    """Test suite for recommendation endpoints."""
    
    @patch('src.main.get_recommendations_for_user')
    def test_user_recommendations_success(self, mock_get_recs, client):
        """Test successful user recommendation request."""
        mock_get_recs.return_value = [
            {
                "title": "Test Movie",
                "average_rating": 4.5,
                "num_ratings": 1000,
                "user_id": 123,
                "recommendation_type": "user_hybrid"
            }
        ]
        
        response = client.get("/recommend/123")
        
        assert response.status_code == 200
        json_response = response.json()
        
        assert json_response["user_id"] == 123
        assert "recommendations" in json_response
        assert "total_recommendations" in json_response
        assert "recommendation_type" in json_response
        assert len(json_response["recommendations"]) == 1
        
        mock_get_recs.assert_called_once_with(123, 10)
    
    @patch('src.main.get_recommendations_for_user')
    def test_user_recommendations_with_limit(self, mock_get_recs, client):
        """Test user recommendation request with custom limit."""
        mock_get_recs.return_value = []
        
        response = client.get("/recommend/456?limit=5")
        
        assert response.status_code == 200
        mock_get_recs.assert_called_once_with(456, 5)
    
    def test_user_recommendations_invalid_user_id(self, client):
        """Test user recommendation request with invalid user ID."""
        response = client.get("/recommend/0")  # user_id must be >= 1
        
        assert response.status_code == 422  # Validation error
    
    def test_user_recommendations_invalid_limit(self, client):
        """Test user recommendation request with invalid limit."""
        response = client.get("/recommend/123?limit=0")  # limit must be >= 1
        
        assert response.status_code == 422  # Validation error
        
        response = client.get("/recommend/123?limit=100")  # limit must be <= 50
        
        assert response.status_code == 422  # Validation error
    
    @patch('src.main.get_recommendations_for_user')
    def test_user_recommendations_error_handling(self, mock_get_recs, client):
        """Test error handling in user recommendation endpoint."""
        mock_get_recs.side_effect = Exception("Test error")
        
        response = client.get("/recommend/123")
        
        assert response.status_code == 500
        assert "Failed to generate recommendations" in response.json()["detail"]
    
    @patch('src.main.get_popular_movies')
    def test_popular_movies_success(self, mock_get_popular, client):
        """Test successful popular movies request."""
        mock_get_popular.return_value = [
            {
                "title": "Popular Movie",
                "average_rating": 4.8,
                "num_ratings": 5000,
                "recommendation_type": "popularity_baseline"
            }
        ]
        
        response = client.get("/movies/popular")
        
        assert response.status_code == 200
        json_response = response.json()
        
        assert "movies" in json_response
        assert "total_movies" in json_response
        assert "recommendation_type" in json_response
        assert json_response["recommendation_type"] == "popularity_baseline"
        assert len(json_response["movies"]) == 1
        
        mock_get_popular.assert_called_once_with(10)
    
    @patch('src.main.get_popular_movies')
    def test_popular_movies_with_limit(self, mock_get_popular, client):
        """Test popular movies request with custom limit."""
        mock_get_popular.return_value = []
        
        response = client.get("/movies/popular?limit=20")
        
        assert response.status_code == 200
        mock_get_popular.assert_called_once_with(20)
    
    @patch('src.main.get_similar_movies')
    def test_similar_movies_success(self, mock_get_similar, client):
        """Test successful similar movies request."""
        mock_get_similar.return_value = [
            {
                "title": "Similar Movie",
                "similarity_score": 0.85,
                "recommendation_type": "collaborative_filtering"
            }
        ]
        
        response = client.get("/movies/similar?movie_title=Test Movie")
        
        assert response.status_code == 200
        json_response = response.json()
        
        assert "query_movie" in json_response
        assert "similar_movies" in json_response
        assert "total_movies" in json_response
        assert "recommendation_type" in json_response
        assert json_response["query_movie"] == "Test Movie"
        assert json_response["recommendation_type"] == "collaborative_filtering"
        
        mock_get_similar.assert_called_once_with("Test Movie", 10)
    
    @patch('src.main.get_similar_movies')
    def test_similar_movies_not_found(self, mock_get_similar, client):
        """Test similar movies request with non-existent movie."""
        mock_get_similar.side_effect = ValueError("Movie not found")
        
        response = client.get("/movies/similar?movie_title=Non-existent Movie")
        
        assert response.status_code == 404
        assert "not found in the recommendation dataset" in response.json()["detail"]
    
    def test_similar_movies_missing_title(self, client):
        """Test similar movies request without movie title."""
        response = client.get("/movies/similar")
        
        assert response.status_code == 422  # Validation error
    
    @patch('src.main.get_similar_movies')
    def test_similar_movies_error_handling(self, mock_get_similar, client):
        """Test error handling in similar movies endpoint."""
        mock_get_similar.side_effect = Exception("Test error")
        
        response = client.get("/movies/similar?movie_title=Test Movie")
        
        assert response.status_code == 500
        assert "Failed to find similar movies" in response.json()["detail"]


class TestAPIDocumentation:
    """Test suite for API documentation endpoints."""
    
    def test_docs_endpoint_accessible(self, client):
        """Test that API documentation is accessible."""
        response = client.get("/docs")
        
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    def test_redoc_endpoint_accessible(self, client):
        """Test that ReDoc documentation is accessible."""
        response = client.get("/redoc")
        
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    def test_openapi_schema_accessible(self, client):
        """Test that OpenAPI schema is accessible."""
        response = client.get("/openapi.json")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        
        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert schema["info"]["title"] == "LatentLens Movie Recommendation API"


class TestResponseFormats:
    """Test suite for response format validation."""
    
    @patch('src.main.get_recommendations_for_user')
    def test_user_recommendations_response_structure(self, mock_get_recs, client):
        """Test that user recommendations response has correct structure."""
        mock_get_recs.return_value = [
            {"title": "Movie 1", "user_id": 123},
            {"title": "Movie 2", "user_id": 123}
        ]
        
        response = client.get("/recommend/123")
        json_response = response.json()
        
        # Check required fields
        required_fields = ["user_id", "recommendations", "total_recommendations", "recommendation_type"]
        for field in required_fields:
            assert field in json_response
        
        # Check data types
        assert isinstance(json_response["user_id"], int)
        assert isinstance(json_response["recommendations"], list)
        assert isinstance(json_response["total_recommendations"], int)
        assert isinstance(json_response["recommendation_type"], str)
    
    @patch('src.main.get_popular_movies')
    def test_popular_movies_response_structure(self, mock_get_popular, client):
        """Test that popular movies response has correct structure."""
        mock_get_popular.return_value = [{"title": "Popular Movie"}]
        
        response = client.get("/movies/popular")
        json_response = response.json()
        
        # Check required fields
        required_fields = ["movies", "total_movies", "recommendation_type"]
        for field in required_fields:
            assert field in json_response
        
        # Check data types
        assert isinstance(json_response["movies"], list)
        assert isinstance(json_response["total_movies"], int)
        assert isinstance(json_response["recommendation_type"], str)
