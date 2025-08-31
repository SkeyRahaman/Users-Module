import pytest
import uuid
import hashlib
from datetime import datetime, timedelta, timezone
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import PasswordResetToken, User

pytestmark = pytest.mark.asyncio  # marks all tests as async


class TestPasswordResetTokenModel:

    async def test_create_reset_token(self, db_session: AsyncSession, test_user: User):
        raw_token = uuid.uuid4().hex
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

        token = PasswordResetToken(
            user_id=test_user.id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        db_session.add(token)
        await db_session.commit()
        await db_session.refresh(token)

        assert token.id is not None
        assert token.user_id == test_user.id
        assert token.token_hash == token_hash
        assert token.used is False

        # Allow up to 1s difference in datetime due to db rounding
        assert abs((token.expires_at.replace(tzinfo=None) - expires_at.replace(tzinfo=None)).total_seconds()) < 1
        assert token.created_at is not None

    async def test_is_expired_method(self, db_session: AsyncSession, test_user: User):
        expired_token = PasswordResetToken(
            user_id=test_user.id,
            token_hash=hashlib.sha256(uuid.uuid4().hex.encode()).hexdigest(),
            expires_at=datetime.now() - timedelta(minutes=1),
        )
        valid_token = PasswordResetToken(
            user_id=test_user.id,
            token_hash=hashlib.sha256(uuid.uuid4().hex.encode()).hexdigest(),
            expires_at=datetime.now() + timedelta(minutes=10),
        )
        db_session.add_all([expired_token, valid_token])
        await db_session.commit()
        await db_session.refresh(expired_token)
        await db_session.refresh(valid_token)

        assert expired_token.is_expired() is True
        assert valid_token.is_expired() is False

    async def test_token_user_relationship(self, test_user_with_password_reset_token):
        test_user, token = test_user_with_password_reset_token
        assert token.user == test_user

    async def test_duplicate_token_hash_raises_integrity_error(self, db_session: AsyncSession, test_user_with_password_reset_token):
        test_user, token = test_user_with_password_reset_token
        token_hash = token.token_hash

        token2 = PasswordResetToken(
            user_id=test_user.id,
            token_hash=token_hash,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=2),
        )
        db_session.add(token2)
        with pytest.raises(IntegrityError):
            await db_session.commit()
        await db_session.rollback()
