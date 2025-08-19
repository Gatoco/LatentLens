"""
Hybrid Recommendation Service for LatentLens

This module implements a hybrid recommendation system that combines collaborative
filtering (SVD) with content-based filtering (KNN) and item-to-item similarity.
The hybrid approach mitigates individual algorithm weaknesses and provides
balanced recommendations between personalization and discovery.

Key Features:
- Weighted combination of multiple recommendation strategies
- Re-ranking logic to balance relevance and diversity
- Cold-start handling for new users and items
- Filtering of already-seen items
- Configurable weights for different recommendation sources

Author: LatentLens Team
License: MIT
"""

import os
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Set, Tuple
import logging
from pathlib import Path
import joblib
import mlflow
from collections import defaultdict

try:
    from .data_loader import DataLoader
    from .recommendation_service import RecommendationService
    from .item_similarity_service import ItemSimilarityService
    from .content_based_model import ContentBasedModel
except ImportError:
    from data_loader import DataLoader
    from recommendation_service import RecommendationService
    from item_similarity_service import ItemSimilarityService
    from content_based_model import ContentBasedModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HybridRecommendationService:
    """
    Hybrid recommendation service that combines multiple recommendation strategies.
    
    This service integrates:
    1. Collaborative Filtering (SVD) - Personalized recommendations based on user ratings
    2. Item-to-Item Similarity (KNN) - Similar items based on rating patterns
    3. Content-Based Filtering - Similar items based on movie features
    4. Popularity Baseline - Fallback for cold-start scenarios
    """
    
    def __init__(self, data_path: str = "data/ml-25m"):
        """
        Initialize the Hybrid Recommendation Service.
        
        Args:
            data_path (str): Path to the MovieLens dataset directory.
        """
        self.data_path = data_path
        self.data_loader = DataLoader(data_path)
        
        # Component services
        self.collaborative_service: Optional[RecommendationService] = None
        self.item_similarity_service: Optional[ItemSimilarityService] = None
        self.content_based_service: Optional[ContentBasedModel] = None
        
        # Data structures
        self.ratings_df: Optional[pd.DataFrame] = None
        self.movies_df: Optional[pd.DataFrame] = None
        self.user_item_matrix: Optional[pd.DataFrame] = None
        
        # User history cache for performance
        self.user_history_cache: Dict[int, Set[int]] = {}
        
        # Hybrid configuration
        self.weights = {
            'collaborative': 0.5,    # SVD-based recommendations
            'item_similarity': 0.3,  # KNN item-to-item similarity
            'content_based': 0.2     # Content-based similarity
        }
        
        # Re-ranking parameters
        self.diversity_weight = 0.1
        self.popularity_weight = 0.05
        
        # State tracking
        self._is_initialized = False
        
        logger.info(f"HybridRecommendationService initialized with data path: {data_path}")
    
    def initialize(self) -> None:
        """
        Initialize all component services and load required data.
        """
        if self._is_initialized:
            logger.info("HybridRecommendationService already initialized")
            return
        
        logger.info("Initializing HybridRecommendationService...")
        
        # Load core data
        logger.info("Loading ratings and movies data...")
        self.ratings_df = self.data_loader.load_ratings()
        self.movies_df = self.data_loader.load_movies()
        
        # Initialize collaborative filtering service
        logger.info("Initializing collaborative filtering service...")
        self.collaborative_service = RecommendationService()
        self.collaborative_service.initialize()
        
        # Initialize item similarity service
        logger.info("Initializing item-to-item similarity service...")
        self.item_similarity_service = ItemSimilarityService(self.data_path)
        self.item_similarity_service.initialize()
        
        # Initialize content-based service
        logger.info("Initializing content-based service...")
        self.content_based_service = ContentBasedModel()
        self.content_based_service.fit(self.movies_df)
        
        # Pre-compute user histories for performance
        logger.info("Pre-computing user histories...")
        self._build_user_history_cache()
        
        self._is_initialized = True
        logger.info("HybridRecommendationService initialization completed")
    
    def _build_user_history_cache(self) -> None:
        """Build cache of user rating histories for fast lookup."""
        user_histories = self.ratings_df.groupby('userId')['movieId'].apply(set).to_dict()
        self.user_history_cache = user_histories
        logger.info(f"Built user history cache for {len(user_histories):,} users")
    
    def get_user_history(self, user_id: int) -> Set[int]:
        """
        Get the set of movies a user has already rated.
        
        Args:
            user_id (int): User ID to get history for.
        
        Returns:
            Set[int]: Set of movie IDs the user has rated.
        """
        return self.user_history_cache.get(user_id, set())
    
    def get_collaborative_candidates(self, user_id: int, n_candidates: int = 50) -> List[Dict[str, Any]]:
        """
        Get recommendation candidates from collaborative filtering (SVD).
        
        Args:
            user_id (int): User ID to get recommendations for.
            n_candidates (int): Number of candidates to generate.
        
        Returns:
            List[Dict[str, Any]]: List of candidate recommendations with scores.
        """
        try:
            # Use the new SVD recommendations from MLflow
            recommendations = self.collaborative_service.get_svd_recommendations(
                user_id=user_id, 
                n_recommendations=n_candidates,
                exclude_seen=True
            )
            
            # Format for hybrid system
            candidates = []
            for rec in recommendations:
                candidates.append({
                    'movieId': rec.get('movieId', 0),
                    'title': rec.get('title', ''),
                    'score': rec.get('predicted_rating', 3.5),  # Use SVD predicted rating
                    'source': 'collaborative_svd',
                    'genres': rec.get('genres', ''),
                    'predicted_rating': rec.get('predicted_rating', 3.5),
                    'recommendation_type': rec.get('recommendation_type', 'svd')
                })
            
            return candidates
            
        except Exception as e:
            logger.warning(f"Error getting collaborative candidates for user {user_id}: {str(e)}")
            return []
    
    def get_item_similarity_candidates(self, user_id: int, n_candidates: int = 30) -> List[Dict[str, Any]]:
        """
        Get recommendation candidates based on item-to-item similarity.
        
        Args:
            user_id (int): User ID to get recommendations for.
            n_candidates (int): Number of candidates to generate.
        
        Returns:
            List[Dict[str, Any]]: List of candidate recommendations with scores.
        """
        try:
            # Get user's highest-rated movies as seeds
            user_ratings = self.ratings_df[self.ratings_df['userId'] == user_id]
            if user_ratings.empty:
                return []
            
            # Sort by rating and recency (using index as proxy for recency)
            user_ratings = user_ratings.sort_values(['rating', 'timestamp'], ascending=[False, False])
            
            # Use top-rated movies as seeds (limit to avoid over-influence)
            seed_movies = user_ratings.head(10)['movieId'].tolist()
            
            candidates = []
            seen_movies = set()
            
            # For each seed movie, get similar items
            for seed_movie_id in seed_movies:
                try:
                    similar_items = self.item_similarity_service.get_similar_items(
                        seed_movie_id, n_similar=10
                    )
                    
                    for item in similar_items:
                        movie_id = item['movieId']
                        if movie_id not in seen_movies:
                            candidates.append({
                                'movieId': movie_id,
                                'title': item['title'],
                                'score': item['similarity_score'],
                                'source': 'item_similarity',
                                'genres': item['genres'],
                                'avg_rating': item['avg_rating'],
                                'num_ratings': item['num_ratings'],
                                'seed_movie': seed_movie_id
                            })
                            seen_movies.add(movie_id)
                            
                            if len(candidates) >= n_candidates:
                                break
                                
                except Exception as e:
                    logger.debug(f"Error getting similar items for movie {seed_movie_id}: {str(e)}")
                    continue
                
                if len(candidates) >= n_candidates:
                    break
            
            return candidates[:n_candidates]
            
        except Exception as e:
            logger.warning(f"Error getting item similarity candidates for user {user_id}: {str(e)}")
            return []
    
    def get_content_based_candidates(self, user_id: int, n_candidates: int = 20) -> List[Dict[str, Any]]:
        """
        Get recommendation candidates based on content similarity.
        
        Args:
            user_id (int): User ID to get recommendations for.
            n_candidates (int): Number of candidates to generate.
        
        Returns:
            List[Dict[str, Any]]: List of candidate recommendations with scores.
        """
        try:
            # Get user's preferred genres based on rating history
            user_ratings = self.ratings_df[self.ratings_df['userId'] == user_id]
            if user_ratings.empty:
                return []
            
            # Get highly-rated movies by the user
            high_rated = user_ratings[user_ratings['rating'] >= 4.0]
            if high_rated.empty:
                high_rated = user_ratings[user_ratings['rating'] >= user_ratings['rating'].mean()]
            
            # Sample some movies for content-based similarity
            seed_movies = high_rated.sample(min(5, len(high_rated)))['movieId'].tolist()
            
            candidates = []
            seen_movies = set()
            
            for seed_movie_id in seed_movies:
                try:
                    # Get similar movies based on content
                    similar_movies = self.content_based_service.get_similar_movies(
                        seed_movie_id, top_n=8
                    )
                    
                    for _, movie_info in similar_movies.iterrows():
                        movie_id = movie_info['movieId']
                        if movie_id not in seen_movies:
                            candidates.append({
                                'movieId': movie_id,
                                'title': movie_info['title'],
                                'score': movie_info['similarity_score'],
                                'source': 'content_based',
                                'genres': movie_info['genres'],
                                'avg_rating': 0.0,  # Will be filled later
                                'num_ratings': 0,   # Will be filled later
                                'seed_movie': seed_movie_id
                            })
                            seen_movies.add(movie_id)
                            
                            if len(candidates) >= n_candidates:
                                break
                                
                except Exception as e:
                    logger.debug(f"Error getting content-based recommendations for movie {seed_movie_id}: {str(e)}")
                    continue
                
                if len(candidates) >= n_candidates:
                    break
            
            return candidates[:n_candidates]
            
        except Exception as e:
            logger.warning(f"Error getting content-based candidates for user {user_id}: {str(e)}")
            return []
    
    def combine_and_rerank(self, candidates_lists: List[List[Dict[str, Any]]], 
                          user_history: Set[int], n_recommendations: int = 10) -> List[Dict[str, Any]]:
        """
        Combine candidates from multiple sources and apply re-ranking.
        
        Args:
            candidates_lists (List[List[Dict]]): Lists of candidates from different sources.
            user_history (Set[int]): Set of movies the user has already seen.
            n_recommendations (int): Number of final recommendations to return.
        
        Returns:
            List[Dict[str, Any]]: Final ranked list of recommendations.
        """
        # Combine all candidates
        all_candidates = {}
        
        for i, candidates in enumerate(candidates_lists):
            source_names = ['collaborative', 'item_similarity', 'content_based']
            source_name = source_names[i] if i < len(source_names) else f'source_{i}'
            weight = self.weights.get(source_name, 0.1)
            
            for candidate in candidates:
                movie_id = candidate['movieId']
                
                # Skip movies the user has already seen
                if movie_id in user_history:
                    continue
                
                if movie_id not in all_candidates:
                    all_candidates[movie_id] = {
                        'movieId': movie_id,
                        'title': candidate['title'],
                        'genres': candidate['genres'],
                        'scores': {},
                        'weighted_score': 0.0,
                        'sources': [],
                        'avg_rating': candidate.get('avg_rating', 0.0),
                        'num_ratings': candidate.get('num_ratings', 0)
                    }
                
                # Add score from this source
                all_candidates[movie_id]['scores'][source_name] = candidate['score']
                all_candidates[movie_id]['weighted_score'] += candidate['score'] * weight
                all_candidates[movie_id]['sources'].append(source_name)
        
        # Convert to list and apply re-ranking
        candidates_list = list(all_candidates.values())
        
        # Apply diversity and popularity adjustments
        for candidate in candidates_list:
            # Diversity bonus: reward movies that appear from multiple sources
            diversity_bonus = len(candidate['sources']) * self.diversity_weight
            
            # Popularity adjustment: slight bonus for well-rated movies
            popularity_bonus = (candidate['avg_rating'] / 5.0) * self.popularity_weight
            
            # Final score
            candidate['final_score'] = (
                candidate['weighted_score'] + 
                diversity_bonus + 
                popularity_bonus
            )
        
        # Sort by final score and return top N
        candidates_list.sort(key=lambda x: x['final_score'], reverse=True)
        
        # Format final recommendations
        final_recommendations = []
        for candidate in candidates_list[:n_recommendations]:
            final_recommendations.append({
                'movieId': candidate['movieId'],
                'title': candidate['title'],
                'genres': candidate['genres'],
                'final_score': candidate['final_score'],
                'weighted_score': candidate['weighted_score'],
                'sources': candidate['sources'],
                'source_scores': candidate['scores'],
                'avg_rating': candidate['avg_rating'],
                'num_ratings': candidate['num_ratings'],
                'recommendation_type': 'hybrid'
            })
        
        return final_recommendations
    
    def get_hybrid_recommendations(self, user_id: int, n_recommendations: int = 10) -> List[Dict[str, Any]]:
        """
        Get hybrid recommendations for a user.
        
        Args:
            user_id (int): User ID to get recommendations for.
            n_recommendations (int): Number of recommendations to return.
        
        Returns:
            List[Dict[str, Any]]: List of hybrid recommendations.
        """
        if not self._is_initialized:
            raise RuntimeError("HybridRecommendationService not initialized. Call initialize() first.")
        
        logger.info(f"Generating hybrid recommendations for user {user_id}")
        
        # Get user history
        user_history = self.get_user_history(user_id)
        logger.debug(f"User {user_id} has rated {len(user_history)} movies")
        
        # Get candidates from each source
        logger.debug("Getting collaborative filtering candidates...")
        collaborative_candidates = self.get_collaborative_candidates(user_id, n_candidates=50)
        
        logger.debug("Getting item similarity candidates...")
        item_similarity_candidates = self.get_item_similarity_candidates(user_id, n_candidates=30)
        
        logger.debug("Getting content-based candidates...")
        content_based_candidates = self.get_content_based_candidates(user_id, n_candidates=20)
        
        # Log candidate counts
        logger.info(f"Generated candidates - Collaborative: {len(collaborative_candidates)}, "
                   f"Item Similarity: {len(item_similarity_candidates)}, "
                   f"Content-based: {len(content_based_candidates)}")
        
        # Combine and re-rank
        final_recommendations = self.combine_and_rerank(
            [collaborative_candidates, item_similarity_candidates, content_based_candidates],
            user_history,
            n_recommendations
        )
        
        logger.info(f"Generated {len(final_recommendations)} hybrid recommendations for user {user_id}")
        
        return final_recommendations
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get the current status of the hybrid recommendation system.
        
        Returns:
            Dict[str, Any]: System status information.
        """
        status = {
            "initialized": self._is_initialized,
            "weights": self.weights,
            "diversity_weight": self.diversity_weight,
            "popularity_weight": self.popularity_weight
        }
        
        if self._is_initialized:
            status.update({
                "users_in_cache": len(self.user_history_cache),
                "total_ratings": len(self.ratings_df) if self.ratings_df is not None else 0,
                "total_movies": len(self.movies_df) if self.movies_df is not None else 0,
                "collaborative_service": self.collaborative_service is not None,
                "item_similarity_service": self.item_similarity_service is not None,
                "content_based_service": self.content_based_service is not None
            })
        
        return status


# Global hybrid service instance
hybrid_service = HybridRecommendationService()


def get_hybrid_recommendations_for_user(user_id: int, n_recommendations: int = 10) -> List[Dict[str, Any]]:
    """
    Convenience function to get hybrid recommendations for a user.
    
    Args:
        user_id (int): User ID to get recommendations for.
        n_recommendations (int): Number of recommendations to return.
    
    Returns:
        List[Dict[str, Any]]: List of hybrid recommendations.
    """
    if not hybrid_service._is_initialized:
        hybrid_service.initialize()
    
    return hybrid_service.get_hybrid_recommendations(user_id, n_recommendations)


def get_hybrid_system_status() -> Dict[str, Any]:
    """
    Get the current status of the hybrid recommendation system.
    
    Returns:
        Dict[str, Any]: System status information.
    """
    return hybrid_service.get_system_status()
