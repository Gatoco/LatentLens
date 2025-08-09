
# FastAPI framework import for API construction
from fastapi import FastAPI

# Application instance: central object for all API routes and configuration
app = FastAPI(
    title="LatentLens API",
    description="LatentLens movie recommendation system API.",
    version="0.1.0",
)

# Health check endpoint for service monitoring and deployment validation
@app.get("/health")
def health_check():
    """
    Health check endpoint. Returns status 'ok' if the API is running.
    Used for automated monitoring and deployment verification.
    """
    return {"status": "ok"}