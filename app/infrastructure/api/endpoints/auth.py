"""Authentication endpoint — POST /token.

Implements OAuth2 Password Flow for JWT token issuance.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.auth.jwt_service import JWTService
from app.infrastructure.auth.password_service import PasswordService
from app.infrastructure.database.models.user import UserModel
from app.infrastructure.database.session import get_db
from app.schemas.user import TokenSchema

router = APIRouter(tags=["auth"])


@router.post("/token", response_model=TokenSchema)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
) -> TokenSchema:
    """Authenticate user and return a JWT access token.

    Uses OAuth2 Password Flow — accepts username/password via
    form-encoded body and returns a bearer token on success.
    """
    result = await db.execute(
        select(UserModel).where(UserModel.username == form_data.username)
    )
    user = result.scalar_one_or_none()

    if user is None or not PasswordService.verify_password(
        form_data.password, user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
        )

    access_token = JWTService.create_token(username=user.username)
    return TokenSchema(access_token=access_token)
