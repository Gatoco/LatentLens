
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
from .item_similarity_service import get_similar_items_by_id, get_movie_information, get_model_status
from .hybrid_recommendation_service import get_hybrid_recommendations_for_user, get_hybrid_system_status, hybrid_service

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


@application_instance.on_event("startup")
async def startup_event():
    """
    Initialize all recommendation models on application startup.
    
    This event handler loads and initializes all the recommendation components:
    - Collaborative filtering (SVD) model from MLflow
    - Item-to-item similarity (KNN) model
    - Content-based filtering model
    - Hybrid recommendation service
    """
    logger.info("🚀 Starting LatentLens API - Initializing recommendation models...")
    
    try:
        # Initialize the hybrid service (this will initialize all component services)
        logger.info("Initializing hybrid recommendation service...")
        hybrid_service.initialize()
        
        logger.info("✅ All recommendation models loaded successfully!")
        logger.info("🎬 LatentLens API is ready to serve hybrid recommendations!")
        
    except Exception as e:
        logger.error(f"❌ Error during model initialization: {str(e)}")
        raise RuntimeError(f"Failed to initialize recommendation models: {str(e)}")


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


@application_instance.get("/recommend/hybrid/{user_id}")
def get_hybrid_user_recommendations(
    user_id: int = Path(..., description="User ID to generate hybrid recommendations for", ge=1),
    limit: int = Query(10, description="Number of recommendations to return", ge=1, le=50)
) -> Dict[str, Any]:
    """
    Get hybrid movie recommendations for a specific user.
    
    This endpoint generates movie recommendations using a hybrid approach that combines:
    1. Collaborative Filtering (SVD) - Personalized recommendations based on user ratings
    2. Item-to-Item Similarity (KNN) - Similar items based on rating patterns  
    3. Content-Based Filtering - Similar items based on movie features
    
    The system uses weighted combination and re-ranking to balance personalization
    and discovery, mitigating cold-start issues and popularity bias.
    
    Args:
        user_id (int): The unique identifier for the user (must be >= 1).
        limit (int): Number of recommendations to return (1-50, default: 10).
    
    Returns:
        Dict[str, Any]: Response containing hybrid recommendations and metadata.
            - user_id (int): The user ID the recommendations were generated for.
            - recommendations (List[Dict]): List of hybrid movie recommendations.
            - total_recommendations (int): Number of recommendations returned.
            - recommendation_type (str): Type of recommendation algorithm used.
            - hybrid_info (Dict): Information about the hybrid combination.
    
    Raises:
        HTTPException: 500 if there's an error generating recommendations.
    
    Example:
        GET /recommend/hybrid/123?limit=5
        Response: {
            "user_id": 123,
            "recommendations": [
                {
                    "movieId": 1196,
                    "title": "Star Wars: Episode V - The Empire Strikes Back (1980)",
                    "genres": "Action|Adventure|Sci-Fi",
                    "final_score": 4.521,
                    "sources": ["collaborative", "item_similarity"],
                    "recommendation_type": "hybrid"
                },
                ...
            ],
            "total_recommendations": 5,
            "recommendation_type": "hybrid_weighted_reranking",
            "hybrid_info": {
                "sources_used": ["collaborative", "item_similarity", "content_based"],
                "weights": {"collaborative": 0.5, "item_similarity": 0.3, "content_based": 0.2}
            }
        }
    """
    try:
        logger.info(f"Generating hybrid recommendations for user {user_id}")
        
        # Generate hybrid recommendations
        recommendations = get_hybrid_recommendations_for_user(user_id, limit)
        
        # Get hybrid system status for metadata
        hybrid_status = get_hybrid_system_status()
        
        response = {
            "user_id": user_id,
            "recommendations": recommendations,
            "total_recommendations": len(recommendations),
            "recommendation_type": "hybrid_weighted_reranking",
            "hybrid_info": {
                "sources_used": ["collaborative", "item_similarity", "content_based"],
                "weights": hybrid_status.get("weights", {}),
                "diversity_weight": hybrid_status.get("diversity_weight", 0),
                "popularity_weight": hybrid_status.get("popularity_weight", 0)
            }
        }
        
        logger.info(f"Successfully generated {len(recommendations)} hybrid recommendations for user {user_id}")
        return response
        
    except Exception as error:
        logger.error(f"Error generating hybrid recommendations for user {user_id}: {str(error)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate hybrid recommendations: {str(error)}"
        )


