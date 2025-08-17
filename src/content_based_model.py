"""
Content-Based Recommendation Model for LatentLens

This module implements content-based filtering using movie metadata such as
genres and titles. It uses TF-IDF vectorization and cosine similarity to
find similar movies based on content features.

Author: LatentLens Team
License: MIT
"""

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Tuple, Optional
import logging
import pickle
import os
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContentBasedModel:
    """
    Content-based recommendation model using TF-IDF and cosine similarity.
    
    This model analyzes movie features (titles, genres) to compute similarity
    between movies and provide recommendations based on content similarity.
    """
    
    def __init__(
        self,
        max_features: int = 5000,
        min_df: int = 1,
        max_df: float = 0.95,
        ngram_range: Tuple[int, int] = (1, 2),
        stop_words: str = 'english'
    ):
        """
        Initialize the content-based model.
        
        Args:
            max_features: Maximum number of features for TF-IDF
            min_df: Minimum document frequency for TF-IDF
            max_df: Maximum document frequency for TF-IDF
            ngram_range: N-gram range for TF-IDF
            stop_words: Stop words for TF-IDF
        """
        self.max_features = max_features
        self.min_df = min_df
        self.max_df = max_df
        self.ngram_range = ngram_range
        self.stop_words = stop_words
        
        # Initialize components
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=max_features,
            min_df=min_df,
            max_df=max_df,
            ngram_range=ngram_range,
            stop_words=stop_words
        )
        
        # Model state
        self.movies_df = None
        self.content_features = None
        self.tfidf_matrix = None
        self.cosine_sim_matrix = None
        self.movie_indices = None
        self.is_fitted = False
        
    def _prepare_content_features(self, movies_df: pd.DataFrame) -> pd.Series:
        """
        Prepare content features by combining title and genres.
        
        Args:
            movies_df: DataFrame with movie data
            
        Returns:
            Series with combined content features
        """
        logger.info("Preparing content features from title and genres...")
        
        # Clean and prepare data
        movies_clean = movies_df.copy()
        
        # Handle missing values
        movies_clean['title'] = movies_clean['title'].fillna('')
        movies_clean['genres'] = movies_clean['genres'].fillna('')
        
        # Extract year from title if present
        movies_clean['year'] = movies_clean['title'].str.extract(r'\((\d{4})\)')
        movies_clean['clean_title'] = movies_clean['title'].str.replace(r'\(\d{4}\)', '', regex=True).str.strip()
        
        # Process genres - replace pipes with spaces
        movies_clean['processed_genres'] = movies_clean['genres'].str.replace('|', ' ', regex=False)
        
        # Combine features: clean title + genres
        # Weight genres more heavily by repeating them
        content_features = (
            movies_clean['clean_title'] + ' ' + 
            movies_clean['processed_genres'] + ' ' + 
            movies_clean['processed_genres']  # Repeat genres for higher weight
        )
        
        # Clean the combined features
        content_features = content_features.str.lower()
        content_features = content_features.str.replace(r'[^\w\s]', ' ', regex=True)
        content_features = content_features.str.replace(r'\s+', ' ', regex=True)
        content_features = content_features.str.strip()
        
        logger.info(f"Content features prepared for {len(content_features)} movies")
        return content_features
    
    def fit(self, movies_df: pd.DataFrame) -> 'ContentBasedModel':
        """
        Fit the content-based model on movie data.
        
        Args:
            movies_df: DataFrame with movie data (must have 'title' and 'genres' columns)
            
        Returns:
            Self for method chaining
        """
        logger.info("Fitting content-based model...")
        
        # Validate input
        required_columns = ['movieId', 'title', 'genres']
        if not all(col in movies_df.columns for col in required_columns):
            raise ValueError(f"Movies DataFrame must contain columns: {required_columns}")
        
        # Store the movies dataframe
        self.movies_df = movies_df.copy()
        
        # Create movie index mapping
        self.movie_indices = pd.Series(
            self.movies_df.index, 
            index=self.movies_df['movieId']
        ).to_dict()
        
        # Prepare content features
        self.content_features = self._prepare_content_features(self.movies_df)
        
        # Fit TF-IDF vectorizer
        logger.info("Fitting TF-IDF vectorizer...")
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(self.content_features)
        
        logger.info(f"TF-IDF matrix shape: {self.tfidf_matrix.shape}")
        logger.info(f"Vocabulary size: {len(self.tfidf_vectorizer.vocabulary_)}")
        
        # Compute cosine similarity matrix
        logger.info("Computing cosine similarity matrix...")
        self.cosine_sim_matrix = cosine_similarity(self.tfidf_matrix)
        
        logger.info(f"Cosine similarity matrix shape: {self.cosine_sim_matrix.shape}")
        
        self.is_fitted = True
        logger.info("Content-based model fitted successfully")
        
        return self
    
    def get_similar_movies(
        self, 
        movie_id: int, 
        n_recommendations: int = 10,
        include_scores: bool = False
    ) -> List[Dict]:
        """
        Get similar movies based on content similarity.
        
        Args:
            movie_id: ID of the movie to find similarities for
            n_recommendations: Number of recommendations to return
            include_scores: Whether to include similarity scores
            
        Returns:
            List of similar movies with metadata
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before making recommendations")
        
        if movie_id not in self.movie_indices:
            raise ValueError(f"Movie ID {movie_id} not found in the dataset")
        
        # Get movie index
        movie_idx = self.movie_indices[movie_id]
        
        # Get similarity scores for this movie
        sim_scores = list(enumerate(self.cosine_sim_matrix[movie_idx]))
        
        # Sort by similarity score (descending)
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        
        # Get top N similar movies (excluding the movie itself)
        similar_movies = sim_scores[1:n_recommendations + 1]
        
        # Prepare recommendations
        recommendations = []
        for idx, score in similar_movies:
            movie_data = {
                'movieId': self.movies_df.iloc[idx]['movieId'],
                'title': self.movies_df.iloc[idx]['title'],
                'genres': self.movies_df.iloc[idx]['genres']
            }
            
            if include_scores:
                movie_data['similarity_score'] = score
                
            recommendations.append(movie_data)
        
        return recommendations
    
    def get_recommendations_by_title(
        self, 
        title: str, 
        n_recommendations: int = 10,
        include_scores: bool = False
    ) -> List[Dict]:
        """
        Get recommendations by movie title.
        
        Args:
            title: Movie title to search for
            n_recommendations: Number of recommendations to return
            include_scores: Whether to include similarity scores
            
        Returns:
            List of similar movies
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before making recommendations")
        
        # Find movie by title (case-insensitive partial match)
        title_matches = self.movies_df[
            self.movies_df['title'].str.contains(title, case=False, na=False)
        ]
        
        if title_matches.empty:
            raise ValueError(f"No movie found with title containing: '{title}'")
        
        # Use the first match
        movie_id = title_matches.iloc[0]['movieId']
        
        logger.info(f"Found movie: {title_matches.iloc[0]['title']} (ID: {movie_id})")
        
        return self.get_similar_movies(
            movie_id=movie_id,
            n_recommendations=n_recommendations,
            include_scores=include_scores
        )
    
    def get_feature_importance(self, movie_id: int, top_features: int = 20) -> List[Tuple[str, float]]:
        """
        Get the most important TF-IDF features for a specific movie.
        
        Args:
            movie_id: Movie ID to analyze
            top_features: Number of top features to return
            
        Returns:
            List of (feature, tfidf_score) tuples
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before analyzing features")
        
        if movie_id not in self.movie_indices:
            raise ValueError(f"Movie ID {movie_id} not found in the dataset")
        
        # Get movie index
        movie_idx = self.movie_indices[movie_id]
        
        # Get TF-IDF scores for this movie
        tfidf_scores = self.tfidf_matrix[movie_idx].toarray()[0]
        
        # Get feature names
        feature_names = self.tfidf_vectorizer.get_feature_names_out()
        
        # Create feature-score pairs
        feature_scores = list(zip(feature_names, tfidf_scores))
        
        # Sort by TF-IDF score (descending)
        feature_scores = sorted(feature_scores, key=lambda x: x[1], reverse=True)
        
        # Return top features with non-zero scores
        return [(feature, score) for feature, score in feature_scores[:top_features] if score > 0]
    
    def analyze_similarity(self, movie_id1: int, movie_id2: int) -> Dict:
        """
        Analyze similarity between two specific movies.
        
        Args:
            movie_id1: First movie ID
            movie_id2: Second movie ID
            
        Returns:
            Dictionary with similarity analysis
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before analyzing similarity")
        
        for mid in [movie_id1, movie_id2]:
            if mid not in self.movie_indices:
                raise ValueError(f"Movie ID {mid} not found in the dataset")
        
        # Get movie indices
        idx1 = self.movie_indices[movie_id1]
        idx2 = self.movie_indices[movie_id2]
        
        # Get similarity score
        similarity_score = self.cosine_sim_matrix[idx1][idx2]
        
        # Get movie information
        movie1_info = self.movies_df.iloc[idx1]
        movie2_info = self.movies_df.iloc[idx2]
        
        # Get top features for both movies
        features1 = self.get_feature_importance(movie_id1, top_features=10)
        features2 = self.get_feature_importance(movie_id2, top_features=10)
        
        # Find common features
        features1_dict = dict(features1)
        features2_dict = dict(features2)
        common_features = set(features1_dict.keys()) & set(features2_dict.keys())
        
        return {
            'movie1': {
                'movieId': movie_id1,
                'title': movie1_info['title'],
                'genres': movie1_info['genres'],
                'top_features': features1
            },
            'movie2': {
                'movieId': movie_id2,
                'title': movie2_info['title'],
                'genres': movie2_info['genres'],
                'top_features': features2
            },
            'similarity_score': similarity_score,
            'common_features': list(common_features),
            'common_feature_count': len(common_features)
        }
    
    def save_model(self, filepath: str) -> None:
        """
        Save the fitted model to disk.
        
        Args:
            filepath: Path to save the model
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before saving")
        
        model_data = {
            'tfidf_vectorizer': self.tfidf_vectorizer,
            'movies_df': self.movies_df,
            'content_features': self.content_features,
            'tfidf_matrix': self.tfidf_matrix,
            'cosine_sim_matrix': self.cosine_sim_matrix,
            'movie_indices': self.movie_indices,
            'model_params': {
                'max_features': self.max_features,
                'min_df': self.min_df,
                'max_df': self.max_df,
                'ngram_range': self.ngram_range,
                'stop_words': self.stop_words
            }
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        
        logger.info(f"Model saved to {filepath}")
    
    @classmethod
    def load_model(cls, filepath: str) -> 'ContentBasedModel':
        """
        Load a fitted model from disk.
        
        Args:
            filepath: Path to the saved model
            
        Returns:
            Loaded ContentBasedModel instance
        """
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        # Create new instance
        model_params = model_data['model_params']
        model = cls(**model_params)
        
        # Restore state
        model.tfidf_vectorizer = model_data['tfidf_vectorizer']
        model.movies_df = model_data['movies_df']
        model.content_features = model_data['content_features']
        model.tfidf_matrix = model_data['tfidf_matrix']
        model.cosine_sim_matrix = model_data['cosine_sim_matrix']
        model.movie_indices = model_data['movie_indices']
        model.is_fitted = True
        
        logger.info(f"Model loaded from {filepath}")
        return model


def create_content_based_model(movies_df: pd.DataFrame, **kwargs) -> ContentBasedModel:
    """
    Convenience function to create and fit a content-based model.
    
    Args:
        movies_df: DataFrame with movie data
        **kwargs: Additional parameters for ContentBasedModel
        
    Returns:
        Fitted ContentBasedModel instance
    """
    model = ContentBasedModel(**kwargs)
    model.fit(movies_df)
    return model


# Demo functionality
if __name__ == "__main__":
    # This section runs when the module is executed directly
    import sys
    from pathlib import Path
    
    # Add parent directory to path to import data_loader
    sys.path.append(str(Path(__file__).parent.parent))
    
    try:
        from src.data_loader import DataLoader
        
        # Load data
        data_loader = DataLoader('../data/ml-25m')
        movies_df = data_loader.load_movies()
        
        print("Creating and fitting content-based model...")
        model = create_content_based_model(movies_df)
        
        # Demo recommendations
        print("\nDemo: Recommendations for 'Toy Story (1995)'")
        recommendations = model.get_recommendations_by_title(
            title="Toy Story",
            n_recommendations=5,
            include_scores=True
        )
        
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec['title']} | {rec['genres']} | Score: {rec['similarity_score']:.4f}")
        
        print("\nDemo: Feature importance for Toy Story")
        toy_story_id = movies_df[movies_df['title'].str.contains('Toy Story', case=False)].iloc[0]['movieId']
        features = model.get_feature_importance(toy_story_id, top_features=10)
        
        for feature, score in features:
            print(f"  {feature}: {score:.4f}")
        
    except ImportError:
        print("Data loader not available for demo")
        print("Module loaded successfully - ready for import")
