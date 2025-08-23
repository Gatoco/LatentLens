"""
Comprehensive Cold Start Tests for LatentLens

This module contains comprehensive tests for cold start scenarios,
including new users, new movies, and insufficient data cases.

Author: LatentLens Team
License: MIT
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import pandas as pd

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
    """Test suite for cold start detection mechanisms."""

    def test_new_user_detection_zero_ratings(self, data_loader):
        """Test detection of completely new users with zero ratings."""
        # Test with a user ID that definitely doesn't exist
        non_existent_user = 999999999
        ratings = data_loader.load_ratings()
        user_ratings = ratings[ratings["userId"] == non_existent_user]

        assert len(user_ratings) == 0, "New user should have no ratings"
        assert user_ratings.empty, "User ratings DataFrame should be empty"

    def test_insufficient_data_detection(self, data_loader):
        """Test detection of users with insufficient rating data."""
        ratings = data_loader.load_ratings()
        user_rating_counts = ratings.groupby("userId").size()
        users_with_few_ratings = user_rating_counts[user_rating_counts < 5]

        if len(users_with_few_ratings) > 0:
            test_user = users_with_few_ratings.index[0]
            user_ratings = ratings[ratings["userId"] == test_user]
            assert (
                len(user_ratings) < 5
            ), "User should have insufficient data for reliable recommendations"

    def test_cold_start_threshold_detection(self, data_loader):
        """Test detection based on configurable rating thresholds."""
        ratings = data_loader.load_ratings()

        # Test different thresholds
        thresholds = [5, 10, 20]

        for threshold in thresholds:
            user_rating_counts = ratings.groupby("userId").size()
            cold_start_users = user_rating_counts[user_rating_counts < threshold]

            # Verify cold start users actually have fewer ratings than threshold
            for user_id in cold_start_users.index[:5]:  # Test first 5 users
                user_count = user_rating_counts[user_id]
                assert (
                    user_count < threshold
                ), f"User {user_id} should be below threshold {threshold}"


class TestColdStartStrategies:
    """Test suite for different cold start recommendation strategies."""

    @patch("src.main.recommender")
    def test_popular_strategy_cold_start(self, mock_recommender, client):
        """Test popular strategy for cold start users."""
        mock_recommender.recommend.return_value = [
            {
                "movieId": 318,
                "title": "Shawshank Redemption, The (1994)",
                "genres": "Crime|Drama",
                "average_rating": 4.429,
                "num_ratings": 317,
                "popularity_rank": 1,
            },
            {
                "movieId": 858,
                "title": "Godfather, The (1972)",
                "genres": "Crime|Drama",
                "average_rating": 4.364,
                "num_ratings": 192,
                "popularity_rank": 2,
            },
        ]

        # Test with non-existent user (cold start scenario)
        response = client.get("/recommend/cold-start/999999?strategy=popular&limit=2")

        assert response.status_code == 200
        json_response = response.json()

        assert json_response["user_id"] == 999999
        assert json_response["strategy"] == "cold_start"
        assert len(json_response["recommendations"]) == 2

        # Verify popular movies have high ratings and many ratings
        for movie in json_response["recommendations"]:
            assert (
                movie["average_rating"] > 4.0
            ), "Popular movies should have high ratings"
            assert movie["num_ratings"] > 100, "Popular movies should have many ratings"

        mock_recommender.recommend.assert_called_once_with(
            999999, "cold_start", 2, strategy="popular"
        )

    @patch("src.main.recommender")
    def test_trending_strategy_cold_start(self, mock_recommender, client):
        """Test trending strategy for cold start users."""
        mock_recommender.recommend.return_value = [
            {
                "movieId": 122886,
                "title": "Mad Max: Fury Road (2015)",
                "genres": "Action|Adventure|Sci-Fi|Thriller",
                "year": 2015,
                "average_rating": 4.1,
                "recent_popularity": True,
            },
            {
                "movieId": 122904,
                "title": "Ant-Man (2015)",
                "genres": "Action|Adventure|Sci-Fi",
                "year": 2015,
                "average_rating": 3.8,
                "recent_popularity": True,
            },
        ]

        response = client.get("/recommend/cold-start/888888?strategy=trending&limit=2")

        assert response.status_code == 200
        json_response = response.json()

        assert json_response["user_id"] == 888888
        assert len(json_response["recommendations"]) == 2

        # Verify trending movies are recent
        for movie in json_response["recommendations"]:
            assert movie["year"] >= 2014, "Trending movies should be recent"
            assert (
                movie["recent_popularity"] == True
            ), "Movies should be marked as trending"

        mock_recommender.recommend.assert_called_once_with(
            888888, "cold_start", 2, strategy="trending"
        )

    @patch("src.main.recommender")
    def test_diverse_strategy_cold_start(self, mock_recommender, client):
        """Test diverse strategy for cold start users."""
        mock_recommender.recommend.return_value = [
            {
                "movieId": 1,
                "title": "Toy Story (1995)",
                "genres": "Adventure|Animation|Children|Comedy|Fantasy",
                "primary_genre": "Animation",
            },
            {
                "movieId": 260,
                "title": "Star Wars: Episode IV - A New Hope (1977)",
                "genres": "Action|Adventure|Sci-Fi",
                "primary_genre": "Action",
            },
            {
                "movieId": 527,
                "title": "Schindler's List (1993)",
                "genres": "Drama|War",
                "primary_genre": "Drama",
            },
        ]

        response = client.get("/recommend/cold-start/777777?strategy=diverse&limit=3")

        assert response.status_code == 200
        json_response = response.json()

        assert json_response["user_id"] == 777777
        assert len(json_response["recommendations"]) == 3

        # Verify genre diversity
        genres = [movie["primary_genre"] for movie in json_response["recommendations"]]
        unique_genres = set(genres)
        assert (
            len(unique_genres) == 3
        ), "Diverse strategy should provide different genres"

        mock_recommender.recommend.assert_called_once_with(
            777777, "cold_start", 3, strategy="diverse"
        )


class TestColdStartAPIIntegration:
    """Test suite for cold start API integration scenarios."""

    def test_cold_start_user_api_flow(self, client):
        """Test complete API flow for cold start user."""
        # Test 1: Try hybrid recommendation for non-existent user
        # This should gracefully handle the cold start scenario
        with patch("src.main.recommender") as mock_recommender:
            mock_recommender.recommend.return_value = [
                {
                    "movieId": 318,
                    "title": "Shawshank Redemption, The (1994)",
                    "genres": "Crime|Drama",
                    "cold_start": True,
                }
            ]

            response = client.get("/recommend/hybrid/999999999")

            # Even for cold start, API should return 200 with fallback recommendations
            assert response.status_code == 200

    def test_cold_start_error_handling(self, client):
        """Test error handling in cold start scenarios."""
        with patch("src.main.recommender") as mock_recommender:
            mock_recommender.recommend.side_effect = Exception(
                "Cold start service error"
            )

            response = client.get("/recommend/cold-start/999999?strategy=popular")

            # API should handle errors gracefully
            assert response.status_code == 500
            json_response = response.json()
            assert "detail" in json_response

    def test_cold_start_strategy_validation(self, client):
        """Test validation of cold start strategies."""
        # Test valid strategies
        valid_strategies = ["popular", "trending", "diverse"]

        for strategy in valid_strategies:
            with patch("src.main.recommender"):
                response = client.get(f"/recommend/cold-start/123?strategy={strategy}")
                # Should not fail on validation
                assert response.status_code != 422

        # Test invalid strategy
        response = client.get("/recommend/cold-start/123?strategy=invalid_strategy")
        assert response.status_code == 422  # Validation error


class TestColdStartDataGeneration:
    """Test suite for cold start data generation."""

    def test_popular_movies_generation(self, data_loader):
        """Test generation of popular movies for cold start."""
        ratings = data_loader.load_ratings()
        movies = data_loader.load_movies()

        # Calculate movie popularity (minimum 100 ratings, minimum 4.0 rating)
        movie_stats = (
            ratings.groupby("movieId").agg({"rating": ["count", "mean"]}).round(3)
        )
        movie_stats.columns = ["num_ratings", "average_rating"]

        popular_movies = movie_stats[
            (movie_stats["num_ratings"] >= 100) & (movie_stats["average_rating"] >= 4.0)
        ].sort_values("average_rating", ascending=False)

        # Verify we have popular movies for cold start
        assert (
            len(popular_movies) > 0
        ), "Should have popular movies available for cold start"
        assert len(popular_movies) >= 10, "Should have at least 10 popular movies"

        # Verify popular movies meet criteria
        for movie_id, stats in popular_movies.head(10).iterrows():
            assert (
                stats["num_ratings"] >= 100
            ), f"Movie {movie_id} should have ≥100 ratings"
            assert (
                stats["average_rating"] >= 4.0
            ), f"Movie {movie_id} should have ≥4.0 rating"

    def test_trending_movies_generation(self, data_loader):
        """Test generation of trending movies for cold start."""
        movies = data_loader.load_movies()

        # Extract year from title and filter recent movies (last 5 years from dataset)
        movies["year"] = movies["title"].str.extract(r"\((\d{4})\)").astype(float)
        recent_movies = movies[movies["year"] >= 2014]  # Dataset ends around 2019

        assert (
            len(recent_movies) > 0
        ), "Should have recent movies for trending recommendations"
        assert (
            len(recent_movies) >= 100
        ), "Should have substantial number of recent movies"

        # Verify year extraction works
        for _, movie in recent_movies.head(10).iterrows():
            assert (
                movie["year"] >= 2014
            ), f"Movie should be from 2014 or later: {movie['title']}"

    def test_diverse_genre_generation(self, data_loader):
        """Test generation of diverse genre recommendations for cold start."""
        movies = data_loader.load_movies()

        # Extract unique genres
        all_genres = set()
        for genres in movies["genres"]:
            if pd.notna(genres) and genres != "(no genres listed)":
                all_genres.update(genres.split("|"))

        # Should have substantial genre diversity
        assert (
            len(all_genres) >= 15
        ), f"Should have at least 15 genres, found {len(all_genres)}"

        # Verify common genres are present
        expected_genres = [
            "Action",
            "Comedy",
            "Drama",
            "Thriller",
            "Romance",
            "Adventure",
        ]
        for genre in expected_genres:
            assert genre in all_genres, f"Expected genre '{genre}' should be present"


class TestColdStartPerformance:
    """Test suite for cold start performance characteristics."""

    @patch("src.main.recommender")
    def test_cold_start_response_time(self, mock_recommender, client):
        """Test that cold start recommendations have acceptable response time."""
        import time

        # Mock quick response
        mock_recommender.recommend.return_value = [
            {"movieId": 1, "title": "Test Movie", "genres": "Action"}
        ]

        start_time = time.time()
        response = client.get("/recommend/cold-start/999999?strategy=popular&limit=5")
        end_time = time.time()

        response_time = end_time - start_time

        assert response.status_code == 200
        assert (
            response_time < 5.0
        ), f"Cold start response should be <5s, got {response_time:.2f}s"

    @patch("src.main.recommender")
    def test_cold_start_recommendation_quality(self, mock_recommender, client):
        """Test that cold start recommendations meet quality criteria."""
        mock_recommender.recommend.return_value = [
            {
                "movieId": 318,
                "title": "Shawshank Redemption, The (1994)",
                "genres": "Crime|Drama",
                "average_rating": 4.429,
                "num_ratings": 317,
                "quality_score": 0.95,
            }
        ]

        response = client.get("/recommend/cold-start/999999?strategy=popular&limit=1")

        assert response.status_code == 200
        json_response = response.json()

        recommendation = json_response["recommendations"][0]
        assert (
            recommendation["average_rating"] > 4.0
        ), "Cold start recommendations should be high quality"
        assert (
            recommendation["num_ratings"] > 100
        ), "Cold start recommendations should be well-established"


if __name__ == "__main__":
    pytest.main([__file__])
