"""
FastAPI main application with hybrid recommendation system
"""

from fastapi import FastAPI, HTTPException, Request
from typing import List, Dict, Optional
import uvicorn
import logging
import time
import json
import pandas as pd
from datetime import datetime
from contextlib import asynccontextmanager

# Configure enhanced logging for production monitoring
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),  # Para docker logs
        logging.FileHandler("logs/api.log", encoding="utf-8"),  # Para persistencia
    ],
)
logger = logging.getLogger(__name__)

# Crear logger específico para métricas
metrics_logger = logging.getLogger("metrics")
metrics_logger.setLevel(logging.INFO)

# Handler para métricas en formato JSON (fácil parsing)
metrics_handler = logging.StreamHandler()
metrics_handler.setFormatter(logging.Formatter("%(message)s"))
metrics_logger.addHandler(metrics_handler)
metrics_logger.propagate = False

# Global variables to store loaded models and services
data_loader = None
recommendation_service = None
hybrid_service = None

# Global variables to store datasets
ratings_data = None
movies_data = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager to handle startup and shutdown events"""

    # Startup
    logger.info("🚀 Starting LatentLens API with Hybrid Recommendation System...")

    global data_loader, recommendation_service, hybrid_service, ratings_data, movies_data

    try:
        # Import modules
        from data_loader import DataLoader
        from recommendation_service import RecommendationService
        from hybrid_recommendation_service import HybridRecommendationService

        # Initialize data loader
        logger.info("📊 Loading data...")
        data_loader = DataLoader()

        # Load datasets into global variables
        logger.info("📊 Loading ratings and movies datasets...")
        ratings_data = data_loader.load_ratings()
        movies_data = data_loader.load_movies()
        logger.info(
            f"✅ Loaded {len(ratings_data)} ratings and {len(movies_data)} movies"
        )

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
    lifespan=lifespan,
)


# Middleware para logging y métricas
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware para logear todas las requests con métricas de tiempo"""

    start_time = time.time()

    # Información del request
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    request_id = f"{int(time.time())}-{hash(f'{client_ip}{user_agent}')}"

    # Log del inicio del request
    logger.info(
        f"🌐 [{request_id}] {request.method} {request.url} - Client: {client_ip}"
    )

    # Procesar request
    try:
        response = await call_next(request)
        processing_time = time.time() - start_time

        # Log del resultado
        logger.info(
            f"✅ [{request_id}] Response: {response.status_code} - Time: {processing_time:.3f}s"
        )

        # Metrics log en formato JSON para análisis
        metrics_data = {
            "timestamp": datetime.now().isoformat(),
            "request_id": request_id,
            "method": request.method,
            "path": str(request.url.path),
            "query_params": dict(request.query_params),
            "status_code": response.status_code,
            "processing_time_seconds": round(processing_time, 3),
            "client_ip": client_ip,
            "user_agent": user_agent[:100],  # Truncar para evitar logs muy largos
        }

        # Log de métricas en formato JSON
        metrics_logger.info(f"METRICS: {json.dumps(metrics_data)}")

        return response

    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(
            f"❌ [{request_id}] Error: {str(e)} - Time: {processing_time:.3f}s"
        )

        # Metrics log para errores
        error_metrics = {
            "timestamp": datetime.now().isoformat(),
            "request_id": request_id,
            "method": request.method,
            "path": str(request.url.path),
            "status_code": 500,
            "processing_time_seconds": round(processing_time, 3),
            "error": str(e),
            "client_ip": client_ip,
        }

        metrics_logger.error(f"ERROR_METRICS: {json.dumps(error_metrics)}")
        raise e


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

    services_ready = all(
        [
            data_loader is not None,
            recommendation_service is not None,
            hybrid_service is not None,
        ]
    )

    if services_ready:
        return {"status": "ready", "services": "all loaded"}
    else:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=503,
            detail={
                "status": "not ready",
                "data_loader": data_loader is not None,
                "recommendation_service": recommendation_service is not None,
                "hybrid_service": hybrid_service is not None,
            },
        )


# System status endpoint
@app.get("/system/status")
async def system_status():
    """Get system status and loaded components"""
    global data_loader, recommendation_service, hybrid_service, ratings_data, movies_data

    status = {
        "data_loader": data_loader is not None,
        "recommendation_service": recommendation_service is not None,
        "hybrid_service": hybrid_service is not None,
        "datasets_loaded": {
            "ratings_data": ratings_data is not None,
            "movies_data": movies_data is not None,
        },
        "services_ready": all(
            [
                data_loader is not None,
                recommendation_service is not None,
                hybrid_service is not None,
                ratings_data is not None,
                movies_data is not None,
            ]
        ),
    }

    if status["services_ready"]:
        # Add some basic stats
        try:
            if ratings_data is not None and movies_data is not None:
                status["data_stats"] = {
                    "num_users": len(ratings_data["userId"].unique()),
                    "num_movies": len(movies_data),
                    "num_ratings": len(ratings_data),
                }
            else:
                status["data_stats"] = {
                    "num_users": 0,
                    "num_movies": 0,
                    "num_ratings": 0,
                }
        except Exception as e:
            status["data_stats_error"] = str(e)

    return status


# Cold start handling functions
def _is_new_user(user_id: int) -> bool:
    """Check if user is new (has no ratings)"""
    global ratings_data
    if ratings_data is None:
        return True

    user_ratings = ratings_data[ratings_data["userId"] == user_id]
    return len(user_ratings) == 0


