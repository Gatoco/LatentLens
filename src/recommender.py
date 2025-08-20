"""
Recommender Class - Unified Recommendation Engine

This module provides a clean, unified interface for all recommendation models
in the LatentLens system. It encapsulates collaborative filtering, content-based,
item-to-item similarity, and cold start strategies in a single class.

Author: LatentLens Team
License: MIT
"""

import logging
from typing import List, Dict, Any, Optional, Set, Union
from abc import ABC, abstractmethod
import pandas as pd

from .recommendation_service import get_recommendations_for_user, get_popular_movies, get_similar_movies
from .item_similarity_service import get_similar_items_by_id, get_movie_information, get_model_status
from .hybrid_recommendation_service import get_hybrid_recommendations_for_user, get_hybrid_system_status, hybrid_service
from .data_loader import DataLoader

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RecommendationStrategy(ABC):
    """Abstract base class for recommendation strategies"""
    
    @abstractmethod
    def get_recommendations(self, user_id: int, n_recommendations: int = 10, **kwargs) -> List[Dict[str, Any]]:
        """Get recommendations for a user"""
        pass


class CollaborativeFilteringStrategy(RecommendationStrategy):
    """Collaborative filtering strategy using SVD model from MLflow"""
    
    def get_recommendations(self, user_id: int, n_recommendations: int = 10, **kwargs) -> List[Dict[str, Any]]:
        """Get collaborative filtering recommendations"""
        return get_recommendations_for_user(user_id, n_recommendations)


class HybridStrategy(RecommendationStrategy):
    """Hybrid recommendation strategy combining multiple approaches"""
    
    def get_recommendations(self, user_id: int, n_recommendations: int = 10, **kwargs) -> List[Dict[str, Any]]:
        """Get hybrid recommendations with automatic cold start handling"""
        return get_hybrid_recommendations_for_user(user_id, n_recommendations)


class PopularityStrategy(RecommendationStrategy):
    """Popularity-based recommendation strategy"""
    
    def get_recommendations(self, user_id: int, n_recommendations: int = 10, **kwargs) -> List[Dict[str, Any]]:
        """Get popular movie recommendations"""
        # For popularity, user_id is not used but we maintain interface consistency
        return get_popular_movies(n_recommendations)


class ItemSimilarityStrategy(RecommendationStrategy):
    """Item-to-item similarity recommendation strategy"""
    
    def get_recommendations(self, user_id: int, n_recommendations: int = 10, **kwargs) -> List[Dict[str, Any]]:
        """Get item similarity recommendations based on movie_id"""
        movie_id = kwargs.get('movie_id')
        if not movie_id:
            raise ValueError("movie_id is required for item similarity recommendations")
        return get_similar_items_by_id(movie_id, n_recommendations)


