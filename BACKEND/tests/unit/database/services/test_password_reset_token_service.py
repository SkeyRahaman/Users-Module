import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta, timezone
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.database.models import User

from app.database.models import PasswordResetToken
from app.database.services.password_reset_token_service import PasswordResetTokenService

@pytest.mark.asyncio
class TestPasswordResetTokenService:

    async def test_create_password_reset_token_success(self, db_session: AsyncSession, test_user: 'User'):
        # Returns: valid PasswordResetToken instance
        token = await PasswordResetTokenService.create_password_reset_token(db_session, test_user.id)
        assert token is not None
        assert token.user_id == test_user.id
        assert isinstance(token.token_hash, str) and len(token.token_hash) == 64  # 32 bytes hex

    async def test_create_password_reset_token_integrity_error(self, db_session: AsyncSession, test_user: 'User', mocker):
        # Simulate IntegrityError
        mocker.patch.object(db_session, 'commit', AsyncMock(side_effect=IntegrityError('msg', 'params', 'orig')))
        token = await PasswordResetTokenService.create_password_reset_token(db_session, test_user.id)
        assert token is None

    async def test_create_password_reset_token_sqlalchemy_error(self, db_session: AsyncSession, test_user: 'User', mocker):
        # Simulate SQLAlchemyError
        mocker.patch.object(db_session, 'commit', AsyncMock(side_effect=SQLAlchemyError()))
        token = await PasswordResetTokenService.create_password_reset_token(db_session, test_user.id)
        assert token is None

    async def test_validate_token_success(self, db_session: AsyncSession, test_user: 'User'):
        # Create a new token (active, unused, unexpired)
        token = await PasswordResetTokenService.create_password_reset_token(db_session, test_user.id)
        assert token is not None
        result = await PasswordResetTokenService.validate_token(db_session, token.token_hash)
        assert result == test_user.id
        # Reuse should fail (token.used == True)
        reused = await PasswordResetTokenService.validate_token(db_session, token.token_hash)
        assert reused is None

    async def test_validate_token_expired(self, db_session: AsyncSession, test_user: 'User'):
        # Create an expired token manually
        expired_token = PasswordResetToken(
            user_id=test_user.id,
            token_hash="expiredtoken",
            used=False,
            expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
            created_at=datetime.now(timezone.utc) - timedelta(hours=2),
        )
        db_session.add(expired_token)
        await db_session.commit()
        result = await PasswordResetTokenService.validate_token(db_session, "expiredtoken")
        assert result is None

    async def test_validate_token_already_used(self, db_session: AsyncSession, test_user: 'User'):
        # Create a token and mark as used
        used_token = PasswordResetToken(
            user_id=test_user.id,
            token_hash="usedtoken",
            used=True,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
            created_at=datetime.now(timezone.utc) - timedelta(hours=2),
        )
        db_session.add(used_token)
        await db_session.commit()
        result = await PasswordResetTokenService.validate_token(db_session, "usedtoken")
        assert result is None

    async def test_validate_token_not_found(self, db_session: AsyncSession):
        # Random non-existent token hash
        result = await PasswordResetTokenService.validate_token(db_session, "nonexistenttoken")
        assert result is None
