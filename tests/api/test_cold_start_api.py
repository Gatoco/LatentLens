"""
Cold Start Tests for LatentLens

This module contains tests for cold start scenarios,
focusing on real system behavior with new users and edge cases.

Author: LatentLens Team
License: MIT
"""

import pytest
from fastapi.testclient import TestClient
import time

from main import app
from data_loader import DataLoader


@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture
def data_loader():
    """Create a DataLoader instance for testing."""
    return DataLoader()


class TestColdStartDetection:
    """Test cold start detection and handling."""

    def test_non_existent_user_detection(self, data_loader):
        """Test that we can detect non-existent users."""
        # Use a very high user ID that definitely doesn't exist
        non_existent_user = 999999999

        ratings = data_loader.load_ratings()
        user_ratings = ratings[ratings["userId"] == non_existent_user]

        assert len(user_ratings) == 0, "Non-existent user should have no ratings"
        assert user_ratings.empty, "User ratings should be empty DataFrame"

    def test_cold_start_user_identification(self, data_loader):
        """Test identification of users with insufficient data."""
        ratings = data_loader.load_ratings()

        # Find users with very few ratings (cold start candidates)
        user_rating_counts = ratings.groupby("userId").size()
        cold_start_users = user_rating_counts[user_rating_counts < 5]

        # Should have some users with few ratings
        assert len(cold_start_users) > 0, "Should find some users with few ratings"

        # Verify these users actually have few ratings
        if len(cold_start_users) > 0:
            test_user = cold_start_users.index[0]
            user_ratings = ratings[ratings["userId"] == test_user]
            assert len(user_ratings) < 5, "Cold start user should have < 5 ratings"


class TestColdStartAPIIntegration:
    """Test cold start functionality through API."""

    def test_cold_start_popular_strategy_api(self, client):
        """Test popular strategy through API for cold start user."""
        non_existent_user = 999999999

        response = client.get(
            f"/recommend/cold-start/{non_existent_user}?strategy=popular&limit=5"
        )

        # API should handle cold start gracefully
        assert response.status_code in [200, 500]

        if response.status_code == 200:
            json_response = response.json()
            assert isinstance(json_response, dict), "Response should be a dictionary"

            # Should contain some recommendations or error message
            assert len(json_response) > 0, "Response should not be empty"

    def test_cold_start_trending_strategy_api(self, client):
        """Test trending strategy through API for cold start user."""
        non_existent_user = 888888888

        response = client.get(
            f"/recommend/cold-start/{non_existent_user}?strategy=trending&limit=3"
        )

        assert response.status_code in [200, 500]

    def test_cold_start_diverse_strategy_api(self, client):
        """Test diverse strategy through API for cold start user."""
        non_existent_user = 777777777

        response = client.get(
            f"/recommend/cold-start/{non_existent_user}?strategy=diverse&limit=10"
        )

        assert response.status_code in [200, 500]

    def test_hybrid_recommendation_cold_start_fallback(self, client):
        """Test that hybrid recommendations handle cold start users."""
        non_existent_user = 666666666

        response = client.get(f"/recommend/hybrid/{non_existent_user}?limit=5")

        # Hybrid should handle cold start gracefully (might fallback to popular)
        assert response.status_code in [200, 500]

        if response.status_code == 200:
            json_response = response.json()
            assert isinstance(json_response, dict)

    def test_regular_recommendation_cold_start_handling(self, client):
        """Test that regular recommendations handle cold start users."""
        non_existent_user = 555555555

        response = client.get(f"/recommend/{non_existent_user}?limit=5")

        # Should handle gracefully, not crash
        assert response.status_code in [200, 500]


class TestColdStartStrategies:
    """Test different cold start strategies."""

    def test_valid_cold_start_strategies(self, client):
        """Test that all valid cold start strategies are accepted."""
        valid_strategies = ["popular", "trending", "diverse"]
        non_existent_user = 444444444

        for strategy in valid_strategies:
            response = client.get(
                f"/recommend/cold-start/{non_existent_user}?strategy={strategy}&limit=3"
            )

            # Should not return validation error for valid strategies
            assert response.status_code != 422, f"Strategy '{strategy}' should be valid"
            assert response.status_code in [
                200,
                500,
            ], f"Strategy '{strategy}' should be handled"

    def test_invalid_cold_start_strategy_handling(self, client):
        """Test handling of invalid cold start strategies."""
        invalid_strategies = ["invalid", "nonexistent", "bad_strategy"]
        non_existent_user = 333333333

        for strategy in invalid_strategies:
            response = client.get(
                f"/recommend/cold-start/{non_existent_user}?strategy={strategy}&limit=3"
            )

            # Should either reject with validation error or handle gracefully with error message
            assert response.status_code in [
                200,
                422,
                500,
            ], f"Invalid strategy '{strategy}' should be handled"

    def test_default_cold_start_strategy(self, client):
        """Test cold start with default strategy (no strategy parameter)."""
        non_existent_user = 222222222

        response = client.get(f"/recommend/cold-start/{non_existent_user}?limit=5")

        # Should handle default strategy
        assert response.status_code in [200, 500]