class ColdStartStrategy(RecommendationStrategy):
    """Cold start recommendation strategy for new users and new movies"""
    
    def __init__(self):
        self.data_loader = DataLoader()
    
    def get_recommendations(self, user_id: int, strategy: str, n_recommendations: int = 10, **kwargs) -> List[Dict[str, Any]]:
        """Get cold start recommendations based on strategy"""
        cold_start_strategy = kwargs.get('cold_start_strategy', kwargs.get('strategy', 'popular'))
        
        if cold_start_strategy == 'popular':
            return self._get_popular_movies(n_recommendations)
        elif cold_start_strategy == 'trending':
            return self._get_trending_movies(n_recommendations)
        elif cold_start_strategy == 'diverse':
            return self._get_diverse_genre_recommendations(n_recommendations)
        else:
            raise ValueError(f"Unknown cold start strategy: {cold_start_strategy}")
    
    def _get_popular_movies(self, n_recommendations: int = 10) -> List[Dict]:
        """Get popular movies for cold start users"""
        ratings = self.data_loader.load_ratings()
        movies = self.data_loader.load_movies()
        
        # Calculate movie popularity
        movie_stats = ratings.groupby('movieId').agg({
            'rating': ['count', 'mean']
        }).round(2)
        movie_stats.columns = ['rating_count', 'avg_rating']
        movie_stats = movie_stats.reset_index()
        
        # Filter for popular movies (high rating count and good average rating)
        popular_movies = movie_stats[
            (movie_stats['rating_count'] >= 100) & 
            (movie_stats['avg_rating'] >= 4.0)
        ].sort_values(['avg_rating', 'rating_count'], ascending=[False, False])
        
        # Get movie details
        popular_with_details = popular_movies.merge(movies, on='movieId', how='left')
        
        # Format response
        recommendations = []
        for _, row in popular_with_details.head(n_recommendations).iterrows():
            recommendations.append({
                'movie_id': int(row['movieId']),
                'title': row['title'],
                'genres': row['genres'],
                'predicted_rating': float(row['avg_rating']),
                'rating_count': int(row['rating_count']),
                'strategy': 'popular'
            })
        
        return recommendations
    
    def _get_trending_movies(self, n_recommendations: int = 10) -> List[Dict]:
        """Get trending/recent movies for cold start users"""
        movies = self.data_loader.load_movies()
        
        # Extract years from movie titles
        movies_copy = movies.copy()
        movies_copy['year'] = movies_copy['title'].str.extract(r'\((\d{4})\)$')[0]
        movies_copy['year'] = pd.to_numeric(movies_copy['year'], errors='coerce')
        
        # Get recent movies (last 5 years)
        max_year = movies_copy['year'].max()
        recent_threshold = max_year - 5
        recent_movies = movies_copy[
            movies_copy['year'] >= recent_threshold
        ].dropna(subset=['year']).sort_values('year', ascending=False)
        
        # Format response
        recommendations = []
        for _, row in recent_movies.head(n_recommendations).iterrows():
            recommendations.append({
                'movie_id': int(row['movieId']),
                'title': row['title'],
                'genres': row['genres'],
                'year': int(row['year']),
                'strategy': 'trending'
            })
        
        return recommendations
    
    def _get_diverse_genre_recommendations(self, n_recommendations: int = 10) -> List[Dict]:
        """Get genre-diverse recommendations for cold start users"""
        movies = self.data_loader.load_movies()
        
        # Extract all unique genres
        all_genres = set()
        for genres_str in movies['genres'].dropna():
            if genres_str != "(no genres listed)":
                all_genres.update(genres_str.split('|'))
        
        # Get movies from different genres
        target_genres = ['Action', 'Comedy', 'Drama', 'Thriller', 'Romance', 'Adventure', 'Sci-Fi']
        recommendations = []
        
        for genre in target_genres:
            if len(recommendations) >= n_recommendations:
                break
                
            genre_movies = movies[
                movies['genres'].str.contains(genre, na=False)
            ].sample(min(2, len(movies[movies['genres'].str.contains(genre, na=False)])))
            
            for _, row in genre_movies.iterrows():
                if len(recommendations) >= n_recommendations:
                    break
                    
                recommendations.append({
                    'movie_id': int(row['movieId']),
                    'title': row['title'],
                    'genres': row['genres'],
                    'primary_genre': genre,
                    'strategy': 'diverse'
                })
        
        return recommendations