def _has_sufficient_ratings(user_id: int, min_ratings: int = 5) -> bool:
    """Check if user has sufficient ratings for collaborative filtering"""
    global ratings_data
    if ratings_data is None:
        return False

    user_ratings = ratings_data[ratings_data["userId"] == user_id]
    return len(user_ratings) >= min_ratings


def _get_popular_movies(top_n: int = 10) -> List[Dict]:
    """Get most popular movies (by number of ratings and average rating)"""
    global ratings_data, movies_data
    if ratings_data is None or movies_data is None:
        return []

    try:
        # Calculate movie popularity metrics
        movie_stats = (
            ratings_data.groupby("movieId").agg({"rating": ["count", "mean"]}).round(2)
        )

        movie_stats.columns = ["rating_count", "avg_rating"]
        movie_stats = movie_stats.reset_index()

        # Filter movies with at least 100 ratings and average rating >= 3.5
        popular_movies = movie_stats[
            (movie_stats["rating_count"] >= 100) & (movie_stats["avg_rating"] >= 3.5)
        ]

        # Create popularity score (combine count and rating)
        popular_movies["popularity_score"] = (
            popular_movies["rating_count"] * 0.3 + popular_movies["avg_rating"] * 0.7
        )

        # Sort by popularity score
        popular_movies = popular_movies.sort_values(
            **{"by": "popularity_score", "ascending": False}
        )

        # Get movie details
        result = []
        for _, movie in popular_movies.head(top_n).iterrows():
            movie_info = movies_data[movies_data["movieId"] == movie["movieId"]]
            if not movie_info.empty:
                result.append(
                    {
                        "movieId": int(movie["movieId"]),
                        "title": movie_info.iloc[0]["title"],
                        "popularity_score": float(movie["popularity_score"]),
                        "rating_count": int(movie["rating_count"]),
                        "avg_rating": float(movie["avg_rating"]),
                        "reason": "popular_movie",
                        "rank": len(result) + 1,
                    }
                )

        return result

    except Exception as e:
        logger.error(f"Error getting popular movies: {e}")
        return []


def _get_trending_movies(top_n: int = 10) -> List[Dict]:
    """Get trending movies (recent movies with good ratings)"""
    global ratings_data, movies_data
    if ratings_data is None or movies_data is None:
        return []

    try:
        # Get recent movies (from last 10 years in the dataset)
        import pandas as pd

        # Create a copy to avoid modifying original data
        movies_copy = movies_data.copy()

        # Extract year from title (assuming format "Title (YYYY)")
        movies_copy["year"] = movies_copy["title"].str.extract(r"\((\d{4})\)$")[0]
        movies_copy["year"] = pd.to_numeric(movies_copy["year"], errors="coerce")

        # Filter recent movies
        recent_threshold = movies_copy["year"].max() - 10  # Last 10 years
        recent_movies = movies_copy[movies_copy["year"] >= recent_threshold]

        # Get rating stats for recent movies
        recent_movie_ids = recent_movies["movieId"].tolist()
        recent_ratings = ratings_data[ratings_data["movieId"].isin(recent_movie_ids)]

        movie_stats = (
            recent_ratings.groupby("movieId")
            .agg({"rating": ["count", "mean"]})
            .round(2)
        )

        movie_stats.columns = ["rating_count", "avg_rating"]
        movie_stats = movie_stats.reset_index()

        # Filter trending movies (at least 20 ratings and avg rating >= 3.8)
        trending_movies = movie_stats[
            (movie_stats["rating_count"] >= 20) & (movie_stats["avg_rating"] >= 3.8)
        ]

        # Sort by average rating, then by count
        trending_movies = trending_movies.sort_values(
            **{"by": ["avg_rating", "rating_count"], "ascending": [False, False]}
        )

        # Get movie details
        result = []
        for _, movie in trending_movies.head(top_n).iterrows():
            movie_info = movies_data[movies_data["movieId"] == movie["movieId"]]
            if not movie_info.empty:
                result.append(
                    {
                        "movieId": int(movie["movieId"]),
                        "title": movie_info.iloc[0]["title"],
                        "rating_count": int(movie["rating_count"]),
                        "avg_rating": float(movie["avg_rating"]),
                        "reason": "trending_movie",
                        "rank": len(result) + 1,
                    }
                )

        return result

    except Exception as e:
        logger.error(f"Error getting trending movies: {e}")
        return []


