"""
Statistics API router for OCT B-Scan Labeler.
Provides global statistics across all scans.
"""

import csv
from io import StringIO

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.db.models import User
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


@router.get("/export/bscans.csv")
async def export_bscans_csv(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """
    Export per-B-scan statistics as CSV.
    """
    rows = await stats_service.get_bscans_export_rows(db)

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "scan_id",
            "bscan_index",
            "bscan_key",
            "healthy",
            "is_labeled",
            "label",
            "cyst",
            "hard_exudate",
            "srf",
            "ped",
            "updated_at",
        ]
    )

    for row in rows:
        writer.writerow(
            [
                row["scan_id"],
                row["bscan_index"],
                row["bscan_key"] or "",
                "" if row["healthy"] is None else row["healthy"],
                row["is_labeled"],
                row["label"],
                "" if row["cyst"] is None else row["cyst"],
                "" if row["hard_exudate"] is None else row["hard_exudate"],
                "" if row["srf"] is None else row["srf"],
                "" if row["ped"] is None else row["ped"],
                row["updated_at"].isoformat() if row["updated_at"] else "",
            ]
        )

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=bscans_export.csv"},
    )
