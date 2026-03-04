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
async def test_update_health_authenticated(auth_client, sample_scan, test_db):
    from sqlalchemy import select
    from app.db.models import BScan

    result = await test_db.execute(
        select(BScan).where(BScan.scan_id == "TEST_SCAN_001").limit(1)
    )
    bscan = result.scalar_one()

    response = await auth_client.post(
        f"/api/v1/bscans/{bscan.id}/health",
        json={"healthy": 0},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["healthy"] == 0
    assert data["label"] == 2
    assert data["is_labeled"] is True


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
async def test_clear_label_clears_health_and_pathology(auth_client, sample_scan, test_db):
    from sqlalchemy import select
    from app.db.models import BScan

    result = await test_db.execute(
        select(BScan).where(BScan.scan_id == "TEST_SCAN_001").limit(1)
    )
    bscan = result.scalar_one()

    set_response = await auth_client.post(
        f"/api/v1/bscans/{bscan.id}/pathology",
        json={"cyst": 1, "hard_exudate": 1, "srf": 0, "ped": 1},
    )
    assert set_response.status_code == 200

    clear_response = await auth_client.delete(f"/api/v1/bscans/{bscan.id}/label")
    assert clear_response.status_code == 200
    data = clear_response.json()

    assert data["healthy"] is None
    assert data["cyst"] is None
    assert data["hard_exudate"] is None
    assert data["srf"] is None
    assert data["ped"] is None
    assert data["label"] == 0
    assert data["is_labeled"] is False


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


@pytest.mark.asyncio
async def test_update_pathology_requires_auth(seeded_client, sample_scan, test_db):
    from sqlalchemy import select
    from app.db.models import BScan

    result = await test_db.execute(
        select(BScan).where(BScan.scan_id == "TEST_SCAN_001").limit(1)
    )
    bscan = result.scalar_one()

    response = await seeded_client.post(
        f"/api/v1/bscans/{bscan.id}/pathology",
        json={"cyst": 1},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_pathology_sets_unhealthy(auth_client, sample_scan, test_db):
    from sqlalchemy import select
    from app.db.models import BScan

    result = await test_db.execute(
        select(BScan).where(BScan.scan_id == "TEST_SCAN_001").limit(1)
    )
    bscan = result.scalar_one()

    response = await auth_client.post(
        f"/api/v1/bscans/{bscan.id}/pathology",
        json={"cyst": 1},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["cyst"] == 1
    assert data["label"] == 2
    assert data["is_labeled"] is True


@pytest.mark.asyncio
async def test_clearing_pathology_keeps_not_healthy_when_healthy_is_zero(
    auth_client, sample_scan, test_db
):
    from sqlalchemy import select
    from app.db.models import BScan

    result = await test_db.execute(
        select(BScan).where(BScan.scan_id == "TEST_SCAN_001").limit(1)
    )
    bscan = result.scalar_one()

    response1 = await auth_client.post(
        f"/api/v1/bscans/{bscan.id}/pathology",
        json={"srf": 1},
    )
    assert response1.status_code == 200
    assert response1.json()["label"] == 2

    response2 = await auth_client.post(
        f"/api/v1/bscans/{bscan.id}/pathology",
        json={"srf": 0},
    )
    assert response2.status_code == 200
    assert response2.json()["srf"] == 0
    assert response2.json()["label"] == 2
    assert response2.json()["is_labeled"] is True
