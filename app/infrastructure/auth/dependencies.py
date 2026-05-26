"""FastAPI dependencies for authentication.

Provides get_current_user dependency that validates JWT tokens
and returns the authenticated user from the database.
"""

from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.auth.jwt_service import JWTService
from app.infrastructure.database.models.user import UserModel
from app.infrastructure.database.session import get_db
from app.schemas.user import UserResponseSchema

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> UserResponseSchema:
    """Validate JWT token and return the authenticated user.

    Args:
        token: JWT from the Authorization header.
        db: Async database session.

    Returns:
        UserResponseSchema with user data.

    Raises:
        HTTPException 401: If token is invalid or user not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = JWTService.verify_token(token)
    if token_data is None:
        raise credentials_exception

    result = await db.execute(
        select(UserModel).where(UserModel.username == token_data.username)
    )
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
        )

    return UserResponseSchema.model_validate(user)
