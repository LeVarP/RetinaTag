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
    async def update_label(
        db: AsyncSession, bscan_id: int, new_label: int
    ) -> BScan:
        """
        Update the label of a B-scan.

        Args:
            db: Database session
            bscan_id: B-scan database ID
            new_label: New label value (1=healthy, 2=unhealthy)

        Returns:
            Updated BScan instance

        Raises:
            ValueError: If label is invalid or B-scan not found
        """
        # Validate label
        if new_label not in (1, 2):
            raise ValueError(f"Invalid label: {new_label}. Must be 1 (healthy) or 2 (unhealthy)")

        # Get B-scan
        bscan = await BScanService.get_bscan_by_id(db, bscan_id)
        if not bscan:
            raise ValueError(f"B-scan with ID {bscan_id} not found")

        # Update label and timestamp
        bscan.label = new_label
        bscan.updated_at = datetime.utcnow()

        await db.flush()
        await db.refresh(bscan)

        return bscan

    @staticmethod
    async def clear_label(db: AsyncSession, bscan_id: int) -> BScan:
        """
        Clear the label of a B-scan (set to unlabeled).

        Args:
            db: Database session
            bscan_id: B-scan database ID

        Returns:
            Updated BScan instance

        Raises:
            ValueError: If B-scan not found
        """
        # Get B-scan
        bscan = await BScanService.get_bscan_by_id(db, bscan_id)
        if not bscan:
            raise ValueError(f"B-scan with ID {bscan_id} not found")

        # Set to unlabeled (0)
        bscan.label = 0
        bscan.updated_at = datetime.utcnow()

        await db.flush()
        await db.refresh(bscan)

        return bscan

    @staticmethod
    async def bulk_update_labels(
        db: AsyncSession, label_updates: dict[int, int]
    ) -> list[BScan]:
        """
        Update labels for multiple B-scans in one transaction.

        Args:
            db: Database session
            label_updates: Dictionary mapping bscan_id -> new_label

        Returns:
            List of updated BScan instances

        Raises:
            ValueError: If any label is invalid or B-scan not found
        """
        updated_bscans = []

        for bscan_id, new_label in label_updates.items():
            bscan = await LabelingService.update_label(db, bscan_id, new_label)
            updated_bscans.append(bscan)

        return updated_bscans


# Global labeling service instance
labeling_service = LabelingService()
