"""
Unit Tests for Data Validation Module

This module contains tests for the data validation functions that ensure
data quality and integrity in the LatentLens recommendation system.

Author: LatentLens Team
License: MIT
"""

import pytest
import pandas as pd
import numpy as np
from src.data_validation import (
    validate_ratings_dataframe,
    validate_movies_dataframe,
    calculate_sparsity_ratio,
    generate_data_quality_report
)


class TestRatingsValidation:
    """Test suite for ratings DataFrame validation."""
    
    def test_valid_ratings_dataframe(self):
        """Test validation of a properly formatted ratings DataFrame."""
        # Arrange: Create a valid ratings DataFrame
        valid_ratings_data = {
            'userId': [1, 2, 3, 1, 2],
            'movieId': [101, 102, 103, 102, 103],
            'rating': [4.0, 3.5, 5.0, 2.5, 4.5],
            'timestamp': [1234567890, 1234567891, 1234567892, 1234567893, 1234567894]
        }
        ratings_dataframe = pd.DataFrame(valid_ratings_data)
        
        # Act: Validate the DataFrame
        validation_result = validate_ratings_dataframe(ratings_dataframe)
        
        # Assert: Should be valid with no errors
        assert validation_result['is_valid'] is True
        assert len(validation_result['errors']) == 0
        assert validation_result['statistics']['total_ratings'] == 5
        assert validation_result['statistics']['unique_users'] == 3
        assert validation_result['statistics']['unique_movies'] == 3
    
    def test_missing_required_columns(self):
        """Test validation when required columns are missing."""
        # Arrange: Create DataFrame missing required columns
        invalid_ratings_data = {
            'user_id': [1, 2, 3],  # Wrong column name
            'rating': [4.0, 3.5, 5.0]
            # Missing movieId
        }
        ratings_dataframe = pd.DataFrame(invalid_ratings_data)
        
        # Act
        validation_result = validate_ratings_dataframe(ratings_dataframe)
        
        # Assert: Should be invalid with specific errors
        assert validation_result['is_valid'] is False
        assert len(validation_result['errors']) > 0
        assert any('Missing required columns' in error for error in validation_result['errors'])
    
    def test_invalid_rating_range(self):
        """Test validation with ratings outside normal range."""
        # Arrange: Create DataFrame with unusual rating values
        unusual_ratings_data = {
            'userId': [1, 2, 3],
            'movieId': [101, 102, 103],
            'rating': [0.0, 6.0, 10.0]  # Outside typical 0.5-5.0 range
        }
        ratings_dataframe = pd.DataFrame(unusual_ratings_data)
        
        # Act
        validation_result = validate_ratings_dataframe(ratings_dataframe)
        
        # Assert: Should have warnings about unusual range
        assert len(validation_result['warnings']) > 0
        assert any('Unusual rating range' in warning for warning in validation_result['warnings'])
    
    def test_duplicate_ratings_detection(self):
        """Test detection of duplicate user-movie rating pairs."""
        # Arrange: Create DataFrame with duplicate user-movie pairs
        duplicate_ratings_data = {
            'userId': [1, 1, 2, 2],
            'movieId': [101, 101, 102, 103],  # User 1 rated movie 101 twice
            'rating': [4.0, 3.5, 5.0, 2.5]
        }
        ratings_dataframe = pd.DataFrame(duplicate_ratings_data)
        
        # Act
        validation_result = validate_ratings_dataframe(ratings_dataframe)
        
        # Assert: Should detect duplicates
        assert len(validation_result['warnings']) > 0
        assert any('duplicate user-movie ratings' in warning for warning in validation_result['warnings'])


class TestMoviesValidation:
    """Test suite for movies DataFrame validation."""
    
    def test_valid_movies_dataframe(self):
        """Test validation of a properly formatted movies DataFrame."""
        # Arrange
        valid_movies_data = {
            'movieId': [101, 102, 103],
            'title': ['Movie A', 'Movie B', 'Movie C'],
            'genres': ['Action', 'Comedy', 'Drama']
        }
        movies_dataframe = pd.DataFrame(valid_movies_data)
        
        # Act
        validation_result = validate_movies_dataframe(movies_dataframe)
        
        # Assert
        assert validation_result['is_valid'] is True
        assert len(validation_result['errors']) == 0
        assert validation_result['statistics']['total_movies'] == 3
    
    def test_duplicate_movie_ids(self):
        """Test detection of duplicate movie IDs."""
        # Arrange
        duplicate_movies_data = {
            'movieId': [101, 102, 101],  # Duplicate movie ID
            'title': ['Movie A', 'Movie B', 'Movie A Duplicate']
        }
        movies_dataframe = pd.DataFrame(duplicate_movies_data)
        
        # Act
        validation_result = validate_movies_dataframe(movies_dataframe)
        
        # Assert
        assert validation_result['is_valid'] is False
        assert any('duplicate movie IDs' in error for error in validation_result['errors'])
    
    def test_empty_titles_detection(self):
        """Test detection of movies with empty titles."""
        # Arrange
        empty_titles_data = {
            'movieId': [101, 102, 103],
            'title': ['Movie A', '', None]  # Empty and null titles
        }
        movies_dataframe = pd.DataFrame(empty_titles_data)
        
        # Act
        validation_result = validate_movies_dataframe(movies_dataframe)
        
        # Assert
        assert len(validation_result['warnings']) > 0
        assert any('empty titles' in warning for warning in validation_result['warnings'])


class TestSparsityCalculation:
    """Test suite for sparsity ratio calculation."""
    
    def test_sparsity_calculation_basic(self):
        """Test basic sparsity calculation."""
        # Arrange: 2 users, 2 movies, 3 ratings out of 4 possible = 25% sparsity
        ratings_data = {
            'userId': [1, 1, 2],
            'movieId': [101, 102, 101],
            'rating': [4.0, 3.5, 5.0]
        }
        ratings_dataframe = pd.DataFrame(ratings_data)
        
        # Act
        sparsity_ratio = calculate_sparsity_ratio(ratings_dataframe)
        
        # Assert: (2*2 - 3) / (2*2) = 1/4 = 0.25
        expected_sparsity = 0.25
        assert abs(sparsity_ratio - expected_sparsity) < 0.001
    
    def test_sparsity_calculation_missing_columns(self):
        """Test sparsity calculation with missing required columns."""
        # Arrange
        invalid_data = {
            'user': [1, 2],  # Wrong column name
            'rating': [4.0, 3.5]
        }
        ratings_dataframe = pd.DataFrame(invalid_data)
        
        # Act & Assert
        with pytest.raises(ValueError):
            calculate_sparsity_ratio(ratings_dataframe)


class TestDataQualityReport:
    """Test suite for data quality report generation."""
    
    def test_quality_report_generation(self):
        """Test generation of comprehensive data quality report."""
        # Arrange
        ratings_data = {
            'userId': [1, 2, 3],
            'movieId': [101, 102, 103],
            'rating': [4.0, 3.5, 5.0]
        }
        movies_data = {
            'movieId': [101, 102, 103],
            'title': ['Movie A', 'Movie B', 'Movie C']
        }
        ratings_df = pd.DataFrame(ratings_data)
        movies_df = pd.DataFrame(movies_data)
        
        # Act
        quality_report = generate_data_quality_report(ratings_df, movies_df)
        
        # Assert
        assert isinstance(quality_report, str)
        assert 'LATENTLENS DATA QUALITY REPORT' in quality_report
        assert 'RATINGS DATASET VALIDATION' in quality_report
        assert 'MOVIES DATASET VALIDATION' in quality_report
        assert '✅ VALID' in quality_report  # Both datasets should be valid
