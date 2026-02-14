"""
Authentication service for password hashing, JWT tokens, and user management.
"""

from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.models import User, UserSettings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Service for authentication operations."""

    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + (
            expires_delta or timedelta(minutes=settings.jwt_access_token_expire_minutes)
        )
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

    @staticmethod
    def decode_access_token(token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
            return payload
        except JWTError:
            return None

    @staticmethod
    async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
        result = await db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    @staticmethod
    async def create_user(
        db: AsyncSession, username: str, password: str, is_admin: bool = False
    ) -> User:
        user = User(
            username=username,
            hashed_password=pwd_context.hash(password),
            is_admin=int(is_admin),
        )
        db.add(user)
        await db.flush()

        user_settings = UserSettings(user_id=user.id)
        db.add(user_settings)
        await db.flush()

        return user

    @staticmethod
    async def authenticate_user(
        db: AsyncSession, username: str, password: str
    ) -> Optional[User]:
        user = await AuthService.get_user_by_username(db, username)
        if user is None:
            return None
        if not pwd_context.verify(password, user.hashed_password):
            return None
        return user

    @staticmethod
    async def change_password(
        db: AsyncSession, user_id: int, current_password: str, new_password: str
    ) -> bool:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user is None:
            return False
        if not pwd_context.verify(current_password, user.hashed_password):
            return False
        user.hashed_password = pwd_context.hash(new_password)
        await db.flush()
        return True

    @staticmethod
    async def ensure_default_admin(db: AsyncSession) -> None:
        """Create default admin user if no users exist."""
        result = await db.execute(select(func.count()).select_from(User))
        count = result.scalar()
        if count == 0:
            await AuthService.create_user(
                db,
                username=settings.default_admin_username,
                password=settings.default_admin_password,
                is_admin=True,
            )
            print(f"+ Default admin user created: {settings.default_admin_username}")


auth_service = AuthService()
