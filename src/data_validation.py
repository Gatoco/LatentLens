"""
Data Validation Utilities for LatentLens

This module provides functions to validate the integrity and quality of
MovieLens datasets. It includes checks for data completeness, value ranges,
and data type consistency.

Author: LatentLens Team
License: MIT
"""

from typing import Dict, List, Tuple, Any
import pandas as pd
import numpy as np


def validate_ratings_dataframe(ratings_dataframe: pd.DataFrame) -> Dict[str, Any]:
    """
    Validate the structure and content of a ratings DataFrame.
    
    This function performs comprehensive validation checks on a ratings
    dataset to ensure it meets the expected format and quality standards
    for the MovieLens recommendation system.
    
    Args:
        ratings_dataframe (pd.DataFrame): The ratings dataset to validate.
            Expected columns: [userId, movieId, rating, timestamp] (optional)
            
    Returns:
        Dict[str, Any]: A validation report containing:
            - is_valid (bool): Overall validation status
            - errors (List[str]): List of validation errors found
            - warnings (List[str]): List of potential issues
            - statistics (Dict): Basic dataset statistics
            
    Example:
        >>> validation_result = validate_ratings_dataframe(ratings_df)
        >>> if validation_result['is_valid']:
        ...     print("Dataset is valid!")
        >>> else:
        ...     print("Errors found:", validation_result['errors'])
    """
    validation_errors = []
    validation_warnings = []
    dataset_statistics = {}
    
    # Required columns for ratings data
    required_columns = ['userId', 'movieId', 'rating']
    optional_columns = ['timestamp']
    
    # Check for required columns
    missing_columns = [col for col in required_columns if col not in ratings_dataframe.columns]
    if missing_columns:
        validation_errors.append(f"Missing required columns: {missing_columns}")
    
    # Check data types
    if 'userId' in ratings_dataframe.columns:
        if not pd.api.types.is_integer_dtype(ratings_dataframe['userId']):
            validation_errors.append("userId column must be integer type")
    
    if 'movieId' in ratings_dataframe.columns:
        if not pd.api.types.is_integer_dtype(ratings_dataframe['movieId']):
            validation_errors.append("movieId column must be integer type")
    
    if 'rating' in ratings_dataframe.columns:
        if not pd.api.types.is_numeric_dtype(ratings_dataframe['rating']):
            validation_errors.append("rating column must be numeric type")
        else:
            # Check rating value range (typically 0.5 to 5.0 for MovieLens)
            min_rating = ratings_dataframe['rating'].min()
            max_rating = ratings_dataframe['rating'].max()
            
            if min_rating < 0.5 or max_rating > 5.0:
                validation_warnings.append(f"Unusual rating range: {min_rating} to {max_rating}")
            
            dataset_statistics['rating_range'] = (min_rating, max_rating)
            dataset_statistics['rating_distribution'] = ratings_dataframe['rating'].value_counts().to_dict()
    
    # Check for missing values
    missing_values_summary = ratings_dataframe.isnull().sum()
    if missing_values_summary.sum() > 0:
        validation_warnings.append(f"Missing values found: {missing_values_summary.to_dict()}")
    
    # Check for duplicate ratings (same user-movie pairs)
    if all(col in ratings_dataframe.columns for col in ['userId', 'movieId']):
        duplicate_ratings_count = ratings_dataframe.duplicated(subset=['userId', 'movieId']).sum()
        if duplicate_ratings_count > 0:
            validation_warnings.append(f"Found {duplicate_ratings_count} duplicate user-movie ratings")
    
    # Basic statistics
    dataset_statistics.update({
        'total_ratings': len(ratings_dataframe),
        'unique_users': ratings_dataframe['userId'].nunique() if 'userId' in ratings_dataframe.columns else 0,
        'unique_movies': ratings_dataframe['movieId'].nunique() if 'movieId' in ratings_dataframe.columns else 0,
        'data_sparsity': calculate_sparsity_ratio(ratings_dataframe) if all(col in ratings_dataframe.columns for col in ['userId', 'movieId']) else None
    })
    
    # Overall validation status
    is_dataset_valid = len(validation_errors) == 0
    
    return {
        'is_valid': is_dataset_valid,
        'errors': validation_errors,
        'warnings': validation_warnings,
        'statistics': dataset_statistics
    }


