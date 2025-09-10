from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.database.services.refresh_token_service import RefreshTokenService
from app.api.dependencies.auth import create_access_token, create_refresh_token
from app.utils.logger import log
from app.database.models.user import User



class AuthService:

    @staticmethod
    async def get_new_tokens(db: AsyncSession, user: User) -> dict:
        """
        Generates new access and refresh tokens for the given user.
        Revokes any existing refresh tokens and stores the new one in the database.

        Returns a dictionary containing the new access token, refresh token, token type, and username.
        """
        access_token = create_access_token(data={"sub": user.username})

        refresh_token = create_refresh_token(data={"sub": user.username})

        refresh_token_entry = await RefreshTokenService.add_refresh_token_to_db(
            db=db,
            raw_token=refresh_token,
            user_id=user.id,
        )

        if not refresh_token_entry:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create refresh token. Please try again later."
            )

        log.info("Access and refresh tokens generated", user_id=user.id, username=user.username)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user_name": user.username,
        }