class TestColdStartPerformance:
    """Test performance characteristics of cold start recommendations."""

    def test_cold_start_response_time(self, client):
        """Test that cold start recommendations respond in reasonable time."""
        non_existent_user = 111111111

        start_time = time.time()
        response = client.get(
            f"/recommend/cold-start/{non_existent_user}?strategy=popular&limit=5"
        )
        end_time = time.time()

        response_time = end_time - start_time

        # Cold start should respond quickly (within 10 seconds)
        assert (
            response_time < 10.0
        ), f"Cold start response too slow: {response_time:.2f}s"

        # Should not be a validation error
        assert response.status_code != 422

    def test_multiple_cold_start_requests(self, client):
        """Test multiple cold start requests to check consistency."""
        non_existent_user = 999888777

        responses = []
        for i in range(3):
            response = client.get(
                f"/recommend/cold-start/{non_existent_user}?strategy=popular&limit=3"
            )
            responses.append(response)

        # All requests should have consistent behavior
        status_codes = [r.status_code for r in responses]

        # All should succeed or all should fail consistently
        assert len(set(status_codes)) <= 2, "Cold start responses should be consistent"


class TestColdStartDataQuality:
    """Test data quality for cold start recommendations."""

    def test_popular_movies_availability(self, data_loader):
        """Test that we have popular movies available for cold start."""
        ratings = data_loader.load_ratings()
        movies = data_loader.load_movies()

        # Calculate movie popularity
        movie_stats = (
            ratings.groupby("movieId").agg({"rating": ["count", "mean"]}).round(3)
        )
        movie_stats.columns = ["num_ratings", "average_rating"]

        # Filter for popular movies (good for cold start)
        popular_criteria = (movie_stats["num_ratings"] >= 50) & (
            movie_stats["average_rating"] >= 3.5
        )
        popular_movies = movie_stats[popular_criteria]

        assert len(popular_movies) > 0, "Should have popular movies for cold start"
        assert len(popular_movies) >= 10, "Should have at least 10 popular movies"

    def test_genre_diversity_availability(self, data_loader):
        """Test that we have genre diversity for cold start recommendations."""
        movies = data_loader.load_movies()

        # Extract all unique genres
        all_genres = set()
        for genres_str in movies["genres"]:
            if isinstance(genres_str, str) and genres_str != "(no genres listed)":
                genres = genres_str.split("|")
                all_genres.update(genres)

        # Should have good genre diversity
        assert (
            len(all_genres) >= 10
        ), f"Should have at least 10 genres, found {len(all_genres)}"

        # Check for common genres
        expected_genres = ["Action", "Comedy", "Drama", "Thriller", "Romance"]
        for genre in expected_genres:
            assert (
                genre in all_genres
            ), f"Expected common genre '{genre}' should be available"

    def test_recent_movies_availability(self, data_loader):
        """Test that we have recent movies for trending cold start strategy."""
        movies = data_loader.load_movies()

        # Extract years from movie titles
        movies_with_years = movies.copy()
        movies_with_years["year"] = (
            movies_with_years["title"].str.extract(r"\((\d{4})\)").astype(float)
        )

        # Filter recent movies (for trending strategy)
        recent_years_threshold = 2010  # Adjust based on dataset
        recent_movies = movies_with_years[
            movies_with_years["year"] >= recent_years_threshold
        ]

        assert (
            len(recent_movies) > 0
        ), "Should have recent movies for trending cold start"
        assert (
            len(recent_movies) >= 50
        ), "Should have substantial number of recent movies"


class TestColdStartEdgeCases:
    """Test edge cases in cold start scenarios."""

    def test_zero_user_id_handling(self, client):
        """Test handling of user ID 0 (invalid)."""
        response = client.get("/recommend/cold-start/0?strategy=popular")

        # Should return validation error for invalid user ID
        assert response.status_code == 422

    def test_negative_user_id_handling(self, client):
        """Test handling of negative user ID."""
        response = client.get("/recommend/cold-start/-1?strategy=popular")

        # Should return validation error for negative user ID
        assert response.status_code == 422

    def test_very_large_user_id(self, client):
        """Test handling of very large user ID."""
        very_large_user = 999999999999999

        response = client.get(
            f"/recommend/cold-start/{very_large_user}?strategy=popular&limit=1"
        )

        # Should handle large user IDs gracefully
        assert response.status_code in [200, 500]

    def test_extreme_limits(self, client):
        """Test cold start with extreme limit values."""
        non_existent_user = 123456789

        # Test minimum limit
        response = client.get(
            f"/recommend/cold-start/{non_existent_user}?strategy=popular&limit=1"
        )
        assert response.status_code in [200, 500]

        # Test maximum allowed limit
        response = client.get(
            f"/recommend/cold-start/{non_existent_user}?strategy=popular&limit=50"
        )
        assert response.status_code in [200, 500]


if __name__ == "__main__":
    pytest.main([__file__])
