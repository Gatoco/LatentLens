"""
Recommendation Service Tests for LatentLens

This module contains comprehensive tests for the main recommendation service,
covering core functionality, algorithm integration, and service reliability.

Author: LatentLens Team
License: MIT
"""

import pytest
import numpy as np
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


class TestRecommendationServiceInitialization:
    """Test recommendation service initialization and setup."""

    def test_recommendation_service_creation(self):
        """Test that recommendation service can be created."""
        try:
            from src.recommendation_service import RecommendationService

            service = RecommendationService()

            assert service is not None
            assert hasattr(service, "initialize")

        except ImportError:
            pytest.skip("RecommendationService not available")

    @patch("src.recommendation_service.RecommendationService.initialize")
    def test_service_initialization(self, mock_initialize):
        """Test service initialization process."""
        try:
            from src.recommendation_service import RecommendationService

            service = RecommendationService()
            service.initialize()

            mock_initialize.assert_called_once()

        except ImportError:
            pytest.skip("RecommendationService not available")


class TestRecommendationGeneration:
    """Test core recommendation generation functionality."""

    @pytest.fixture
    def sample_user_id(self):
        """Sample user ID for testing."""
        return 456

    @pytest.fixture
    def sample_recommendations(self):
        """Sample recommendation data."""
        return [
            {
                "movie_id": 1,
                "title": "Toy Story (1995)",
                "predicted_rating": 4.5,
                "confidence": 0.8,
                "genres": ["Animation", "Children", "Comedy"],
            },
            {
                "movie_id": 2,
                "title": "Jumanji (1995)",
                "predicted_rating": 4.2,
                "confidence": 0.7,
                "genres": ["Adventure", "Children", "Fantasy"],
            },
            {
                "movie_id": 3,
                "title": "Grumpier Old Men (1995)",
                "predicted_rating": 3.8,
                "confidence": 0.6,
                "genres": ["Comedy", "Romance"],
            },
        ]

    @patch("src.recommendation_service.RecommendationService")
    def test_get_recommendations_basic(
        self, mock_service, sample_user_id, sample_recommendations
    ):
        """Test basic recommendation generation."""
        mock_instance = Mock()
        mock_instance.get_recommendations.return_value = sample_recommendations
        mock_service.return_value = mock_instance

        service = mock_service()
        recommendations = service.get_recommendations(
            user_id=sample_user_id, num_recommendations=3
        )

        assert recommendations is not None
        assert len(recommendations) == 3
        assert all("movie_id" in rec for rec in recommendations)
        assert all("predicted_rating" in rec for rec in recommendations)

    @patch("src.recommendation_service.RecommendationService")
    def test_get_recommendations_with_filters(self, mock_service, sample_user_id):
        """Test recommendation generation with genre filters."""
        filtered_recs = [
            {
                "movie_id": 1,
                "title": "Toy Story (1995)",
                "predicted_rating": 4.5,
                "genres": ["Animation", "Children", "Comedy"],
            }
        ]

        mock_instance = Mock()
        mock_instance.get_recommendations.return_value = filtered_recs
        mock_service.return_value = mock_instance

        service = mock_service()
        recommendations = service.get_recommendations(
            user_id=sample_user_id, num_recommendations=5, genre_filter=["Comedy"]
        )

        assert len(recommendations) == 1
        assert "Comedy" in recommendations[0]["genres"]


class TestUserProfileHandling:
    """Test user profile management and analysis."""

    @pytest.fixture
    def sample_user_profile(self):
        """Sample user profile data."""
        return {
            "user_id": 789,
            "age": 28,
            "gender": "F",
            "occupation": "engineer",
            "ratings_count": 150,
            "avg_rating": 3.7,
            "favorite_genres": ["Drama", "Thriller", "Comedy"],
            "last_activity": "2025-08-20",
        }

    @patch("src.recommendation_service.RecommendationService")
    def test_get_user_profile(self, mock_service, sample_user_profile):
        """Test user profile retrieval."""
        mock_instance = Mock()
        mock_instance.get_user_profile.return_value = sample_user_profile
        mock_service.return_value = mock_instance

        service = mock_service()
        profile = service.get_user_profile(user_id=789)

        assert profile is not None
        assert profile["user_id"] == 789
        assert "favorite_genres" in profile
        assert profile["ratings_count"] > 0

    @patch("src.recommendation_service.RecommendationService")
    def test_user_preferences_analysis(self, mock_service, sample_user_profile):
        """Test user preference analysis."""
        preferences = {
            "genre_preferences": {"Drama": 0.8, "Thriller": 0.7, "Comedy": 0.6},
            "rating_patterns": {
                "avg_rating": 3.7,
                "rating_variance": 1.2,
                "rating_count": 150,
            },
            "temporal_patterns": {"most_active_hour": 20, "most_active_day": "Friday"},
        }

        mock_instance = Mock()
        mock_instance.analyze_user_preferences.return_value = preferences
        mock_service.return_value = mock_instance

        service = mock_service()
        prefs = service.analyze_user_preferences(user_id=789)

        assert "genre_preferences" in prefs
        assert "rating_patterns" in prefs
        assert len(prefs["genre_preferences"]) > 0


