"""
Users API router. Handles user settings and password management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models import User
from app.db.schemas import (
    PasswordChange,
    UserSettingsResponse,
    UserSettingsUpdate,
)
from app.api.dependencies import get_current_user
from app.services.user_settings_service import user_settings_service
from app.services.auth_service import auth_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me/settings", response_model=UserSettingsResponse)
async def get_my_settings(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current user's settings."""
    settings = await user_settings_service.get_settings(db, user.id)
    return UserSettingsResponse(
        auto_advance=bool(settings.auto_advance),
        hotkey_healthy=settings.hotkey_healthy,
        hotkey_unhealthy=settings.hotkey_unhealthy,
        hotkey_next=settings.hotkey_next,
        hotkey_prev=settings.hotkey_prev,
    )


@router.put("/me/settings", response_model=UserSettingsResponse)
async def update_my_settings(
    updates: UserSettingsUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update current user's settings (partial update)."""
    settings = await user_settings_service.update_settings(db, user.id, updates)
    return UserSettingsResponse(
        auto_advance=bool(settings.auto_advance),
        hotkey_healthy=settings.hotkey_healthy,
        hotkey_unhealthy=settings.hotkey_unhealthy,
        hotkey_next=settings.hotkey_next,
        hotkey_prev=settings.hotkey_prev,
    )


@router.post("/me/password")
async def change_my_password(
    data: PasswordChange,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Change current user's password."""
    success = await auth_service.change_password(
        db, user.id, data.current_password, data.new_password
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )
    return {"message": "Password changed successfully"}
