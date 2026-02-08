"""
FastAPI main application for OCT B-Scan Labeler.
Configures CORS, routers, and application lifecycle.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db.database import init_db, dispose_engine
from app.api.v1 import scans, bscans, stats


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.
    Handles startup and shutdown events.
    """
    # Startup: Initialize database
    await init_db()
    print("✓ Database initialized")
    print(f"✓ Data directory: {settings.data_dir}")
    print(f"✓ Cache directory: {settings.cache_dir}")
    print(f"✓ Preview format: {settings.preview_format}")
    print(f"✓ Normalization: {settings.normalization_method}")

    yield

    # Shutdown: Dispose database engine
    await dispose_engine()
    print("✓ Database connection closed")


# Create FastAPI application
app = FastAPI(
    title="OCT B-Scan Labeler API",
    description="Backend API for rapid OCT B-scan labeling with keyboard-first navigation",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(scans.router, prefix="/api/v1")
app.include_router(bscans.router, prefix="/api/v1")
app.include_router(stats.router, prefix="/api/v1")


@app.get("/")
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "name": "OCT B-Scan Labeler API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.
    """
    return {
        "status": "healthy",
        "database": "ok",
        "cache_dir": str(settings.cache_dir),
        "data_dir": str(settings.data_dir),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
    )
