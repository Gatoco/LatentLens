"""
Item-to-Item Similarity Service Module for LatentLens

This module implements item-to-item similarity using K-Nearest Neighbors (KNN)
for efficient movie recommendation based on user rating patterns. It provides
ultra-fast similarity lookup for cold-start scenarios and related products.

Key Features:
- Pre-computed similarity matrix using sparse user-item ratings
- KNN-based nearest neighbors for scalable similarity search
- Movie ID-based API for integration with existing systems
- Cold-start support for new users through item similarities

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
import logging
from sklearn.neighbors import NearestNeighbors
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer

try:
    from .data_loader import DataLoader
except ImportError:
    from data_loader import DataLoader

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ItemSimilarityService:
    """
    Service class for item-to-item similarity using K-Nearest Neighbors.
    
    This service pre-computes a similarity matrix using user rating patterns
    and provides fast lookup for finding the most similar movies to any given
    movie ID. Uses sparse matrices for memory efficiency.
    """
    
    def __init__(self, data_path: str = "../data/ml-25m"):
        """
        Initialize the Item Similarity Service.
        
        Args:
            data_path (str): Path to the MovieLens dataset directory.
        """
        self.data_path = data_path
        self.data_loader = DataLoader(data_path)
        
        # Core data structures
        self.ratings_df: Optional[pd.DataFrame] = None
        self.movies_df: Optional[pd.DataFrame] = None
        self.movie_user_matrix: Optional[pd.DataFrame] = None
        self.movie_user_matrix_sparse: Optional[csr_matrix] = None
        
        # KNN model and mappings
        self.knn_model: Optional[NearestNeighbors] = None
        self.movie_id_to_index: Optional[Dict[int, int]] = None
        self.index_to_movie_id: Optional[Dict[int, int]] = None
        self.movie_features: Optional[pd.DataFrame] = None
        
        # Model state
        self._is_initialized = False
        self._model_path = os.path.join(data_path, "models", "item_similarity_knn.pkl")
        
        logger.info(f"ItemSimilarityService initialized with data path: {data_path}")
    
    def initialize(self, min_ratings_per_movie: int = 50, min_ratings_per_user: int = 20) -> None:
        """
        Initialize the service by loading data and training the KNN model.
        
        Args:
            min_ratings_per_movie (int): Minimum ratings required per movie for inclusion.
            min_ratings_per_user (int): Minimum ratings required per user for inclusion.
        """
        if self._is_initialized:
            logger.info("ItemSimilarityService already initialized")
            return
        
        logger.info("Initializing ItemSimilarityService...")
        
        # Try to load pre-trained model first
        if self._load_pretrained_model():
            self._is_initialized = True
            logger.info("Successfully loaded pre-trained KNN model")
            return
        
        # Load and prepare data
        logger.info("Loading MovieLens data...")
        self._load_data()
        
        # Filter data for quality
        logger.info(f"Filtering data (min_ratings_per_movie={min_ratings_per_movie}, min_ratings_per_user={min_ratings_per_user})...")
        self._filter_data(min_ratings_per_movie, min_ratings_per_user)
        
        # Create user-item matrix
        logger.info("Creating movie-user matrix...")
        self._create_movie_user_matrix()
        
        # Train KNN model
        logger.info("Training K-Nearest Neighbors model...")
        self._train_knn_model()
        
        # Create movie features for metadata
        logger.info("Preparing movie features...")
        self._prepare_movie_features()
        
        # Save the trained model
        self._save_model()
        
        self._is_initialized = True
        logger.info("ItemSimilarityService initialization completed")
    
    def _load_data(self) -> None:
        """Load ratings and movies data from the dataset."""
        self.ratings_df = self.data_loader.load_ratings()
        self.movies_df = self.data_loader.load_movies()
        
        logger.info(f"Loaded {len(self.ratings_df):,} ratings for {self.ratings_df['movieId'].nunique():,} movies")
        logger.info(f"Loaded {len(self.movies_df):,} movie records")
    
    def _filter_data(self, min_ratings_per_movie: int, min_ratings_per_user: int) -> None:
        """
        Filter data to remove movies and users with insufficient ratings.
        
        Args:
            min_ratings_per_movie (int): Minimum ratings per movie.
            min_ratings_per_user (int): Minimum ratings per user.
        """
        original_ratings = len(self.ratings_df)
        original_movies = self.ratings_df['movieId'].nunique()
        original_users = self.ratings_df['userId'].nunique()
        
        # Filter movies with sufficient ratings
        movie_counts = self.ratings_df['movieId'].value_counts()
        valid_movies = movie_counts[movie_counts >= min_ratings_per_movie].index
        self.ratings_df = self.ratings_df[self.ratings_df['movieId'].isin(valid_movies)]
        
        # Filter users with sufficient ratings
        user_counts = self.ratings_df['userId'].value_counts()
        valid_users = user_counts[user_counts >= min_ratings_per_user].index
        self.ratings_df = self.ratings_df[self.ratings_df['userId'].isin(valid_users)]
        
        # Filter movies again after user filtering
        movie_counts = self.ratings_df['movieId'].value_counts()
        valid_movies = movie_counts[movie_counts >= min_ratings_per_movie].index
        self.ratings_df = self.ratings_df[self.ratings_df['movieId'].isin(valid_movies)]
        
        # Filter movies dataframe to match filtered ratings
        self.movies_df = self.movies_df[self.movies_df['movieId'].isin(self.ratings_df['movieId'].unique())]
        
        filtered_ratings = len(self.ratings_df)
        filtered_movies = self.ratings_df['movieId'].nunique()
        filtered_users = self.ratings_df['userId'].nunique()
        
        logger.info(f"Data filtering results:")
        logger.info(f"  Ratings: {original_ratings:,} → {filtered_ratings:,} ({(filtered_ratings/original_ratings)*100:.1f}%)")
        logger.info(f"  Movies: {original_movies:,} → {filtered_movies:,} ({(filtered_movies/original_movies)*100:.1f}%)")
        logger.info(f"  Users: {original_users:,} → {filtered_users:,} ({(filtered_users/original_users)*100:.1f}%)")
    
    def _create_movie_user_matrix(self) -> None:
        """Create the movie-user matrix and convert to sparse format."""
        # Create pivot table with movies as rows and users as columns
        logger.info("Creating pivot table...")
        self.movie_user_matrix = self.ratings_df.pivot_table(
            index='movieId', 
            columns='userId', 
            values='rating', 
            fill_value=0
        )
        
        logger.info(f"Movie-User matrix shape: {self.movie_user_matrix.shape}")
        
        # Convert to sparse matrix for memory efficiency
        logger.info("Converting to sparse matrix...")
        self.movie_user_matrix_sparse = csr_matrix(self.movie_user_matrix.values)
        
        # Create mappings between movie IDs and matrix indices
        self.movie_id_to_index = {movie_id: idx for idx, movie_id in enumerate(self.movie_user_matrix.index)}
        self.index_to_movie_id = {idx: movie_id for movie_id, idx in self.movie_id_to_index.items()}
        
        logger.info(f"Sparse matrix density: {(self.movie_user_matrix_sparse.nnz / (self.movie_user_matrix_sparse.shape[0] * self.movie_user_matrix_sparse.shape[1]))*100:.4f}%")
    
    def _train_knn_model(self, n_neighbors: int = 21, metric: str = 'cosine') -> None:
        """
        Train the K-Nearest Neighbors model on the movie-user matrix.
        
        Args:
            n_neighbors (int): Number of neighbors to find (includes the item itself).
            metric (str): Distance metric to use ('cosine', 'euclidean', etc.).
        """
        self.knn_model = NearestNeighbors(
            n_neighbors=n_neighbors,
            metric=metric,
            algorithm='brute',  # Better for sparse, high-dimensional data
            n_jobs=-1  # Use all available cores
        )
        
        logger.info(f"Training KNN with {n_neighbors} neighbors using {metric} metric...")
        self.knn_model.fit(self.movie_user_matrix_sparse)
        
        logger.info("KNN model training completed")
    
    def _prepare_movie_features(self) -> None:
        """Prepare movie features for enhanced similarity results."""
        # Calculate movie statistics
        movie_stats = self.ratings_df.groupby('movieId').agg({
            'rating': ['mean', 'count', 'std'],
            'userId': 'nunique'
        }).round(4)
        
        # Flatten column names
        movie_stats.columns = ['avg_rating', 'num_ratings', 'rating_std', 'num_users']
        movie_stats = movie_stats.reset_index()
        
        # Merge with movie metadata
        self.movie_features = self.movies_df.merge(movie_stats, on='movieId', how='left')
        self.movie_features = self.movie_features.fillna(0)
        
        logger.info(f"Prepared features for {len(self.movie_features)} movies")
    
    def _save_model(self) -> None:
        """Save the trained model and mappings to disk."""
        os.makedirs(os.path.dirname(self._model_path), exist_ok=True)
        
        model_data = {
            'knn_model': self.knn_model,
            'movie_user_matrix_sparse': self.movie_user_matrix_sparse,
            'movie_id_to_index': self.movie_id_to_index,
            'index_to_movie_id': self.index_to_movie_id,
            'movie_features': self.movie_features,
            'movies_df': self.movies_df
        }
        
        with open(self._model_path, 'wb') as f:
            pickle.dump(model_data, f)
        
        logger.info(f"Model saved to {self._model_path}")
    
    def _load_pretrained_model(self) -> bool:
        """
        Load a pre-trained model from disk.
        
        Returns:
            bool: True if model was loaded successfully, False otherwise.
        """
        if not os.path.exists(self._model_path):
            logger.info("No pre-trained model found")
            return False
        
        try:
            with open(self._model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            self.knn_model = model_data['knn_model']
            self.movie_user_matrix_sparse = model_data['movie_user_matrix_sparse']
            self.movie_id_to_index = model_data['movie_id_to_index']
            self.index_to_movie_id = model_data['index_to_movie_id']
            self.movie_features = model_data['movie_features']
            self.movies_df = model_data['movies_df']
            
            return True
            
        except Exception as e:
            logger.error(f"Error loading pre-trained model: {str(e)}")
            return False
    
    def get_similar_items(self, movie_id: int, n_similar: int = 10) -> List[Dict[str, Any]]:
        """
        Get the most similar movies to a given movie ID.
        
        Args:
            movie_id (int): The movie ID to find similar movies for.
            n_similar (int): Number of similar movies to return.
        
        Returns:
            List[Dict[str, Any]]: List of similar movies with metadata.
        
        Raises:
            ValueError: If movie_id is not found in the dataset.
            RuntimeError: If the service is not initialized.
        """
        if not self._is_initialized:
            raise RuntimeError("ItemSimilarityService not initialized. Call initialize() first.")
        
        if movie_id not in self.movie_id_to_index:
            raise ValueError(f"Movie ID {movie_id} not found in the similarity index")
        
        # Get the movie index
        movie_index = self.movie_id_to_index[movie_id]
        
        # Find similar movies using KNN
        # Request n_similar + 1 because the first result is the movie itself
        distances, indices = self.knn_model.kneighbors(
            self.movie_user_matrix_sparse[movie_index],
            n_neighbors=n_similar + 1
        )
        
        # Prepare results (skip the first item which is the movie itself)
        similar_movies = []
        for i in range(1, len(indices[0])):  # Skip index 0 (the movie itself)
            similar_movie_index = indices[0][i]
            similar_movie_id = self.index_to_movie_id[similar_movie_index]
            similarity_score = 1 - distances[0][i]  # Convert distance to similarity
            
            # Get movie metadata
            movie_info = self.movie_features[self.movie_features['movieId'] == similar_movie_id].iloc[0]
            
            similar_movies.append({
                'movieId': int(similar_movie_id),
                'title': movie_info['title'],
                'genres': movie_info['genres'],
                'similarity_score': float(similarity_score),
                'avg_rating': float(movie_info['avg_rating']),
                'num_ratings': int(movie_info['num_ratings']),
                'num_users': int(movie_info['num_users'])
            })
        
        return similar_movies
    
    def get_movie_info(self, movie_id: int) -> Dict[str, Any]:
        """
        Get information about a specific movie.
        
        Args:
            movie_id (int): The movie ID to get information for.
        
        Returns:
            Dict[str, Any]: Movie information and statistics.
        
        Raises:
            ValueError: If movie_id is not found.
        """
        if not self._is_initialized:
            raise RuntimeError("ItemSimilarityService not initialized. Call initialize() first.")
        
        if movie_id not in self.movie_id_to_index:
            raise ValueError(f"Movie ID {movie_id} not found in the dataset")
        
        movie_info = self.movie_features[self.movie_features['movieId'] == movie_id].iloc[0]
        
        return {
            'movieId': int(movie_info['movieId']),
            'title': movie_info['title'],
            'genres': movie_info['genres'],
            'avg_rating': float(movie_info['avg_rating']),
            'num_ratings': int(movie_info['num_ratings']),
            'num_users': int(movie_info['num_users']),
            'rating_std': float(movie_info.get('rating_std', 0))
        }
    
    def get_similarity_matrix_info(self) -> Dict[str, Any]:
        """
        Get information about the similarity matrix and model.
        
        Returns:
            Dict[str, Any]: Information about the model state.
        """
        if not self._is_initialized:
            return {"initialized": False}
        
        return {
            "initialized": True,
            "total_movies": len(self.movie_id_to_index),
            "matrix_shape": self.movie_user_matrix_sparse.shape,
            "matrix_density": float((self.movie_user_matrix_sparse.nnz / (self.movie_user_matrix_sparse.shape[0] * self.movie_user_matrix_sparse.shape[1]))),
            "knn_neighbors": self.knn_model.n_neighbors,
            "knn_metric": self.knn_model.metric
        }


# Global service instance
item_similarity_service = ItemSimilarityService("data/ml-25m")


def get_similar_items_by_id(movie_id: int, n_similar: int = 10) -> List[Dict[str, Any]]:
    """
    Convenience function to get similar movies by movie ID.
    
    Args:
        movie_id (int): The movie ID to find similar movies for.
        n_similar (int): Number of similar movies to return.
    
    Returns:
        List[Dict[str, Any]]: List of similar movies.
    """
    if not item_similarity_service._is_initialized:
        item_similarity_service.initialize()
    
    return item_similarity_service.get_similar_items(movie_id, n_similar)


def get_movie_information(movie_id: int) -> Dict[str, Any]:
    """
    Convenience function to get movie information by ID.
    
    Args:
        movie_id (int): The movie ID to get information for.
    
    Returns:
        Dict[str, Any]: Movie information and statistics.
    """
    if not item_similarity_service._is_initialized:
        item_similarity_service.initialize()
    
    return item_similarity_service.get_movie_info(movie_id)


def get_model_status() -> Dict[str, Any]:
    """
    Get the current status of the item similarity model.
    
    Returns:
        Dict[str, Any]: Model status information.
    """
    return item_similarity_service.get_similarity_matrix_info()
