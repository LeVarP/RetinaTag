#!/usr/bin/env python3
"""
Bulk import script for OCT-500 dataset.
Imports all scans from OCT-500 directory into the database.
Stores paths to original files instead of copying them.
"""

import argparse
import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.db.database import AsyncSessionLocal
from app.services.scan_service import scan_service
from app.services.bscan_service import bscan_service


async def import_single_scan(scan_id: str, source_dir: Path, file_pattern: str = "*.bmp",
                            path_prefix: str = None) -> dict:
    """
    Import a single scan from a directory.

    Args:
        scan_id: Unique identifier for the scan
        source_dir: Directory containing B-scan images
        file_pattern: Glob pattern for image files (default: *.bmp)

    Returns:
        Dictionary with import statistics
    """
    stats = {
        "scan_id": scan_id,
        "total_files": 0,
        "imported": 0,
        "skipped": 0,
        "errors": 0,
        "success": False
    }

    # Validate source directory
    if not source_dir.exists() or not source_dir.is_dir():
        print(f"  ❌ Error: Invalid directory: {source_dir}")
        return stats

    # Find all image files
    image_files = sorted(source_dir.glob(file_pattern))
    if not image_files:
        print(f"  ⚠️  No files matching '{file_pattern}' in {source_dir}")
        return stats

    stats["total_files"] = len(image_files)

    # Database session
    async with AsyncSessionLocal() as db:
        try:
            # Create scan record
            await scan_service.create_scan(db, scan_id)
        except ValueError:
            # Scan already exists, continue with B-scans
            pass

        # Import each B-scan
        for source_file in image_files:
            # Parse bscan index from filename (1.bmp = index 1, 2.bmp = index 2, etc.)
            try:
                bscan_index = int(source_file.stem)
            except ValueError:
                print(f"    Warning: Skipping file with non-numeric name: {source_file.name}")
                continue

            try:
                # Check if B-scan already exists
                existing = await bscan_service.get_bscan_by_index(db, scan_id, bscan_index)

                if existing:
                    stats["skipped"] += 1
                    continue

                # Create B-scan record with path to original file
                # Use path_prefix if provided (for Docker compatibility)
                file_path = str(source_file.absolute())
                if path_prefix:
                    file_path = file_path.replace(str(source_dir.parent.absolute()), path_prefix)

                await bscan_service.create_bscan(
                    db,
                    scan_id=scan_id,
                    bscan_index=bscan_index,
                    path=file_path,
                )

                stats["imported"] += 1

            except Exception as e:
                print(f"    Error importing {source_file.name}: {e}")
                stats["errors"] += 1
                continue

        # Commit after each scan to prevent data loss on errors
        try:
            await db.commit()
        except Exception as e:
            print(f"    Error committing scan {scan_id}: {e}")
            await db.rollback()
            stats["success"] = False
            return stats

    stats["success"] = stats["imported"] > 0 or stats["skipped"] > 0
    return stats