def _get_diverse_genre_recommendations(top_n: int = 10) -> List[Dict]:
    """Get diverse recommendations across different genres"""
    global ratings_data, movies_data
    if ratings_data is None or movies_data is None:
        return []

    try:
        # Get top genres by movie count
        all_genres = []
        for genres_str in movies_data["genres"].dropna():
            genres = genres_str.split("|")
            all_genres.extend(genres)

        from collections import Counter

        genre_counts = Counter(all_genres)
        top_genres = [
            genre
            for genre, _ in genre_counts.most_common(8)
            if genre != "(no genres listed)"
        ]

        # Get best movie from each genre
        result = []
        movies_per_genre = max(1, top_n // len(top_genres))

        for genre in top_genres:
            # Find movies with this genre
            genre_movies = movies_data[
                movies_data["genres"].str.contains(genre, na=False)
            ]
            genre_movie_ids = genre_movies["movieId"].tolist()

            # Get rating stats for genre movies
            genre_ratings = ratings_data[ratings_data["movieId"].isin(genre_movie_ids)]

            if len(genre_ratings) > 0:
                movie_stats = (
                    genre_ratings.groupby("movieId")
                    .agg({"rating": ["count", "mean"]})
                    .round(2)
                )

                movie_stats.columns = ["rating_count", "avg_rating"]
                movie_stats = movie_stats.reset_index()

                # Filter and sort
                good_movies = movie_stats[
                    (movie_stats["rating_count"] >= 50)
                    & (movie_stats["avg_rating"] >= 3.5)
                ]

                good_movies = good_movies.sort_values(
                    **{"by": "avg_rating", "ascending": False}
                )

                # Add top movies from this genre
                for _, movie in good_movies.head(movies_per_genre).iterrows():
                    if len(result) >= top_n:
                        break

                    movie_info = movies_data[movies_data["movieId"] == movie["movieId"]]
                    if not movie_info.empty:
                        result.append(
                            {
                                "movieId": int(movie["movieId"]),
                                "title": movie_info.iloc[0]["title"],
                                "genre": genre,
                                "rating_count": int(movie["rating_count"]),
                                "avg_rating": float(movie["avg_rating"]),
                                "reason": f"top_in_genre_{genre.lower()}",
                                "rank": len(result) + 1,
                            }
                        )

            if len(result) >= top_n:
                break

        return result[:top_n]

    except Exception as e:
        logger.error(f"Error getting diverse genre recommendations: {e}")
        return []


# Hybrid recommendation endpoint
@app.get("/recommend/hybrid/{user_id}", tags=["Recomendaciones"])
async def get_hybrid_recommendations(user_id: int, top_n: int = 10):
    """
    Get hybrid recommendations for a user with cold start handling

    Combines collaborative filtering, item-to-item similarity, and content-based filtering.
    Handles cold start problem for new users and users with insufficient data.

    Args:
        user_id (int): User ID to get recommendations for
        top_n (int): Number of recommendations to return (default: 10)

    Returns:
        Dict containing hybrid recommendations and metadata
    """
    global hybrid_service, recommendation_service, ratings_data, movies_data

    # MONITORING: Log inicio de recomendación
    start_time = time.time()
    logger.info(
        f"🎯 Starting hybrid recommendation for user_id={user_id}, top_n={top_n}"
    )

    if hybrid_service is None:
        raise HTTPException(status_code=503, detail="Hybrid service not available")

    if recommendation_service is None:
        raise HTTPException(
            status_code=503, detail="Recommendation service not available"
        )

    if ratings_data is None or movies_data is None:
        raise HTTPException(status_code=503, detail="Data not available")

    try:
        # COLD START HANDLING: Check if user is new or has insufficient data
        is_new_user = _is_new_user(user_id)
        has_sufficient_data = _has_sufficient_ratings(user_id, min_ratings=5)

        logger.info(
            f"👤 User {user_id} analysis - New user: {is_new_user}, Sufficient data: {has_sufficient_data}"
        )

        # Handle Cold Start Problem
        if is_new_user:
            logger.info(f"Cold start: User {user_id} is completely new (no ratings)")

            # Strategy for new users: Popular + Trending + Diverse recommendations
            popular_movies = _get_popular_movies(top_n=max(4, top_n // 3))
            trending_movies = _get_trending_movies(top_n=max(3, top_n // 4))
            diverse_movies = _get_diverse_genre_recommendations(
                top_n=max(3, top_n // 3)
            )

            # Combine and deduplicate
            seen_movie_ids = set()
            cold_start_recommendations = []

            # Add popular movies first
            for movie in popular_movies:
                if (
                    movie["movieId"] not in seen_movie_ids
                    and len(cold_start_recommendations) < top_n
                ):
                    seen_movie_ids.add(movie["movieId"])
                    movie["rank"] = len(cold_start_recommendations) + 1
                    cold_start_recommendations.append(movie)

            # Add trending movies
            for movie in trending_movies:
                if (
                    movie["movieId"] not in seen_movie_ids
                    and len(cold_start_recommendations) < top_n
                ):
                    seen_movie_ids.add(movie["movieId"])
                    movie["rank"] = len(cold_start_recommendations) + 1
                    cold_start_recommendations.append(movie)

            # Add diverse movies
            for movie in diverse_movies:
                if (
                    movie["movieId"] not in seen_movie_ids
                    and len(cold_start_recommendations) < top_n
                ):
                    seen_movie_ids.add(movie["movieId"])
                    movie["rank"] = len(cold_start_recommendations) + 1
                    cold_start_recommendations.append(movie)

            return {
                "user_id": user_id,
                "top_n": top_n,
                "cold_start_strategy": "new_user_popular_and_diverse",
                "recommendations": cold_start_recommendations[:top_n],
                "total_recommendations": len(cold_start_recommendations[:top_n]),
                "algorithm": "cold_start_handling",
                "status": "new_user_recommendations_provided",
                "strategy_breakdown": {
                    "popular_movies": len(
                        [
                            r
                            for r in cold_start_recommendations
                            if r["reason"] == "popular_movie"
                        ]
                    ),
                    "trending_movies": len(
                        [
                            r
                            for r in cold_start_recommendations
                            if r["reason"] == "trending_movie"
                        ]
                    ),
                    "diverse_genre_movies": len(
                        [
                            r
                            for r in cold_start_recommendations
                            if "top_in_genre" in r["reason"]
                        ]
                    ),
                },
            }

        elif not has_sufficient_data:
            logger.info(
                f"Cold start: User {user_id} has insufficient ratings for full collaborative filtering"
            )

            # Strategy for users with few ratings: Content-based + Popular movies
            user_ratings = ratings_data[ratings_data["userId"] == user_id]
            user_movies = user_ratings["movieId"].tolist()

            # Get genres from user's rated movies
            user_movie_info = movies_data[movies_data["movieId"].isin(user_movies)]
            user_genres = set()
            if not user_movie_info.empty:
                for _, movie_row in user_movie_info.iterrows():
                    genres_value = movie_row["genres"]
                    if (
                        genres_value is not None
                        and str(genres_value).strip() != ""
                        and str(genres_value) != "nan"
                    ):
                        user_genres.update(str(genres_value).split("|"))

            # Remove invalid genre
            user_genres.discard("(no genres listed)")

            # Get recommendations based on user's genre preferences
            genre_based_recommendations = []
            if user_genres:
                for genre in list(user_genres)[:3]:  # Top 3 user genres
                    genre_movies = _get_diverse_genre_recommendations(top_n=3)
                    genre_movies_filtered = [
                        m for m in genre_movies if genre.lower() in m["reason"]
                    ]
                    genre_based_recommendations.extend(genre_movies_filtered[:2])

            # Fill remaining slots with popular movies
            popular_movies = _get_popular_movies(top_n=top_n)

            # Combine and deduplicate
            seen_movie_ids = set(user_movies)  # Exclude already rated movies
            limited_data_recommendations = []

            # Add genre-based recommendations first
            for movie in genre_based_recommendations:
                if (
                    movie["movieId"] not in seen_movie_ids
                    and len(limited_data_recommendations) < top_n
                ):
                    seen_movie_ids.add(movie["movieId"])
                    movie["rank"] = len(limited_data_recommendations) + 1
                    limited_data_recommendations.append(movie)

            # Fill with popular movies
            for movie in popular_movies:
                if (
                    movie["movieId"] not in seen_movie_ids
                    and len(limited_data_recommendations) < top_n
                ):
                    seen_movie_ids.add(movie["movieId"])
                    movie["rank"] = len(limited_data_recommendations) + 1
                    limited_data_recommendations.append(movie)

            return {
                "user_id": user_id,
                "top_n": top_n,
                "cold_start_strategy": "limited_data_content_and_popular",
                "user_rating_count": len(user_ratings),
                "user_preferred_genres": list(user_genres),
                "recommendations": limited_data_recommendations[:top_n],
                "total_recommendations": len(limited_data_recommendations[:top_n]),
                "algorithm": "cold_start_handling",
                "status": "limited_data_recommendations_provided",
            }

        # NORMAL HYBRID PROCESSING for users with sufficient data
        logger.info(f"Normal hybrid processing for user {user_id} with sufficient data")

        # Step 1: Generate SVD Collaborative Filtering Candidates (20 movies)
        logger.info(f"Generating SVD candidates for user {user_id}")

        # Reuse existing SVD logic from collaborative endpoint
        svd_recommendations = recommendation_service.get_svd_recommendations(
            user_id=user_id,
            n_recommendations=20,  # Generate 20 candidates as specified
            exclude_seen=True,
        )

        # Extract movieId list from SVD predictions
        svd_movie_candidates = [rec["movieId"] for rec in svd_recommendations]

        logger.info(
            f"Generated {len(svd_movie_candidates)} SVD candidates: {svd_movie_candidates[:5]}..."
        )

        # Step 2: Generate Item-to-Item Similarity Candidates (KNN)
        logger.info(f"Generating KNN similarity candidates for user {user_id}")

        # Step 2a: Get User's Positive Rating History (ratings > 4.0)
        user_ratings = ratings_data[ratings_data["userId"] == user_id]
        positive_ratings = user_ratings[user_ratings["rating"] > 4.0]
        positive_movie_ids = positive_ratings["movieId"].tolist()

        logger.info(
            f"Found {len(positive_movie_ids)} positive movies for user {user_id}"
        )

        # Step 2b: Get Similar Movies for each positive movie (5 similar movies per positive movie)
        all_similar_movies = set()

        for movie_id in positive_movie_ids[
            :10
        ]:  # Limit to first 10 to avoid too many API calls
            try:
                # Get movie title for the KNN method that expects movie title
                movie_info = movies_data[movies_data["movieId"] == movie_id]
                if not movie_info.empty:
                    movie_title = movie_info.iloc[0]["title"]

                    # Get 5 similar movies using KNN
                    similar_movies = (
                        recommendation_service.get_collaborative_recommendations(
                            movie_title=movie_title, num_recommendations=5
                        )
                    )

                    # Extract movieIds from similar movies (need to convert title back to movieId)
                    for sim_movie in similar_movies:
                        sim_title = sim_movie["title"]
                        sim_movie_info = movies_data[movies_data["title"] == sim_title]
                        if not sim_movie_info.empty:
                            all_similar_movies.add(sim_movie_info.iloc[0]["movieId"])

            except Exception as e:
                logger.warning(
                    f"Could not get similar movies for movie_id {movie_id}: {e}"
                )
                continue

        # Step 2c: Convert set to list and remove duplicates
        knn_movie_candidates = list(all_similar_movies)

        logger.info(
            f"Generated {len(knn_movie_candidates)} KNN candidates: {knn_movie_candidates[:5]}..."
        )

        # Step 3: Combine and Weight Candidates
        logger.info(f"Combining and weighting candidates for user {user_id}")

        from collections import defaultdict

        # Initialize scoring dictionary
        scores = defaultdict(float)

        # Step 3a: Weight SVD candidates (base score = 1.0)
        for movie_id in svd_movie_candidates:
            scores[movie_id] = 1.0

        logger.info(
            f"Assigned base scores to {len(svd_movie_candidates)} SVD candidates"
        )

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
            movie_info = movies_data[movies_data["movieId"] == movie_id]
            if not movie_info.empty:
                movie_title = movie_info.iloc[0]["title"]

                # Determine source(s) of recommendation
                sources = []
                if movie_id in svd_movie_candidates:
                    sources.append("svd")
                if movie_id in knn_movie_candidates:
                    sources.append("knn")

                final_recommendations.append(
                    {
                        "movieId": int(movie_id),
                        "title": movie_title,
                        "hybrid_score": float(score),
                        "sources": sources,
                        "rank": len(final_recommendations) + 1,
                    }
                )

        logger.info(
            f"Generated {len(final_recommendations)} final hybrid recommendations"
        )

        # Return complete hybrid recommendation results
        return {
            "user_id": user_id,
            "top_n": top_n,
            "step": "candidate_weighting_and_ranking",
            "recommendations": final_recommendations,
            "total_recommendations": len(final_recommendations),
            "candidate_sources": {
                "svd_candidates": {"count": len(svd_movie_candidates), "weight": 1.0},
                "knn_candidates": {"count": len(knn_movie_candidates), "weight": 0.5},
            },
            "scoring_summary": {
                "total_unique_candidates": len(scores),
                "candidates_from_both_sources": len(
                    [
                        m
                        for m in scores
                        if m in svd_movie_candidates and m in knn_movie_candidates
                    ]
                ),
                "svd_only": len(
                    [
                        m
                        for m in scores
                        if m in svd_movie_candidates and m not in knn_movie_candidates
                    ]
                ),
                "knn_only": len(
                    [
                        m
                        for m in scores
                        if m not in svd_movie_candidates and m in knn_movie_candidates
                    ]
                ),
            },
            "algorithm": "hybrid_recommendation_system_step3",
            "status": "candidate_weighting_completed",
        }

    except Exception as e:
        logger.error(f"Error generating hybrid recommendations for user {user_id}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error generating recommendations: {str(e)}"
        )


# Cold Start specific endpoints
@app.get("/recommend/cold-start/{user_id}", tags=["Cold Start"])
async def get_cold_start_recommendations(
    user_id: int, top_n: int = 10, strategy: str = "auto"
):
    """
    Get recommendations specifically designed for cold start scenarios

    Args:
        user_id (int): User ID to get recommendations for
        top_n (int): Number of recommendations to return (default: 10)
        strategy (str): Cold start strategy ("auto", "popular", "trending", "diverse")

    Returns:
        Dict containing cold start recommendations and metadata
    """
    global ratings_data, movies_data

    if ratings_data is None or movies_data is None:
        raise HTTPException(status_code=503, detail="Data not available")

    try:
        is_new_user = _is_new_user(user_id)
        has_sufficient_data = _has_sufficient_ratings(user_id, min_ratings=5)

        user_context = {
            "is_new_user": is_new_user,
            "has_sufficient_data": has_sufficient_data,
            "rating_count": 0,
        }

        if not is_new_user:
            user_ratings = ratings_data[ratings_data["userId"] == user_id]
            user_context["rating_count"] = len(user_ratings)

        if strategy == "auto":
            if is_new_user:
                strategy = "diverse"
            elif not has_sufficient_data:
                strategy = "popular"
            else:
                # User has enough data, redirect to hybrid
                return await get_hybrid_recommendations(user_id, top_n)

        recommendations = []
        strategy_used = strategy

        if strategy == "popular":
            recommendations = _get_popular_movies(top_n)
        elif strategy == "trending":
            recommendations = _get_trending_movies(top_n)
        elif strategy == "diverse":
            recommendations = _get_diverse_genre_recommendations(top_n)
        else:
            raise HTTPException(status_code=400, detail=f"Invalid strategy: {strategy}")

        return {
            "user_id": user_id,
            "top_n": top_n,
            "strategy_used": strategy_used,
            "user_context": user_context,
            "recommendations": recommendations,
            "total_recommendations": len(recommendations),
            "algorithm": "cold_start_specialized",
            "status": "cold_start_recommendations_provided",
        }

    except Exception as e:
        logger.error(
            f"Error generating cold start recommendations for user {user_id}: {e}"
        )
        raise HTTPException(
            status_code=500,
            detail=f"Error generating cold start recommendations: {str(e)}",
        )


@app.get("/movies/new", tags=["Movies"])
async def get_new_movies(limit: int = 20, min_year: Optional[int] = None):
    """
    Get new movies that might have limited ratings (addressing cold start for items)

    Args:
        limit (int): Maximum number of movies to return
        min_year (Optional[int]): Minimum year to consider (default: last 5 years)

    Returns:
        List of new movies with rating statistics
    """
    global ratings_data, movies_data

    if ratings_data is None or movies_data is None:
        raise HTTPException(status_code=503, detail="Data not available")

    try:
        import pandas as pd

        # Create a copy to avoid modifying original data
        movies_copy = movies_data.copy()

        # Extract year from title
        movies_copy["year"] = movies_copy["title"].str.extract(r"\((\d{4})\)$")[0]
        movies_copy["year"] = pd.to_numeric(movies_copy["year"], errors="coerce")

        # Set default minimum year to last 5 years
        if min_year is None:
            min_year = movies_copy["year"].max() - 5

        # Filter recent movies
        recent_movies = movies_copy[
            (movies_copy["year"] >= min_year) & (movies_copy["year"].notna())
        ]

        # Get rating statistics for these movies
        result = []
        for _, movie in recent_movies.iterrows():
            movie_id = movie["movieId"]
            movie_ratings = ratings_data[ratings_data["movieId"] == movie_id]

            movie_info = {
                "movieId": int(movie_id),
                "title": movie["title"],
                "year": (
                    int(movie["year"])
                    if (
                        movie["year"] is not None
                        and str(movie["year"]).strip() not in ["", "nan"]
                    )
                    else None
                ),
                "genres": movie["genres"],
                "rating_count": len(movie_ratings),
                "cold_start_level": (
                    "high"
                    if len(movie_ratings) < 10
                    else "medium" if len(movie_ratings) < 50 else "low"
                ),
            }

            if len(movie_ratings) > 0:
                movie_info.update(
                    {
                        "avg_rating": float(movie_ratings["rating"].mean()),
                        "rating_std": float(movie_ratings["rating"].std()),
                    }
                )
            else:
                movie_info.update(
                    {
                        "avg_rating": None,
                        "rating_std": None,
                        "cold_start_level": "extreme",
                    }
                )

            result.append(movie_info)

        # Sort by year (newest first) and then by rating count
        result.sort(key=lambda x: (x["year"] or 0, x["rating_count"]), reverse=True)

        return {
            "min_year": min_year,
            "total_new_movies": len(result),
            "movies": result[:limit],
            "cold_start_summary": {
                "extreme": len(
                    [m for m in result if m["cold_start_level"] == "extreme"]
                ),
                "high": len([m for m in result if m["cold_start_level"] == "high"]),
                "medium": len([m for m in result if m["cold_start_level"] == "medium"]),
                "low": len([m for m in result if m["cold_start_level"] == "low"]),
            },
        }

    except Exception as e:
        logger.error(f"Error getting new movies: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error retrieving new movies: {str(e)}"
        )


@app.get("/recommend/for-new-movie/{movie_id}", tags=["Cold Start"])
async def get_recommendations_for_new_movie(movie_id: int, top_n: int = 10):
    """
    Get similar movies for a new movie with limited ratings (content-based approach)

    Args:
        movie_id (int): Movie ID to find similar movies for
        top_n (int): Number of similar movies to return

    Returns:
        Dict containing similar movies based on content
    """
    global ratings_data, movies_data

    if ratings_data is None or movies_data is None:
        raise HTTPException(status_code=503, detail="Data not available")

    try:
        import pandas as pd

        # Get target movie info
        target_movie = movies_data[movies_data["movieId"] == movie_id]
        if target_movie.empty:
            raise HTTPException(status_code=404, detail=f"Movie {movie_id} not found")

        target_movie = target_movie.iloc[0]
        target_genres = (
            set(target_movie["genres"].split("|"))
            if pd.notna(target_movie["genres"])
            else set()
        )

        # Get rating count for target movie
        target_ratings = ratings_data[ratings_data["movieId"] == movie_id]
        target_rating_count = len(target_ratings)
        target_avg_rating = (
            target_ratings["rating"].mean() if len(target_ratings) > 0 else None
        )

        # Find similar movies based on genres
        similar_movies = []

        for _, movie in movies_data.iterrows():
            if movie["movieId"] == movie_id:
                continue

            movie_genres = (
                set(str(movie["genres"]).split("|"))
                if (
                    movie["genres"] is not None
                    and str(movie["genres"]).strip() not in ["", "nan"]
                )
                else set()
            )

            # Calculate genre similarity (Jaccard similarity)
            if target_genres and movie_genres:
                intersection = len(target_genres.intersection(movie_genres))
                union = len(target_genres.union(movie_genres))
                genre_similarity = intersection / union if union > 0 else 0
            else:
                genre_similarity = 0

            # Only consider movies with at least some genre overlap
            if genre_similarity > 0:
                # Get rating stats for this movie
                movie_ratings = ratings_data[
                    ratings_data["movieId"] == movie["movieId"]
                ]

                similar_movies.append(
                    {
                        "movieId": int(movie["movieId"]),
                        "title": movie["title"],
                        "genres": movie["genres"],
                        "genre_similarity": float(genre_similarity),
                        "shared_genres": list(target_genres.intersection(movie_genres)),
                        "rating_count": len(movie_ratings),
                        "avg_rating": (
                            float(movie_ratings["rating"].mean())
                            if len(movie_ratings) > 0
                            else None
                        ),
                    }
                )

        # Sort by genre similarity and rating quality
        similar_movies.sort(
            key=lambda x: (x["genre_similarity"], x["avg_rating"] or 0), reverse=True
        )

        # Add rank
        for i, movie in enumerate(similar_movies[:top_n]):
            movie["rank"] = i + 1

        return {
            "target_movie": {
                "movieId": int(movie_id),
                "title": target_movie["title"],
                "genres": target_movie["genres"],
                "rating_count": int(target_rating_count),
                "avg_rating": (
                    float(target_avg_rating) if target_avg_rating is not None else None
                ),
                "cold_start_level": (
                    "high"
                    if target_rating_count < 10
                    else "medium" if target_rating_count < 50 else "low"
                ),
            },
            "similar_movies": similar_movies[:top_n],
            "total_similar_movies": len(similar_movies),
            "algorithm": "content_based_similarity",
            "similarity_method": "genre_jaccard",
            "status": "content_based_recommendations_for_new_movie",
        }

    except Exception as e:
        logger.error(f"Error getting recommendations for new movie {movie_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating recommendations for new movie: {str(e)}",
        )


# Individual algorithm endpoints (for comparison)
@app.get("/recommend/collaborative/{user_id}")
async def get_collaborative_recommendations(user_id: int, n_recommendations: int = 10):
    """Get recommendations using collaborative filtering only"""
    global recommendation_service

    if recommendation_service is None:
        raise HTTPException(
            status_code=503, detail="Recommendation service not available"
        )

    try:
        recommendations = recommendation_service.get_svd_recommendations(
            user_id, n_recommendations
        )
        return {
            "user_id": user_id,
            "algorithm": "collaborative_filtering_svd",
            "recommendations": recommendations,
            "total_recommendations": len(recommendations),
        }
    except Exception as e:
        logger.error(
            f"Error generating collaborative recommendations for user {user_id}: {e}"
        )
        raise HTTPException(
            status_code=500, detail=f"Error generating recommendations: {str(e)}"
        )


@app.get("/recommend/item-similarity/{user_id}")
async def get_item_similarity_recommendations(
    user_id: int, n_recommendations: int = 10
):
    """Get recommendations using item-to-item similarity only"""
    global recommendation_service

    if recommendation_service is None:
        raise HTTPException(
            status_code=503, detail="Recommendation service not available"
        )

    try:
        # Use collaborative recommendations instead since get_knn_item_recommendations doesn't exist
        # Get user's top rated movies first
        if ratings_data is None or movies_data is None:
            raise HTTPException(status_code=503, detail="Data not available")

        user_ratings = ratings_data[ratings_data["userId"] == user_id]
        if user_ratings.empty:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")

        # Get highest rated movie by user
        max_rating_idx = user_ratings["rating"].argmax()
        top_movie = user_ratings.iloc[max_rating_idx]
        top_movie_info = movies_data[movies_data["movieId"] == top_movie["movieId"]]

        if top_movie_info.empty:
            raise HTTPException(status_code=404, detail="Movie information not found")

        movie_title = top_movie_info.iloc[0]["title"]

        recommendations = recommendation_service.get_collaborative_recommendations(
            movie_title, n_recommendations
        )
        return {
            "user_id": user_id,
            "algorithm": "item_to_item_similarity",
            "recommendations": recommendations,
            "total_recommendations": len(recommendations),
        }
    except Exception as e:
        logger.error(
            f"Error generating item similarity recommendations for user {user_id}: {e}"
        )
        raise HTTPException(
            status_code=500, detail=f"Error generating recommendations: {str(e)}"
        )


@app.get("/recommend/content-based/{user_id}")
async def get_content_based_recommendations(user_id: int, n_recommendations: int = 10):
    """Get recommendations using content-based filtering only"""
    global recommendation_service

    if recommendation_service is None:
        raise HTTPException(
            status_code=503, detail="Recommendation service not available"
        )

    try:
        # Since get_content_based_recommendations doesn't exist, use genre-based recommendations
        if ratings_data is None or movies_data is None:
            raise HTTPException(status_code=503, detail="Data not available")

        user_ratings = ratings_data[ratings_data["userId"] == user_id]
        if user_ratings.empty:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")

        # Get user's favorite genres from their rated movies
        user_movies = user_ratings["movieId"].tolist()
        user_movie_info = movies_data[movies_data["movieId"].isin(user_movies)]

        # Extract genres
        user_genres = set()
        if not user_movie_info.empty:
            for _, movie_row in user_movie_info.iterrows():
                genres_value = movie_row["genres"]
                if (
                    genres_value is not None
                    and str(genres_value).strip() != ""
                    and str(genres_value) != "nan"
                ):
                    user_genres.update(str(genres_value).split("|"))

        # Get diverse recommendations based on user's preferred genres
        recommendations = _get_diverse_genre_recommendations(n_recommendations)
        return {
            "user_id": user_id,
            "algorithm": "content_based_filtering",
            "recommendations": recommendations,
            "total_recommendations": len(recommendations),
        }
    except Exception as e:
        logger.error(
            f"Error generating content-based recommendations for user {user_id}: {e}"
        )
        raise HTTPException(
            status_code=500, detail=f"Error generating recommendations: {str(e)}"
        )


# Movie information endpoint
@app.get("/movies/{movie_id}")
async def get_movie_info(movie_id: int):
    """Get information about a specific movie"""
    global ratings_data, movies_data

    if ratings_data is None or movies_data is None:
        raise HTTPException(status_code=503, detail="Data not available")

    try:
        # Get movie information
        movie_info = movies_data[movies_data["movieId"] == movie_id]
        if movie_info.empty:
            raise HTTPException(status_code=404, detail=f"Movie {movie_id} not found")

        movie = movie_info.iloc[0]

        # Get rating statistics
        movie_ratings = ratings_data[ratings_data["movieId"] == movie_id]

        result = {
            "movieId": int(movie["movieId"]),
            "title": movie["title"],
            "genres": movie["genres"],
            "rating_count": len(movie_ratings),
        }

        if len(movie_ratings) > 0:
            result.update(
                {
                    "avg_rating": float(movie_ratings["rating"].mean()),
                    "rating_std": float(movie_ratings["rating"].std()),
                    "favorite_genres": (
                        movie["genres"].split("|") if movie["genres"] else []
                    ),
                }
            )
        else:
            result.update(
                {
                    "avg_rating": None,
                    "rating_std": None,
                    "favorite_genres": [],
                }
            )

        return result
    except Exception as e:
        logger.error(f"Error getting movie info for {movie_id}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error retrieving movie information: {str(e)}"
        )


# User stats endpoint
@app.get("/users/{user_id}/stats")
async def get_user_stats(user_id: int):
    """Get statistics about a user's rating history"""
    global ratings_data, movies_data

    if ratings_data is None or movies_data is None:
        raise HTTPException(status_code=503, detail="Data not available")

    try:
        user_ratings = ratings_data[ratings_data["userId"] == user_id]

        if len(user_ratings) == 0:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")

        # Get user's favorite genres
        user_movies = user_ratings["movieId"].tolist()
        user_movie_info = movies_data[movies_data["movieId"].isin(user_movies)]

        genre_counts = {}
        if not user_movie_info.empty:
            for _, movie_row in user_movie_info.iterrows():
                genres_value = movie_row["genres"]
                if (
                    genres_value is not None
                    and str(genres_value).strip() != ""
                    and str(genres_value) != "nan"
                ):
                    for genre in str(genres_value).split("|"):
                        if genre != "(no genres listed)":
                            genre_counts[genre] = genre_counts.get(genre, 0) + 1

        favorite_genres = sorted(
            genre_counts.items(), key=lambda x: x[1], reverse=True
        )[:5]
        favorite_genres = [genre for genre, count in favorite_genres]

        stats = {
            "user_id": user_id,
            "total_ratings": len(user_ratings),
            "average_rating": float(user_ratings["rating"].mean()),
            "rating_std": float(user_ratings["rating"].std()),
            "min_rating": float(user_ratings["rating"].min()),
            "max_rating": float(user_ratings["rating"].max()),
            "favorite_genres": favorite_genres,
        }

        return stats

    except Exception as e:
        logger.error(f"Error getting user stats for {user_id}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error retrieving user statistics: {str(e)}"
        )


# Basic recommendation endpoint (redirects to hybrid)
@app.get("/recommend/{user_id}")
async def get_recommendations(user_id: int, limit: int = 10):
    """Get recommendations for a user (uses hybrid algorithm)"""
    return await get_hybrid_recommendations(user_id, limit)


# Popular movies endpoint
@app.get("/movies/popular")
async def get_popular_movies(limit: int = 10):
    """Get popular movies based on ratings"""
    global ratings_data, movies_data

    if ratings_data is None or movies_data is None:
        raise HTTPException(status_code=503, detail="Data not available")

    try:
        popular_movies = _get_popular_movies(top_n=limit)
        return {
            "popular_movies": popular_movies,
            "total_movies": len(popular_movies),
            "algorithm": "popularity_based",
            "criteria": "rating_count_and_average",
        }
    except Exception as e:
        logger.error(f"Error getting popular movies: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error retrieving popular movies: {str(e)}"
        )


# Similar movies endpoint
@app.get("/movies/similar")
async def get_similar_movies(movie_title: Optional[str] = None, limit: int = 10):
    """Get movies similar to the provided movie title"""
    global ratings_data, movies_data, recommendation_service

    if movie_title is None:
        raise HTTPException(status_code=422, detail="movie_title parameter is required")

    if ratings_data is None or movies_data is None:
        raise HTTPException(status_code=503, detail="Data not available")

    if recommendation_service is None:
        raise HTTPException(
            status_code=503, detail="Recommendation service not available"
        )

    try:
        # Find movie by title
        matching_movies = movies_data[
            movies_data["title"].str.contains(movie_title, case=False, na=False)
        ]

        if matching_movies.empty:
            raise HTTPException(
                status_code=404, detail=f"Movie '{movie_title}' not found"
            )

        # Use the first match
        target_movie = matching_movies.iloc[0]
        movie_id = target_movie["movieId"]

        # Get similar movies using collaborative filtering
        similar_movies = recommendation_service.get_collaborative_recommendations(
            movie_title=movie_title, num_recommendations=limit
        )

        return {
            "target_movie": {
                "movieId": int(movie_id),
                "title": target_movie["title"],
                "genres": target_movie["genres"],
            },
            "similar_movies": similar_movies,
            "total_similar": len(similar_movies),
            "algorithm": "collaborative_filtering",
        }

    except Exception as e:
        logger.error(f"Error getting similar movies for '{movie_title}': {e}")
        raise HTTPException(
            status_code=500, detail=f"Error retrieving similar movies: {str(e)}"
        )


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
