"""Tests for user settings service."""

import pytest
from app.services.auth_service import auth_service
from app.services.user_settings_service import user_settings_service
from app.db.schemas import UserSettingsUpdate


@pytest.mark.asyncio
async def test_get_settings_creates_defaults(test_db):
    user = await auth_service.create_user(test_db, "testuser", "pass")
    await test_db.commit()

    settings = await user_settings_service.get_settings(test_db, user.id)
    assert settings.auto_advance == 1
    assert settings.hotkey_healthy == "a"
    assert settings.hotkey_unhealthy == "s"


@pytest.mark.asyncio
async def test_update_settings_partial(test_db):
    user = await auth_service.create_user(test_db, "updater", "pass")
    await test_db.commit()

    updates = UserSettingsUpdate(auto_advance=False)
    settings = await user_settings_service.update_settings(test_db, user.id, updates)
    await test_db.commit()

    assert settings.auto_advance == 0
    assert settings.hotkey_healthy == "a"  # Unchanged


@pytest.mark.asyncio
async def test_update_all_settings(test_db):
    user = await auth_service.create_user(test_db, "fullupdate", "pass")
    await test_db.commit()

    updates = UserSettingsUpdate(
        auto_advance=False,
        hotkey_healthy="d",
        hotkey_unhealthy="f",
        hotkey_next="ArrowDown",
        hotkey_prev="ArrowUp",
    )
    settings = await user_settings_service.update_settings(test_db, user.id, updates)
    await test_db.commit()

    assert settings.auto_advance == 0
    assert settings.hotkey_healthy == "d"
    assert settings.hotkey_unhealthy == "f"
    assert settings.hotkey_next == "ArrowDown"
    assert settings.hotkey_prev == "ArrowUp"
