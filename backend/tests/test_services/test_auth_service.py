"""Tests for auth service."""

import pytest
from datetime import timedelta
from app.services.auth_service import auth_service


def test_hash_password():
    hashed = auth_service.hash_password("testpass")
    assert hashed != "testpass"
    assert len(hashed) > 20


def test_verify_password_correct():
    hashed = auth_service.hash_password("mypassword")
    assert auth_service.verify_password("mypassword", hashed) is True


def test_verify_password_incorrect():
    hashed = auth_service.hash_password("mypassword")
    assert auth_service.verify_password("wrong", hashed) is False


def test_create_access_token():
    token = auth_service.create_access_token({"sub": "testuser"})
    assert isinstance(token, str)
    assert len(token) > 10


def test_decode_valid_token():
    token = auth_service.create_access_token({"sub": "testuser"})
    payload = auth_service.decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == "testuser"


def test_decode_expired_token():
    token = auth_service.create_access_token(
        {"sub": "testuser"}, expires_delta=timedelta(seconds=-1)
    )
    payload = auth_service.decode_access_token(token)
    assert payload is None


def test_decode_invalid_token():
    payload = auth_service.decode_access_token("garbage.token.here")
    assert payload is None


@pytest.mark.asyncio
async def test_create_user(test_db):
    user = await auth_service.create_user(test_db, "alice", "pass123")
    await test_db.commit()
    assert user.username == "alice"
    assert user.hashed_password != "pass123"


@pytest.mark.asyncio
async def test_authenticate_user_success(test_db):
    await auth_service.create_user(test_db, "bob", "secret")
    await test_db.commit()
    user = await auth_service.authenticate_user(test_db, "bob", "secret")
    assert user is not None
    assert user.username == "bob"


@pytest.mark.asyncio
async def test_authenticate_user_wrong_password(test_db):
    await auth_service.create_user(test_db, "carol", "correct")
    await test_db.commit()
    user = await auth_service.authenticate_user(test_db, "carol", "wrong")
    assert user is None


@pytest.mark.asyncio
async def test_ensure_default_admin_creates(test_db):
    await auth_service.ensure_default_admin(test_db)
    await test_db.commit()
    admin = await auth_service.get_user_by_username(test_db, "admin")
    assert admin is not None
    assert admin.is_admin == 1


@pytest.mark.asyncio
async def test_ensure_default_admin_idempotent(test_db):
    await auth_service.ensure_default_admin(test_db)
    await test_db.commit()
    await auth_service.ensure_default_admin(test_db)
    await test_db.commit()
    # Should still only have one admin
    admin = await auth_service.get_user_by_username(test_db, "admin")
    assert admin is not None
