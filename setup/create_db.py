#!/usr/bin/env python3
"""
Create an empty RetinaTag database with the required schema.

Usage:
    python setup/create_db.py
    python setup/create_db.py --output /custom/path/oct_labeler.db
"""

import argparse
import csv
import sqlite3
import sys
from pathlib import Path
from typing import Optional

SCHEMA = """
-- OCT scans (one scan = one tomogram with many B-scan frames)
CREATE TABLE IF NOT EXISTS scans (
    scan_id   TEXT PRIMARY KEY,
    created_at DATETIME NOT NULL DEFAULT (datetime('now')),
    updated_at DATETIME NOT NULL DEFAULT (datetime('now'))
);

-- Individual B-scan frames within a scan
CREATE TABLE IF NOT EXISTS bscans (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_id     TEXT    NOT NULL REFERENCES scans(scan_id) ON DELETE CASCADE,
    bscan_index INTEGER NOT NULL,
    bscan_key   TEXT,
    path        TEXT    NOT NULL UNIQUE,
    cyst        INTEGER,
    hard_exudate INTEGER,
    srf         INTEGER,
    ped         INTEGER,
    healthy     INTEGER,
    is_labeled  INTEGER NOT NULL DEFAULT 0,
    label       INTEGER NOT NULL DEFAULT 0,  -- 0=unlabeled, 1=healthy, 2=unhealthy
    updated_at  DATETIME NOT NULL DEFAULT (datetime('now'))
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_scan_bscan ON bscans(scan_id, bscan_index);
CREATE INDEX IF NOT EXISTS idx_scan_label ON bscans(scan_id, label);
CREATE INDEX IF NOT EXISTS idx_scan_is_labeled ON bscans(scan_id, is_labeled);
CREATE INDEX IF NOT EXISTS idx_label ON bscans(label);

-- User accounts
CREATE TABLE IF NOT EXISTS users (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    username        TEXT    NOT NULL UNIQUE,
    hashed_password TEXT    NOT NULL,
    is_active       INTEGER NOT NULL DEFAULT 1,
    is_admin        INTEGER NOT NULL DEFAULT 0,
    created_at      DATETIME NOT NULL DEFAULT (datetime('now')),
    updated_at      DATETIME NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS ix_users_username ON users(username);

-- Per-user labeling preferences
CREATE TABLE IF NOT EXISTS user_settings (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id          INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    auto_advance     INTEGER NOT NULL DEFAULT 1,
    hotkey_healthy   TEXT    NOT NULL DEFAULT 'a',
    hotkey_unhealthy TEXT    NOT NULL DEFAULT 's',
    hotkey_cyst      TEXT    NOT NULL DEFAULT '1',
    hotkey_hard_exudate TEXT NOT NULL DEFAULT '2',
    hotkey_srf       TEXT    NOT NULL DEFAULT '3',
    hotkey_ped       TEXT    NOT NULL DEFAULT '4',
    hotkey_next      TEXT    NOT NULL DEFAULT 'ArrowRight',
    hotkey_prev      TEXT    NOT NULL DEFAULT 'ArrowLeft',
    updated_at       DATETIME NOT NULL DEFAULT (datetime('now'))
);
"""

DEFAULT_PATH = Path("data/database/oct_labeler.db")
DEFAULT_CSV_PATH = Path(
    "backend/app/db/Overview info_all_sheets - Overview info_all_sheets.csv"
)


def parse_optional_int(value: Optional[str]) -> Optional[int]:
    if value is None:
        return None

    normalized = value.strip()
    if normalized == "":
        return None

    try:
        return int(normalized)
    except ValueError:
        return None


def derive_healthy(healthy: Optional[int], unhealthy: Optional[int]) -> Optional[int]:
    if healthy in (0, 1):
        return healthy
    if unhealthy == 1:
        return 0
    return None


def derive_label(healthy: Optional[int]) -> int:
    if healthy == 1:
        return 1
    if healthy == 0:
        return 2
    return 0


def derive_hard_exudate(primary: Optional[int], secondary: Optional[int]) -> Optional[int]:
    if primary in (0, 1) or secondary in (0, 1):
        return 1 if primary == 1 or secondary == 1 else 0
    return None


def derive_is_labeled(
    cyst: Optional[int],
    hard_exudate: Optional[int],
    srf: Optional[int],
    ped: Optional[int],
    healthy: Optional[int],
) -> int:
    marker_values = (cyst, hard_exudate, srf, ped, healthy)
    return 1 if any(value in (0, 1) for value in marker_values) else 0