async def bulk_import_oct500(base_dir: Path, start_id: int = 10401, end_id: int = 10500,
                              file_pattern: str = "*.bmp", max_concurrent: int = 5,
                              use_docker_paths: bool = False) -> None:
    """
    Bulk import all OCT-500 scans.

    Args:
        base_dir: Base directory containing scan folders (e.g., /path/to/OCT-500/OCTA_3mm 3/OCT)
        start_id: Start scan ID (default: 10401)
        end_id: End scan ID (default: 10500)
        file_pattern: File pattern to match (default: *.bmp)
        max_concurrent: Maximum concurrent imports (default: 5)
    """
    print("=" * 80)
    print("OCT-500 Bulk Import")
    print("=" * 80)
    print(f"Base directory: {base_dir}")
    print(f"Scan IDs: {start_id} to {end_id}")
    print(f"File pattern: {file_pattern}")
    print(f"Max concurrent: {max_concurrent}")
    print("=" * 80)

    # Validate base directory
    if not base_dir.exists():
        print(f"❌ Error: Base directory does not exist: {base_dir}")
        sys.exit(1)

    # Collect all scan directories
    scan_dirs = []
    for scan_id in range(start_id, end_id + 1):
        scan_dir = base_dir / str(scan_id)
        if scan_dir.exists() and scan_dir.is_dir():
            scan_dirs.append((str(scan_id), scan_dir))
        else:
            print(f"⚠️  Warning: Scan directory not found: {scan_dir}")

    total_scans = len(scan_dirs)
    print(f"\nFound {total_scans} scan directories to import")
    print()

    if total_scans == 0:
        print("❌ No scan directories found. Exiting.")
        sys.exit(1)

    # Process scans with concurrency limit
    all_stats = []
    semaphore = asyncio.Semaphore(max_concurrent)

    async def import_with_semaphore(scan_id: str, scan_dir: Path) -> dict:
        async with semaphore:
            print(f"[{len(all_stats)+1}/{total_scans}] Importing scan {scan_id}...")
            stats = await import_single_scan(scan_id, scan_dir, file_pattern)
            status = "✓" if stats["success"] else "✗"
            print(f"  {status} {scan_id}: {stats['imported']} imported, {stats['skipped']} skipped, {stats['errors']} errors")
            return stats

    # Import all scans
    tasks = [import_with_semaphore(scan_id, scan_dir) for scan_id, scan_dir in scan_dirs]
    all_stats = await asyncio.gather(*tasks)

    # Print summary
    print()
    print("=" * 80)
    print("IMPORT SUMMARY")
    print("=" * 80)

    total_imported = sum(s["imported"] for s in all_stats)
    total_skipped = sum(s["skipped"] for s in all_stats)
    total_errors = sum(s["errors"] for s in all_stats)
    total_files = sum(s["total_files"] for s in all_stats)
    successful_scans = sum(1 for s in all_stats if s["success"])

    print(f"Total scans processed: {total_scans}")
    print(f"Successful scans: {successful_scans}")
    print(f"Total B-scans found: {total_files}")
    print(f"Imported: {total_imported}")
    print(f"Skipped (already exist): {total_skipped}")
    print(f"Errors: {total_errors}")
    print()

    if total_errors > 0:
        print("⚠️  Some errors occurred during import. Check the output above for details.")

    if successful_scans == total_scans:
        print("✓ All scans imported successfully!")

    print()
    print("Next steps:")
    print("  1. Start the backend: cd backend && uvicorn app.main:app --reload")
    print("  2. Start the frontend: cd frontend && npm run dev")
    print("  3. Open browser: http://localhost:5173")
    print("=" * 80)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Bulk import OCT-500 dataset into the labeling system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Import all scans from OCT-500 directory
  python scripts/bulk_import_oct500.py --base-dir "/Users/levarp/Documents/OCT-500/OCTA_3mm 3/OCT"

  # Import specific range of scans
  python scripts/bulk_import_oct500.py --base-dir "/path/to/OCT" --start 10401 --end 10450

  # Import with custom file pattern and concurrency
  python scripts/bulk_import_oct500.py --base-dir "/path/to/OCT" --pattern "*.tif" --concurrent 10
        """,
    )

    parser.add_argument(
        "--base-dir",
        required=True,
        type=Path,
        help="Base directory containing scan folders (e.g., /path/to/OCT-500/OCTA_3mm 3/OCT)",
    )

    parser.add_argument(
        "--start",
        type=int,
        default=10401,
        help="Start scan ID (default: 10401)",
    )

    parser.add_argument(
        "--end",
        type=int,
        default=10500,
        help="End scan ID (default: 10500)",
    )

    parser.add_argument(
        "--pattern",
        default="*.bmp",
        help="File pattern for images (default: *.bmp)",
    )

    parser.add_argument(
        "--concurrent",
        type=int,
        default=5,
        help="Maximum concurrent imports (default: 5)",
    )

    args = parser.parse_args()

    # Validate scan ID range
    if args.start > args.end:
        print("❌ Error: --start must be less than or equal to --end")
        sys.exit(1)

    # Run async import
    asyncio.run(bulk_import_oct500(
        args.base_dir,
        args.start,
        args.end,
        args.pattern,
        args.concurrent
    ))


if __name__ == "__main__":
    main()
