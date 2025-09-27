import hashlib
from fastapi import Depends, status, Header
from fastapi.security import OAuth2PasswordBearer
from fastapi.exceptions import HTTPException
from typing import Optional
from datetime import timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError, DecodeError
from datetime import datetime, timezone


from app.api.dependencies.database import get_db
from app.config import Config
from app.database.services.user_service import UserService
from app.database.services.refresh_token_service import RefreshTokenService 
from app.database.models.user import User
from app.auth.jwt import JWTManager
from app.utils.logger import log

oauth2_scheme =  OAuth2PasswordBearer(tokenUrl = Config.URL_PREFIX+"auth/token")

def create_access_token(data: dict, expire_delta: Optional[timedelta] = None):
    """
    A small wrapper around JWTManager.encode for cleaner usage.
    """
    return JWTManager.encode_access_token(data, expire_delta)

def create_refresh_token(data: dict, expire_delta: Optional[timedelta] = None):
    """
    A small wrapper around JWTManager.encode for cleaner usage.
    """
    return JWTManager.encode_refresh_token(data, expire_delta)

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = JWTManager.decode_access_token(token)
        user_name = payload.get("sub")
        if not user_name:
            log.error("Invalid access token payload")
            raise credentials_exception
    except ExpiredSignatureError:
        log.error("Access token has expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except (InvalidTokenError, DecodeError, UnicodeDecodeError):
        # Covers invalid signature, corrupt payload, etc.
        log.error("Invalid access token or unable to decode")
        raise credentials_exception

    user = await UserService.get_user_by_username(db=db, username=user_name)
    if not user:
        raise credentials_exception

    return user

async def authenticate_refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db)
    ) -> User:
    """
    Validates the provided refresh token and returns the associated user if valid.
    Raises HTTPException if the token is invalid, expired, revoked, or already used.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate refresh token.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = JWTManager.decode_refresh_token(refresh_token)
        user_name = payload.get("sub")
        if not user_name:
            log.error("Invalid refresh token payload")
            raise credentials_exception
    except ExpiredSignatureError:
        log.error("Refresh token has expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except (InvalidTokenError, DecodeError, UnicodeDecodeError):
        log.error("Invalid refresh token")
        raise credentials_exception

    user = await UserService.get_user_by_username(db=db, username=user_name)
    if not user or user.is_deleted:
        log.error("User not found or is deleted", extra={"username": user_name})
        raise credentials_exception

    # Verify the token exists in DB and is valid
    token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
    refresh_token_entry = await RefreshTokenService.validate_refresh_token(db, token_hash, user.id)
    if not refresh_token_entry:
        log.error("Invalid refresh token hash or user mismatch", extra={"username": user_name})
        raise credentials_exception
    if refresh_token_entry.revoked:
        log.error("Refresh token has been revoked", extra={"token_id": refresh_token_entry.id})
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been revoked.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if refresh_token_entry.used:
        log.error("Refresh token has already been used", extra={"token_id": refresh_token_entry.id})
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has already been used.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def require_permission(required_scope: str):
    async def dependency(
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
    ):
        user_permissions = await UserService.get_all_permissions_for_user(db=db, user_id=current_user.id)
        if not user_permissions or required_scope not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permission: {required_scope}"
            )
    return Depends(dependency)
