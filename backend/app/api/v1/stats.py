"""
Statistics API router for OCT B-Scan Labeler.
Provides global statistics across all scans.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.schemas import GlobalStats
from app.services.stats_service import stats_service

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("", response_model=GlobalStats)
async def get_global_stats(db: AsyncSession = Depends(get_db)):
    """
    Get global statistics across all scans.

    Returns:
        Global statistics including:
        - Total scans and B-scans
        - Label distribution (healthy, unhealthy, unlabeled)
        - Overall completion percentage
    """
    stats = await stats_service.get_global_stats(db)
    return stats


@router.get("/summary")
async def get_scans_summary(db: AsyncSession = Depends(get_db)):
    """
    Get a summary of all scans with basic metrics.

    Returns:
        Dictionary with scan summaries and counts
    """
    summary = await stats_service.get_scans_summary(db)
    return summary