def import_csv_data(conn: sqlite3.Connection, csv_path: Path) -> tuple[int, int, int]:
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path.resolve()}")

    scan_ids: set[str] = set()
    raw_rows: list[dict] = []
    skipped_rows = 0

    with csv_path.open("r", newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            scan_id = (row.get("scan_id") or "").strip()
            bscan_index_raw = (row.get("bscan_index") or "").strip()
            path = (row.get("path") or "").strip()

            if not scan_id or not bscan_index_raw or not path:
                skipped_rows += 1
                continue

            try:
                bscan_index = int(bscan_index_raw)
            except ValueError:
                skipped_rows += 1
                continue

            healthy = derive_healthy(
                parse_optional_int(row.get("Healthy")),
                parse_optional_int(row.get("Unhealthy")),
            )
            cyst = parse_optional_int(row.get("Cyst"))
            srf = parse_optional_int(row.get("SRF"))
            ped = parse_optional_int(row.get("PED"))
            hard_exudate = derive_hard_exudate(
                parse_optional_int(row.get("Hard exudate")),
                parse_optional_int(row.get("Hard Exudate")),
            )
            is_labeled = derive_is_labeled(
                cyst=cyst,
                hard_exudate=hard_exudate,
                srf=srf,
                ped=ped,
                healthy=healthy,
            )

            raw_rows.append(
                {
                    "scan_id": scan_id,
                    "bscan_index": bscan_index,
                    "bscan_key": (row.get("bscan_key") or "").strip() or None,
                    "path": path,
                    "cyst": cyst,
                    "hard_exudate": hard_exudate,
                    "srf": srf,
                    "ped": ped,
                    "healthy": healthy,
                    "is_labeled": is_labeled,
                    "label": derive_label(healthy),
                }
            )

    scan_min_index: dict[str, int] = {}
    scan_has_zero: dict[str, bool] = {}
    for row in raw_rows:
        scan_id = row["scan_id"]
        bscan_index = row["bscan_index"]
        scan_min_index[scan_id] = min(scan_min_index.get(scan_id, bscan_index), bscan_index)
        scan_has_zero[scan_id] = scan_has_zero.get(scan_id, False) or bscan_index == 0

    scans_to_shift = {
        scan_id
        for scan_id, min_index in scan_min_index.items()
        if min_index == 1 and not scan_has_zero.get(scan_id, False)
    }

    seen_paths: set[str] = set()
    seen_pairs: set[tuple[str, int]] = set()
    bscan_rows: list[tuple] = []

    for row in raw_rows:
        scan_id = row["scan_id"]
        bscan_index = row["bscan_index"] - 1 if scan_id in scans_to_shift else row["bscan_index"]
        key = (scan_id, bscan_index)
        if key in seen_pairs or row["path"] in seen_paths:
            skipped_rows += 1
            continue

        scan_ids.add(scan_id)
        bscan_rows.append(
            (
                scan_id,
                bscan_index,
                row["bscan_key"],
                row["path"],
                row["cyst"],
                row["hard_exudate"],
                row["srf"],
                row["ped"],
                row["healthy"],
                row["is_labeled"],
                row["label"],
            )
        )

        seen_pairs.add(key)
        seen_paths.add(row["path"])

    conn.executemany(
        "INSERT OR IGNORE INTO scans(scan_id) VALUES (?)",
        [(scan_id,) for scan_id in sorted(scan_ids)],
    )

    conn.executemany(
        """
        INSERT INTO bscans (
            scan_id, bscan_index, bscan_key, path,
            cyst, hard_exudate, srf, ped, healthy, is_labeled, label
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        bscan_rows,
    )

    return len(scan_ids), len(bscan_rows), skipped_rows


def create_database(db_path: Path, csv_path: Optional[Path]) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)

    if csv_path is not None:
        scan_count, bscan_count, skipped_rows = import_csv_data(conn, csv_path)
        print(f"Loaded CSV data: {scan_count} scans, {bscan_count} bscans")
        if skipped_rows:
            print(f"Skipped malformed/duplicate rows: {skipped_rows}")

    conn.commit()
    conn.close()

    print(f"Database created: {db_path.resolve()}")
    print(f"Tables: scans, bscans, users, user_settings")


def main():
    parser = argparse.ArgumentParser(description="Create an empty RetinaTag database")
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=DEFAULT_PATH,
        help=f"Path to the database file (default: {DEFAULT_PATH})",
    )
    parser.add_argument(
        "--csv",
        type=Path,
        default=DEFAULT_CSV_PATH,
        help=f"Path to CSV for initial seed (default: {DEFAULT_CSV_PATH})",
    )
    parser.add_argument(
        "--no-seed",
        action="store_true",
        help="Create schema only, without loading CSV data",
    )
    args = parser.parse_args()

    if args.output.exists():
        print(f"Database already exists: {args.output.resolve()}", file=sys.stderr)
        print("Delete it first if you want to recreate.", file=sys.stderr)
        sys.exit(1)

    create_database(args.output, None if args.no_seed else args.csv)


if __name__ == "__main__":
    main()
