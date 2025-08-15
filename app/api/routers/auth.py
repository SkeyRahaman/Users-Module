from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.database import get_db
from app.database.services.user_service import UserService
from app.auth.password_hash import PasswordHasher
from app.api.dependencies.auth import create_access_token

router = APIRouter(
    prefix="/auth",
    tags=["AUTHENTICATION"]
)

@router.post("/token", name="token")
async def get_token(
    request: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    # Assume UserService.get_user_by_username is async
    user = await UserService.get_user_by_username(db=db, username=request.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid Credentials.",
        )
    if user.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Inactive user.",
        )

    valid_password = PasswordHasher.verify_password(request.password, user.password)
    if not valid_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Credentials.",
        )
    # Usually create_access_token is synchronous, if not change as needed
    access_token = create_access_token(data={"sub": user.username})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_name": user.username
    }
