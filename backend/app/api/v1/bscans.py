"""
B-scans API router for OCT B-Scan Labeler.
Handles B-scan labeling operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models import User
from app.db.schemas import (
    BScanResponse,
    BScanLabelUpdate,
    BScanHealthUpdate,
    BScanPathologyUpdate,
)
from app.api.dependencies import get_current_user
from app.services.labeling_service import labeling_service
from app.services.bscan_service import bscan_service

router = APIRouter(prefix="/bscans", tags=["bscans"])


@router.post("/{bscan_id}/label", response_model=BScanResponse)
async def update_bscan_label(
    bscan_id: int,
    label_update: BScanLabelUpdate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
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


@router.post("/{bscan_id}/health", response_model=BScanResponse)
async def update_bscan_health(
    bscan_id: int,
    health_update: BScanHealthUpdate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """Update health status: 1=healthy, 0=not healthy."""
    try:
        updated_bscan = await labeling_service.update_health(
            db, bscan_id, health_update.healthy
        )

        response = await bscan_service.build_bscan_response(
            db, updated_bscan, include_preview_url=True
        )
        return response
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.delete("/{bscan_id}/label", response_model=BScanResponse)
async def clear_bscan_label(
    bscan_id: int,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """
    Clear all label fields of a B-scan (set to unlabeled).

    Args:
        bscan_id: B-scan database ID

    Returns:
        Updated B-scan metadata

    Raises:
        404: If B-scan not found
    """
    try:
        # Clear all labeling markers and health values.
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


@router.post("/{bscan_id}/pathology", response_model=BScanResponse)
async def update_bscan_pathology(
    bscan_id: int,
    pathology_update: BScanPathologyUpdate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """
    Update pathology markers for a B-scan.

    Health rule:
    - if any pathology marker is 1 -> healthy becomes 0 (not healthy)
    - otherwise health value is not auto-promoted to healthy
    """
    try:
        updated_bscan = await labeling_service.update_pathology(
            db,
            bscan_id,
            cyst=pathology_update.cyst,
            hard_exudate=pathology_update.hard_exudate,
            srf=pathology_update.srf,
            ped=pathology_update.ped,
        )

        response = await bscan_service.build_bscan_response(
            db, updated_bscan, include_preview_url=True
        )

        return response
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )
