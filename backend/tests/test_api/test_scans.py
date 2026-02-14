"""Tests for scan API endpoints."""

import pytest


@pytest.mark.asyncio
async def test_list_scans_empty(client):
    response = await client.get("/api/v1/scans")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_list_scans_with_data(client, sample_scan):
    response = await client.get("/api/v1/scans")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["scan_id"] == "TEST_SCAN_001"
    assert data[0]["stats"]["total_bscans"] == 5


@pytest.mark.asyncio
async def test_get_scan_stats(client, sample_scan):
    response = await client.get("/api/v1/scans/TEST_SCAN_001/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total_bscans"] == 5
    assert data["labeled"] == 0
    assert data["unlabeled"] == 5


@pytest.mark.asyncio
async def test_get_bscan_by_index(client, sample_scan):
    response = await client.get("/api/v1/scans/TEST_SCAN_001/bscans/1")
    assert response.status_code == 200
    data = response.json()
    assert data["bscan_index"] == 1
    assert data["scan_id"] == "TEST_SCAN_001"


@pytest.mark.asyncio
async def test_get_scan_not_found(client):
    response = await client.get("/api/v1/scans/NONEXISTENT/stats")
    assert response.status_code == 404
