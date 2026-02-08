"""
Scan management service for OCT B-Scan Labeler.
Handles listing scans with progress statistics.
"""

from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Scan, BScan
from app.db.schemas import ScanResponse, ScanStats


class ScanService:
    """Service for managing OCT scans."""

    @staticmethod
    async def list_scans(db: AsyncSession) -> List[ScanResponse]:
        """
        List all scans with embedded progress statistics.

        Args:
            db: Database session

        Returns:
            List of scans with their statistics
        """
        # Query all scans
        result = await db.execute(select(Scan).order_by(Scan.created_at.desc()))
        scans = result.scalars().all()

        # Build response with stats for each scan
        scan_responses = []
        for scan in scans:
            stats = await ScanService.get_scan_stats(db, scan.scan_id)
            scan_responses.append(
                ScanResponse(
                    scan_id=scan.scan_id,
                    created_at=scan.created_at,
                    updated_at=scan.updated_at,
                    stats=stats,
                )
            )

        return scan_responses

    @staticmethod
    async def get_scan_by_id(db: AsyncSession, scan_id: str) -> Optional[Scan]:
        """
        Get a scan by its ID.

        Args:
            db: Database session
            scan_id: Scan identifier

        Returns:
            Scan model instance or None if not found
        """
        result = await db.execute(select(Scan).where(Scan.scan_id == scan_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_scan_stats(db: AsyncSession, scan_id: str) -> ScanStats:
        """
        Calculate statistics for a specific scan.

        Statistics include:
        - Total number of B-scans
        - Number of labeled B-scans (healthy + unhealthy)
        - Number of healthy labels
        - Number of unhealthy labels
        - Number of unlabeled B-scans

        Args:
            db: Database session
            scan_id: Scan identifier

        Returns:
            ScanStats with calculated metrics
        """
        # Count total B-scans
        total_result = await db.execute(
            select(func.count(BScan.id)).where(BScan.scan_id == scan_id)
        )
        total_bscans = total_result.scalar() or 0

        # Count by label type
        # Label encoding: 0=unlabeled, 1=healthy, 2=unhealthy
        label_counts_result = await db.execute(
            select(BScan.label, func.count(BScan.id))
            .where(BScan.scan_id == scan_id)
            .group_by(BScan.label)
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

        return ScanStats(
            total_bscans=total_bscans,
            labeled_bscans=labeled_count,
            healthy_count=healthy_count,
            unhealthy_count=unhealthy_count,
            unlabeled_count=unlabeled_count,
            completion_percentage=round(completion_percentage, 2),
        )

    @staticmethod
    async def create_scan(db: AsyncSession, scan_id: str) -> Scan:
        """
        Create a new scan record.

        Args:
            db: Database session
            scan_id: Unique scan identifier

        Returns:
            Created Scan instance

        Raises:
            ValueError: If scan_id already exists
        """
        # Check if scan already exists
        existing = await ScanService.get_scan_by_id(db, scan_id)
        if existing:
            raise ValueError(f"Scan with ID '{scan_id}' already exists")

        # Create new scan
        scan = Scan(scan_id=scan_id)
        db.add(scan)
        await db.flush()
        await db.refresh(scan)

        return scan

    @staticmethod
    async def delete_scan(db: AsyncSession, scan_id: str) -> bool:
        """
        Delete a scan and all associated B-scans.

        Args:
            db: Database session
            scan_id: Scan identifier

        Returns:
            True if scan was deleted, False if not found
        """
        scan = await ScanService.get_scan_by_id(db, scan_id)
        if not scan:
            return False

        await db.delete(scan)
        await db.flush()

        return True


# Global scan service instance
scan_service = ScanService()