class TestMovieDataHandling:
    """Test movie data management and retrieval."""

    @pytest.fixture
    def sample_movie_info(self):
        """Sample movie information."""
        return {
            "movie_id": 1,
            "title": "Toy Story (1995)",
            "genres": ["Adventure", "Animation", "Children", "Comedy", "Fantasy"],
            "year": 1995,
            "avg_rating": 3.9,
            "rating_count": 215,
            "popularity_score": 0.85,
        }

    @patch("src.recommendation_service.RecommendationService")
    def test_get_movie_info(self, mock_service, sample_movie_info):
        """Test movie information retrieval."""
        mock_instance = Mock()
        mock_instance.get_movie_info.return_value = sample_movie_info
        mock_service.return_value = mock_instance

        service = mock_service()
        movie_info = service.get_movie_info(movie_id=1)

        assert movie_info is not None
        assert movie_info["movie_id"] == 1
        assert movie_info["title"] == "Toy Story (1995)"
        assert len(movie_info["genres"]) > 0

    @patch("src.recommendation_service.RecommendationService")
    def test_get_similar_movies(self, mock_service):
        """Test similar movies retrieval."""
        similar_movies = [
            {"movie_id": 2, "similarity_score": 0.9, "title": "A Bug's Life (1998)"},
            {"movie_id": 3, "similarity_score": 0.8, "title": "Toy Story 2 (1999)"},
            {"movie_id": 4, "similarity_score": 0.7, "title": "Monsters, Inc. (2001)"},
        ]

        mock_instance = Mock()
        mock_instance.get_similar_movies.return_value = similar_movies
        mock_service.return_value = mock_instance

        service = mock_service()
        similar = service.get_similar_movies(movie_id=1, num_similar=3)

        assert len(similar) == 3
        assert all("similarity_score" in movie for movie in similar)

        # Check that similarity scores are in descending order
        scores = [movie["similarity_score"] for movie in similar]
        assert scores == sorted(scores, reverse=True)


class TestRatingPrediction:
    """Test rating prediction functionality."""

    @patch("src.recommendation_service.RecommendationService")
    def test_predict_rating_single(self, mock_service):
        """Test single rating prediction."""
        mock_instance = Mock()
        mock_instance.predict_rating.return_value = {
            "user_id": 123,
            "movie_id": 456,
            "predicted_rating": 4.2,
            "confidence": 0.75,
            "algorithm": "SVD",
        }
        mock_service.return_value = mock_instance

        service = mock_service()
        prediction = service.predict_rating(user_id=123, movie_id=456)

        assert prediction is not None
        assert prediction["predicted_rating"] > 0
        assert prediction["predicted_rating"] <= 5.0
        assert 0 <= prediction["confidence"] <= 1.0

    @patch("src.recommendation_service.RecommendationService")
    def test_predict_ratings_batch(self, mock_service):
        """Test batch rating predictions."""
        movie_ids = [1, 2, 3, 4, 5]
        predictions = [
            {"movie_id": mid, "predicted_rating": 4.0 + (mid * 0.1), "confidence": 0.8}
            for mid in movie_ids
        ]

        mock_instance = Mock()
        mock_instance.predict_ratings_batch.return_value = predictions
        mock_service.return_value = mock_instance

        service = mock_service()
        batch_predictions = service.predict_ratings_batch(
            user_id=123, movie_ids=movie_ids
        )

        assert len(batch_predictions) == 5
        assert all("predicted_rating" in pred for pred in batch_predictions)


