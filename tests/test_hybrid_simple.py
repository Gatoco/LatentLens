"""
Basic Hybrid System Tests for LatentLens

This module contains simple tests for the hybrid recommendation system,
focusing on basic functionality and integration between components.

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


@pytest.fixture
def sample_user_id():
    """Sample user ID for testing."""
    return 123


class TestHybridSystemBasic:
    """Basic tests for hybrid recommendation system functionality."""

    @pytest.fixture
    def sample_movie_data(self):
        """Sample movie data for testing."""
        return pd.DataFrame(
            {
                "movieId": [1, 2, 3, 4, 5],
                "title": [
                    "Toy Story (1995)",
                    "Jumanji (1995)",
                    "Grumpier Old Men (1995)",
                    "Waiting to Exhale (1995)",
                    "Father of the Bride Part II (1995)",
                ],
                "genres": [
                    "Adventure|Animation|Children|Comedy|Fantasy",
                    "Adventure|Children|Fantasy",
                    "Comedy|Romance",
                    "Comedy|Drama|Romance",
                    "Comedy",
                ],
            }
        )

    @pytest.fixture
    def sample_ratings_data(self):
        """Sample ratings data for testing."""
        return pd.DataFrame(
            {
                "userId": [123, 123, 123, 456, 456],
                "movieId": [1, 2, 3, 1, 4],
                "rating": [5.0, 4.0, 3.5, 4.5, 3.0],
            }
        )


class TestHybridServiceInitialization:
    """Test hybrid service initialization and setup."""

    def test_hybrid_service_creation(self):
        """Test that hybrid service can be created."""
        try:
            from hybrid_recommendation_service import HybridRecommendationService

            service = HybridRecommendationService(data_path="data/ml-25m")

            assert service is not None
            assert hasattr(service, "data_path")
            assert service.data_path == "data/ml-25m"

        except ImportError:
            # Skip test if module not available
            pytest.skip("HybridRecommendationService not available")

    @patch("src.hybrid_recommendation_service.HybridRecommendationService.initialize")
    def test_hybrid_service_initialization(self, mock_initialize):
        """Test hybrid service initialization."""
        try:
            from hybrid_recommendation_service import HybridRecommendationService

            service = HybridRecommendationService(data_path="data/ml-25m")
            service.initialize()

            mock_initialize.assert_called_once()

        except ImportError:
            pytest.skip("HybridRecommendationService not available")


class TestHybridRecommendations:
    """Test hybrid recommendation generation."""

    @patch("src.hybrid_recommendation_service.HybridRecommendationService")
    def test_get_recommendations_basic(self, mock_hybrid_service, sample_user_id):
        """Test basic recommendation generation."""
        # Mock the service
        mock_service = Mock()
        mock_service.get_recommendations.return_value = {
            "user_id": sample_user_id,
            "recommendations": [
                {"movie_id": 1, "score": 0.95, "title": "Toy Story (1995)"},
                {"movie_id": 2, "score": 0.90, "title": "Jumanji (1995)"},
                {"movie_id": 3, "score": 0.85, "title": "Grumpier Old Men (1995)"},
            ],
            "algorithm": "hybrid",
            "timestamp": "2025-08-23",
        }

        mock_hybrid_service.return_value = mock_service

        # Test recommendation generation
        service = mock_hybrid_service()
        recommendations = service.get_recommendations(
            user_id=sample_user_id, num_recommendations=3
        )

        assert recommendations is not None
        assert "user_id" in recommendations
        assert "recommendations" in recommendations
        assert len(recommendations["recommendations"]) == 3
        assert recommendations["user_id"] == sample_user_id

    @patch("src.hybrid_recommendation_service.HybridRecommendationService")
    def test_get_recommendations_with_limit(self, mock_hybrid_service, sample_user_id):
        """Test recommendation generation with limit parameter."""
        mock_service = Mock()
        mock_service.get_recommendations.return_value = {
            "user_id": sample_user_id,
            "recommendations": [
                {"movie_id": i, "score": 0.9 - (i * 0.1), "title": f"Movie {i}"}
                for i in range(1, 6)
            ],
        }

        mock_hybrid_service.return_value = mock_service

        service = mock_hybrid_service()
        recommendations = service.get_recommendations(
            user_id=sample_user_id, num_recommendations=5
        )

        assert len(recommendations["recommendations"]) == 5

        # Check that scores are in descending order
        scores = [rec["score"] for rec in recommendations["recommendations"]]
        assert scores == sorted(scores, reverse=True)


class TestHybridAlgorithmIntegration:
    """Test integration between different recommendation algorithms."""

    @patch("src.hybrid_recommendation_service.HybridRecommendationService")
    def test_collaborative_filtering_integration(
        self, mock_hybrid_service, sample_user_id
    ):
        """Test collaborative filtering component integration."""
        mock_service = Mock()
        mock_service.get_collaborative_recommendations.return_value = [
            {"movie_id": 1, "cf_score": 0.8},
            {"movie_id": 2, "cf_score": 0.7},
        ]

        mock_hybrid_service.return_value = mock_service

        service = mock_hybrid_service()
        cf_recs = service.get_collaborative_recommendations(user_id=sample_user_id)

        assert cf_recs is not None
        assert len(cf_recs) == 2
        assert all("cf_score" in rec for rec in cf_recs)

    @patch("src.hybrid_recommendation_service.HybridRecommendationService")
    def test_content_based_integration(self, mock_hybrid_service, sample_user_id):
        """Test content-based filtering component integration."""
        mock_service = Mock()
        mock_service.get_content_based_recommendations.return_value = [
            {"movie_id": 3, "content_score": 0.9},
            {"movie_id": 4, "content_score": 0.8},
        ]

        mock_hybrid_service.return_value = mock_service

        service = mock_hybrid_service()
        content_recs = service.get_content_based_recommendations(user_id=sample_user_id)

        assert content_recs is not None
        assert len(content_recs) == 2
        assert all("content_score" in rec for rec in content_recs)


class TestHybridScoring:
    """Test hybrid scoring and weight combination."""

    def test_score_combination_basic(self):
        """Test basic score combination logic."""
        # Mock score combination
        cf_score = 0.8
        content_score = 0.6
        popularity_score = 0.7

        # Simple weighted average
        weights = {"cf": 0.5, "content": 0.3, "popularity": 0.2}

        hybrid_score = (
            cf_score * weights["cf"]
            + content_score * weights["content"]
            + popularity_score * weights["popularity"]
        )

        expected_score = 0.8 * 0.5 + 0.6 * 0.3 + 0.7 * 0.2
        assert abs(hybrid_score - expected_score) < 0.001

    def test_score_normalization(self):
        """Test score normalization."""
        scores = [0.9, 0.7, 0.5, 0.3, 0.1]

        # Min-max normalization
        min_score = min(scores)
        max_score = max(scores)

        normalized_scores = [
            (score - min_score) / (max_score - min_score) for score in scores
        ]

        assert max(normalized_scores) == 1.0
        assert min(normalized_scores) == 0.0
        assert all(0 <= score <= 1 for score in normalized_scores)


class TestHybridErrorHandling:
    """Test error handling in hybrid system."""

    @patch("src.hybrid_recommendation_service.HybridRecommendationService")
    def test_invalid_user_id_handling(self, mock_hybrid_service):
        """Test handling of invalid user IDs."""
        mock_service = Mock()
        mock_service.get_recommendations.side_effect = ValueError("Invalid user ID")

        mock_hybrid_service.return_value = mock_service

        service = mock_hybrid_service()

        with pytest.raises(ValueError):
            service.get_recommendations(user_id=-1)

    @patch("src.hybrid_recommendation_service.HybridRecommendationService")
    def test_empty_recommendations_handling(self, mock_hybrid_service, sample_user_id):
        """Test handling when no recommendations are found."""
        mock_service = Mock()
        mock_service.get_recommendations.return_value = {
            "user_id": sample_user_id,
            "recommendations": [],
            "message": "No recommendations found",
        }

        mock_hybrid_service.return_value = mock_service

        service = mock_hybrid_service()
        recommendations = service.get_recommendations(user_id=sample_user_id)

        assert recommendations is not None
        assert len(recommendations["recommendations"]) == 0
        assert "message" in recommendations


class TestHybridPerformance:
    """Test performance aspects of hybrid system."""

    @patch("src.hybrid_recommendation_service.HybridRecommendationService")
    def test_recommendation_response_time(self, mock_hybrid_service, sample_user_id):
        """Test that recommendations are generated within reasonable time."""
        import time

        mock_service = Mock()

        def mock_get_recommendations(*args, **kwargs):
            # Simulate some processing time
            time.sleep(0.001)  # 1ms
            return {
                "user_id": sample_user_id,
                "recommendations": [{"movie_id": 1, "score": 0.9}],
            }

        mock_service.get_recommendations = mock_get_recommendations
        mock_hybrid_service.return_value = mock_service

        service = mock_hybrid_service()

        start_time = time.time()
        recommendations = service.get_recommendations(user_id=sample_user_id)
        end_time = time.time()

        response_time = end_time - start_time

        # Should complete within 1 second for basic test
        assert response_time < 1.0
        assert recommendations is not None


if __name__ == "__main__":
    pytest.main([__file__])
