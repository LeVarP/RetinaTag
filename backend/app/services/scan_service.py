"""
Scan management service for OCT B-Scan Labeler.
Handles listing scans with progress statistics.
"""

from typing import List, Optional
from sqlalchemy import select, func, case
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
        result = await db.execute(
            select(
                func.count(BScan.id).label("total_bscans"),
                func.sum(case((BScan.is_labeled == 1, 1), else_=0)).label("labeled_count"),
                func.sum(case((BScan.healthy == 1, 1), else_=0)).label("healthy_count"),
                func.sum(case((BScan.healthy == 0, 1), else_=0)).label("not_healthy_count"),
                func.sum(case((BScan.healthy.is_(None), 1), else_=0)).label("not_necessary_healthy_count"),
                func.sum(case((BScan.cyst == 1, 1), else_=0)).label("cyst_positive"),
                func.sum(case((BScan.hard_exudate == 1, 1), else_=0)).label("hard_exudate_positive"),
                func.sum(case((BScan.srf == 1, 1), else_=0)).label("srf_positive"),
                func.sum(case((BScan.ped == 1, 1), else_=0)).label("ped_positive"),
                func.sum(case((BScan.cyst == 0, 1), else_=0)).label("cyst_negative"),
                func.sum(case((BScan.hard_exudate == 0, 1), else_=0)).label("hard_exudate_negative"),
                func.sum(case((BScan.srf == 0, 1), else_=0)).label("srf_negative"),
                func.sum(case((BScan.ped == 0, 1), else_=0)).label("ped_negative"),
            )
            .where(BScan.scan_id == scan_id)
        )
        row = result.one()
        total_bscans = row.total_bscans or 0
        labeled_count = row.labeled_count or 0
        healthy_count = row.healthy_count or 0
        unhealthy_count = row.not_healthy_count or 0
        not_necessary_healthy_count = row.not_necessary_healthy_count or 0
        cyst_positive = row.cyst_positive or 0
        hard_exudate_positive = row.hard_exudate_positive or 0
        srf_positive = row.srf_positive or 0
        ped_positive = row.ped_positive or 0
        cyst_negative = row.cyst_negative or 0
        hard_exudate_negative = row.hard_exudate_negative or 0
        srf_negative = row.srf_negative or 0
        ped_negative = row.ped_negative or 0
        unlabeled_count = max(total_bscans - labeled_count, 0)
        cyst_empty = max(total_bscans - cyst_positive - cyst_negative, 0)
        hard_exudate_empty = max(total_bscans - hard_exudate_positive - hard_exudate_negative, 0)
        srf_empty = max(total_bscans - srf_positive - srf_negative, 0)
        ped_empty = max(total_bscans - ped_positive - ped_negative, 0)

        # Calculate completion percentage
        completion_percentage = (
            (labeled_count / total_bscans * 100) if total_bscans > 0 else 0.0
        )

        return ScanStats(
            total_bscans=total_bscans,
            labeled=labeled_count,
            unlabeled=unlabeled_count,
            healthy=healthy_count,
            unhealthy=unhealthy_count,
            not_necessary_healthy=not_necessary_healthy_count,
            cyst_positive=cyst_positive,
            hard_exudate_positive=hard_exudate_positive,
            srf_positive=srf_positive,
            ped_positive=ped_positive,
            cyst_negative=cyst_negative,
            hard_exudate_negative=hard_exudate_negative,
            srf_negative=srf_negative,
            ped_negative=ped_negative,
            cyst_empty=cyst_empty,
            hard_exudate_empty=hard_exudate_empty,
            srf_empty=srf_empty,
            ped_empty=ped_empty,
            percent_complete=round(completion_percentage, 2),
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
