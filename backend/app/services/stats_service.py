"""
Statistics service for OCT B-Scan Labeler.
Provides global and aggregated statistics across all scans.
"""

from sqlalchemy import select, func, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Scan, BScan
from app.db.schemas import GlobalStats


class StatsService:
    """Service for calculating global statistics."""

    @staticmethod
    async def get_global_stats(db: AsyncSession) -> GlobalStats:
        """
        Calculate global statistics across all scans.

        Statistics include:
        - Total number of scans
        - Total number of B-scans across all scans
        - Number of labeled B-scans (healthy + unhealthy)
        - Number of healthy labels
        - Number of unhealthy labels
        - Number of unlabeled B-scans
        - Overall completion percentage

        Args:
            db: Database session

        Returns:
            GlobalStats with calculated metrics
        """
        # Count total scans
        total_scans_result = await db.execute(select(func.count(Scan.scan_id)))
        total_scans = total_scans_result.scalar() or 0

        # Count total B-scans
        total_bscans_result = await db.execute(select(func.count(BScan.id)))
        total_bscans = total_bscans_result.scalar() or 0

        counts_result = await db.execute(
            select(
                func.sum(case((BScan.is_labeled == 1, 1), else_=0)).label("labeled_count"),
                func.sum(case((BScan.healthy == 1, 1), else_=0)).label("healthy_count"),
                func.sum(case((BScan.healthy == 0, 1), else_=0)).label("not_healthy_count"),
                func.sum(case((BScan.healthy.is_(None), 1), else_=0)).label("not_necessary_healthy_count"),
                func.sum(case((BScan.cyst == 1, 1), else_=0)).label("cyst_positive"),
                func.sum(case((BScan.hard_exudate == 1, 1), else_=0)).label("hard_exudate_positive"),
                func.sum(case((BScan.srf == 1, 1), else_=0)).label("srf_positive"),
                func.sum(case((BScan.ped == 1, 1), else_=0)).label("ped_positive"),
            )
        )
        counts = counts_result.one()
        labeled_count = counts.labeled_count or 0
        healthy_count = counts.healthy_count or 0
        unhealthy_count = counts.not_healthy_count or 0
        not_necessary_healthy_count = counts.not_necessary_healthy_count or 0
        cyst_positive = counts.cyst_positive or 0
        hard_exudate_positive = counts.hard_exudate_positive or 0
        srf_positive = counts.srf_positive or 0
        ped_positive = counts.ped_positive or 0
        unlabeled_count = max(total_bscans - labeled_count, 0)

        # Calculate completion percentage
        completion_percentage = (
            (labeled_count / total_bscans * 100) if total_bscans > 0 else 0.0
        )

        return GlobalStats(
            total_scans=total_scans,
            total_bscans=total_bscans,
            total_labeled=labeled_count,
            total_unlabeled=unlabeled_count,
            total_healthy=healthy_count,
            total_unhealthy=unhealthy_count,
            total_not_necessary_healthy=not_necessary_healthy_count,
            total_cyst_positive=cyst_positive,
            total_hard_exudate_positive=hard_exudate_positive,
            total_srf_positive=srf_positive,
            total_ped_positive=ped_positive,
            percent_complete=round(completion_percentage, 2),
        )

    @staticmethod
    async def get_scans_summary(db: AsyncSession) -> dict:
        """
        Get a summary of all scans with basic metrics.

        Args:
            db: Database session

        Returns:
            Dictionary with scan summaries
        """
        # Query scans with B-scan counts
        result = await db.execute(
            select(
                Scan.scan_id,
                Scan.created_at,
                Scan.updated_at,
                func.count(BScan.id).label("total_bscans"),
                func.sum(BScan.is_labeled).label("labeled_count"),
            )
            .outerjoin(BScan, Scan.scan_id == BScan.scan_id)
            .group_by(Scan.scan_id, Scan.created_at, Scan.updated_at)
            .order_by(Scan.created_at.desc())
        )

        scans_summary = []
        for row in result.all():
            scan_id, created_at, updated_at, total, labeled = row
            completion = (labeled / total * 100) if total > 0 else 0.0
            scans_summary.append({
                "scan_id": scan_id,
                "created_at": created_at,
                "updated_at": updated_at,
                "total_bscans": total or 0,
                "labeled_bscans": labeled or 0,
                "completion_percentage": round(completion, 2),
            })

        return {
            "total_scans": len(scans_summary),
            "scans": scans_summary,
        }

    @staticmethod
    async def get_bscans_export_rows(db: AsyncSession) -> list[dict]:
        """Get flattened B-scan rows for CSV export."""
        result = await db.execute(
            select(
                BScan.scan_id,
                BScan.bscan_index,
                BScan.bscan_key,
                BScan.healthy,
                BScan.is_labeled,
                BScan.label,
                BScan.cyst,
                BScan.hard_exudate,
                BScan.srf,
                BScan.ped,
                BScan.updated_at,
            )
            .order_by(BScan.scan_id.asc(), BScan.bscan_index.asc())
        )

        rows = []
        for row in result.all():
            rows.append(
                {
                    "scan_id": row.scan_id,
                    "bscan_index": row.bscan_index,
                    "bscan_key": row.bscan_key,
                    "healthy": row.healthy,
                    "is_labeled": row.is_labeled,
                    "label": row.label,
                    "cyst": row.cyst,
                    "hard_exudate": row.hard_exudate,
                    "srf": row.srf,
                    "ped": row.ped,
                    "updated_at": row.updated_at,
                }
            )

        return rows


# Global stats service instance
stats_service = StatsService()
