"""
User settings service for managing per-user labeling preferences.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import UserSettings
from app.db.schemas import UserSettingsUpdate


class UserSettingsService:
    """Service for managing user settings."""

    @staticmethod
    async def get_settings(db: AsyncSession, user_id: int) -> UserSettings:
        result = await db.execute(
            select(UserSettings).where(UserSettings.user_id == user_id)
        )
        settings = result.scalar_one_or_none()
        if settings is None:
            settings = UserSettings(user_id=user_id)
            db.add(settings)
            await db.flush()
        return settings

    @staticmethod
    async def update_settings(
        db: AsyncSession, user_id: int, updates: UserSettingsUpdate
    ) -> UserSettings:
        settings = await UserSettingsService.get_settings(db, user_id)
        update_data = updates.model_dump(exclude_none=True)
        for key, value in update_data.items():
            if key == "auto_advance":
                setattr(settings, key, int(value))
            else:
                setattr(settings, key, value)
        await db.flush()
        return settings


user_settings_service = UserSettingsService()
