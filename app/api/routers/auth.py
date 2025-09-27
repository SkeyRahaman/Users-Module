from fastapi import APIRouter, Depends, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.database import get_db
from app.database.services.user_service import UserService
from app.database.services.password_reset_token_service import PasswordResetTokenService
from app.database.services.auth_service import AuthService
from app.database.services.refresh_token_service import RefreshTokenService
from app.auth.password_hash import PasswordHasher
from app.schemas.auth import PasswordResetRequest, PasswordResetConfirm
from app.api.dependencies.auth import get_current_user, authenticate_refresh_token
from app.utils.logger import log
from app.database.models import User

router = APIRouter(
    prefix="/auth",
    tags=["AUTHENTICATION"]
)

@router.post("/token", name="token")
async def get_token(
    request: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    user = await UserService.get_user_by_username(db=db, username=request.username)
    if not user or user.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials or inactive user.",
        )

    valid_password = PasswordHasher.verify_password(request.password, user.password)
    if not valid_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials.",
        )
    result = await AuthService.get_new_tokens(db, user)
    log.info("User logged in", extra={"user_id": user.id, "username": user.username})
    return result

@router.post("/password-reset/request", status_code=status.HTTP_200_OK)
async def request_password_reset(
    data: PasswordResetRequest,
    db: AsyncSession = Depends(get_db),
):
    user = await UserService.get_user_by_email(db, data.email)
    if user:
        log.info("Password reset initiated", extra={"user_id": user.id, "email": user.email})
        success = await UserService.reset_user_password(db, user.id)
        if not success:
            log.error("Password reset failed for user id %s", user.id)

    # Always return this response to prevent user enumeration
    return {"message": "If this email is registered, a password reset email has been sent."}


@router.post("/password-reset/confirm", status_code=status.HTTP_200_OK)
async def confirm_password_reset(
    data: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db),
):
    user_id = await PasswordResetTokenService.validate_token(db, data.token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token."
        )
    result = await UserService.update_user_password(db, user_id, data.new_password)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset password. Please try again later."
        )
    log.info("Password reset successful", extra={"user_id": user_id})
    return {"message": "Password has been reset successfully."}

@router.post("/token/refresh", status_code=status.HTTP_200_OK)
async def refresh_access_token(
    refresh_token: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    user = await authenticate_refresh_token(refresh_token, db)
    log.info("Refresh token validated", extra={"user_id": user.id, "username": user.username})
    return await AuthService.get_new_tokens(db, user)

@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    current_user_id = current_user.id
    current_username = current_user.username
    
    success = await RefreshTokenService.revoke_user_tokens(db, current_user_id)
    if success == 0:
        log.error(f"All refresh tokens already revoked for user {current_user_id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="All refresh tokens already revoked."
        )
    log.info("User logged out", extra={"user_id": current_user_id, "username": current_username})
    return {"message": "Successfully logged out."}
    
