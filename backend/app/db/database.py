"""
Database connection and session management for OCT B-Scan Labeler.
Configures SQLite with async support using aiosqlite.
"""

import csv
import os
from pathlib import Path
from typing import AsyncGenerator, Optional
from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.models import Base, Scan, BScan


# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite+aiosqlite:///./data/database/oct_labeler.db"
)

# Ensure database directory exists
db_path = DATABASE_URL.replace("sqlite+aiosqlite:///", "")
db_dir = Path(db_path).parent
db_dir.mkdir(parents=True, exist_ok=True)

CSV_SEED_PATH = (
    Path(__file__).resolve().parent / "Overview info_all_sheets - Overview info_all_sheets.csv"
)

# Create async engine
# StaticPool is used for SQLite to avoid threading issues
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL query logging
    connect_args={"check_same_thread": False},  # SQLite specific
    poolclass=StaticPool,  # Use StaticPool for SQLite
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


def _parse_optional_int(value: Optional[str]) -> Optional[int]:
    """Parse integer-like CSV cell, returning None for empty/invalid values."""
    if value is None:
        return None

    normalized = value.strip()
    if normalized == "":
        return None

    try:
        return int(normalized)
    except ValueError:
        return None


def _derive_healthy(healthy: Optional[int], unhealthy: Optional[int]) -> Optional[int]:
    """
    Map CSV Healthy/Unhealthy flags into tri-state healthy field:
    - 1 => healthy
    - 0 => not healthy
    - None => not necessary healthy
    """
    if healthy in (0, 1):
        return healthy
    if unhealthy == 1:
        return 0
    return None


def _derive_label(healthy: Optional[int]) -> int:
    """Backward-compatible label derived from healthy field."""
    if healthy == 1:
        return 1
    if healthy == 0:
        return 2
    return 0


def _derive_hard_exudate(primary: Optional[int], secondary: Optional[int]) -> Optional[int]:
    """Merge duplicated hard exudate CSV flags using logical OR, preserving empty values."""
    if primary in (0, 1) or secondary in (0, 1):
        return 1 if primary == 1 or secondary == 1 else 0
    return None


def _derive_is_labeled(
    cyst: Optional[int],
    hard_exudate: Optional[int],
    srf: Optional[int],
    ped: Optional[int],
    healthy: Optional[int],
) -> int:
    """
    Marker-based labeling flag.
    Labeled if any marker field is explicitly 0 or 1.
    """
    marker_values = (cyst, hard_exudate, srf, ped, healthy)
    return 1 if any(value in (0, 1) for value in marker_values) else 0


def _normalize_bscan_indexes(sync_conn) -> None:
    """
    Normalize B-scan indexes to 0-based per scan.
    If a scan has no index 0 and minimum index is 1, shift all its indexes by -1.
    """
    candidates = sync_conn.execute(
        text(
            """
            SELECT scan_id
            FROM bscans
            GROUP BY scan_id
            HAVING MIN(bscan_index) = 1
               AND SUM(CASE WHEN bscan_index = 0 THEN 1 ELSE 0 END) = 0
            """
        )
    ).fetchall()

    for (scan_id,) in candidates:
        # Two-step shift avoids temporary UNIQUE conflicts on (scan_id, bscan_index).
        sync_conn.execute(
            text(
                """
                UPDATE bscans
                SET bscan_index = bscan_index + 10000
                WHERE scan_id = :scan_id
                """
            ),
            {"scan_id": scan_id},
        )
        sync_conn.execute(
            text(
                """
                UPDATE bscans
                SET bscan_index = bscan_index - 10001
                WHERE scan_id = :scan_id
                """
            ),
            {"scan_id": scan_id},
        )


