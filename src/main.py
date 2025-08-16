
"""
LatentLens FastAPI Application

This module defines the main FastAPI application for the LatentLens movie 
recommendation system. It provides REST API endpoints for health checks 
and will include movie recommendation endpoints in future iterations.

Author: LatentLens Team
License: MIT
"""

from fastapi import FastAPI

# Application instance with comprehensive metadata for API documentation
application_instance = FastAPI(
    title="LatentLens Movie Recommendation API",
    description="A hybrid recommendation system for movies using collaborative filtering and popularity baselines.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


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


# Export the app instance for uvicorn and other ASGI servers
app = application_instance