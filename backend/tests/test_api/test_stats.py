"""Tests for statistics API endpoints."""

import pytest


@pytest.mark.asyncio
async def test_global_stats_empty(client):
    response = await client.get("/api/v1/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total_scans"] == 0
    assert data["total_bscans"] == 0


@pytest.mark.asyncio
async def test_global_stats_with_data(client, sample_scan):
    response = await client.get("/api/v1/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total_scans"] == 1
    assert data["total_bscans"] == 5
    assert data["total_unlabeled"] == 5
