"""
FastAPI main application for OCT B-Scan Labeler.
Configures CORS, routers, and application lifecycle.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.config import settings
from app.db.database import init_db, dispose_engine, AsyncSessionLocal
from app.api.v1 import scans, bscans, stats, auth, users
from app.services.auth_service import auth_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.
    Handles startup and shutdown events.
    """
    # Startup: Initialize database
    await init_db()
    print("✓ Database initialized")

    # Seed default admin user
    async with AsyncSessionLocal() as session:
        await auth_service.ensure_default_admin(session)
        await session.commit()

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

# Global exception handlers
@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    """
    Handle Pydantic validation errors with detailed messages.
    """
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "message": "Data validation failed. Please check the request format.",
            "details": exc.errors(),
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Catch-all handler for unexpected exceptions.
    Prevents exposing stack traces to clients.
    """
    # Log the full exception (in production, use proper logging)
    import traceback
    print(f"❌ Unexpected error: {exc}")
    print(traceback.format_exc())

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": str(exc) if settings.debug else "An unexpected error occurred. Please try again or contact support.",
            "type": exc.__class__.__name__,
        },
    )


# Include API routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
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
