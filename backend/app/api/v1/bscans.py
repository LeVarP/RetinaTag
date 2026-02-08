"""
B-scans API router for OCT B-Scan Labeler.
Handles B-scan labeling operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.schemas import BScanResponse, BScanLabelUpdate
from app.services.labeling_service import labeling_service
from app.services.bscan_service import bscan_service

router = APIRouter(prefix="/bscans", tags=["bscans"])


@router.post("/{bscan_id}/label", response_model=BScanResponse)
async def update_bscan_label(
    bscan_id: int,
    label_update: BScanLabelUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Update the label of a B-scan.

    Args:
        bscan_id: B-scan database ID
        label_update: New label (1=healthy, 2=unhealthy)

    Returns:
        Updated B-scan metadata

    Raises:
        400: If label is invalid
        404: If B-scan not found
    """
    try:
        # Update label
        updated_bscan = await labeling_service.update_label(
            db, bscan_id, label_update.label
        )

        # Build response with navigation metadata
        response = await bscan_service.build_bscan_response(
            db, updated_bscan, include_preview_url=True
        )

        return response

    except ValueError as e:
        # Handle validation errors or not found
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
            )


@router.delete("/{bscan_id}/label", response_model=BScanResponse)
async def clear_bscan_label(
    bscan_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Clear the label of a B-scan (set to unlabeled).

    Args:
        bscan_id: B-scan database ID

    Returns:
        Updated B-scan metadata

    Raises:
        404: If B-scan not found
    """
    try:
        # Clear label (set to 0 = unlabeled)
        updated_bscan = await labeling_service.clear_label(db, bscan_id)

        # Build response with navigation metadata
        response = await bscan_service.build_bscan_response(
            db, updated_bscan, include_preview_url=True
        )

        return response

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )


@router.get("/{bscan_id}", response_model=BScanResponse)
async def get_bscan_by_id(
    bscan_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get a B-scan by its database ID.

    Args:
        bscan_id: B-scan database ID

    Returns:
        B-scan metadata with navigation info

    Raises:
        404: If B-scan not found
    """
    bscan = await bscan_service.get_bscan_by_id(db, bscan_id)
    if not bscan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"B-scan with ID {bscan_id} not found",
        )

    response = await bscan_service.build_bscan_response(
        db, bscan, include_preview_url=True
    )

    return response