def _ensure_bscan_columns(sync_conn) -> None:
    """
    Lightweight migration for existing SQLite DBs:
    add columns introduced by expanded CSV schema when they are missing.
    """
    result = sync_conn.execute(text("PRAGMA table_info(bscans)"))
    existing_columns = {row[1] for row in result}

    required_columns = {
        "bscan_key": "TEXT",
        "cyst": "INTEGER",
        "hard_exudate": "INTEGER",
        "srf": "INTEGER",
        "ped": "INTEGER",
        "healthy": "INTEGER",
        "is_labeled": "INTEGER NOT NULL DEFAULT 0",
    }

    for column_name, column_type in required_columns.items():
        if column_name not in existing_columns:
            sync_conn.execute(
                text(f"ALTER TABLE bscans ADD COLUMN {column_name} {column_type}")
            )

    # Best-effort cleanup of legacy schema: keep health status in `healthy` only.
    if "unhealthy" in existing_columns:
        try:
            sync_conn.execute(text("ALTER TABLE bscans DROP COLUMN unhealthy"))
            existing_columns.remove("unhealthy")
        except Exception:
            # Older SQLite versions may not support DROP COLUMN; keep running safely.
            pass

    if "hard_exudate_alt" in existing_columns:
        sync_conn.execute(
            text(
                """
                UPDATE bscans
                SET hard_exudate = CASE
                    WHEN COALESCE(hard_exudate, 0) = 1
                      OR COALESCE(hard_exudate_alt, 0) = 1
                    THEN 1
                    WHEN hard_exudate IN (0, 1)
                      OR hard_exudate_alt IN (0, 1)
                    THEN 0
                    ELSE NULL
                END
                """
            )
        )

    # Backfill marker-based labeling status for existing rows.
    has_unhealthy_column = "unhealthy" in existing_columns
    healthy_backfill_sql = """
        UPDATE bscans
        SET healthy = CASE
            WHEN healthy IN (0, 1) THEN healthy
    """
    if has_unhealthy_column:
        healthy_backfill_sql += """
            WHEN unhealthy = 1 THEN 0
        """
    healthy_backfill_sql += """
            ELSE NULL
        END
    """
    sync_conn.execute(text(healthy_backfill_sql))

    sync_conn.execute(
        text(
            """
            UPDATE bscans
            SET is_labeled = CASE
                WHEN cyst IN (0, 1)
                  OR hard_exudate IN (0, 1)
                  OR srf IN (0, 1)
                  OR ped IN (0, 1)
                  OR healthy IN (0, 1)
                THEN 1
                ELSE 0
            END
            """
        )
    )

    sync_conn.execute(
        text(
            """
            UPDATE bscans
            SET label = CASE
                WHEN healthy = 1 THEN 1
                WHEN healthy = 0 THEN 2
                ELSE 0
            END
            """
        )
    )

    sync_conn.execute(
        text(
            "CREATE INDEX IF NOT EXISTS idx_scan_is_labeled ON bscans(scan_id, is_labeled)"
        )
    )

    _normalize_bscan_indexes(sync_conn)


def _ensure_user_settings_columns(sync_conn) -> None:
    """
    Lightweight migration for user hotkey settings.
    Adds pathology hotkey columns when missing.
    """
    result = sync_conn.execute(text("PRAGMA table_info(user_settings)"))
    existing_columns = {row[1] for row in result}

    required_columns = {
        "hotkey_cyst": "TEXT NOT NULL DEFAULT '1'",
        "hotkey_hard_exudate": "TEXT NOT NULL DEFAULT '2'",
        "hotkey_srf": "TEXT NOT NULL DEFAULT '3'",
        "hotkey_ped": "TEXT NOT NULL DEFAULT '4'",
    }

    for column_name, column_type in required_columns.items():
        if column_name not in existing_columns:
            sync_conn.execute(
                text(f"ALTER TABLE user_settings ADD COLUMN {column_name} {column_type}")
            )

    # Backfill empty values to defaults for already existing rows.
    sync_conn.execute(
        text(
            """
            UPDATE user_settings
            SET
                hotkey_cyst = COALESCE(NULLIF(hotkey_cyst, ''), '1'),
                hotkey_hard_exudate = COALESCE(NULLIF(hotkey_hard_exudate, ''), '2'),
                hotkey_srf = COALESCE(NULLIF(hotkey_srf, ''), '3'),
                hotkey_ped = COALESCE(NULLIF(hotkey_ped, ''), '4')
            """
        )
    )


