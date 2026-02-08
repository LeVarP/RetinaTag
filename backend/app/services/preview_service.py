"""
Preview generation and caching service for OCT B-Scan Labeler.
Manages conversion of 16-bit images to 8-bit previews with disk caching.
"""

from pathlib import Path
from typing import Optional
import os
from datetime import datetime

from app.utils.image_processing import generate_preview, get_image_info
from app.config import settings


class PreviewService:
    """Service for managing B-scan preview generation and caching."""

    def __init__(self):
        """Initialize preview service with configuration."""
        self.cache_dir = settings.cache_dir / "previews"
        self.preview_format = settings.preview_format
        self.preview_quality = settings.preview_quality
        self.normalization_method = settings.normalization_method
        self.percentile_low = settings.percentile_low
        self.percentile_high = settings.percentile_high

        # Ensure cache directory exists
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get_preview_path(self, scan_id: str, bscan_index: int) -> Path:
        """
        Get the file path for a preview image.

        Args:
            scan_id: Scan identifier
            bscan_index: B-scan index within scan

        Returns:
            Path where preview is (or will be) stored
        """
        scan_cache_dir = self.cache_dir / scan_id
        scan_cache_dir.mkdir(parents=True, exist_ok=True)
        return scan_cache_dir / f"{bscan_index}.{self.preview_format}"

    def preview_exists(self, scan_id: str, bscan_index: int) -> bool:
        """
        Check if preview already exists in cache.

        Args:
            scan_id: Scan identifier
            bscan_index: B-scan index

        Returns:
            True if preview exists, False otherwise
        """
        preview_path = self.get_preview_path(scan_id, bscan_index)
        return preview_path.exists()

    def get_preview_metadata(self, scan_id: str, bscan_index: int) -> Optional[dict]:
        """
        Get metadata about a cached preview.

        Args:
            scan_id: Scan identifier
            bscan_index: B-scan index

        Returns:
            Dictionary with preview metadata, or None if preview doesn't exist
        """
        preview_path = self.get_preview_path(scan_id, bscan_index)
        if not preview_path.exists():
            return None

        stat = preview_path.stat()
        return {
            "path": str(preview_path),
            "size_bytes": stat.st_size,
            "modified_time": datetime.fromtimestamp(stat.st_mtime),
            "format": self.preview_format,
        }

    def generate_preview_for_bscan(
        self,
        source_path: Path,
        scan_id: str,
        bscan_index: int,
        force_regenerate: bool = False
    ) -> Path:
        """
        Generate preview for a B-scan, or return cached version.

        Args:
            source_path: Path to source 16-bit image
            scan_id: Scan identifier
            bscan_index: B-scan index
            force_regenerate: If True, regenerate even if cached version exists

        Returns:
            Path to preview image (cached or newly generated)

        Raises:
            FileNotFoundError: If source image doesn't exist
            ValueError: If image processing fails
        """
        preview_path = self.get_preview_path(scan_id, bscan_index)

        # Return cached version if it exists and force_regenerate is False
        if preview_path.exists() and not force_regenerate:
            return preview_path

        # Check if source exists
        if not source_path.exists():
            raise FileNotFoundError(f"Source image not found: {source_path}")

        # Generate preview
        norm_kwargs = {}
        if self.normalization_method == "percentile":
            norm_kwargs = {
                "low_percentile": self.percentile_low,
                "high_percentile": self.percentile_high,
            }

        generate_preview(
            source_path=source_path,
            output_path=preview_path,
            format=self.preview_format,
            quality=self.preview_quality,
            normalization_method=self.normalization_method,
            **norm_kwargs
        )

        return preview_path

    def get_or_generate_preview(
        self,
        source_path: Path,
        scan_id: str,
        bscan_index: int
    ) -> Path:
        """
        Get preview from cache or generate if not exists (convenience method).

        Args:
            source_path: Path to source 16-bit image
            scan_id: Scan identifier
            bscan_index: B-scan index

        Returns:
            Path to preview image

        Raises:
            FileNotFoundError: If source image doesn't exist
            ValueError: If image processing fails
        """
        return self.generate_preview_for_bscan(
            source_path=source_path,
            scan_id=scan_id,
            bscan_index=bscan_index,
            force_regenerate=False
        )

    def clear_cache_for_scan(self, scan_id: str) -> int:
        """
        Clear all cached previews for a specific scan.

        Args:
            scan_id: Scan identifier

        Returns:
            Number of preview files deleted
        """
        scan_cache_dir = self.cache_dir / scan_id
        if not scan_cache_dir.exists():
            return 0

        count = 0
        for preview_file in scan_cache_dir.glob(f"*.{self.preview_format}"):
            preview_file.unlink()
            count += 1

        # Remove empty directory
        if scan_cache_dir.exists() and not any(scan_cache_dir.iterdir()):
            scan_cache_dir.rmdir()

        return count

    def clear_all_cache(self) -> int:
        """
        Clear entire preview cache.

        Returns:
            Total number of preview files deleted
        """
        if not self.cache_dir.exists():
            return 0

        count = 0
        for scan_dir in self.cache_dir.iterdir():
            if scan_dir.is_dir():
                count += self.clear_cache_for_scan(scan_dir.name)

        return count

    def get_cache_stats(self) -> dict:
        """
        Get statistics about preview cache.

        Returns:
            Dictionary with cache statistics
        """
        if not self.cache_dir.exists():
            return {
                "total_scans": 0,
                "total_previews": 0,
                "total_size_bytes": 0,
                "total_size_mb": 0.0,
            }

        total_scans = 0
        total_previews = 0
        total_size = 0

        for scan_dir in self.cache_dir.iterdir():
            if scan_dir.is_dir():
                total_scans += 1
                for preview_file in scan_dir.glob(f"*.{self.preview_format}"):
                    total_previews += 1
                    total_size += preview_file.stat().st_size

        return {
            "total_scans": total_scans,
            "total_previews": total_previews,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
        }


# Global preview service instance
preview_service = PreviewService()
