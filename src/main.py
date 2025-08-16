
"""
LatentLens FastAPI Application

This module defines the main FastAPI application for the LatentLens movie 
recommendation system. It provides REST API endpoints for health checks 
and movie recommendations using collaborative filtering and popularity baselines.

Author: LatentLens Team
License: MIT
"""

from fastapi import FastAPI, HTTPException, Path, Query
from typing import List, Dict, Any
import logging

from .recommendation_service import get_recommendations_for_user, get_popular_movies, get_similar_movies

# Application instance with comprehensive metadata for API documentation
application_instance = FastAPI(
    title="LatentLens Movie Recommendation API",
    description="A hybrid recommendation system for movies using collaborative filtering and popularity baselines.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@application_instance.get("/health")
def get_health_status():
    """
    Health check endpoint for service monitoring.
    
    This endpoint is used by load balancers, monitoring systems, and 
    deployment pipelines to verify that the API service is running 
    and responding to requests.
    
    Returns:
        dict: A dictionary containing the service status.
            - status (str): Always "ok" when the service is healthy.
    
    Example:
        GET /health
        Response: {"status": "ok"}
    """
    health_response = {"status": "ok"}
    return health_response


@application_instance.get("/recommend/{user_id}")
def get_user_recommendations(
    user_id: int = Path(..., description="User ID to generate recommendations for", ge=1),
    limit: int = Query(10, description="Number of recommendations to return", ge=1, le=50)
) -> Dict[str, Any]:
    """
    Get personalized movie recommendations for a specific user.
    
    This endpoint generates movie recommendations using a hybrid approach
    that combines popularity baselines with collaborative filtering techniques.
    
    Args:
        user_id (int): The unique identifier for the user (must be >= 1).
        limit (int): Number of recommendations to return (1-50, default: 10).
    
    Returns:
        Dict[str, Any]: Response containing recommendations and metadata.
            - user_id (int): The user ID the recommendations were generated for.
            - recommendations (List[Dict]): List of movie recommendations.
            - total_recommendations (int): Number of recommendations returned.
            - recommendation_type (str): Type of recommendation algorithm used.
    
    Raises:
        HTTPException: 500 if there's an error generating recommendations.
    
    Example:
        GET /recommend/123?limit=5
        Response: {
            "user_id": 123,
            "recommendations": [
                {
                    "title": "The Shawshank Redemption (1994)",
                    "average_rating": 4.41,
                    "num_ratings": 81482,
                    "recommendation_type": "user_hybrid"
                },
                ...
            ],
            "total_recommendations": 5,
            "recommendation_type": "hybrid_popularity_baseline"
        }
    """
    try:
        logger.info(f"Generating recommendations for user {user_id}")
        
        # Generate recommendations using the recommendation service
        recommendations = get_recommendations_for_user(user_id, limit)
        
        response = {
            "user_id": user_id,
            "recommendations": recommendations,
            "total_recommendations": len(recommendations),
            "recommendation_type": "hybrid_popularity_baseline"
        }
        
        logger.info(f"Successfully generated {len(recommendations)} recommendations for user {user_id}")
        return response
        
    except Exception as error:
        logger.error(f"Error generating recommendations for user {user_id}: {str(error)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate recommendations: {str(error)}"
        )


@application_instance.get("/movies/popular")
def get_popular_movie_recommendations(
    limit: int = Query(10, description="Number of popular movies to return", ge=1, le=50)
) -> Dict[str, Any]:
    """
    Get popular movie recommendations based on ratings and popularity.
    
    This endpoint returns the highest-rated movies that have received
    sufficient ratings to ensure statistical significance.
    
    Args:
        limit (int): Number of popular movies to return (1-50, default: 10).
    
    Returns:
        Dict[str, Any]: Response containing popular movies and metadata.
    
    Example:
        GET /movies/popular?limit=5
        Response: {
            "movies": [...],
            "total_movies": 5,
            "recommendation_type": "popularity_baseline"
        }
    """
    try:
        logger.info(f"Fetching {limit} popular movies")
        
        popular_movies = get_popular_movies(limit)
        
        response = {
            "movies": popular_movies,
            "total_movies": len(popular_movies),
            "recommendation_type": "popularity_baseline"
        }
        
        logger.info(f"Successfully fetched {len(popular_movies)} popular movies")
        return response
        
    except Exception as error:
        logger.error(f"Error fetching popular movies: {str(error)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch popular movies: {str(error)}"
        )


@application_instance.get("/movies/similar")
def get_similar_movie_recommendations(
    movie_title: str = Query(..., description="Movie title to find similar movies for"),
    limit: int = Query(10, description="Number of similar movies to return", ge=1, le=50)
) -> Dict[str, Any]:
    """
    Get movies similar to a given movie using collaborative filtering.
    
    This endpoint finds movies that are similar to the provided movie title
    using collaborative filtering with K-Nearest Neighbors algorithm.
    
    Args:
        movie_title (str): The title of the movie to find similar movies for.
        limit (int): Number of similar movies to return (1-50, default: 10).
    
    Returns:
        Dict[str, Any]: Response containing similar movies and metadata.
    
    Raises:
        HTTPException: 404 if the movie is not found, 500 for other errors.
    
    Example:
        GET /movies/similar?movie_title=The Matrix (1999)&limit=5
    """
    try:
        logger.info(f"Finding movies similar to '{movie_title}'")
        
        similar_movies = get_similar_movies(movie_title, limit)
        
        response = {
            "query_movie": movie_title,
            "similar_movies": similar_movies,
            "total_movies": len(similar_movies),
            "recommendation_type": "collaborative_filtering"
        }
        
        logger.info(f"Successfully found {len(similar_movies)} movies similar to '{movie_title}'")
        return response
        
    except ValueError as ve:
        logger.warning(f"Movie not found: {movie_title}")
        raise HTTPException(
            status_code=404,
            detail=f"Movie '{movie_title}' not found in the recommendation dataset"
        )
    except Exception as error:
        logger.error(f"Error finding similar movies for '{movie_title}': {str(error)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to find similar movies: {str(error)}"
        )


# Export the app instance for uvicorn and other ASGI servers
app = application_instance