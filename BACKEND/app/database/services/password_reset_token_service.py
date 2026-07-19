from sqlalchemy import select
import secrets
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.database.models import PasswordResetToken
from app.config import Config


class PasswordResetTokenService:

    @staticmethod
    async def validate_token(db: AsyncSession, token_hash: str) -> bool:
        """
        Checks if the provided token_hash corresponds to a valid, unused, and unexpired PasswordResetToken.
        Returns user associated with the token if valid, None otherwise.
        """
        query = select(PasswordResetToken).where(
            PasswordResetToken.token_hash == token_hash,
            PasswordResetToken.used == False,
            PasswordResetToken.expires_at > datetime.now(timezone.utc)
        )
        result = await db.execute(query)
        token = result.scalar_one_or_none()
        if not token:
            return None
        token.used = True
        db.add(token)
        await db.commit()
        await db.refresh(token)
        return token.user_id
    
    @staticmethod
    async def create_password_reset_token(
        db: AsyncSession,
        user_id: int,
        expiration_hours: int = Config.PASSWORD_REST_TOKEN_EXPIRE_HOURS
    ) -> PasswordResetToken | None:
        """
        Creates and saves a new PasswordResetToken for the given user_id.
        Generates a secure random token hash and sets expiration.

        Returns the PasswordResetToken instance or None if an error occurs.
        """
        try:
            # Generate a secure random token hash (hex string)
            raw_token = secrets.token_bytes(32)
            token_hash = raw_token.hex()

            expires_at = datetime.now(timezone.utc) + timedelta(hours=expiration_hours)

            token_entry = PasswordResetToken(
                user_id=user_id,
                token_hash=token_hash,
                expires_at=expires_at,
                used=False,
                created_at=datetime.now(timezone.utc)
            )
            db.add(token_entry)
            await db.commit()
            await db.refresh(token_entry)
            return token_entry
        except (IntegrityError, SQLAlchemyError):
            await db.rollback()
            return None
