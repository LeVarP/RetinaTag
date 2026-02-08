"""
B-scan management service for OCT B-Scan Labeler.
Handles B-scan retrieval, navigation, and metadata.
"""

from typing import Optional
from pathlib import Path
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import BScan
from app.db.schemas import BScanResponse


class BScanService:
    """Service for managing individual B-scans."""

    @staticmethod
    async def get_bscan_by_id(db: AsyncSession, bscan_id: int) -> Optional[BScan]:
        """
        Get a B-scan by its database ID.

        Args:
            db: Database session
            bscan_id: B-scan database ID

        Returns:
            BScan model instance or None if not found
        """
        result = await db.execute(select(BScan).where(BScan.id == bscan_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_bscan_by_index(
        db: AsyncSession, scan_id: str, bscan_index: int
    ) -> Optional[BScan]:
        """
        Get a B-scan by scan ID and index.

        Args:
            db: Database session
            scan_id: Scan identifier
            bscan_index: B-scan index within scan

        Returns:
            BScan model instance or None if not found
        """
        result = await db.execute(
            select(BScan).where(
                BScan.scan_id == scan_id, BScan.bscan_index == bscan_index
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_next_bscan_index(
        db: AsyncSession, scan_id: str, current_index: int
    ) -> Optional[int]:
        """
        Get the index of the next B-scan (sequential navigation).

        Args:
            db: Database session
            scan_id: Scan identifier
            current_index: Current B-scan index

        Returns:
            Next B-scan index or None if at the end
        """
        result = await db.execute(
            select(BScan.bscan_index)
            .where(BScan.scan_id == scan_id, BScan.bscan_index > current_index)
            .order_by(BScan.bscan_index.asc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_prev_bscan_index(
        db: AsyncSession, scan_id: str, current_index: int
    ) -> Optional[int]:
        """
        Get the index of the previous B-scan (sequential navigation).

        Args:
            db: Database session
            scan_id: Scan identifier
            current_index: Current B-scan index

        Returns:
            Previous B-scan index or None if at the beginning
        """
        result = await db.execute(
            select(BScan.bscan_index)
            .where(BScan.scan_id == scan_id, BScan.bscan_index < current_index)
            .order_by(BScan.bscan_index.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_next_unlabeled_index(
        db: AsyncSession, scan_id: str, current_index: int
    ) -> Optional[int]:
        """
        Get the index of the next unlabeled B-scan.

        Args:
            db: Database session
            scan_id: Scan identifier
            current_index: Current B-scan index

        Returns:
            Next unlabeled B-scan index or None if all remaining are labeled
        """
        # Label 0 = unlabeled
        result = await db.execute(
            select(BScan.bscan_index)
            .where(
                BScan.scan_id == scan_id,
                BScan.bscan_index > current_index,
                BScan.label == 0,
            )
            .order_by(BScan.bscan_index.asc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def build_bscan_response(
        db: AsyncSession, bscan: BScan, include_preview_url: bool = True
    ) -> BScanResponse:
        """
        Build a BScanResponse with navigation metadata.

        Args:
            db: Database session
            bscan: BScan model instance
            include_preview_url: Whether to include preview URL

        Returns:
            BScanResponse with all metadata
        """
        # Get navigation indexes
        prev_index = await BScanService.get_prev_bscan_index(
            db, bscan.scan_id, bscan.bscan_index
        )
        next_index = await BScanService.get_next_bscan_index(
            db, bscan.scan_id, bscan.bscan_index
        )
        next_unlabeled = await BScanService.get_next_unlabeled_index(
            db, bscan.scan_id, bscan.bscan_index
        )

        # Build preview URL if requested
        preview_url = None
        if include_preview_url:
            preview_url = f"/api/v1/scans/{bscan.scan_id}/bscans/{bscan.bscan_index}/preview"

        return BScanResponse(
            id=bscan.id,
            scan_id=bscan.scan_id,
            bscan_index=bscan.bscan_index,
            path=bscan.path,
            label=bscan.label,
            updated_at=bscan.updated_at,
            preview_url=preview_url,
            prev_index=prev_index,
            next_index=next_index,
            next_unlabeled_index=next_unlabeled,
        )

    @staticmethod
    async def create_bscan(
        db: AsyncSession, scan_id: str, bscan_index: int, path: str
    ) -> BScan:
        """
        Create a new B-scan record.

        Args:
            db: Database session
            scan_id: Scan identifier
            bscan_index: B-scan index within scan
            path: File path to source image

        Returns:
            Created BScan instance

        Raises:
            ValueError: If B-scan with same scan_id/index already exists
        """
        # Check if B-scan already exists
        existing = await BScanService.get_bscan_by_index(db, scan_id, bscan_index)
        if existing:
            raise ValueError(
                f"B-scan with scan_id='{scan_id}' and index={bscan_index} already exists"
            )

        # Create new B-scan
        bscan = BScan(scan_id=scan_id, bscan_index=bscan_index, path=path, label=0)
        db.add(bscan)
        await db.flush()
        await db.refresh(bscan)

        return bscan

    @staticmethod
    async def get_total_bscans(db: AsyncSession, scan_id: str) -> int:
        """
        Get total number of B-scans in a scan.

        Args:
            db: Database session
            scan_id: Scan identifier

        Returns:
            Total count of B-scans
        """
        result = await db.execute(
            select(BScan).where(BScan.scan_id == scan_id)
        )
        return len(result.scalars().all())


# Global B-scan service instance
bscan_service = BScanService()