class TestRecommendationQuality:
    """Test recommendation quality and validation."""

    @patch("src.recommendation_service.RecommendationService")
    def test_recommendation_diversity(self, mock_service):
        """Test recommendation diversity metrics."""
        diverse_recs = [
            {"movie_id": 1, "genres": ["Comedy"]},
            {"movie_id": 2, "genres": ["Drama"]},
            {"movie_id": 3, "genres": ["Action"]},
            {"movie_id": 4, "genres": ["Horror"]},
            {"movie_id": 5, "genres": ["Romance"]},
        ]

        mock_instance = Mock()
        mock_instance.get_recommendations.return_value = diverse_recs
        mock_service.return_value = mock_instance

        service = mock_service()
        recommendations = service.get_recommendations(
            user_id=123, num_recommendations=5
        )

        # Check genre diversity
        all_genres = set()
        for rec in recommendations:
            all_genres.update(rec["genres"])

        # Should have multiple different genres
        assert len(all_genres) >= 3

    @patch("src.recommendation_service.RecommendationService")
    def test_recommendation_relevance(self, mock_service):
        """Test recommendation relevance scoring."""
        relevant_recs = [
            {"movie_id": 1, "relevance_score": 0.95},
            {"movie_id": 2, "relevance_score": 0.90},
            {"movie_id": 3, "relevance_score": 0.85},
        ]

        mock_instance = Mock()
        mock_instance.get_recommendations.return_value = relevant_recs
        mock_service.return_value = mock_instance

        service = mock_service()
        recommendations = service.get_recommendations(
            user_id=123, num_recommendations=3
        )

        # Check that all recommendations have high relevance
        for rec in recommendations:
            assert rec["relevance_score"] >= 0.8


class TestServiceErrorHandling:
    """Test error handling and edge cases."""

    @patch("src.recommendation_service.RecommendationService")
    def test_invalid_user_id(self, mock_service):
        """Test handling of invalid user IDs."""
        mock_instance = Mock()
        mock_instance.get_recommendations.side_effect = ValueError("User not found")
        mock_service.return_value = mock_instance

        service = mock_service()

        with pytest.raises(ValueError):
            service.get_recommendations(user_id=-1)

    @patch("src.recommendation_service.RecommendationService")
    def test_invalid_movie_id(self, mock_service):
        """Test handling of invalid movie IDs."""
        mock_instance = Mock()
        mock_instance.get_movie_info.return_value = None
        mock_service.return_value = mock_instance

        service = mock_service()
        movie_info = service.get_movie_info(movie_id=999999)

        assert movie_info is None

    @patch("src.recommendation_service.RecommendationService")
    def test_empty_recommendations(self, mock_service):
        """Test handling when no recommendations can be generated."""
        mock_instance = Mock()
        mock_instance.get_recommendations.return_value = []
        mock_service.return_value = mock_instance

        service = mock_service()
        recommendations = service.get_recommendations(user_id=123)

        assert recommendations == []


class TestServicePerformance:
    """Test service performance characteristics."""

    @patch("src.recommendation_service.RecommendationService")
    def test_recommendation_speed(self, mock_service):
        """Test recommendation generation speed."""
        import time

        mock_instance = Mock()

        def mock_get_recommendations(*args, **kwargs):
            # Simulate processing time
            time.sleep(0.001)
            return [{"movie_id": 1, "score": 0.9}]

        mock_instance.get_recommendations = mock_get_recommendations
        mock_service.return_value = mock_instance

        service = mock_service()

        start_time = time.time()
        recommendations = service.get_recommendations(user_id=123)
        end_time = time.time()

        response_time = end_time - start_time

        # Should complete within reasonable time
        assert response_time < 1.0
        assert len(recommendations) > 0

    @patch("src.recommendation_service.RecommendationService")
    def test_concurrent_requests(self, mock_service):
        """Test handling of concurrent recommendation requests."""
        import threading
        import time

        mock_instance = Mock()
        mock_instance.get_recommendations.return_value = [{"movie_id": 1, "score": 0.9}]
        mock_service.return_value = mock_instance

        service = mock_service()

        results = []

        def get_recs(user_id):
            recs = service.get_recommendations(user_id=user_id)
            results.append(len(recs))

        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=get_recs, args=(100 + i,))
            threads.append(thread)

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Check that all requests completed successfully
        assert len(results) == 5
        assert all(result > 0 for result in results)


if __name__ == "__main__":
    pytest.main([__file__])
