from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.exceptions import HTTPException
from typing import Optional
from datetime import timedelta
from sqlalchemy.orm import Session
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError, DecodeError


from app.api.dependencies.database import get_db
from app.config import Config
from app.database.services.user_service import UserService
from app.database.models.user import User
from app.auth.jwt import JWTManager

oauth2_scheme =  OAuth2PasswordBearer(tokenUrl = Config.URL_PREFIX+"auth/token")

def create_access_token(data: dict, expire_delta: Optional[timedelta] = None):
    """
    A small wrapper around JWTManager.encode for cleaner usage.
    """
    return JWTManager.encode(data, expire_delta)


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = JWTManager.decode(token)
        user_name = payload.get("sub")
        if not user_name:
            raise credentials_exception
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except (InvalidTokenError, DecodeError, UnicodeDecodeError):
        # Covers invalid signature, corrupt payload, etc.
        raise credentials_exception

    user = await UserService.get_user_by_username(db=db, username=user_name)
    if not user:
        raise credentials_exception

    return user

def require_permission(required_scope: str):
    async def dependency(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
    ):
        user_permissions = await UserService.get_all_permissions_for_user(db=db, user_id=current_user.id)
        if not user_permissions or required_scope not in {i.name for i in user_permissions}:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permission: {required_scope}"
            )
    return Depends(dependency)
