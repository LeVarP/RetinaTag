#!/usr/bin/env python3
"""
OCT scan import CLI tool.
Imports B-scans from a directory into the database and copies files to data/scans/.
"""

import argparse
import asyncio
import sys
from pathlib import Path
from typing import List

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.db.database import AsyncSessionLocal
from app.services.scan_service import scan_service
from app.services.bscan_service import bscan_service
from app.config import settings


async def import_scan(scan_id: str, source_dir: Path, file_pattern: str = "*.png") -> None:
    """
    Import a scan from a directory.

    Args:
        scan_id: Unique identifier for the scan
        source_dir: Directory containing B-scan images
        file_pattern: Glob pattern for image files (default: *.png)
    """
    print(f"Importing scan: {scan_id}")
    print(f"Source directory: {source_dir}")
    print("=" * 60)

    # Validate source directory
    if not source_dir.exists():
        print(f"❌ Error: Source directory does not exist: {source_dir}")
        sys.exit(1)

    if not source_dir.is_dir():
        print(f"❌ Error: Source path is not a directory: {source_dir}")
        sys.exit(1)

    # Find all image files
    image_files = sorted(source_dir.glob(file_pattern))
    if not image_files:
        print(f"❌ Error: No files matching pattern '{file_pattern}' found in {source_dir}")
        sys.exit(1)

    print(f"✓ Found {len(image_files)} B-scan images")

    # Create scan directory
    scan_dir = settings.scans_dir / scan_id
    scan_dir.mkdir(parents=True, exist_ok=True)
    print(f"✓ Created scan directory: {scan_dir}")

    # Database session
    async with AsyncSessionLocal() as db:
        try:
            # Create scan record
            scan = await scan_service.create_scan(db, scan_id)
            print(f"✓ Created scan record: {scan_id}")
        except ValueError as e:
            print(f"⚠️  Warning: {e}")
            print("   Skipping scan creation, adding B-scans to existing scan...")

        # Import each B-scan
        imported_count = 0
        skipped_count = 0

        for i, source_file in enumerate(image_files):
            bscan_index = i
            dest_filename = f"{bscan_index}.png"
            dest_path = scan_dir / dest_filename

            try:
                # Check if B-scan already exists
                existing = await bscan_service.get_bscan_by_index(db, scan_id, bscan_index)

                if existing:
                    print(f"  [{i+1}/{len(image_files)}] Skipped: B-scan {bscan_index} already exists")
                    skipped_count += 1
                    continue

                # Copy file
                import shutil
                shutil.copy2(source_file, dest_path)

                # Create B-scan record
                await bscan_service.create_bscan(
                    db,
                    scan_id=scan_id,
                    bscan_index=bscan_index,
                    path=str(dest_path.absolute()),
                )

                print(f"  [{i+1}/{len(image_files)}] Imported: {source_file.name} → {dest_filename}")
                imported_count += 1

            except Exception as e:
                print(f"  [{i+1}/{len(image_files)}] Error: {source_file.name} - {e}")
                continue

        await db.commit()

    print("=" * 60)
    print(f"✓ Import complete!")
    print(f"  Total files: {len(image_files)}")
    print(f"  Imported: {imported_count}")
    print(f"  Skipped: {skipped_count}")
    print(f"\nNext steps:")
    print(f"  1. Start the backend: cd backend && uvicorn app.main:app --reload")
    print(f"  2. Start the frontend: cd frontend && npm run dev")
    print(f"  3. Open browser: http://localhost:5173")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Import OCT B-scans into the labeling system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Import scan with ID 'SCAN_001' from directory
  python scripts/import_scan.py --scan-id SCAN_001 --source /path/to/scans/

  # Import with custom file pattern
  python scripts/import_scan.py --scan-id SCAN_002 --source /data/oct/ --pattern "*.tif"
        """,
    )

    parser.add_argument(
        "--scan-id",
        required=True,
        help="Unique identifier for this scan (e.g., SCAN_001, ABC123)",
    )

    parser.add_argument(
        "--source",
        required=True,
        type=Path,
        help="Directory containing B-scan images",
    )

    parser.add_argument(
        "--pattern",
        default="*.png",
        help="File pattern for images (default: *.png)",
    )

    args = parser.parse_args()

    # Run async import
    asyncio.run(import_scan(args.scan_id, args.source, args.pattern))


if __name__ == "__main__":
    main()
