"""
FastAPI dependency functions for authentication.
"""

from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models import User
from app.services.auth_service import auth_service


async def get_current_user_optional(
    request: Request, db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """Extract user from JWT in httpOnly cookie. Returns None if not authenticated."""
    token = request.cookies.get("access_token")
    if not token:
        return None
    payload = auth_service.decode_access_token(token)
    if payload is None:
        return None
    username: Optional[str] = payload.get("sub")
    if username is None:
        return None
    user = await auth_service.get_user_by_username(db, username)
    return user


async def get_current_user(
    request: Request, db: AsyncSession = Depends(get_db)
) -> User:
    """Require authenticated user. Raises 401 if not authenticated."""
    user = await get_current_user_optional(request, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return user


async def require_admin(user: User = Depends(get_current_user)) -> User:
    """Require admin user. Raises 403 if not admin."""
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return user
