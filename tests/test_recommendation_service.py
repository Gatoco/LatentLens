"""
Unit Tests for Recommendation Service Module

This module contains tests for the recommendation service that provides
movie recommendations using popularity baselines and collaborative filtering.

Author: LatentLens Team
License: MIT
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock

from src.recommendation_service import (
    RecommendationService,
    get_recommendations_for_user,
    get_popular_movies,
    get_similar_movies
)


@pytest.fixture
def sample_data():
    """Create sample data for testing."""
    return pd.DataFrame({
        'userId': [1, 1, 2, 2, 3, 3, 4, 4] * 10,
        'title': ['Movie A', 'Movie B', 'Movie A', 'Movie C', 'Movie B', 'Movie C', 'Movie A', 'Movie D'] * 10,
        'rating': [5.0, 4.0, 4.5, 3.0, 4.5, 5.0, 3.5, 4.0] * 10
    })


@pytest.fixture
def recommendation_service():
    """Create a recommendation service instance for testing."""
    return RecommendationService()


class TestRecommendationService:
    """Test suite for RecommendationService class."""
    
    def test_initialization(self, recommendation_service):
        """Test that the service initializes properly."""
        assert not recommendation_service._is_initialized
        assert recommendation_service.data_df is None
        assert recommendation_service.movie_stats is None
    
    @patch('src.recommendation_service.load_and_prepare_data')
    def test_initialize_loads_data(self, mock_load_data, recommendation_service, sample_data):
        """Test that initialize method loads data correctly."""
        mock_load_data.return_value = sample_data
        
        recommendation_service.initialize()
        
        assert recommendation_service._is_initialized
        assert recommendation_service.data_df is not None
        assert recommendation_service.movie_stats is not None
        mock_load_data.assert_called_once()
    
    @patch('src.recommendation_service.load_and_prepare_data')
    def test_get_popular_recommendations(self, mock_load_data, recommendation_service, sample_data):
        """Test popular recommendations functionality."""
        mock_load_data.return_value = sample_data
        
        recommendations = recommendation_service.get_popular_recommendations(num_recommendations=2)
        
        assert len(recommendations) <= 2
        assert all('title' in rec for rec in recommendations)
        assert all('average_rating' in rec for rec in recommendations)
        assert all('num_ratings' in rec for rec in recommendations)
        assert all(rec['recommendation_type'] == 'popularity_baseline' for rec in recommendations)
    
    @patch('src.recommendation_service.load_and_prepare_data')
    def test_get_collaborative_recommendations_movie_not_found(self, mock_load_data, recommendation_service, sample_data):
        """Test collaborative filtering with non-existent movie."""
        mock_load_data.return_value = sample_data
        
        with pytest.raises(ValueError, match="Movie 'Non-existent Movie' not found"):
            recommendation_service.get_collaborative_recommendations('Non-existent Movie')
    
    @patch('src.recommendation_service.load_and_prepare_data')
    def test_get_user_recommendations(self, mock_load_data, recommendation_service, sample_data):
        """Test user recommendations functionality."""
        mock_load_data.return_value = sample_data
        
        recommendations = recommendation_service.get_user_recommendations(
            user_id=123, 
            num_recommendations=3
        )
        
        assert len(recommendations) <= 3
        assert all(rec['user_id'] == 123 for rec in recommendations)
        assert all('title' in rec for rec in recommendations)
    
    def test_double_initialization(self, recommendation_service):
        """Test that calling initialize twice doesn't cause issues."""
        with patch('src.recommendation_service.load_and_prepare_data') as mock_load:
            mock_load.return_value = pd.DataFrame({'userId': [1], 'title': ['Test'], 'rating': [5.0]})
            
            recommendation_service.initialize()
            recommendation_service.initialize()  # Second call
            
            # Should only load data once
            assert mock_load.call_count == 1
            assert recommendation_service._is_initialized


class TestConvenienceFunctions:
    """Test suite for convenience functions."""
    
    @patch('src.recommendation_service.recommendation_service')
    def test_get_recommendations_for_user(self, mock_service):
        """Test get_recommendations_for_user convenience function."""
        mock_service.get_user_recommendations.return_value = [
            {"title": "Test Movie", "user_id": 123}
        ]
        
        result = get_recommendations_for_user(123, 5)
        
        mock_service.get_user_recommendations.assert_called_once_with(123, 5)
        assert result == [{"title": "Test Movie", "user_id": 123}]
    
    @patch('src.recommendation_service.recommendation_service')
    def test_get_popular_movies(self, mock_service):
        """Test get_popular_movies convenience function."""
        mock_service.get_popular_recommendations.return_value = [
            {"title": "Popular Movie", "average_rating": 4.5}
        ]
        
        result = get_popular_movies(10)
        
        mock_service.get_popular_recommendations.assert_called_once_with(10)
        assert result == [{"title": "Popular Movie", "average_rating": 4.5}]
    
    @patch('src.recommendation_service.recommendation_service')
    def test_get_similar_movies(self, mock_service):
        """Test get_similar_movies convenience function."""
        mock_service.get_collaborative_recommendations.return_value = [
            {"title": "Similar Movie", "similarity_score": 0.85}
        ]
        
        result = get_similar_movies("Test Movie", 5)
        
        mock_service.get_collaborative_recommendations.assert_called_once_with("Test Movie", 5)
        assert result == [{"title": "Similar Movie", "similarity_score": 0.85}]


class TestDataProcessing:
    """Test suite for data processing methods."""
    
    @patch('src.recommendation_service.load_and_prepare_data')
    def test_prepare_collaborative_filtering(self, mock_load_data, recommendation_service):
        """Test collaborative filtering preparation."""
        # Create larger sample data for filtering
        sample_data = pd.DataFrame({
            'userId': list(range(1, 101)) * 100,  # 100 users, 100 ratings each
            'title': [f'Movie {i%50}' for i in range(10000)],  # 50 unique movies
            'rating': np.random.uniform(1, 5, 10000)
        })
        mock_load_data.return_value = sample_data
        
        recommendation_service.initialize()
        
        # Check that collaborative filtering components are created
        assert recommendation_service.movie_user_matrix is not None
        assert recommendation_service.movie_user_matrix_sparse is not None
        assert recommendation_service.knn_model is not None


class TestErrorHandling:
    """Test suite for error handling scenarios."""
    
    @patch('src.recommendation_service.load_and_prepare_data')
    def test_invalid_recommendation_type(self, mock_load_data, recommendation_service, sample_data):
        """Test handling of invalid recommendation type."""
        mock_load_data.return_value = sample_data
        
        with pytest.raises(ValueError, match="Unsupported recommendation type"):
            recommendation_service.get_user_recommendations(
                user_id=123, 
                recommendation_type="invalid_type"
            )
    
    @patch('src.recommendation_service.load_and_prepare_data')
    def test_empty_data_handling(self, mock_load_data, recommendation_service):
        """Test handling of empty data."""
        mock_load_data.return_value = pd.DataFrame(columns=['userId', 'title', 'rating'])
        
        # Should not raise an error, but might return empty results
        recommendation_service.initialize()
        assert recommendation_service._is_initialized
