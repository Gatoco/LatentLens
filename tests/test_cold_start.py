import pytest
import numpy as np
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
import time

class TestColdStart:
    """Comprehensive tests for cold start recommendation functionality."""
    
    @pytest.fixture
    def new_user_profile(self):
        """Profile for a new user with no history."""
        return {
            'user_id': 99999,
            'age': 25,
            'gender': 'M',
            'occupation': 'student',
            'zip_code': '12345',
            'registration_date': '2025-08-21',
            'interaction_count': 0
        }
    
    @pytest.fixture
    def sparse_user_profile(self):
        """Profile for user with minimal interactions."""
        return {
            'user_id': 88888,
            'age': 30,
            'gender': 'F',
            'occupation': 'engineer',
            'interaction_count': 2,
            'ratings': [
                {'movie_id': 1, 'rating': 5.0},
                {'movie_id': 50, 'rating': 4.0}
            ]
        }

class TestColdStartDetection:
    """Test cold start user detection functionality."""
    
    def test_new_user_detection(self, new_user_profile):
        """Test detection of completely new users."""
        from tests.test_cold_start import ColdStartHandler
        
        handler = ColdStartHandler()
        
        is_cold_start = handler.is_cold_start_user(new_user_profile)
        
        assert is_cold_start == True
        
        cold_start_type = handler.get_cold_start_type(new_user_profile)
        assert cold_start_type == 'new_user'
    
    def test_sparse_user_detection(self, sparse_user_profile):
        """Test detection of users with sparse data."""
        from tests.test_cold_start import ColdStartHandler
        
        handler = ColdStartHandler(min_interactions_threshold=5)
        
        is_cold_start = handler.is_cold_start_user(sparse_user_profile)
        
        assert is_cold_start == True
        
        cold_start_type = handler.get_cold_start_type(sparse_user_profile)
        assert cold_start_type == 'sparse_user'

class TestPopularityBasedRecommendations:
    """Test popularity-based recommendations for cold start users."""
    
    def test_global_popularity_recommendations(self, new_user_profile):
        """Test global popularity-based recommendations."""
        from tests.test_cold_start import ColdStartHandler
        
        handler = ColdStartHandler()
        
        recommendations = handler.get_popularity_recommendations(
            user_profile=new_user_profile,
            num_recommendations=10
        )
        
        assert len(recommendations) <= 10
        assert all('movie_id' in rec for rec in recommendations)
        assert all('popularity_score' in rec for rec in recommendations)
        
        # Should be sorted by popularity
        scores = [rec['popularity_score'] for rec in recommendations]
        assert scores == sorted(scores, reverse=True)
    
    def test_demographic_popularity_recommendations(self, new_user_profile):
        """Test demographic-based popularity recommendations."""
        from tests.test_cold_start import ColdStartHandler
        
        handler = ColdStartHandler()
        
        demographic_recs = handler.get_demographic_popularity_recommendations(
            user_profile=new_user_profile,
            num_recommendations=10
        )
        
        assert len(demographic_recs) <= 10
        assert all('movie_id' in rec for rec in demographic_recs)
        assert all('demographic_score' in rec for rec in demographic_recs)

class TestContentBasedColdStart:
    """Test content-based approaches for cold start."""
    
    def test_genre_based_recommendations(self, sparse_user_profile):
        """Test genre-based recommendations for sparse users."""
        from tests.test_cold_start import ColdStartHandler
        
        handler = ColdStartHandler()
        
        genre_recs = handler.get_genre_based_recommendations(
            user_profile=sparse_user_profile,
            num_recommendations=10
        )
        
        assert len(genre_recs) <= 10
        assert all('movie_id' in rec for rec in genre_recs)
        assert all('genre_match_score' in rec for rec in genre_recs)

# Mock implementation
class ColdStartHandler:
    """Mock cold start handler for testing."""
    
    def __init__(self, min_interactions_threshold=10):
        self.min_interactions_threshold = min_interactions_threshold
        self.popular_movies = [
            {'movie_id': 1, 'popularity_score': 0.95},
            {'movie_id': 2, 'popularity_score': 0.90},
            {'movie_id': 3, 'popularity_score': 0.85},
            {'movie_id': 4, 'popularity_score': 0.80},
            {'movie_id': 5, 'popularity_score': 0.75}
        ]
    
    def is_cold_start_user(self, user_profile):
        """Check if user is cold start."""
        interaction_count = user_profile.get('interaction_count', 0)
        return interaction_count < self.min_interactions_threshold
    
    def get_cold_start_type(self, user_profile):
        """Determine type of cold start."""
        interaction_count = user_profile.get('interaction_count', 0)
        
        if interaction_count == 0:
            return 'new_user'
        elif interaction_count < self.min_interactions_threshold:
            return 'sparse_user'
        else:
            return 'not_cold_start'
    
    def get_popularity_recommendations(self, user_profile, num_recommendations=10):
        """Get popularity-based recommendations."""
        return self.popular_movies[:num_recommendations]
    
    def get_demographic_popularity_recommendations(self, user_profile, num_recommendations=10):
        """Get demographic-based popularity recommendations."""
        # Mock demographic filtering
        demographic_movies = []
        for movie in self.popular_movies[:num_recommendations]:
            demographic_movies.append({
                'movie_id': movie['movie_id'],
                'demographic_score': movie['popularity_score'] * 0.9  # Slight adjustment
            })
        return demographic_movies
    
    def get_genre_based_recommendations(self, user_profile, num_recommendations=10):
        """Get genre-based recommendations."""
        # Mock genre-based recommendations
        genre_movies = []
        for i in range(min(num_recommendations, 5)):
            genre_movies.append({
                'movie_id': 100 + i,
                'genre_match_score': 0.8 - (i * 0.1)
            })
        return genre_movies
