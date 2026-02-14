#!/usr/bin/env python3
"""
Create an empty RetinaTag database with the required schema.

Usage:
    python setup/create_db.py
    python setup/create_db.py --output /custom/path/oct_labeler.db
"""

import argparse
import sqlite3
import sys
from pathlib import Path

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
    path        TEXT    NOT NULL UNIQUE,
    label       INTEGER NOT NULL DEFAULT 0,  -- 0=unlabeled, 1=healthy, 2=unhealthy
    updated_at  DATETIME NOT NULL DEFAULT (datetime('now'))
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_scan_bscan ON bscans(scan_id, bscan_index);
CREATE INDEX IF NOT EXISTS idx_scan_label ON bscans(scan_id, label);
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
    hotkey_next      TEXT    NOT NULL DEFAULT 'ArrowRight',
    hotkey_prev      TEXT    NOT NULL DEFAULT 'ArrowLeft',
    updated_at       DATETIME NOT NULL DEFAULT (datetime('now'))
);
"""

DEFAULT_PATH = Path("data/database/oct_labeler.db")


def create_database(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)
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
    args = parser.parse_args()

    if args.output.exists():
        print(f"Database already exists: {args.output.resolve()}", file=sys.stderr)
        print("Delete it first if you want to recreate.", file=sys.stderr)
        sys.exit(1)

    create_database(args.output)


if __name__ == "__main__":
    main()
