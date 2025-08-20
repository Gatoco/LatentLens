
"""
LatentLens FastAPI Application

This module defines the main FastAPI application for the LatentLens movie 
recommendation system. It provides REST API endpoints for health checks 
and movie recommendations using a unified Recommender class that encapsulates
all recommendation strategies.

Author: LatentLens Team
License: MIT
"""

from fastapi import FastAPI, HTTPException, Path, Query
from typing import List, Dict, Any
import logging

from .recommender import get_recommender
from .hybrid_recommendation_service import get_hybrid_system_status
from .recommendation_service import get_similar_movies

# Application instance with comprehensive metadata for API documentation
application_instance = FastAPI(
    title="LatentLens Movie Recommendation API",
    description="A unified recommendation system for movies using multiple strategies through a clean Recommender interface.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global recommender instance
recommender = get_recommender()


@application_instance.on_event("startup")
async def startup_event():
    """
    Initialize all recommendation models on application startup.
    
    This event handler initializes the unified Recommender class which
    encapsulates all recommendation strategies and models.
    """
    logger.info("🚀 Starting LatentLens API - Initializing unified recommendation engine...")
    
    try:
        # Initialize the unified recommender (this will initialize all strategies)
        logger.info("Initializing unified Recommender class...")
        global recommender
        recommender = get_recommender()
        
        logger.info("✅ All recommendation models loaded successfully!")
        logger.info("🎬 LatentLens API is ready to serve unified recommendations!")
        
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
        logger.info(f"Generating collaborative filtering recommendations for user {user_id}")
        
        # Use unified recommender with collaborative filtering strategy
        result = recommender.get_recommendations(
            user_id=user_id,
            strategy='collaborative',
            n_recommendations=limit
        )
        
        logger.info(f"Successfully generated {result['n_recommendations']} recommendations for user {user_id}")
        return result
        
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
        
        # Use unified recommender with popularity strategy
        result = recommender.get_popular_movies(n_recommendations=limit)
        
        logger.info(f"Successfully fetched {result['n_recommendations']} popular movies")
        return result
        
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
        
        # Use unified recommender with hybrid strategy (includes automatic cold start handling)
        result = recommender.get_recommendations(
            user_id=user_id,
            strategy='hybrid',
            n_recommendations=limit
        )
        
        # Add hybrid system status for metadata
        hybrid_status = get_hybrid_system_status()
        result['hybrid_info'] = {
            "sources_used": ["collaborative", "item_similarity", "content_based"],
            "weights": hybrid_status.get("weights", {}),
            "diversity_weight": hybrid_status.get("diversity_weight", 0),
            "popularity_weight": hybrid_status.get("popularity_weight", 0)
        }
        
        logger.info(f"Successfully generated {result['n_recommendations']} hybrid recommendations for user {user_id}")
        return result
        
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
        
        # Get unified system status from recommender
        system_status = recommender.get_system_status()
        
        response = {
            "api_version": "1.0.0",
            "status": "operational" if system_status.get("recommender_status") == "healthy" else "initializing",
            "unified_recommender": system_status
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
        
        # Use unified recommender for movie-to-movie recommendations
        result = recommender.get_movie_recommendations(
            movie_id=movie_id,
            n_recommendations=limit,
            strategy='item_similarity'
        )
        
        logger.info(f"Successfully found {result['n_recommendations']} movies similar to movie ID {movie_id}")
        return result
        
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
        logger.info("Retrieving unified model status")
        
        # Get comprehensive status from unified recommender
        model_status = recommender.get_system_status()
        
        logger.info("Successfully retrieved model status")
        return {
            "model_status": "operational",
            "unified_recommender": model_status,
            "available_strategies": model_status.get("available_strategies", [])
        }
        
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


# Cold Start Endpoints using Unified Recommender
@application_instance.get("/recommend/cold-start/{user_id}")
def get_cold_start_recommendations(
    user_id: int = Path(..., description="User ID for cold start recommendations"),
    strategy: str = Query("popular", description="Cold start strategy: popular, trending, or diverse"),
    n_recommendations: int = Query(10, ge=1, le=50, description="Number of recommendations")
):
    """
    Get cold start recommendations for new users or users with insufficient data.
    
    This endpoint provides recommendations for users who are new to the system
    or have insufficient rating history using various cold start strategies.
    """
    try:
        logger.info(f"Generating cold start recommendations for user {user_id} with strategy {strategy}")
        
        # Use unified recommender with cold start strategy
        result = recommender.get_recommendations(
            user_id=user_id,
            strategy='cold_start',
            n_recommendations=n_recommendations,
            cold_start_strategy=strategy
        )
        
        logger.info(f"Successfully generated {result['n_recommendations']} cold start recommendations")
        return result
        
    except Exception as e:
        logger.error(f"Error generating cold start recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating cold start recommendations: {str(e)}")


@application_instance.get("/movies/new")
def get_new_movies(
    years_back: int = Query(5, ge=1, le=20, description="How many years back to look for new movies"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of movies to return")
):
    """
    Get recent/new movies for discovery and cold start scenarios.
    
    This endpoint returns movies from recent years that can be recommended
    to new users or for movie discovery purposes.
    """
    try:
        logger.info(f"Getting new movies from last {years_back} years")
        
        # Use unified recommender to get new movies
        result = recommender.get_new_movies(years_back=years_back, limit=limit)
        
        logger.info(f"Successfully retrieved {result['n_movies']} new movies")
        return result
        
    except Exception as e:
        logger.error(f"Error getting new movies: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting new movies: {str(e)}")


@application_instance.get("/recommend/for-new-movie/{movie_id}")
def get_recommendations_for_new_movie(
    movie_id: int = Path(..., description="Movie ID for content-based recommendations"),
    n_recommendations: int = Query(10, ge=1, le=50, description="Number of recommendations")
):
    """
    Get content-based recommendations for new movies with limited rating data.
    
    This endpoint provides recommendations for movies that are new to the system
    and have insufficient collaborative filtering data.
    """
    try:
        logger.info(f"Generating recommendations for new movie {movie_id}")
        
        # Use unified recommender for movie-to-movie recommendations
        result = recommender.get_movie_recommendations(
            movie_id=movie_id,
            n_recommendations=n_recommendations,
            strategy='item_similarity'
        )
        
        logger.info(f"Successfully generated {result['n_recommendations']} recommendations for new movie")
        return result
        
    except Exception as e:
        logger.error(f"Error generating recommendations for new movie: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating recommendations for new movie: {str(e)}")


# Export the app instance for uvicorn and other ASGI servers
app = application_instance