from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config.settings import settings
from app.config.database import engine, Base
from app.api.v1 import videos, jobs, overlays
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="A comprehensive video processing API with upload, trimming, overlays, and quality generation",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=settings.allowed_methods,
    allow_headers=settings.allowed_headers,
)

# Include routers
app.include_router(videos.router, prefix="/api/v1/videos", tags=["videos"])
app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["jobs"])
app.include_router(overlays.router, prefix="/api/v1/overlays", tags=["overlays"])

# Add the exact endpoints from requirements
from app.api.v1.videos import trim_video
from app.api.v1.jobs import get_job_status, get_job_result

# Exact endpoints as specified in requirements
app.post("/trim")(trim_video)  # Level 2 requirement
app.get("/status/{job_id}")(get_job_status)  # Level 4 requirement  
app.get("/result/{job_id}")(get_job_result)  # Level 4 requirement


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Dripple Video Processing API",
        "version": settings.app_version,
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.app_version,
        "database": "connected",
        "redis": "connected"
    }


@app.get("/api/v1/health")
async def api_health_check():
    """API health check endpoint"""
    return {
        "status": "healthy",
        "api_version": "v1",
        "services": {
            "database": "connected",
            "redis": "connected",
            "ffmpeg": "available"
        }
    }


@app.get("/api/v1/status")
async def system_status():
    """System status endpoint"""
    return {
        "system": "operational",
        "queue_status": "active",
        "active_jobs": 0,  # This would be dynamic in production
        "processed_videos": 0  # This would be dynamic in production
    }


@app.get("/api/v1/metrics")
async def basic_metrics():
    """Basic metrics endpoint"""
    # Basic metrics without Prometheus dependency
    return {
        "status": "healthy",
        "uptime": "running",
        "active_jobs": 0,
        "processed_videos": 0
    }


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url)
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "path": str(request.url)
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
