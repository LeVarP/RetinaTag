"""
Scans API router for OCT B-Scan Labeler.
Handles scan listing, retrieval, and B-scan access.
"""

from pathlib import Path
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.schemas import ScanResponse, ScanStats, BScanResponse
from app.services.scan_service import scan_service
from app.services.bscan_service import bscan_service
from app.services.preview_service import preview_service

router = APIRouter(prefix="/scans", tags=["scans"])


@router.get("", response_model=List[ScanResponse])
async def list_scans(db: AsyncSession = Depends(get_db)):
    """
    List all scans with embedded progress statistics.

    Returns:
        List of scans with their statistics
    """
    scans = await scan_service.list_scans(db)
    return scans


@router.get("/{scan_id}/stats", response_model=ScanStats)
async def get_scan_stats(scan_id: str, db: AsyncSession = Depends(get_db)):
    """
    Get detailed statistics for a specific scan.

    Args:
        scan_id: Scan identifier

    Returns:
        Statistics for the scan

    Raises:
        404: If scan not found
    """
    # Verify scan exists
    scan = await scan_service.get_scan_by_id(db, scan_id)
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scan '{scan_id}' not found",
        )

    stats = await scan_service.get_scan_stats(db, scan_id)
    return stats


@router.get("/{scan_id}/bscans/{bscan_index}", response_model=BScanResponse)
async def get_bscan_by_index(
    scan_id: str, bscan_index: int, db: AsyncSession = Depends(get_db)
):
    """
    Get a B-scan by scan ID and index with navigation metadata.

    Args:
        scan_id: Scan identifier
        bscan_index: B-scan index within scan

    Returns:
        B-scan metadata with preview URL and navigation indexes

    Raises:
        404: If scan or B-scan not found
    """
    # Verify scan exists
    scan = await scan_service.get_scan_by_id(db, scan_id)
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scan '{scan_id}' not found",
        )

    # Get B-scan
    bscan = await bscan_service.get_bscan_by_index(db, scan_id, bscan_index)
    if not bscan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"B-scan with index {bscan_index} not found in scan '{scan_id}'",
        )

    # Build response with navigation metadata
    response = await bscan_service.build_bscan_response(db, bscan, include_preview_url=True)
    return response


@router.get("/{scan_id}/bscans/{bscan_index}/preview")
async def get_bscan_preview(
    scan_id: str, bscan_index: int, db: AsyncSession = Depends(get_db)
):
    """
    Get the preview image for a B-scan.

    Generates preview on-demand if not cached.
    Returns 8-bit WebP/PNG image with HTTP caching headers.

    Args:
        scan_id: Scan identifier
        bscan_index: B-scan index within scan

    Returns:
        FileResponse with preview image

    Raises:
        404: If scan or B-scan not found
        500: If preview generation fails
    """
    # Verify scan exists
    scan = await scan_service.get_scan_by_id(db, scan_id)
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scan '{scan_id}' not found",
        )

    # Get B-scan
    bscan = await bscan_service.get_bscan_by_index(db, scan_id, bscan_index)
    if not bscan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"B-scan with index {bscan_index} not found in scan '{scan_id}'",
        )

    # Get or generate preview
    try:
        source_path = Path(bscan.path)
        preview_path = preview_service.get_or_generate_preview(
            source_path=source_path,
            scan_id=scan_id,
            bscan_index=bscan_index,
        )

        # Determine media type based on format
        media_type_map = {
            "webp": "image/webp",
            "png": "image/png",
            "jpeg": "image/jpeg",
            "jpg": "image/jpeg",
        }
        media_type = media_type_map.get(
            preview_service.preview_format.lower(), "application/octet-stream"
        )

        # Return file with caching headers
        return FileResponse(
            path=preview_path,
            media_type=media_type,
            headers={
                "Cache-Control": "public, max-age=31536000",  # Cache for 1 year
                "ETag": f'"{scan_id}-{bscan_index}"',
            },
        )

    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source image not found: {e}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate preview: {e}",
        )
