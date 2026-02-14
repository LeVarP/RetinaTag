"""
Authentication API router. Handles login, logout, status check, and admin-only registration.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.database import get_db
from app.db.models import User
from app.db.schemas import (
    AuthStatusResponse,
    UserLogin,
    UserRegister,
    UserResponse,
)
from app.api.dependencies import get_current_user_optional, require_admin
from app.services.auth_service import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=UserResponse)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    """Authenticate user and set httpOnly JWT cookie."""
    user = await auth_service.authenticate_user(
        db, credentials.username, credentials.password
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    token = auth_service.create_access_token({"sub": user.username})

    response = JSONResponse(
        content=UserResponse.model_validate(user, from_attributes=True).model_dump(
            mode="json"
        )
    )
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,  # Set True in production with HTTPS
        samesite="lax",
        max_age=settings.jwt_access_token_expire_minutes * 60,
        path="/",
    )
    return response


@router.post("/logout")
async def logout():
    """Clear the auth cookie."""
    response = JSONResponse(content={"message": "Logged out"})
    response.delete_cookie("access_token", path="/")
    return response


@router.get("/me", response_model=AuthStatusResponse)
async def get_auth_status(
    user: User | None = Depends(get_current_user_optional),
):
    """Check current authentication status."""
    if user is None:
        return AuthStatusResponse(authenticated=False, user=None)
    return AuthStatusResponse(
        authenticated=True,
        user=UserResponse.model_validate(user, from_attributes=True),
    )


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    """Register a new user (admin-only)."""
    existing = await auth_service.get_user_by_username(db, user_data.username)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken",
        )
    user = await auth_service.create_user(db, user_data.username, user_data.password)
    return UserResponse.model_validate(user, from_attributes=True)
