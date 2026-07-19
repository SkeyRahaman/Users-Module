import hashlib
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime, timezone, timedelta
from sqlalchemy.exc import IntegrityError

from app.database.models import RefreshToken
from app.utils.logger import log
from app.config import Config


class RefreshTokenService:

    @staticmethod
    async def add_refresh_token_to_db(
        db: AsyncSession,
        raw_token: str,
        user_id: int,
        expires_at: datetime | None = None
    ) -> RefreshToken:
        """
        Creates and saves a new RefreshToken for the given user_id.
        Generates a SHA-256 hash of the provided raw_token and sets expiration.

        Returns the RefreshToken instance.
        """
        if expires_at is None:
            expires_at = datetime.now(timezone.utc) + timedelta(days=Config.REFRESH_TOKEN_EXPIRE_DAYS)

        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()

        # Revoke old tokens and add new token in a single transaction for atomicity

        stmt = (
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id, RefreshToken.revoked == False)
            .values(revoked=True)
        )
        await db.execute(stmt)
        log.info("Old Refresh Tokens revoked", user_id=user_id)
        token_entry = RefreshToken(
            user_id=user_id,
            refresh_token_hash=token_hash,
            expires_at=expires_at,
            revoked=False,
            used=False,
        )
        db.add(token_entry)
        log.info("New Refresh Token created", user_id=user_id)
        try:
            await db.commit()
            await db.refresh(token_entry)
            log.info("Refresh Token added to DB", user_id = user_id)
            return token_entry
        except IntegrityError as e:
            log.error("Failed to add Refresh Token to DB: %s", str(e), user_id=user_id)
            await db.rollback()
            return None
    
    @staticmethod
    async def use_refresh_token(db: AsyncSession, token: RefreshToken) -> None:
        """
        Marks the given RefreshToken as used.
        """
        token.used = True
        db.add(token)
        await db.commit()
        await db.refresh(token)
        log.info("Refresh Token used", token_id=token.id)


    @staticmethod
    async def validate_refresh_token(db: AsyncSession, token_hash: str, user_id: int) -> RefreshToken | None:
        """
        Retrieves a RefreshToken by its hash and associated user_id.
        Returns None if not found.
        """
        query = select(RefreshToken).where(
            RefreshToken.refresh_token_hash == token_hash,
            RefreshToken.user_id == user_id
        )
        result = await db.execute(query)
        log.info("Refresh Token retrieved from DB", user_id=user_id, token_hash=token_hash)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def revoke_user_tokens(db: AsyncSession, user_id: int) -> int:
        """
        Revokes all active (not revoked) refresh tokens for the specified user.
        Returns the number of tokens revoked.
        """
        stmt = (
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id, RefreshToken.revoked == False)
            .values(revoked=True)
        )
        result = await db.execute(stmt)
        await db.commit()
        log.info("User's refresh tokens revoked", extra={"user_id": user_id, "revoked_count": result.rowcount})
        return result.rowcount

