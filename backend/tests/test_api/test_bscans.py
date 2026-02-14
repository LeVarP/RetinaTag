"""Tests for B-scan labeling API endpoints."""

import pytest


@pytest.mark.asyncio
async def test_label_bscan_requires_auth(seeded_client, sample_scan, test_db):
    """Labeling without auth should fail with 401."""
    from sqlalchemy import select
    from app.db.models import BScan

    result = await test_db.execute(
        select(BScan).where(BScan.scan_id == "TEST_SCAN_001").limit(1)
    )
    bscan = result.scalar_one()

    response = await seeded_client.post(
        f"/api/v1/bscans/{bscan.id}/label",
        json={"label": 1},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_label_bscan_authenticated(auth_client, sample_scan, test_db):
    from sqlalchemy import select
    from app.db.models import BScan

    result = await test_db.execute(
        select(BScan).where(BScan.scan_id == "TEST_SCAN_001").limit(1)
    )
    bscan = result.scalar_one()

    response = await auth_client.post(
        f"/api/v1/bscans/{bscan.id}/label",
        json={"label": 1},
    )
    assert response.status_code == 200
    assert response.json()["label"] == 1


@pytest.mark.asyncio
async def test_clear_label_requires_auth(seeded_client, sample_scan, test_db):
    from sqlalchemy import select
    from app.db.models import BScan

    result = await test_db.execute(
        select(BScan).where(BScan.scan_id == "TEST_SCAN_001").limit(1)
    )
    bscan = result.scalar_one()

    response = await seeded_client.delete(f"/api/v1/bscans/{bscan.id}/label")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_bscan_by_id_no_auth_needed(seeded_client, sample_scan, test_db):
    """GET endpoints remain public."""
    from sqlalchemy import select
    from app.db.models import BScan

    result = await test_db.execute(
        select(BScan).where(BScan.scan_id == "TEST_SCAN_001").limit(1)
    )
    bscan = result.scalar_one()

    response = await seeded_client.get(f"/api/v1/bscans/{bscan.id}")
    assert response.status_code == 200
