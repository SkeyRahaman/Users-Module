from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies.database import get_db
from app.database.services.user_service import UserService
from app.auth.password import PasswordHasher
from app.api.dependencies.auth import create_access_token

router = APIRouter(
    prefix="/auth",
    tags=["AUTHENTICATION"]
)

@router.post("/token", name="token")
def get_token(request: OAuth2PasswordRequestForm = Depends(OAuth2PasswordRequestForm), db:Session = Depends(get_db)):
    user = UserService.get_user_by_username(db=db,username=request.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid Credentials.",
        )
    if user.is_deleted : 
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Inactive user.",
        )
    if not PasswordHasher.verify_password(request.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Credentials.",
        )
    access_token = create_access_token(data={"sub": user.username})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_name": user.username
    }