def calculate_sparsity_ratio(ratings_dataframe: pd.DataFrame) -> float:
    """
    Calculate the sparsity ratio of the user-item rating matrix.
    
    Sparsity indicates how sparse the ratings matrix is, which affects
    the performance of collaborative filtering algorithms.
    
    Args:
        ratings_dataframe (pd.DataFrame): DataFrame with userId and movieId columns
        
    Returns:
        float: Sparsity ratio between 0.0 (dense) and 1.0 (sparse)
    """
    if 'userId' not in ratings_dataframe.columns or 'movieId' not in ratings_dataframe.columns:
        raise ValueError("DataFrame must contain 'userId' and 'movieId' columns")
    
    unique_users_count = ratings_dataframe['userId'].nunique()
    unique_movies_count = ratings_dataframe['movieId'].nunique()
    total_possible_ratings = unique_users_count * unique_movies_count
    actual_ratings_count = len(ratings_dataframe)
    
    sparsity_ratio = 1.0 - (actual_ratings_count / total_possible_ratings)
    return sparsity_ratio


def validate_movies_dataframe(movies_dataframe: pd.DataFrame) -> Dict[str, Any]:
    """
    Validate the structure and content of a movies DataFrame.
    
    Args:
        movies_dataframe (pd.DataFrame): The movies dataset to validate.
            Expected columns: [movieId, title, genres] (optional)
            
    Returns:
        Dict[str, Any]: A validation report similar to validate_ratings_dataframe
    """
    validation_errors = []
    validation_warnings = []
    dataset_statistics = {}
    
    # Required columns for movies data
    required_columns = ['movieId', 'title']
    optional_columns = ['genres']
    
    # Check for required columns
    missing_columns = [col for col in required_columns if col not in movies_dataframe.columns]
    if missing_columns:
        validation_errors.append(f"Missing required columns: {missing_columns}")
    
    # Check for empty titles
    if 'title' in movies_dataframe.columns:
        empty_titles_count = movies_dataframe['title'].isnull().sum() + (movies_dataframe['title'] == '').sum()
        if empty_titles_count > 0:
            validation_warnings.append(f"Found {empty_titles_count} movies with empty titles")
    
    # Check for duplicate movie IDs
    if 'movieId' in movies_dataframe.columns:
        duplicate_movie_ids_count = movies_dataframe['movieId'].duplicated().sum()
        if duplicate_movie_ids_count > 0:
            validation_errors.append(f"Found {duplicate_movie_ids_count} duplicate movie IDs")
    
    # Basic statistics
    dataset_statistics.update({
        'total_movies': len(movies_dataframe),
        'unique_movie_ids': movies_dataframe['movieId'].nunique() if 'movieId' in movies_dataframe.columns else 0
    })
    
    # Overall validation status
    is_dataset_valid = len(validation_errors) == 0
    
    return {
        'is_valid': is_dataset_valid,
        'errors': validation_errors,
        'warnings': validation_warnings,
        'statistics': dataset_statistics
    }


def generate_data_quality_report(ratings_df: pd.DataFrame, movies_df: pd.DataFrame) -> str:
    """
    Generate a comprehensive data quality report for MovieLens datasets.
    
    Args:
        ratings_df (pd.DataFrame): The ratings dataset
        movies_df (pd.DataFrame): The movies dataset
        
    Returns:
        str: A formatted report string suitable for logging or display
    """
    ratings_validation = validate_ratings_dataframe(ratings_df)
    movies_validation = validate_movies_dataframe(movies_df)
    
    report_lines = [
        "=" * 60,
        "LATENTLENS DATA QUALITY REPORT",
        "=" * 60,
        "",
        "RATINGS DATASET VALIDATION:",
        f"Status: {'✅ VALID' if ratings_validation['is_valid'] else '❌ INVALID'}",
        f"Total Ratings: {ratings_validation['statistics'].get('total_ratings', 'N/A'):,}",
        f"Unique Users: {ratings_validation['statistics'].get('unique_users', 'N/A'):,}",
        f"Unique Movies: {ratings_validation['statistics'].get('unique_movies', 'N/A'):,}",
        f"Data Sparsity: {ratings_validation['statistics'].get('data_sparsity', 'N/A'):.4f}" if ratings_validation['statistics'].get('data_sparsity') else "Data Sparsity: N/A",
        "",
        "MOVIES DATASET VALIDATION:",
        f"Status: {'✅ VALID' if movies_validation['is_valid'] else '❌ INVALID'}",
        f"Total Movies: {movies_validation['statistics'].get('total_movies', 'N/A'):,}",
        "",
    ]
    
    # Add errors if any
    if ratings_validation['errors'] or movies_validation['errors']:
        report_lines.extend([
            "VALIDATION ERRORS:",
            *[f"- Ratings: {error}" for error in ratings_validation['errors']],
            *[f"- Movies: {error}" for error in movies_validation['errors']],
            ""
        ])
    
    # Add warnings if any
    if ratings_validation['warnings'] or movies_validation['warnings']:
        report_lines.extend([
            "WARNINGS:",
            *[f"- Ratings: {warning}" for warning in ratings_validation['warnings']],
            *[f"- Movies: {warning}" for warning in movies_validation['warnings']],
            ""
        ])
    
    report_lines.append("=" * 60)
    
    return "\n".join(report_lines)
