"""
Labeling service for OCT B-Scan Labeler.
Handles updating and validating B-scan labels.
"""

from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import BScan
from app.services.bscan_service import BScanService


class LabelingService:
    """Service for managing B-scan labels."""

    @staticmethod
    def _has_pathology_flags(bscan: BScan) -> bool:
        return any(value == 1 for value in (bscan.cyst, bscan.hard_exudate, bscan.srf, bscan.ped))

    @staticmethod
    def _derive_is_labeled(bscan: BScan, db_mode: str = "original") -> int:
        if db_mode == "simple":
            return 1 if bscan.healthy in (-1, 1) else 0
        marker_values = (bscan.cyst, bscan.hard_exudate, bscan.srf, bscan.ped, bscan.healthy)
        return 1 if any(value in (0, 1) for value in marker_values) else 0

    @staticmethod
    def _derive_label(bscan: BScan, db_mode: str = "original") -> int:
        if bscan.healthy == 1:
            return 1
        if db_mode == "simple":
            return 2 if bscan.healthy == -1 else 0
        if bscan.healthy == 0:
            return 2
        return 0

    @staticmethod
    async def update_label(
        db: AsyncSession, bscan_id: int, new_label: int, db_mode: str = "original"
    ) -> BScan:
        """
        Update the label of a B-scan.

        Args:
            db: Database session
            bscan_id: B-scan database ID
            new_label: New label value (1=healthy, 2=unhealthy)
            db_mode: 'original' or 'simple'

        Returns:
            Updated BScan instance

        Raises:
            ValueError: If label is invalid or B-scan not found
        """
        # Backward-compatible endpoint: maps legacy label to healthy.
        if new_label not in (1, 2):
            raise ValueError(f"Invalid label: {new_label}. Must be 1 (healthy) or 2 (unhealthy)")

        # Get B-scan
        bscan = await BScanService.get_bscan_by_id(db, bscan_id)
        if not bscan:
            raise ValueError(f"B-scan with ID {bscan_id} not found")

        # In simple mode unhealthy maps to -1; in original mode it maps to 0.
        bscan.healthy = 1 if new_label == 1 else (-1 if db_mode == "simple" else 0)
        bscan.label = LabelingService._derive_label(bscan, db_mode)
        bscan.is_labeled = LabelingService._derive_is_labeled(bscan, db_mode)
        bscan.updated_at = datetime.utcnow()

        await db.flush()
        await db.refresh(bscan)

        return bscan

    @staticmethod
    async def update_health(
        db: AsyncSession, bscan_id: int, healthy: int, db_mode: str = "original"
    ) -> BScan:
        """
        Update health status of a B-scan.

        Original mode: healthy must be 0 (not healthy) or 1 (healthy).
        Simple mode: healthy must be -1 (unhealthy) or 1 (healthy).
        """
        if db_mode == "simple":
            if healthy not in (-1, 1):
                raise ValueError("Healthy value must be -1 or 1 in simple mode")
        else:
            if healthy not in (0, 1):
                raise ValueError("Healthy value must be 0 or 1")

        bscan = await BScanService.get_bscan_by_id(db, bscan_id)
        if not bscan:
            raise ValueError(f"B-scan with ID {bscan_id} not found")

        bscan.healthy = healthy
        bscan.label = LabelingService._derive_label(bscan, db_mode)
        bscan.is_labeled = LabelingService._derive_is_labeled(bscan, db_mode)
        bscan.updated_at = datetime.utcnow()

        await db.flush()
        await db.refresh(bscan)

        return bscan

    @staticmethod
    async def clear_label(db: AsyncSession, bscan_id: int, db_mode: str = "original") -> BScan:
        """
        Clear all labeling fields of a B-scan (set to unlabeled).

        In original mode: healthy/pathology fields → null.
        In simple mode: healthy → 0 (not labeled); pathology fields → null.
        """
        # Get B-scan
        bscan = await BScanService.get_bscan_by_id(db, bscan_id)
        if not bscan:
            raise ValueError(f"B-scan with ID {bscan_id} not found")

        # In simple mode 0 means "not labeled"; in original mode None means the same.
        bscan.healthy = 0 if db_mode == "simple" else None
        bscan.cyst = None
        bscan.hard_exudate = None
        bscan.srf = None
        bscan.ped = None
        bscan.label = LabelingService._derive_label(bscan, db_mode)
        bscan.is_labeled = LabelingService._derive_is_labeled(bscan, db_mode)
        bscan.updated_at = datetime.utcnow()

        await db.flush()
        await db.refresh(bscan)

        return bscan

    @staticmethod
    async def bulk_update_labels(
        db: AsyncSession, label_updates: dict[int, int], db_mode: str = "original"
    ) -> list[BScan]:
        """
        Update labels for multiple B-scans in one transaction.

        Args:
            db: Database session
            label_updates: Dictionary mapping bscan_id -> new_label
            db_mode: 'original' or 'simple'

        Returns:
            List of updated BScan instances

        Raises:
            ValueError: If any label is invalid or B-scan not found
        """
        updated_bscans = []

        for bscan_id, new_label in label_updates.items():
            bscan = await LabelingService.update_label(db, bscan_id, new_label, db_mode=db_mode)
            updated_bscans.append(bscan)

        return updated_bscans

    @staticmethod
    async def update_pathology(
        db: AsyncSession,
        bscan_id: int,
        cyst: int | None = None,
        hard_exudate: int | None = None,
        srf: int | None = None,
        ped: int | None = None,
        db_mode: str = "original",
    ) -> BScan:
        """
        Update pathology markers and derive health/label state.

        Rule:
        - If any pathology marker is 1 => healthy is set to 0 (original) or -1 (simple)
        - Otherwise healthy is not auto-promoted to 1
        """
        bscan = await BScanService.get_bscan_by_id(db, bscan_id)
        if not bscan:
            raise ValueError(f"B-scan with ID {bscan_id} not found")

        if cyst is not None:
            bscan.cyst = cyst
        if hard_exudate is not None:
            bscan.hard_exudate = hard_exudate
        if srf is not None:
            bscan.srf = srf
        if ped is not None:
            bscan.ped = ped

        # Pathology-positive scans are not healthy by definition.
        if LabelingService._has_pathology_flags(bscan):
            bscan.healthy = -1 if db_mode == "simple" else 0

        bscan.label = LabelingService._derive_label(bscan, db_mode)
        bscan.is_labeled = LabelingService._derive_is_labeled(bscan, db_mode)
        bscan.updated_at = datetime.utcnow()

        await db.flush()
        await db.refresh(bscan)

        return bscan


# Global labeling service instance
labeling_service = LabelingService()
