"""
Database connection and session management for OCT B-Scan Labeler.
Configures SQLite with async support using aiosqlite.
"""

import os
from pathlib import Path
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.models import Base


# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite+aiosqlite:///./data/database/oct_labeler.db"
)

# Ensure database directory exists
db_path = DATABASE_URL.replace("sqlite+aiosqlite:///", "")
db_dir = Path(db_path).parent
db_dir.mkdir(parents=True, exist_ok=True)

# Create async engine
# StaticPool is used for SQLite to avoid threading issues
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL query logging
    connect_args={"check_same_thread": False},  # SQLite specific
    poolclass=StaticPool,  # Use StaticPool for SQLite
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def init_db() -> None:
    """
    Initialize database by creating all tables.
    Should be called on application startup.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting database session in FastAPI endpoints.

    Usage:
        @app.get("/items")
        async def read_items(db: AsyncSession = Depends(get_db)):
            # Use db session here
            ...

    Yields:
        AsyncSession: Database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def dispose_engine() -> None:
    """
    Dispose database engine.
    Should be called on application shutdown.
    """
    await engine.dispose()
