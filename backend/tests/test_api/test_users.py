"""Tests for user settings and password API endpoints."""

import pytest


@pytest.mark.asyncio
async def test_get_settings_default(auth_client):
    response = await auth_client.get("/api/v1/users/me/settings")
    assert response.status_code == 200
    data = response.json()
    assert data["auto_advance"] is True
    assert data["hotkey_healthy"] == "a"
    assert data["hotkey_unhealthy"] == "s"
    assert data["hotkey_next"] == "ArrowRight"
    assert data["hotkey_prev"] == "ArrowLeft"


@pytest.mark.asyncio
async def test_update_settings_partial(auth_client):
    response = await auth_client.put(
        "/api/v1/users/me/settings",
        json={"auto_advance": False},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["auto_advance"] is False
    # Other fields unchanged
    assert data["hotkey_healthy"] == "a"
    assert data["hotkey_unhealthy"] == "s"


@pytest.mark.asyncio
async def test_update_settings_hotkeys(auth_client):
    response = await auth_client.put(
        "/api/v1/users/me/settings",
        json={"hotkey_healthy": "d", "hotkey_unhealthy": "f"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["hotkey_healthy"] == "d"
    assert data["hotkey_unhealthy"] == "f"


@pytest.mark.asyncio
async def test_settings_requires_auth(seeded_client):
    response = await seeded_client.get("/api/v1/users/me/settings")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_change_password_success(auth_client):
    response = await auth_client.post(
        "/api/v1/users/me/password",
        json={"current_password": "admin", "new_password": "newpass123"},
    )
    assert response.status_code == 200

    # Can login with new password
    login_resp = await auth_client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "newpass123"},
    )
    assert login_resp.status_code == 200


@pytest.mark.asyncio
async def test_change_password_wrong_current(auth_client):
    response = await auth_client.post(
        "/api/v1/users/me/password",
        json={"current_password": "wrong", "new_password": "newpass123"},
    )
    assert response.status_code == 400
