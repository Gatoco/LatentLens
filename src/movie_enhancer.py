"""
API Response Enhancement Script for LatentLens

This script improves all API responses to include complete movie information
(movieId, title, genres) by performing joins with the movies dataframe.

Author: LatentLens Team
License: MIT
"""

import pandas as pd
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MovieEnhancer:
    """
    Utility class to enhance API responses with complete movie information.
    
    This class provides methods to enrich movie recommendations with title
    and genres information by joining with the movies dataframe.
    """
    
    def __init__(self, data_path: str = "data/ml-25m"):
        """
        Initialize the MovieEnhancer.
        
        Args:
            data_path (str): Path to the MovieLens dataset directory.
        """
        self.data_path = data_path
        self.movies_df: Optional[pd.DataFrame] = None
        self._is_initialized = False
        
    def initialize(self) -> None:
        """Load movies dataframe for enhancement operations."""
        if self._is_initialized:
            return
            
        movies_path = Path(self.data_path) / "movies.csv"
        if not movies_path.exists():
            raise FileNotFoundError(f"Movies file not found: {movies_path}")
            
        self.movies_df = pd.read_csv(movies_path)
        logger.info(f"Loaded {len(self.movies_df):,} movies for enhancement")
        self._is_initialized = True
    
    def enhance_single_movie(self, movie: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance a single movie recommendation with complete information.
        
        Args:
            movie (Dict): Movie dictionary with at least movieId.
        
        Returns:
            Dict: Enhanced movie with title and genres.
        """
        if not self._is_initialized:
            self.initialize()
            
        # Make a copy to avoid modifying the original
        enhanced_movie = movie.copy()
        
        movie_id = movie.get('movieId')
        if movie_id is None:
            logger.warning("Movie missing movieId, cannot enhance")
            return enhanced_movie
            
        # Find movie information
        movie_info = self.movies_df[self.movies_df['movieId'] == movie_id]
        
        if movie_info.empty:
            logger.warning(f"Movie ID {movie_id} not found in movies database")
            # Add placeholder information
            enhanced_movie.setdefault('title', f"Unknown Movie (ID: {movie_id})")
            enhanced_movie.setdefault('genres', "Unknown")
        else:
            movie_row = movie_info.iloc[0]
            enhanced_movie.setdefault('title', movie_row['title'])
            enhanced_movie.setdefault('genres', movie_row['genres'])
            
        return enhanced_movie
    
    def enhance_movie_list(self, movies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Enhance a list of movie recommendations with complete information.
        
        Args:
            movies (List[Dict]): List of movie dictionaries with at least movieId.
        
        Returns:
            List[Dict]: Enhanced list with title and genres added.
        """
        if not self._is_initialized:
            self.initialize()
            
        enhanced_movies = []
        
        for movie in movies:
            enhanced_movie = self.enhance_single_movie(movie)
            enhanced_movies.append(enhanced_movie)
            
        return enhanced_movies


# Global enhancer instance
movie_enhancer = MovieEnhancer()


def enhance_api_response(response: Any) -> Any:
    """
    Convenience function to enhance any API response.
    
    Args:
        response: API response to enhance.
    
    Returns:
        Enhanced response with complete movie information.
    """
    if isinstance(response, dict):
        # Make a copy to avoid modifying the original
        enhanced_response = response.copy()
        
        # Look for common patterns in API responses
        if 'recommendations' in response:
            enhanced_response['recommendations'] = movie_enhancer.enhance_movie_list(
                response['recommendations']
            )
        elif 'movies' in response:
            enhanced_response['movies'] = movie_enhancer.enhance_movie_list(
                response['movies']
            )
        elif 'similar_movies' in response:
            enhanced_response['similar_movies'] = movie_enhancer.enhance_movie_list(
                response['similar_movies']
            )
            
        return enhanced_response
    elif isinstance(response, list):
        return movie_enhancer.enhance_movie_list(response)
    else:
        return response
