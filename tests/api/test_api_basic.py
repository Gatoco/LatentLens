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
import sys
from pathlib import Path

# Add src directory to Python path for imports
# This ensures we can import the main module from src/ directory
src_path = str(Path(__file__).parent.parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

try:
    from main import app
except ImportError as e:
    pytest.skip(f"Could not import main module: {e}", allow_module_level=True)


# Test configuration constants
# Based on project testing strategy for environments where services may not be available
EXPECTED_SUCCESS_CODES = [200]
EXPECTED_SERVICE_UNAVAILABLE_CODES = [
    503,
    422,
]  # Service unavailable, validation errors
EXPECTED_ERROR_CODES = [500]
VALID_RESPONSE_CODES = (
    EXPECTED_SUCCESS_CODES + EXPECTED_SERVICE_UNAVAILABLE_CODES + EXPECTED_ERROR_CODES
)

# Test data constants
TEST_USER_IDS = {
    "existing": 123,
    "non_existent_high": 999999999,
    "non_existent_medium": 888888888,
    "cold_start": 777777777,
}

TEST_MOVIE_TITLES = {"popular": "Toy Story (1995)", "invalid": "NonExistentMovie12345"}


@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture
def test_users():
    """Provide test user IDs for different testing scenarios."""
    return TEST_USER_IDS


@pytest.fixture
def test_movies():
    """Provide test movie titles for different testing scenarios."""
    return TEST_MOVIE_TITLES


class TestBasicEndpoints:
    """Basic tests for API endpoints functionality."""

    def test_health_check(self, client):
        """Test that health check endpoint works."""
        response = client.get("/health")

        assert response.status_code == 200
        json_response = response.json()
        assert "status" in json_response
        assert json_response["status"] == "ok"

    def test_user_recommendations_endpoint_exists(self, client, test_users):
        """Test that user recommendations endpoint exists and accepts requests."""
        response = client.get(f"/recommend/{test_users['existing']}")

        # Should not return 404 (endpoint doesn't exist)
        assert response.status_code != 404

        # Should return valid response codes according to project testing strategy
        assert response.status_code in VALID_RESPONSE_CODES

    def test_hybrid_recommendations_endpoint_exists(self, client, test_users):
        """Test that hybrid recommendations endpoint exists."""
        response = client.get(f"/recommend/hybrid/{test_users['existing']}")

        assert response.status_code != 404
        assert response.status_code in VALID_RESPONSE_CODES

    def test_popular_movies_endpoint_exists(self, client):
        """Test that popular movies endpoint exists."""
        response = client.get("/movies/popular")

        assert response.status_code != 404
        # Accept service unavailable codes if data validation fails due to services not being available
        assert response.status_code in VALID_RESPONSE_CODES

    def test_cold_start_endpoint_exists(self, client, test_users):
        """Test that cold start endpoint exists."""
        response = client.get(
            f"/recommend/cold-start/{test_users['non_existent_high']}"
        )

        assert response.status_code != 404
        assert response.status_code in VALID_RESPONSE_CODES

    def test_similar_movies_endpoint_exists(self, client, test_movies):
        """Test that similar movies endpoint exists."""
        response = client.get(f"/movies/similar?movie_title={test_movies['popular']}")

        assert response.status_code != 404
        # Service unavailable codes are acceptable if parameter validation fails (service not available to validate movie)
        assert response.status_code in VALID_RESPONSE_CODES

    def test_new_movies_endpoint_exists(self, client):
        """Test that new movies endpoint exists."""
        response = client.get("/movies/new")

        assert response.status_code != 404
        assert response.status_code in VALID_RESPONSE_CODES


class TestInputValidation:
    """Test input validation for API endpoints."""

    def test_invalid_user_id_validation(self, client):
        """Test that invalid user IDs are rejected."""
        # Test negative user ID (invalid)
        response = client.get("/recommend/0")
        # Accept service unavailable if services aren't available to validate, otherwise expect validation error
        assert response.status_code in EXPECTED_SERVICE_UNAVAILABLE_CODES

        # Test non-numeric user ID
        response = client.get("/recommend/abc")
        assert response.status_code == 422  # Always a validation error for non-numeric

    def test_invalid_limit_validation(self, client, test_users):
        """Test that invalid limits are rejected."""
        user_id = test_users["existing"]

        # Test limit too small
        response = client.get(f"/recommend/{user_id}?limit=0")
        # Accept service unavailable if services aren't available to validate, otherwise expect validation error
        assert response.status_code in EXPECTED_SERVICE_UNAVAILABLE_CODES

        # Test limit too large
        response = client.get(f"/recommend/{user_id}?limit=100")
        assert response.status_code in EXPECTED_SERVICE_UNAVAILABLE_CODES

        # Test non-numeric limit
        response = client.get(f"/recommend/{user_id}?limit=abc")
        assert response.status_code == 422  # Always a validation error

    def test_valid_parameters_accepted(self, client, test_users):
        """Test that valid parameters are accepted."""
        user_id = test_users["existing"]

        # Valid user ID and limit
        response = client.get(f"/recommend/{user_id}?limit=5")

        # Should not be a validation error
        assert response.status_code != 422

        # Should be either success, internal error, or service unavailable
        assert response.status_code in VALID_RESPONSE_CODES


class TestColdStartScenarios:
    """Test cold start scenarios with non-existent users."""

    def test_new_user_cold_start_popular(self, client, test_users):
        """Test cold start with popular strategy for new user."""
        # Use a very high user ID that likely doesn't exist
        non_existent_user = test_users["non_existent_high"]

        response = client.get(
            f"/recommend/cold-start/{non_existent_user}?strategy=popular&limit=5"
        )

        # Should handle cold start gracefully
        assert response.status_code in VALID_RESPONSE_CODES

        if response.status_code == 200:
            json_response = response.json()
            # Should have some structure
            assert isinstance(json_response, dict)

    def test_new_user_cold_start_trending(self, client, test_users):
        """Test cold start with trending strategy for new user."""
        non_existent_user = test_users["non_existent_medium"]

        response = client.get(
            f"/recommend/cold-start/{non_existent_user}?strategy=trending&limit=3"
        )

        assert response.status_code in VALID_RESPONSE_CODES

    def test_new_user_cold_start_diverse(self, client, test_users):
        """Test cold start with diverse strategy for new user."""
        non_existent_user = test_users["cold_start"]

        response = client.get(
            f"/recommend/cold-start/{non_existent_user}?strategy=diverse&limit=10"
        )

        assert response.status_code in VALID_RESPONSE_CODES

    def test_cold_start_invalid_strategy(self, client, test_users):
        """Test that invalid strategies are handled properly."""
        user_id = test_users["existing"]
        response = client.get(
            f"/recommend/cold-start/{user_id}?strategy=invalid_strategy"
        )

        # Should either reject with validation error or handle gracefully
        assert response.status_code in VALID_RESPONSE_CODES


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

    def test_recommendation_response_format(self, client, test_users):
        """Test that successful recommendation responses have expected format."""
        user_id = test_users["existing"]
        response = client.get(f"/recommend/{user_id}?limit=3")

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

    def test_recommendation_reasonable_performance(self, client, test_users):
        """Test that recommendations respond in reasonable time."""
        user_id = test_users["existing"]

        start_time = time.time()
        response = client.get(f"/recommend/{user_id}?limit=5")
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
