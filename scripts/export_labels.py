#!/usr/bin/env python3
"""
Label export CLI tool.
Exports labeled B-scan data to CSV or JSON format.
"""

import argparse
import asyncio
import sys
import csv
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.db.database import AsyncSessionLocal
from app.db.models import Scan, BScan
from sqlalchemy import select


async def export_to_csv(output_path: Path, scan_id: str = None) -> None:
    """
    Export labels to CSV format.

    Args:
        output_path: Path to output CSV file
        scan_id: Optional scan ID to filter (exports all if None)
    """
    async with AsyncSessionLocal() as db:
        # Build query
        query = select(BScan).join(Scan)

        if scan_id:
            query = query.where(Scan.scan_id == scan_id)

        query = query.order_by(Scan.scan_id, BScan.bscan_index)

        # Execute query
        result = await db.execute(query)
        bscans = result.scalars().all()

        if not bscans:
            print("❌ No B-scans found to export")
            sys.exit(1)

        # Write CSV
        with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = [
                "scan_id",
                "bscan_index",
                "label",
                "label_name",
                "path",
                "updated_at",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()

            for bscan in bscans:
                label_name = {0: "unlabeled", 1: "healthy", 2: "unhealthy"}.get(
                    bscan.label, "unknown"
                )

                writer.writerow(
                    {
                        "scan_id": bscan.scan_id,
                        "bscan_index": bscan.bscan_index,
                        "label": bscan.label,
                        "label_name": label_name,
                        "path": bscan.path,
                        "updated_at": bscan.updated_at.isoformat(),
                    }
                )

        print(f"✓ Exported {len(bscans)} B-scans to {output_path}")


async def export_to_json(output_path: Path, scan_id: str = None) -> None:
    """
    Export labels to JSON format.

    Args:
        output_path: Path to output JSON file
        scan_id: Optional scan ID to filter (exports all if None)
    """
    async with AsyncSessionLocal() as db:
        # Build query
        query = select(BScan).join(Scan)

        if scan_id:
            query = query.where(Scan.scan_id == scan_id)

        query = query.order_by(Scan.scan_id, BScan.bscan_index)

        # Execute query
        result = await db.execute(query)
        bscans = result.scalars().all()

        if not bscans:
            print("❌ No B-scans found to export")
            sys.exit(1)

        # Build JSON structure
        export_data = {
            "export_date": datetime.utcnow().isoformat(),
            "total_bscans": len(bscans),
            "scans": {},
        }

        # Group by scan_id
        for bscan in bscans:
            if bscan.scan_id not in export_data["scans"]:
                export_data["scans"][bscan.scan_id] = {
                    "scan_id": bscan.scan_id,
                    "bscans": [],
                }

            label_name = {0: "unlabeled", 1: "healthy", 2: "unhealthy"}.get(
                bscan.label, "unknown"
            )

            export_data["scans"][bscan.scan_id]["bscans"].append(
                {
                    "bscan_index": bscan.bscan_index,
                    "label": bscan.label,
                    "label_name": label_name,
                    "path": bscan.path,
                    "updated_at": bscan.updated_at.isoformat(),
                }
            )

        # Convert scans dict to list
        export_data["scans"] = list(export_data["scans"].values())
        export_data["total_scans"] = len(export_data["scans"])

        # Write JSON
        with open(output_path, "w", encoding="utf-8") as jsonfile:
            json.dump(export_data, jsonfile, indent=2, ensure_ascii=False)

        print(f"✓ Exported {len(bscans)} B-scans to {output_path}")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Export labeled B-scan data to CSV or JSON",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Export all labels to CSV
  python scripts/export_labels.py --output labels.csv --format csv

  # Export labels for specific scan to JSON
  python scripts/export_labels.py --scan-id SCAN_001 --output scan_001.json --format json

  # Export all to JSON
  python scripts/export_labels.py --output all_labels.json --format json
        """,
    )

    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="Path to output file",
    )

    parser.add_argument(
        "--format",
        choices=["csv", "json"],
        default="csv",
        help="Export format (default: csv)",
    )

    parser.add_argument(
        "--scan-id",
        help="Export labels for specific scan only (optional)",
    )

    args = parser.parse_args()

    print(f"Exporting labels to {args.format.upper()} format...")
    print("=" * 60)

    # Run export
    if args.format == "csv":
        asyncio.run(export_to_csv(args.output, args.scan_id))
    else:
        asyncio.run(export_to_json(args.output, args.scan_id))

    print("=" * 60)
    print("✓ Export complete!")


if __name__ == "__main__":
    main()
