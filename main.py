"""
FastAPI main application with hybrid recommendation system
"""

from fastapi import FastAPI, HTTPException
from typing import List, Dict, Optional
import uvicorn
import logging
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables to store loaded models and services
data_loader = None
recommendation_service = None
hybrid_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager to handle startup and shutdown events"""
    
    # Startup
    logger.info("🚀 Starting LatentLens API with Hybrid Recommendation System...")
    
    global data_loader, recommendation_service, hybrid_service
    
    try:
        # Import modules
        from src.data_loader import DataLoader
        from src.recommendation_service import RecommendationService
        from src.hybrid_recommendation_service import HybridRecommendationService
        
        # Initialize data loader
        logger.info("📊 Loading data...")
        data_loader = DataLoader()
        
        # Initialize recommendation service
        logger.info("🤖 Initializing recommendation models...")
        recommendation_service = RecommendationService()
        recommendation_service.initialize()
        
        # Initialize hybrid service
        logger.info("🔄 Setting up hybrid recommendation system...")
        hybrid_service = HybridRecommendationService(data_path="data/ml-25m")
        hybrid_service.initialize()
        
        logger.info("✅ All services initialized successfully!")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize services: {e}")
        raise e
    
    yield
    
    # Shutdown
    logger.info("⏹️ Shutting down LatentLens API...")

# Create FastAPI app with lifespan
app = FastAPI(
    title="LatentLens - Hybrid Recommendation API",
    description="Advanced movie recommendation system combining multiple algorithms",
    version="2.0.0",
    lifespan=lifespan
)

# Health check endpoint (liveness)
@app.get("/health")
async def health_check():
    """Health check endpoint - always returns OK if server is running"""
    return {"status": "ok"}

# Readiness check endpoint
@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint - returns OK only when all services are loaded"""
    global data_loader, recommendation_service, hybrid_service
    
    services_ready = all([
        data_loader is not None,
        recommendation_service is not None,
        hybrid_service is not None
    ])
    
    if services_ready:
        return {
            "status": "ready",
            "services": "all loaded"
        }
    else:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=503, 
            detail={
                "status": "not ready",
                "data_loader": data_loader is not None,
                "recommendation_service": recommendation_service is not None,
                "hybrid_service": hybrid_service is not None
            }
        )

# System status endpoint
@app.get("/system/status")
async def system_status():
    """Get system status and loaded components"""
    global data_loader, recommendation_service, hybrid_service
    
    status = {
        "data_loader": data_loader is not None,
        "recommendation_service": recommendation_service is not None,
        "hybrid_service": hybrid_service is not None,
        "services_ready": all([
            data_loader is not None,
            recommendation_service is not None,
            hybrid_service is not None
        ])
    }
    
    if status["services_ready"]:
        # Add some basic stats
        try:
            status["data_stats"] = {
                "num_users": len(data_loader.ratings['userId'].unique()) if data_loader else 0,
                "num_movies": len(data_loader.movies) if data_loader else 0,
                "num_ratings": len(data_loader.ratings) if data_loader else 0
            }
        except Exception as e:
            status["data_stats_error"] = str(e)
    
    return status

# Hybrid recommendation endpoint
@app.get("/recommend/hybrid/{user_id}")
async def get_hybrid_recommendations(
    user_id: int,
    n_recommendations: int = 10
):
    """
    Get hybrid recommendations for a user
    
    Combines collaborative filtering, item-to-item similarity, and content-based filtering
    """
    global hybrid_service
    
    if hybrid_service is None:
        raise HTTPException(status_code=503, detail="Hybrid service not available")
    
    try:
        # Get recommendations
        recommendations = hybrid_service.get_hybrid_recommendations(
            user_id=user_id,
            n_recommendations=n_recommendations
        )
        
        return {
            "user_id": user_id,
            "recommendations": recommendations,
            "algorithm": "hybrid_recommendation_system",
            "total_recommendations": len(recommendations)
        }
        
    except Exception as e:
        logger.error(f"Error generating hybrid recommendations for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")

# Individual algorithm endpoints (for comparison)
@app.get("/recommend/collaborative/{user_id}")
async def get_collaborative_recommendations(user_id: int, n_recommendations: int = 10):
    """Get recommendations using collaborative filtering only"""
    global recommendation_service
    
    if recommendation_service is None:
        raise HTTPException(status_code=503, detail="Recommendation service not available")
    
    try:
        recommendations = recommendation_service.get_svd_recommendations(user_id, n_recommendations)
        return {
            "user_id": user_id,
            "algorithm": "collaborative_filtering_svd",
            "recommendations": recommendations,
            "total_recommendations": len(recommendations)
        }
    except Exception as e:
        logger.error(f"Error generating collaborative recommendations for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")

@app.get("/recommend/item-similarity/{user_id}")
async def get_item_similarity_recommendations(user_id: int, n_recommendations: int = 10):
    """Get recommendations using item-to-item similarity only"""
    global recommendation_service
    
    if recommendation_service is None:
        raise HTTPException(status_code=503, detail="Recommendation service not available")
    
    try:
        recommendations = recommendation_service.get_knn_item_recommendations(user_id, n_recommendations)
        return {
            "user_id": user_id,
            "algorithm": "item_to_item_similarity",
            "recommendations": recommendations,
            "total_recommendations": len(recommendations)
        }
    except Exception as e:
        logger.error(f"Error generating item similarity recommendations for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")

@app.get("/recommend/content-based/{user_id}")
async def get_content_based_recommendations(user_id: int, n_recommendations: int = 10):
    """Get recommendations using content-based filtering only"""
    global recommendation_service
    
    if recommendation_service is None:
        raise HTTPException(status_code=503, detail="Recommendation service not available")
    
    try:
        recommendations = recommendation_service.get_content_based_recommendations(user_id, n_recommendations)
        return {
            "user_id": user_id,
            "algorithm": "content_based_filtering",
            "recommendations": recommendations,
            "total_recommendations": len(recommendations)
        }
    except Exception as e:
        logger.error(f"Error generating content-based recommendations for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")

# Movie information endpoint
@app.get("/movies/{movie_id}")
async def get_movie_info(movie_id: int):
    """Get information about a specific movie"""
    global data_loader
    
    if data_loader is None:
        raise HTTPException(status_code=503, detail="Data loader not available")
    
    try:
        movie_info = data_loader.get_movie_info(movie_id)
        if movie_info is None:
            raise HTTPException(status_code=404, detail=f"Movie {movie_id} not found")
        return movie_info
    except Exception as e:
        logger.error(f"Error getting movie info for {movie_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving movie information: {str(e)}")

# User stats endpoint
@app.get("/users/{user_id}/stats")
async def get_user_stats(user_id: int):
    """Get statistics about a user's rating history"""
    global data_loader
    
    if data_loader is None:
        raise HTTPException(status_code=503, detail="Data loader not available")
    
    try:
        user_ratings = data_loader.ratings[data_loader.ratings['userId'] == user_id]
        
        if len(user_ratings) == 0:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")
        
        stats = {
            "user_id": user_id,
            "total_ratings": len(user_ratings),
            "average_rating": float(user_ratings['rating'].mean()),
            "rating_std": float(user_ratings['rating'].std()),
            "min_rating": float(user_ratings['rating'].min()),
            "max_rating": float(user_ratings['rating'].max()),
            "favorite_genres": data_loader.get_user_favorite_genres(user_id, top_n=5)
        }
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting user stats for {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving user statistics: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
