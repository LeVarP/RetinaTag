#!/usr/bin/env python3
"""
Database initialization script for OCT B-Scan Labeler.
Creates all tables and ensures required directories exist.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path to allow imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.database import init_db, engine
from app.db.models import Base
from app.config import settings


async def main() -> None:
    """Initialize database and create all required directories."""
    print("OCT B-Scan Labeler - Database Initialization")
    print("=" * 50)

    # Ensure all required directories exist
    print("\n1. Creating required directories...")
    settings.ensure_directories()
    print(f"   ✓ Data directory: {settings.data_dir}")
    print(f"   ✓ Scans directory: {settings.scans_dir}")
    print(f"   ✓ Cache directory: {settings.cache_dir}")
    print(f"   ✓ Database directory: {settings.data_dir / 'database'}")

    # Initialize database
    print("\n2. Creating database tables...")
    try:
        await init_db()
        print("   ✓ Database initialized successfully")

        # Verify tables were created
        async with engine.begin() as conn:
            def get_tables(conn):
                inspector = __import__('sqlalchemy').inspect(conn)
                return inspector.get_table_names()

            tables = await conn.run_sync(get_tables)
            print(f"\n3. Verifying tables...")
            for table in tables:
                print(f"   ✓ Table '{table}' created")

    except Exception as e:
        print(f"\n   ✗ Error initializing database: {e}", file=sys.stderr)
        sys.exit(1)

    # Show database location
    db_file = str(settings.data_dir / "database" / "oct_labeler.db")
    print(f"\n4. Database location:")
    print(f"   {db_file}")

    # Show next steps
    print("\n" + "=" * 50)
    print("Initialization complete!")
    print("\nNext steps:")
    print("  1. Import OCT scans:")
    print("     python scripts/import_scan.py --scan-id ABC123 --source /path/to/scans/")
    print("\n  2. Start the backend server:")
    print("     uvicorn app.main:app --reload")
    print("\n  3. Access API documentation:")
    print("     http://localhost:8000/docs")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
