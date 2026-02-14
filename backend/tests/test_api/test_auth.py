"""Tests for authentication API endpoints."""

import pytest


@pytest.mark.asyncio
async def test_login_success(seeded_client):
    response = await seeded_client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "admin"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "admin"
    assert data["is_admin"] is True
    assert "access_token" in response.cookies


@pytest.mark.asyncio
async def test_login_wrong_password(seeded_client):
    response = await seeded_client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "wrong"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_user(seeded_client):
    response = await seeded_client.post(
        "/api/v1/auth/login",
        json={"username": "nobody", "password": "test"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_logout(auth_client):
    response = await auth_client.post("/api/v1/auth/logout")
    assert response.status_code == 200
    assert response.json()["message"] == "Logged out"


@pytest.mark.asyncio
async def test_auth_me_authenticated(auth_client):
    response = await auth_client.get("/api/v1/auth/me")
    assert response.status_code == 200
    data = response.json()
    assert data["authenticated"] is True
    assert data["user"]["username"] == "admin"


@pytest.mark.asyncio
async def test_auth_me_unauthenticated(seeded_client):
    response = await seeded_client.get("/api/v1/auth/me")
    assert response.status_code == 200
    data = response.json()
    assert data["authenticated"] is False
    assert data["user"] is None


@pytest.mark.asyncio
async def test_register_requires_admin(seeded_client):
    """Registration without auth should fail with 401."""
    response = await seeded_client.post(
        "/api/v1/auth/register",
        json={"username": "newuser", "password": "test1234"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_register_success(auth_client):
    response = await auth_client.post(
        "/api/v1/auth/register",
        json={"username": "newuser", "password": "test1234"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"
    assert data["is_admin"] is False


@pytest.mark.asyncio
async def test_register_duplicate_username(auth_client):
    await auth_client.post(
        "/api/v1/auth/register",
        json={"username": "dup_user", "password": "test1234"},
    )
    response = await auth_client.post(
        "/api/v1/auth/register",
        json={"username": "dup_user", "password": "test1234"},
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_register_invalid_username(auth_client):
    response = await auth_client.post(
        "/api/v1/auth/register",
        json={"username": "ab", "password": "test1234"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_short_password(auth_client):
    response = await auth_client.post(
        "/api/v1/auth/register",
        json={"username": "validuser", "password": "ab"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_new_user_can_login(auth_client):
    """Newly created user can log in."""
    await auth_client.post(
        "/api/v1/auth/register",
        json={"username": "logintest", "password": "mypass123"},
    )
    response = await auth_client.post(
        "/api/v1/auth/login",
        json={"username": "logintest", "password": "mypass123"},
    )
    assert response.status_code == 200
    assert response.json()["username"] == "logintest"
