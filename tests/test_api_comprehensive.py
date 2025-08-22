"""
Comprehensive API Tests for LatentLens

This module contains comprehensive tests for all FastAPI endpoints,
including health checks, recommendations, cold start scenarios, and error handling.

Author: LatentLens Team
License: MIT
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import json

from src.main import application_instance


@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(application_instance)


class TestHealthEndpoint:
    """Comprehensive test suite for the health check endpoint."""
    
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
    
    def test_health_check_content_type(self, client):
        """Test that health check returns correct content type."""
        response = client.get("/health")
        
        assert response.headers["content-type"] == "application/json"


class TestHybridRecommendationEndpoint:
    """Test suite for hybrid recommendation endpoint."""
    
    @patch('src.main.recommender')
    def test_hybrid_recommendations_success(self, mock_recommender, client):
        """Test successful hybrid recommendation request."""
        mock_recommender.recommend.return_value = [
            {
                "movieId": 1,
                "title": "Toy Story (1995)",
                "genres": "Adventure|Animation|Children|Comedy|Fantasy",
                "final_score": 4.5,
                "weighted_score": 4.2,
                "sources": ["collaborative", "item_similarity"],
                "source_scores": {
                    "collaborative": 4.5,
                    "item_similarity": 3.9
                }
            }
        ]
        
        response = client.get("/recommend/hybrid/123?limit=5")
        
        assert response.status_code == 200
        json_response = response.json()
        
        assert json_response["user_id"] == 123
        assert json_response["strategy"] == "hybrid"
        assert "recommendations" in json_response
        assert "n_recommendations" in json_response
        assert len(json_response["recommendations"]) == 1
        
        # Verify recommendation structure
        recommendation = json_response["recommendations"][0]
        assert "movieId" in recommendation
        assert "title" in recommendation
        assert "final_score" in recommendation
        
        mock_recommender.recommend.assert_called_once_with(123, "hybrid", 5)
    
    @patch('src.main.recommender')
    def test_hybrid_recommendations_with_default_limit(self, mock_recommender, client):
        """Test hybrid recommendations with default limit."""
        mock_recommender.recommend.return_value = []
        
        response = client.get("/recommend/hybrid/456")
        
        assert response.status_code == 200
        mock_recommender.recommend.assert_called_once_with(456, "hybrid", 10)
    
    def test_hybrid_recommendations_invalid_user_id(self, client):
        """Test hybrid recommendations with invalid user ID."""
        response = client.get("/recommend/hybrid/0")  # user_id must be >= 1
        
        assert response.status_code == 422  # Validation error
    
    def test_hybrid_recommendations_invalid_limit(self, client):
        """Test hybrid recommendations with invalid limit."""
        response = client.get("/recommend/hybrid/123?limit=0")  # limit must be >= 1
        
        assert response.status_code == 422  # Validation error
        
        response = client.get("/recommend/hybrid/123?limit=100")  # limit must be <= 50
        
        assert response.status_code == 422  # Validation error


class TestCollaborativeRecommendationEndpoint:
    """Test suite for collaborative recommendation endpoint."""
    
    @patch('src.main.recommender')
    def test_collaborative_recommendations_success(self, mock_recommender, client):
        """Test successful collaborative recommendation request."""
        mock_recommender.recommend.return_value = [
            {
                "movieId": 2,
                "title": "Jumanji (1995)",
                "genres": "Adventure|Children|Fantasy",
                "predicted_rating": 4.2
            }
        ]
        
        response = client.get("/recommend/collaborative/789?limit=3")
        
        assert response.status_code == 200
        json_response = response.json()
        
        assert json_response["user_id"] == 789
        assert json_response["strategy"] == "collaborative"
        assert len(json_response["recommendations"]) == 1
        
        mock_recommender.recommend.assert_called_once_with(789, "collaborative", 3)


class TestPopularityRecommendationEndpoint:
    """Test suite for popularity recommendation endpoint."""
    
    @patch('src.main.recommender')
    def test_popular_recommendations_success(self, mock_recommender, client):
        """Test successful popular recommendation request."""
        mock_recommender.recommend.return_value = [
            {
                "movieId": 318,
                "title": "Shawshank Redemption, The (1994)",
                "genres": "Crime|Drama",
                "average_rating": 4.429,
                "num_ratings": 317
            }
        ]
        
        response = client.get("/recommend/popular?limit=5")
        
        assert response.status_code == 200
        json_response = response.json()
        
        assert json_response["strategy"] == "popularity"
        assert "recommendations" in json_response
        assert len(json_response["recommendations"]) == 1
        
        mock_recommender.recommend.assert_called_once_with(None, "popularity", 5)


class TestColdStartRecommendationEndpoint:
    """Test suite for cold start recommendation endpoint."""
    
    @patch('src.main.recommender')
    def test_cold_start_popular_strategy(self, mock_recommender, client):
        """Test cold start recommendations with popular strategy."""
        mock_recommender.recommend.return_value = [
            {
                "movieId": 260,
                "title": "Star Wars: Episode IV - A New Hope (1977)",
                "genres": "Action|Adventure|Sci-Fi",
                "average_rating": 4.231,
                "num_ratings": 247
            }
        ]
        
        # Test with a non-existent user ID (cold start scenario)
        response = client.get("/recommend/cold-start/999999?strategy=popular&limit=5")
        
        assert response.status_code == 200
        json_response = response.json()
        
        assert json_response["user_id"] == 999999
        assert json_response["strategy"] == "cold_start"
        assert "recommendations" in json_response
        assert len(json_response["recommendations"]) == 1
        
        mock_recommender.recommend.assert_called_once_with(999999, "cold_start", 5, strategy="popular")
    
    @patch('src.main.recommender')
    def test_cold_start_trending_strategy(self, mock_recommender, client):
        """Test cold start recommendations with trending strategy."""
        mock_recommender.recommend.return_value = [
            {
                "movieId": 122886,
                "title": "Mad Max: Fury Road (2015)",
                "genres": "Action|Adventure|Sci-Fi|Thriller",
                "year": 2015,
                "average_rating": 4.1
            }
        ]
        
        response = client.get("/recommend/cold-start/888888?strategy=trending&limit=3")
        
        assert response.status_code == 200
        json_response = response.json()
        
        assert json_response["user_id"] == 888888
        assert json_response["strategy"] == "cold_start"
        
        mock_recommender.recommend.assert_called_once_with(888888, "cold_start", 3, strategy="trending")
    
    @patch('src.main.recommender')
    def test_cold_start_diverse_strategy(self, mock_recommender, client):
        """Test cold start recommendations with diverse strategy."""
        mock_recommender.recommend.return_value = [
            {
                "movieId": 1,
                "title": "Toy Story (1995)",
                "genres": "Adventure|Animation|Children|Comedy|Fantasy",
                "genre_diversity": True
            }
        ]
        
        response = client.get("/recommend/cold-start/777777?strategy=diverse&limit=10")
        
        assert response.status_code == 200
        mock_recommender.recommend.assert_called_once_with(777777, "cold_start", 10, strategy="diverse")
    
    def test_cold_start_invalid_strategy(self, client):
        """Test cold start recommendations with invalid strategy."""
        response = client.get("/recommend/cold-start/123?strategy=invalid")
        
        assert response.status_code == 422  # Validation error


class TestMovieEndpoints:
    """Test suite for movie-related endpoints."""
    
    @patch('src.main.recommender')
    def test_popular_movies_success(self, mock_recommender, client):
        """Test successful popular movies request."""
        mock_recommender.recommend.return_value = [
            {
                "movieId": 318,
                "title": "Shawshank Redemption, The (1994)",
                "genres": "Crime|Drama",
                "average_rating": 4.429,
                "num_ratings": 317
            }
        ]
        
        response = client.get("/movies/popular?limit=10")
        
        assert response.status_code == 200
        json_response = response.json()
        
        assert isinstance(json_response, list)
        assert len(json_response) == 1
        
        movie = json_response[0]
        assert "movieId" in movie
        assert "title" in movie
        assert "average_rating" in movie
    
    @patch('src.main.get_similar_movies')
    def test_similar_movies_success(self, mock_get_similar, client):
        """Test successful similar movies request."""
        mock_get_similar.return_value = [
            {
                "movieId": 2,
                "title": "Jumanji (1995)",
                "genres": "Adventure|Children|Fantasy",
                "similarity_score": 0.85
            }
        ]
        
        response = client.get("/movies/similar?movie_title=Toy Story (1995)&limit=5")
        
        assert response.status_code == 200
        json_response = response.json()
        
        assert isinstance(json_response, list)
        assert len(json_response) == 1
        
        movie = json_response[0]
        assert "movieId" in movie
        assert "title" in movie
        assert "similarity_score" in movie
        
        mock_get_similar.assert_called_once_with("Toy Story (1995)", 5)


class TestErrorHandling:
    """Test suite for error handling scenarios."""
    
    @patch('src.main.recommender')
    def test_recommendation_service_error(self, mock_recommender, client):
        """Test handling of recommendation service errors."""
        mock_recommender.recommend.side_effect = Exception("Service unavailable")
        
        response = client.get("/recommend/hybrid/123")
        
        assert response.status_code == 500
        json_response = response.json()
        assert "detail" in json_response
    
    @patch('src.main.recommender')
    def test_empty_recommendations(self, mock_recommender, client):
        """Test handling of empty recommendation responses."""
        mock_recommender.recommend.return_value = []
        
        response = client.get("/recommend/hybrid/123")
        
        assert response.status_code == 200
        json_response = response.json()
        
        assert json_response["user_id"] == 123
        assert json_response["n_recommendations"] == 0
        assert json_response["recommendations"] == []
    
    def test_invalid_endpoint(self, client):
        """Test handling of invalid endpoint requests."""
        response = client.get("/invalid/endpoint")
        
        assert response.status_code == 404
    
    def test_method_not_allowed(self, client):
        """Test handling of invalid HTTP methods."""
        response = client.post("/health")
        
        assert response.status_code == 405


class TestAPIDocumentation:
    """Test suite for API documentation endpoints."""
    
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
        assert "text/html" in response.headers["content-type"]
    
    def test_redoc_page_accessible(self, client):
        """Test that ReDoc documentation page is accessible."""
        response = client.get("/redoc")
        
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]


if __name__ == "__main__":
    pytest.main([__file__])
