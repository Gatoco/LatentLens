"""
Recommendation Service Module for LatentLens

This module provides functions to load trained models and generate movie
recommendations using both popularity baseline and collaborative filtering
approaches.

Author: LatentLens Team
License: MIT
"""

import os
import pickle
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import joblib
from sklearn.neighbors import NearestNeighbors
from scipy.sparse import csr_matrix

try:
    from .data_loader import load_and_prepare_data
except ImportError:
    from data_loader import load_and_prepare_data


class RecommendationService:
    """
    Service class for generating movie recommendations.
    
    This class encapsulates the logic for loading models and generating
    recommendations using different approaches (popularity baseline,
    collaborative filtering).
    """
    
    def __init__(self):
        """Initialize the recommendation service."""
        self.data_df: Optional[pd.DataFrame] = None
        self.movie_stats: Optional[pd.DataFrame] = None
        self.knn_model: Optional[NearestNeighbors] = None
        self.movie_user_matrix: Optional[pd.DataFrame] = None
        self.movie_user_matrix_sparse: Optional[csr_matrix] = None
        self._is_initialized = False
    
    def initialize(self) -> None:
        """
        Initialize the recommendation service by loading data and preparing models.
        
        This method loads the MovieLens data, prepares the movie statistics for
        baseline recommendations, and sets up the collaborative filtering model.
        """
        if self._is_initialized:
            return
            
        print("Initializing recommendation service...")
        
        # Load and prepare data
        self.data_df = load_and_prepare_data()
        
        # Prepare movie statistics for baseline recommendations
        self.movie_stats = self.data_df.groupby('title').agg(
            num_ratings=('rating', 'count'),
            mean_rating=('rating', 'mean')
        ).reset_index()
        
        # Prepare collaborative filtering model
        self._prepare_collaborative_filtering()
        
        self._is_initialized = True
        print("Recommendation service initialized successfully.")
    
    def _prepare_collaborative_filtering(self) -> None:
        """
        Prepare the collaborative filtering model with filtered data.
        
        This method creates a subset of the data with popular movies and active
        users to make the recommendation model more efficient and relevant.
        """
        # Check if we have enough data to work with
        if len(self.data_df) == 0:
            print("Warning: No data available for collaborative filtering")
            self.movie_user_matrix = pd.DataFrame()
            self.movie_user_matrix_sparse = csr_matrix((0, 0))
            self.knn_model = None
            return
        
        # Filter for popular movies and active users to improve performance
        movie_counts = self.data_df['title'].value_counts()
        popular_movies = movie_counts.head(15000).index
        
        user_counts = self.data_df['userId'].value_counts()
        active_users = user_counts.head(40000).index
        
        # Create filtered dataset
        filtered_df = self.data_df[
            self.data_df['title'].isin(popular_movies) & 
            self.data_df['userId'].isin(active_users)
        ]
        
        # Check if filtered data is sufficient
        if len(filtered_df) == 0:
            print("Warning: Filtered dataset is empty for collaborative filtering")
            self.movie_user_matrix = pd.DataFrame()
            self.movie_user_matrix_sparse = csr_matrix((0, 0))
            self.knn_model = None
            return
        
        # Create user-movie matrix
        self.movie_user_matrix = filtered_df.pivot_table(
            index='title', 
            columns='userId', 
            values='rating'
        ).fillna(0)
        
        # Check if matrix has sufficient size
        if self.movie_user_matrix.shape[0] == 0 or self.movie_user_matrix.shape[1] == 0:
            print("Warning: User-movie matrix is empty for collaborative filtering")
            self.movie_user_matrix_sparse = csr_matrix((0, 0))
            self.knn_model = None
            return
        
        # Convert to sparse matrix for efficiency
        self.movie_user_matrix_sparse = csr_matrix(self.movie_user_matrix.values)
        
        # Train KNN model only if we have sufficient data
        self.knn_model = NearestNeighbors(metric='cosine', algorithm='brute')
        self.knn_model.fit(self.movie_user_matrix_sparse)
        
        print(f"Collaborative filtering prepared with {len(filtered_df)} interactions")
    
    def get_popular_recommendations(
        self, 
        num_recommendations: int = 10,
        min_ratings_threshold: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        Get movie recommendations based on popularity and rating.
        
        This method returns the most highly-rated movies that have received
        a minimum number of ratings to ensure statistical significance.
        
        Args:
            num_recommendations (int): Number of recommendations to return.
            min_ratings_threshold (int): Minimum number of ratings required.
            
        Returns:
            List[Dict[str, Any]]: List of movie recommendations with metadata.
        """
        if not self._is_initialized:
            self.initialize()
        
        # Filter movies with sufficient ratings
        qualified_movies = self.movie_stats[
            self.movie_stats['num_ratings'] >= min_ratings_threshold
        ]
        
        # Sort by rating and get top recommendations
        top_movies = qualified_movies.sort_values(
            by='mean_rating', 
            ascending=False
        ).head(num_recommendations)
        
        # Format response
        recommendations = []
        for _, movie in top_movies.iterrows():
            recommendations.append({
                "title": movie['title'],
                "average_rating": round(movie['mean_rating'], 2),
                "num_ratings": int(movie['num_ratings']),
                "recommendation_type": "popularity_baseline"
            })
        
        return recommendations
    
    def get_collaborative_recommendations(
        self, 
        movie_title: str,
        num_recommendations: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get movie recommendations based on collaborative filtering.
        
        This method finds movies similar to the given movie title using
        K-Nearest Neighbors with cosine similarity.
        
        Args:
            movie_title (str): Title of the movie to base recommendations on.
            num_recommendations (int): Number of recommendations to return.
            
        Returns:
            List[Dict[str, Any]]: List of similar movie recommendations.
            
        Raises:
            ValueError: If the movie title is not found in the dataset or
                       if collaborative filtering is not available.
        """
        if not self._is_initialized:
            self.initialize()
        
        # Check if collaborative filtering is available
        if self.knn_model is None or self.movie_user_matrix is None:
            raise ValueError("Collaborative filtering is not available due to insufficient data")
        
        try:
            # Find movie index
            movie_index = list(self.movie_user_matrix.index).index(movie_title)
            
            # Get similar movies
            distances, indices = self.knn_model.kneighbors(
                self.movie_user_matrix_sparse[movie_index], 
                n_neighbors=min(num_recommendations + 1, self.movie_user_matrix.shape[0])  # +1 because it includes the input movie
            )
            
            # Format recommendations (skip the first one as it's the input movie)
            recommendations = []
            for i in range(1, len(indices.flatten())):
                similar_movie = self.movie_user_matrix.index[indices.flatten()[i]]
                similarity_score = 1 - distances.flatten()[i]  # Convert distance to similarity
                
                recommendations.append({
                    "title": similar_movie,
                    "similarity_score": round(similarity_score, 3),
                    "recommendation_type": "collaborative_filtering"
                })
            
            return recommendations
            
        except ValueError:
            raise ValueError(f"Movie '{movie_title}' not found in the recommendation dataset")
    
    def get_user_recommendations(
        self, 
        user_id: int,
        num_recommendations: int = 10,
        recommendation_type: str = "hybrid"
    ) -> List[Dict[str, Any]]:
        """
        Get personalized movie recommendations for a user.
        
        Note: This is a simplified implementation. In practice, you would
        need the user's rating history to provide truly personalized recommendations.
        For now, it returns popular recommendations as a fallback.
        
        Args:
            user_id (int): The user ID to generate recommendations for.
            num_recommendations (int): Number of recommendations to return.
            recommendation_type (str): Type of recommendation ("popular", "collaborative", "hybrid").
            
        Returns:
            List[Dict[str, Any]]: List of personalized movie recommendations.
        """
        if not self._is_initialized:
            self.initialize()
        
        # For this MVP, we'll return popular recommendations
        # In a production system, you would:
        # 1. Get the user's rating history
        # 2. Find similar users or movies
        # 3. Generate personalized recommendations
        
        if recommendation_type in ["popular", "hybrid"]:
            recommendations = self.get_popular_recommendations(num_recommendations)
            
            # Add user_id to each recommendation for tracking
            for rec in recommendations:
                rec["user_id"] = user_id
                rec["recommendation_type"] = f"user_{recommendation_type}"
            
            return recommendations
        
        else:
            raise ValueError(f"Unsupported recommendation type: {recommendation_type}")


# Global service instance
recommendation_service = RecommendationService()


def get_recommendations_for_user(
    user_id: int, 
    num_recommendations: int = 10
) -> List[Dict[str, Any]]:
    """
    Convenience function to get recommendations for a user.
    
    Args:
        user_id (int): The user ID to generate recommendations for.
        num_recommendations (int): Number of recommendations to return.
        
    Returns:
        List[Dict[str, Any]]: List of movie recommendations.
    """
    return recommendation_service.get_user_recommendations(user_id, num_recommendations)


def get_popular_movies(num_movies: int = 10) -> List[Dict[str, Any]]:
    """
    Convenience function to get popular movie recommendations.
    
    Args:
        num_movies (int): Number of popular movies to return.
        
    Returns:
        List[Dict[str, Any]]: List of popular movies.
    """
    return recommendation_service.get_popular_recommendations(num_movies)


def get_similar_movies(movie_title: str, num_movies: int = 10) -> List[Dict[str, Any]]:
    """
    Convenience function to get movies similar to a given movie.
    
    Args:
        movie_title (str): Title of the movie to find similar movies for.
        num_movies (int): Number of similar movies to return.
        
    Returns:
        List[Dict[str, Any]]: List of similar movies.
    """
    return recommendation_service.get_collaborative_recommendations(movie_title, num_movies)
