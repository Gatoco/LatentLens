"""
Recommendation Service Module for LatentLens

This module provides functions to load trained models and generate movie
recommendations using both popularity baseline and collaborative filtering
approaches with MLflow integration.

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
import logging

try:
    from .data_loader import load_and_prepare_data
    from .mlflow_svd_service import MLflowSVDService
except ImportError:
    from data_loader import load_and_prepare_data
    from mlflow_svd_service import MLflowSVDService

logger = logging.getLogger(__name__)


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
        self.mlflow_svd_service: Optional[MLflowSVDService] = None
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
        
        # Initialize MLflow SVD service
        self._initialize_mlflow_svd()
        
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
        
        interactions = len(filtered_df)
        print(f"Collaborative filtering prepared with {interactions:,} interactions")
    
    def _initialize_mlflow_svd(self) -> None:
        """
        Initialize MLflow SVD service and try to load existing model.
        If no model exists, train a new one.
        """
        logger.info("Initializing MLflow SVD service...")
        
        try:
            # Initialize MLflow SVD service
            self.mlflow_svd_service = MLflowSVDService()
            
            # Try to load existing model
            model_loaded = self.mlflow_svd_service.load_latest_model()
            
            if model_loaded:
                logger.info("✅ Successfully loaded SVD model from MLflow")
            else:
                logger.info("No existing SVD model found. Training new model...")
                self._train_and_save_svd_model()
                
        except Exception as e:
            logger.error(f"Failed to initialize MLflow SVD service: {e}")
            self.mlflow_svd_service = None
    
    def _train_and_save_svd_model(self) -> None:
        """Train and save a new SVD model to MLflow"""
        if not hasattr(self, 'data_df') or self.data_df is None:
            logger.error("No data available for SVD training")
            return
        
        try:
            # Prepare ratings DataFrame for Surprise
            ratings_df = self.data_df[['userId', 'movieId', 'rating']].copy()
            
            # Sample data if too large (for faster training)
            if len(ratings_df) > 1000000:  # 1M ratings
                logger.info("Sampling data for SVD training...")
                ratings_df = ratings_df.sample(n=1000000, random_state=42)
            
            # Train and save model
            model_uri = self.mlflow_svd_service.train_and_save_model(
                ratings_df=ratings_df,
                n_factors=100,
                n_epochs=20,
                lr_all=0.005,
                reg_all=0.02
            )
            
            logger.info(f"✅ SVD model trained and saved to MLflow: {model_uri}")
            
        except Exception as e:
            logger.error(f"Failed to train SVD model: {e}")
            self.mlflow_svd_service = None
    
    def get_svd_recommendations(
        self, 
        user_id: int, 
        n_recommendations: int = 10,
        exclude_seen: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get recommendations using MLflow-loaded SVD model
        
        Args:
            user_id: User ID to get recommendations for
            n_recommendations: Number of recommendations to return
            exclude_seen: Whether to exclude movies user has already rated
            
        Returns:
            List of movie recommendations with predicted ratings
        """
        if not self.mlflow_svd_service or not self.mlflow_svd_service.is_model_loaded():
            logger.warning("SVD model not available, falling back to popular recommendations")
            return self.get_popular_recommendations(n_recommendations)
        
        try:
            # Get all movie IDs as candidates
            all_movies = self.data_df['movieId'].unique()
            
            # Exclude movies user has already rated if requested
            if exclude_seen:
                user_movies = set(self.data_df[self.data_df['userId'] == user_id]['movieId'])
                candidate_movies = [m for m in all_movies if m not in user_movies]
            else:
                candidate_movies = all_movies
            
            # Limit candidates for performance
            if len(candidate_movies) > 5000:
                candidate_movies = np.random.choice(candidate_movies, 5000, replace=False)
            
            # Get predictions from SVD model
            recommendations = self.mlflow_svd_service.get_user_recommendations(
                user_id=user_id,
                movie_ids=candidate_movies,
                n_recommendations=n_recommendations
            )
            
            # Convert to our format with movie metadata
            result = []
            for movie_id, predicted_rating in recommendations:
                movie_info = self.data_df[self.data_df['movieId'] == movie_id].iloc[0]
                
                result.append({
                    'movieId': int(movie_id),
                    'title': movie_info['title'],
                    'genres': movie_info.get('genres', 'Unknown'),
                    'predicted_rating': float(predicted_rating),
                    'recommendation_type': 'svd_collaborative'
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating SVD recommendations for user {user_id}: {e}")
            return self.get_popular_recommendations(n_recommendations)
    
    def get_collaborative_recommendations(
        self, 
        movie_title: str, 
        num_recommendations: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get recommendations using KNN collaborative filtering (item-to-item similarity).
        This method has been updated to work with the new SVD implementation.
        """
        logger.info(f"Getting collaborative recommendations for: {movie_title}")
        
        # For user-based recommendations, redirect to SVD
        if isinstance(movie_title, (int, float)):
            logger.info("Redirecting to SVD recommendations for user-based query")
            return self.get_svd_recommendations(int(movie_title), num_recommendations)
        
        # Continue with original KNN implementation for item-to-item similarity
        if not self._is_initialized:
            raise ValueError("Service not initialized. Call initialize() first.")
        
        if self.knn_model is None:
            raise ValueError("KNN model not available")
        
        try:
            # Find movie index
            movie_index = list(self.movie_user_matrix.index).index(movie_title)
            
        except ValueError:
            raise ValueError(f"Movie '{movie_title}' not found in the recommendation dataset")
        
        # Get movie vector and find similar movies
        movie_vector = self.movie_user_matrix_sparse[movie_index].reshape(1, -1)
        distances, indices = self.knn_model.kneighbors(
            movie_vector, 
            n_neighbors=num_recommendations + 1
        )
        
        # Prepare recommendations (exclude the input movie itself)
        recommendations = []
        similar_movies = list(zip(indices.flatten()[1:], distances.flatten()[1:]))
        
        for idx, distance in similar_movies:
            similar_movie_title = self.movie_user_matrix.index[idx]
            similarity_score = 1 - distance  # Convert distance to similarity
            
            recommendations.append({
                'title': similar_movie_title,
                'similarity_score': similarity_score,
                'recommendation_type': 'collaborative_knn'
            })
        
        return recommendations
    
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
