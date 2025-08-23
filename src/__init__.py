"""
LatentLens: Hybrid Movie Recommendation System

This package provides a complete movie recommendation system built with
FastAPI, MLflow, and collaborative filtering algorithms. It includes
data loading utilities, text preprocessing, and a REST API for serving
movie recommendations.

Main Components:
    - data_loader: Functions for loading and preparing MovieLens datasets
    - preprocessing: Text processing utilities for movie titles and metadata
    - main: FastAPI application with REST endpoints

Usage:
    # For API development
    from main import app
    
    # For data processing
    from data_loader import load_and_prepare_data
    from preprocessing import extract_movie_title_without_year

Author: LatentLens Team
License: MIT
Version: 0.1.0
"""

# Package metadata
__version__ = "0.1.0"
__author__ = "LatentLens Team"
__license__ = "MIT"

# Public API exports
__all__ = [
    "load_and_prepare_data",
    "extract_movie_title_without_year",
    "normalize_movie_title",
    "app",
    "get_recommendations_for_user",
    "get_popular_movies",
    "get_similar_movies",
]

# Import main components for easier access
try:
    from .data_loader import load_and_prepare_data
    from .preprocessing import extract_movie_title_without_year, normalize_movie_title
    from .main import app
    from .recommendation_service import (
        get_recommendations_for_user, 
        get_popular_movies, 
        get_similar_movies
    )
except ImportError:
    # Handle cases where dependencies might not be available
    # This allows the package to be imported even if some modules fail
    pass
