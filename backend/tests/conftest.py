"""
Shared test fixtures for backend tests.
Provides in-memory SQLite database and authenticated test clients.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.models import Base, Scan, BScan
from app.db.database import get_db
from app.main import app
from app.services.auth_service import auth_service

TEST_DATABASE_URL = "sqlite+aiosqlite://"


@pytest.fixture
async def test_engine():
    """Create a fresh in-memory database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def test_db(test_engine):
    """Provide a database session for tests."""
    TestSession = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with TestSession() as session:
        yield session


@pytest.fixture
async def client(test_engine):
    """Create test HTTP client with overridden DB dependency."""
    TestSession = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )

    async def override_get_db():
        async with TestSession() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
async def seeded_client(client, test_db):
    """Client with default admin user seeded."""
    await auth_service.ensure_default_admin(test_db)
    await test_db.commit()
    yield client


@pytest.fixture
async def auth_client(seeded_client):
    """Client that is logged in as admin."""
    response = await seeded_client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "admin"},
    )
    assert response.status_code == 200
    yield seeded_client


@pytest.fixture
async def sample_scan(test_db):
    """Create a sample scan with B-scans for testing."""
    scan = Scan(scan_id="TEST_SCAN_001")
    test_db.add(scan)
    await test_db.flush()

    for i in range(5):
        bscan = BScan(
            scan_id="TEST_SCAN_001",
            bscan_index=i + 1,
            path=f"/data/scans/TEST_SCAN_001/{i + 1}.png",
            label=0,
        )
        test_db.add(bscan)

    await test_db.commit()
    return scan
