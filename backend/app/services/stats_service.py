"""
Statistics service for OCT B-Scan Labeler.
Provides global and aggregated statistics across all scans.
"""

from sqlalchemy import select, func
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

        # Count by label type
        # Label encoding: 0=unlabeled, 1=healthy, 2=unhealthy
        label_counts_result = await db.execute(
            select(BScan.label, func.count(BScan.id)).group_by(BScan.label)
        )
        label_counts = {label: count for label, count in label_counts_result.all()}

        # Extract counts
        unlabeled_count = label_counts.get(0, 0)
        healthy_count = label_counts.get(1, 0)
        unhealthy_count = label_counts.get(2, 0)

        # Labeled = healthy + unhealthy (remember: viewed = labeled)
        labeled_count = healthy_count + unhealthy_count

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
                func.sum(func.cast(BScan.label != 0, db.bind.dialect.type_descriptor(int))).label("labeled_count"),
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


# Global stats service instance
stats_service = StatsService()
