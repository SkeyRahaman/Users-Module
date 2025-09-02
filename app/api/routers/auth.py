from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession


from app.api.dependencies.database import get_db
from app.database.services.user_service import UserService
from app.database.services.password_reset_token_service import PasswordResetTokenService
from app.auth.password_hash import PasswordHasher
from app.schemas.auth import PasswordResetRequest, PasswordResetConfirm
from app.api.dependencies.auth import create_access_token, require_permission
from app.utils.logger import log

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
    log.info("Token generated", user_id=user.id, username=user.username)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_name": user.username
    }

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

