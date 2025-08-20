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
@app.get("/recommend/hybrid/{user_id}", tags=["Recomendaciones"])
async def get_hybrid_recommendations(
    user_id: int,
    top_n: int = 10
):
    """
    Get hybrid recommendations for a user
    
    Combines collaborative filtering, item-to-item similarity, and content-based filtering
    
    Args:
        user_id (int): User ID to get recommendations for
        top_n (int): Number of recommendations to return (default: 10)
        
    Returns:
        Dict containing hybrid recommendations and metadata
    """
    global hybrid_service, recommendation_service
    
    if hybrid_service is None:
        raise HTTPException(status_code=503, detail="Hybrid service not available")
    
    if recommendation_service is None:
        raise HTTPException(status_code=503, detail="Recommendation service not available")
    
    try:
        # Step 1: Generate SVD Collaborative Filtering Candidates (20 movies)
        logger.info(f"Generating SVD candidates for user {user_id}")
        
        # Reuse existing SVD logic from collaborative endpoint
        svd_recommendations = recommendation_service.get_svd_recommendations(
            user_id=user_id, 
            n_recommendations=20,  # Generate 20 candidates as specified
            exclude_seen=True
        )
        
        # Extract movieId list from SVD predictions
        svd_movie_candidates = [rec['movieId'] for rec in svd_recommendations]
        
        logger.info(f"Generated {len(svd_movie_candidates)} SVD candidates: {svd_movie_candidates[:5]}...")
        
        # Step 2: Generate Item-to-Item Similarity Candidates (KNN)
        logger.info(f"Generating KNN similarity candidates for user {user_id}")
        
        # Step 2a: Get User's Positive Rating History (ratings > 4.0)
        user_ratings = data_loader.ratings[data_loader.ratings['userId'] == user_id]
        positive_ratings = user_ratings[user_ratings['rating'] > 4.0]
        positive_movie_ids = positive_ratings['movieId'].tolist()
        
        logger.info(f"Found {len(positive_movie_ids)} positive movies for user {user_id}")
        
        # Step 2b: Get Similar Movies for each positive movie (5 similar movies per positive movie)
        all_similar_movies = set()
        
        for movie_id in positive_movie_ids[:10]:  # Limit to first 10 to avoid too many API calls
            try:
                # Get movie title for the KNN method that expects movie title
                movie_info = data_loader.movies[data_loader.movies['movieId'] == movie_id]
                if not movie_info.empty:
                    movie_title = movie_info.iloc[0]['title']
                    
                    # Get 5 similar movies using KNN
                    similar_movies = recommendation_service.get_collaborative_recommendations(
                        movie_title=movie_title,
                        num_recommendations=5
                    )
                    
                    # Extract movieIds from similar movies (need to convert title back to movieId)
                    for sim_movie in similar_movies:
                        sim_title = sim_movie['title']
                        sim_movie_info = data_loader.movies[data_loader.movies['title'] == sim_title]
                        if not sim_movie_info.empty:
                            all_similar_movies.add(sim_movie_info.iloc[0]['movieId'])
                            
            except Exception as e:
                logger.warning(f"Could not get similar movies for movie_id {movie_id}: {e}")
                continue
        
        # Step 2c: Convert set to list and remove duplicates
        knn_movie_candidates = list(all_similar_movies)
        
        logger.info(f"Generated {len(knn_movie_candidates)} KNN candidates: {knn_movie_candidates[:5]}...")
        
        # Step 3: Combine and Weight Candidates
        logger.info(f"Combining and weighting candidates for user {user_id}")
        
        from collections import defaultdict
        
        # Initialize scoring dictionary
        scores = defaultdict(float)
        
        # Step 3a: Weight SVD candidates (base score = 1.0)
        for movie_id in svd_movie_candidates:
            scores[movie_id] = 1.0
        
        logger.info(f"Assigned base scores to {len(svd_movie_candidates)} SVD candidates")
        
        # Step 3b: Weight KNN candidates (increment score by 0.5)
        # This rewards movies suggested by both models
        for movie_id in knn_movie_candidates:
            scores[movie_id] += 0.5
            
        logger.info(f"Applied KNN weights to {len(knn_movie_candidates)} candidates")
        
        # Sort candidates by combined score (descending)
        sorted_candidates = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        # Extract top_n recommendations
        final_recommendations = []
        
        for movie_id, score in sorted_candidates[:top_n]:
            # Get movie information
            movie_info = data_loader.movies[data_loader.movies['movieId'] == movie_id]
            if not movie_info.empty:
                movie_title = movie_info.iloc[0]['title']
                
                # Determine source(s) of recommendation
                sources = []
                if movie_id in svd_movie_candidates:
                    sources.append("svd")
                if movie_id in knn_movie_candidates:
                    sources.append("knn")
                
                final_recommendations.append({
                    "movieId": int(movie_id),
                    "title": movie_title,
                    "hybrid_score": float(score),
                    "sources": sources,
                    "rank": len(final_recommendations) + 1
                })
        
        logger.info(f"Generated {len(final_recommendations)} final hybrid recommendations")
        
        # Return complete hybrid recommendation results
        return {
            "user_id": user_id,
            "top_n": top_n,
            "step": "candidate_weighting_and_ranking",
            "recommendations": final_recommendations,
            "total_recommendations": len(final_recommendations),
            "candidate_sources": {
                "svd_candidates": {
                    "count": len(svd_movie_candidates),
                    "weight": 1.0
                },
                "knn_candidates": {
                    "count": len(knn_movie_candidates),
                    "weight": 0.5
                }
            },
            "scoring_summary": {
                "total_unique_candidates": len(scores),
                "candidates_from_both_sources": len([m for m in scores if m in svd_movie_candidates and m in knn_movie_candidates]),
                "svd_only": len([m for m in scores if m in svd_movie_candidates and m not in knn_movie_candidates]),
                "knn_only": len([m for m in scores if m not in svd_movie_candidates and m in knn_movie_candidates])
            },
            "algorithm": "hybrid_recommendation_system_step3",
            "status": "candidate_weighting_completed"
        }
        
    except Exception as e:
        logger.error(f"Error generating hybrid recommendations for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")
        
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