@application_instance.get("/system/status")
def get_system_status() -> Dict[str, Any]:
    """
    Get comprehensive system status for all recommendation components.
    
    This endpoint provides detailed information about the state of all
    recommendation services including the hybrid system, individual models,
    and overall system health.
    
    Returns:
        Dict[str, Any]: Comprehensive system status information.
    
    Example:
        GET /system/status
        Response: {
            "hybrid_system": {
                "initialized": true,
                "weights": {"collaborative": 0.5, "item_similarity": 0.3, "content_based": 0.2},
                "users_in_cache": 162541
            },
            "item_similarity": {
                "initialized": true,
                "total_movies": 13172,
                "matrix_density": 0.011530
            }
        }
    """
    try:
        logger.info("Retrieving comprehensive system status")
        
        # Get status from all services
        hybrid_status = get_hybrid_system_status()
        similarity_status = get_model_status()
        
        response = {
            "hybrid_system": hybrid_status,
            "item_similarity": similarity_status,
            "api_version": "0.1.0",
            "status": "operational" if hybrid_status.get("initialized", False) else "initializing"
        }
        
        logger.info("Successfully retrieved system status")
        return response
        
    except Exception as error:
        logger.error(f"Error retrieving system status: {str(error)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve system status: {str(error)}"
        )


@application_instance.get("/similar/{movie_id}")
def get_item_to_item_similar_movies(
    movie_id: int = Path(..., description="Movie ID to find similar movies for", ge=1),
    limit: int = Query(10, description="Number of similar movies to return", ge=1, le=50)
) -> Dict[str, Any]:
    """
    Get movies similar to a given movie ID using item-to-item collaborative filtering.
    
    This endpoint finds movies that are similar to the provided movie ID using
    K-Nearest Neighbors on user rating patterns. This is ideal for cold-start
    scenarios and "related products" functionality.
    
    Args:
        movie_id (int): The unique identifier of the movie to find similar movies for.
        limit (int): Number of similar movies to return (1-50, default: 10).
    
    Returns:
        Dict[str, Any]: Response containing similar movies and metadata.
            - query_movie (Dict): Information about the queried movie.
            - similar_movies (List[Dict]): List of similar movies with similarity scores.
            - total_movies (int): Number of similar movies returned.
            - recommendation_type (str): Type of recommendation algorithm used.
    
    Raises:
        HTTPException: 404 if the movie ID is not found, 500 for other errors.
    
    Example:
        GET /similar/1?limit=5
        Response: {
            "query_movie": {
                "movieId": 1,
                "title": "Toy Story (1995)",
                "genres": "Adventure|Animation|Children|Comedy|Fantasy",
                "avg_rating": 3.92,
                "num_ratings": 81834
            },
            "similar_movies": [
                {
                    "movieId": 3114,
                    "title": "Toy Story 2 (1999)",
                    "similarity_score": 0.8456,
                    "avg_rating": 3.84,
                    "num_ratings": 56789
                },
                ...
            ],
            "total_movies": 5,
            "recommendation_type": "item_to_item_knn"
        }
    """
    try:
        logger.info(f"Finding movies similar to movie ID {movie_id}")
        
        # Get information about the queried movie
        query_movie = get_movie_information(movie_id)
        
        # Get similar movies using item-to-item KNN
        similar_movies = get_similar_items_by_id(movie_id, limit)
        
        response = {
            "query_movie": query_movie,
            "similar_movies": similar_movies,
            "total_movies": len(similar_movies),
            "recommendation_type": "item_to_item_knn"
        }
        
        logger.info(f"Successfully found {len(similar_movies)} movies similar to movie ID {movie_id}")
        return response
        
    except ValueError as ve:
        logger.warning(f"Movie ID not found: {movie_id}")
        raise HTTPException(
            status_code=404,
            detail=f"Movie ID {movie_id} not found in the similarity index"
        )
    except Exception as error:
        logger.error(f"Error finding similar movies for movie ID {movie_id}: {str(error)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to find similar movies: {str(error)}"
        )


@application_instance.get("/model/status")
def get_similarity_model_status() -> Dict[str, Any]:
    """
    Get the current status of the item similarity model.
    
    This endpoint provides information about the loaded similarity model,
    including matrix dimensions, density, and configuration parameters.
    
    Returns:
        Dict[str, Any]: Model status and configuration information.
    
    Example:
        GET /model/status
        Response: {
            "initialized": true,
            "total_movies": 15623,
            "matrix_shape": [15623, 162541],
            "matrix_density": 0.0234,
            "knn_neighbors": 21,
            "knn_metric": "cosine"
        }
    """
    try:
        logger.info("Retrieving similarity model status")
        
        model_status = get_model_status()
        
        logger.info("Successfully retrieved model status")
        return model_status
        
    except Exception as error:
        logger.error(f"Error retrieving model status: {str(error)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve model status: {str(error)}"
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