class Recommender:
    """
    Unified Recommendation Engine
    
    This class provides a clean interface to all recommendation models and strategies
    in the LatentLens system. It encapsulates collaborative filtering, content-based,
    item-to-item similarity, and cold start approaches in a single, easy-to-use class.
    """
    
    def __init__(self):
        """Initialize the recommender with all available strategies"""
        self.strategies = {
            'collaborative': CollaborativeFilteringStrategy(),
            'hybrid': HybridStrategy(),
            'popularity': PopularityStrategy(),
            'item_similarity': ItemSimilarityStrategy(),
            'cold_start': ColdStartStrategy()
        }
        self.data_loader = DataLoader()
        logger.info("🎬 Recommender initialized with all strategies")
    
    def get_recommendations(
        self, 
        user_id: int, 
        strategy: str = 'hybrid', 
        n_recommendations: int = 10,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get recommendations using the specified strategy
        
        Args:
            user_id: Target user ID
            strategy: Recommendation strategy ('hybrid', 'collaborative', 'popularity', 'item_similarity', 'cold_start')
            n_recommendations: Number of recommendations to return
            **kwargs: Additional parameters for specific strategies
        
        Returns:
            Dict containing recommendations and metadata
        """
        if strategy not in self.strategies:
            raise ValueError(f"Unknown strategy: {strategy}. Available: {list(self.strategies.keys())}")
        
        # Check for cold start scenario automatically for user-based strategies
        if strategy in ['hybrid', 'collaborative'] and self._is_cold_start_user(user_id):
            logger.info(f"Cold start detected for user {user_id}, switching to cold start strategy")
            strategy = 'cold_start'
            kwargs.setdefault('strategy', 'popular')
        
        try:
            recommendations = self.strategies[strategy].get_recommendations(
                user_id, n_recommendations, **kwargs
            )
            
            return {
                'user_id': user_id,
                'strategy': strategy,
                'n_recommendations': len(recommendations),
                'recommendations': recommendations,
                'metadata': {
                    'cold_start_detected': self._is_cold_start_user(user_id),
                    'total_available_strategies': len(self.strategies),
                    'kwargs': kwargs
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting recommendations for user {user_id} with strategy {strategy}: {str(e)}")
            # Fallback to popularity-based recommendations
            if strategy != 'popularity':
                logger.info("Falling back to popularity-based recommendations")
                return self.get_recommendations(user_id, 'popularity', n_recommendations)
            else:
                raise
    
    def get_movie_recommendations(
        self, 
        movie_id: int, 
        n_recommendations: int = 10,
        strategy: str = 'item_similarity'
    ) -> Dict[str, Any]:
        """
        Get movie-to-movie recommendations
        
        Args:
            movie_id: Target movie ID
            n_recommendations: Number of recommendations to return
            strategy: Strategy to use ('item_similarity' or 'content_based')
        
        Returns:
            Dict containing movie recommendations and metadata
        """
        try:
            if strategy == 'item_similarity':
                recommendations = get_similar_items_by_id(movie_id, n_recommendations)
            else:
                # Content-based fallback could be implemented here
                recommendations = get_similar_items_by_id(movie_id, n_recommendations)
            
            return {
                'movie_id': movie_id,
                'strategy': strategy,
                'n_recommendations': len(recommendations),
                'recommendations': recommendations,
                'metadata': {
                    'movie_info': get_movie_information(movie_id)
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting movie recommendations for movie {movie_id}: {str(e)}")
            raise
    
    def get_popular_movies(self, n_recommendations: int = 10) -> Dict[str, Any]:
        """Get popular movies baseline"""
        recommendations = get_popular_movies(n_recommendations)
        
        return {
            'strategy': 'popularity',
            'n_recommendations': len(recommendations),
            'recommendations': recommendations,
            'metadata': {
                'description': 'Most popular movies based on user ratings'
            }
        }
    
    def get_new_movies(self, years_back: int = 5, limit: int = 20) -> Dict[str, Any]:
        """Get recent/new movies for discovery"""
        movies = self.data_loader.load_movies()
        
        # Extract years and filter recent movies
        movies_copy = movies.copy()
        movies_copy['year'] = movies_copy['title'].str.extract(r'\((\d{4})\)$')[0]
        movies_copy['year'] = pd.to_numeric(movies_copy['year'], errors='coerce')
        
        max_year = movies_copy['year'].max()
        recent_threshold = max_year - years_back
        recent_movies = movies_copy[
            movies_copy['year'] >= recent_threshold
        ].dropna(subset=['year']).sort_values('year', ascending=False)
        
        # Format response
        new_movies = []
        for _, row in recent_movies.head(limit).iterrows():
            new_movies.append({
                'movie_id': int(row['movieId']),
                'title': row['title'],
                'genres': row['genres'],
                'year': int(row['year'])
            })
        
        return {
            'strategy': 'new_movies',
            'years_back': years_back,
            'threshold_year': int(recent_threshold),
            'n_movies': len(new_movies),
            'movies': new_movies,
            'metadata': {
                'max_year_in_dataset': int(max_year),
                'total_movies_in_dataset': len(movies)
            }
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        try:
            # Get status from various components
            hybrid_status = get_hybrid_system_status()
            model_status = get_model_status()
            
            return {
                'recommender_status': 'healthy',
                'available_strategies': list(self.strategies.keys()),
                'hybrid_system': hybrid_status,
                'model_status': model_status,
                'cold_start_enabled': True,
                'components': {
                    'collaborative_filtering': 'loaded',
                    'item_similarity': 'loaded', 
                    'content_based': 'loaded',
                    'hybrid_service': 'loaded',
                    'cold_start': 'loaded'
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting system status: {str(e)}")
            return {
                'recommender_status': 'error',
                'error': str(e),
                'available_strategies': list(self.strategies.keys())
            }
    
    def _is_cold_start_user(self, user_id: int) -> bool:
        """Check if user is in cold start scenario"""
        try:
            ratings = self.data_loader.load_ratings()
            user_ratings = ratings[ratings['userId'] == user_id]
            
            # New user (no ratings) or insufficient data (<5 ratings)
            return len(user_ratings) == 0 or len(user_ratings) < 5
            
        except Exception as e:
            logger.warning(f"Could not check cold start status for user {user_id}: {str(e)}")
            return False
    
    def _calculate_content_similarity(self, movie_id: int, target_genres: Set[str]) -> float:
        """Calculate content-based similarity using Jaccard similarity on genres"""
        try:
            movies = self.data_loader.load_movies()
            movie_info = movies[movies['movieId'] == movie_id]
            
            if movie_info.empty:
                return 0.0
            
            movie_genres = set(movie_info.iloc[0]['genres'].split('|'))
            
            # Jaccard similarity: intersection / union
            intersection = len(movie_genres.intersection(target_genres))
            union = len(movie_genres.union(target_genres))
            
            return intersection / union if union > 0 else 0.0
            
        except Exception as e:
            logger.warning(f"Could not calculate content similarity for movie {movie_id}: {str(e)}")
            return 0.0


# Global recommender instance
recommender_instance = None

def get_recommender() -> Recommender:
    """Get the global recommender instance (singleton pattern)"""
    global recommender_instance
    if recommender_instance is None:
        recommender_instance = Recommender()
    return recommender_instance