async def seed_db_from_csv(
    session: AsyncSession, csv_path: Path = CSV_SEED_PATH
) -> int:
    """
    Seed scans/bscans from CSV if database is empty.

    Returns number of inserted B-scan rows.
    """
    existing_count_result = await session.execute(select(func.count(BScan.id)))
    existing_count = existing_count_result.scalar() or 0
    if existing_count > 0:
        return 0

    if not csv_path.exists():
        print(f"⚠ CSV seed file not found: {csv_path}")
        return 0

    existing_scans_result = await session.execute(select(Scan.scan_id))
    known_scans = set(existing_scans_result.scalars().all())

    inserted_rows = 0
    skipped_rows = 0
    raw_rows: list[dict] = []

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

            healthy = _derive_healthy(
                _parse_optional_int(row.get("Healthy")),
                _parse_optional_int(row.get("Unhealthy")),
            )
            cyst = _parse_optional_int(row.get("Cyst"))
            srf = _parse_optional_int(row.get("SRF"))
            ped = _parse_optional_int(row.get("PED"))
            hard_exudate = _derive_hard_exudate(
                _parse_optional_int(row.get("Hard exudate")),
                _parse_optional_int(row.get("Hard Exudate")),
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
    seen_scan_indexes: set[tuple[str, int]] = set()
    bscans_to_insert: list[BScan] = []
    for row in raw_rows:
        scan_id = row["scan_id"]
        bscan_index = row["bscan_index"] - 1 if scan_id in scans_to_shift else row["bscan_index"]

        key = (scan_id, bscan_index)
        if row["path"] in seen_paths or key in seen_scan_indexes:
            skipped_rows += 1
            continue

        if scan_id not in known_scans:
            session.add(Scan(scan_id=scan_id))
            known_scans.add(scan_id)

        is_labeled = _derive_is_labeled(
            cyst=row["cyst"],
            hard_exudate=row["hard_exudate"],
            srf=row["srf"],
            ped=row["ped"],
            healthy=row["healthy"],
        )

        bscans_to_insert.append(
            BScan(
                scan_id=scan_id,
                bscan_index=bscan_index,
                bscan_key=row["bscan_key"],
                path=row["path"],
                cyst=row["cyst"],
                hard_exudate=row["hard_exudate"],
                srf=row["srf"],
                ped=row["ped"],
                healthy=row["healthy"],
                is_labeled=is_labeled,
                label=_derive_label(row["healthy"]),
            )
        )

        seen_paths.add(row["path"])
        seen_scan_indexes.add(key)
        inserted_rows += 1

    if bscans_to_insert:
        session.add_all(bscans_to_insert)
        await session.flush()

    if skipped_rows:
        print(f"⚠ CSV seed skipped {skipped_rows} malformed/duplicate rows")

    return inserted_rows


async def init_db() -> None:
    """
    Initialize database by creating all tables.
    Should be called on application startup.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(_ensure_bscan_columns)
        await conn.run_sync(_ensure_user_settings_columns)

    async with AsyncSessionLocal() as session:
        inserted_rows = await seed_db_from_csv(session)
        await session.commit()
        if inserted_rows:
            print(f"✓ Seeded database from CSV: {inserted_rows} B-scans")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting database session in FastAPI endpoints.

    Usage:
        @app.get("/items")
        async def read_items(db: AsyncSession = Depends(get_db)):
            # Use db session here
            ...

    Yields:
        AsyncSession: Database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def dispose_engine() -> None:
    """
    Dispose database engine.
    Should be called on application shutdown.
    """
    await engine.dispose()
