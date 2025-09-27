import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone, timedelta

from app.database.services.refresh_token_service import RefreshTokenService
from app.database.models import RefreshToken


@pytest.mark.asyncio
class TestRefreshTokenService:

    @pytest.fixture
    def mock_db(self):
        return AsyncMock()

    @pytest.fixture
    def mock_token(self):
        token = MagicMock(spec=RefreshToken)
        token.id = 10
        token.user_id = 1
        token.refresh_token_hash = "abc123hash"
        token.revoked = False
        token.used = False
        return token

    async def test_add_refresh_token_to_db_success(self, mock_db):
        raw_token = "sometoken"
        user_id = 1
        with patch('app.database.services.refresh_token_service.log') as mock_log, \
             patch('app.database.services.refresh_token_service.Config') as mock_config:
            mock_config.REFRESH_TOKEN_EXPIRE_DAYS = 30
            mock_db.execute = AsyncMock()
            mock_db.add = MagicMock()
            mock_db.commit = AsyncMock()
            mock_db.refresh = AsyncMock()

            result = await RefreshTokenService.add_refresh_token_to_db(mock_db, raw_token, user_id)

            assert isinstance(result, RefreshToken)
            mock_db.execute.assert_awaited_once()
            mock_db.add.assert_called_once()
            mock_db.commit.assert_awaited_once()
            mock_db.refresh.assert_awaited_once()

    async def test_add_refresh_token_to_db_with_expires_at(self, mock_db):
        raw_token = "sometoken"
        user_id = 1
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        with patch('app.database.services.refresh_token_service.log'):
            mock_db.execute = AsyncMock()
            mock_db.add = MagicMock()
            mock_db.commit = AsyncMock()
            mock_db.refresh = AsyncMock()

            result = await RefreshTokenService.add_refresh_token_to_db(mock_db, raw_token, user_id, expires_at)

            assert isinstance(result, RefreshToken)
            assert result.expires_at == expires_at

    async def test_add_refresh_token_to_db_integrity_error(self, mock_db):
        raw_token = "sometoken"
        user_id = 1
        with patch('app.database.services.refresh_token_service.Config') as mock_config:
            mock_config.REFRESH_TOKEN_EXPIRE_DAYS = 30
            mock_db.execute = AsyncMock()
            mock_db.add = MagicMock()
            mock_db.commit = AsyncMock(side_effect=IntegrityError("", None, None))
            mock_db.rollback = AsyncMock()

            result = await RefreshTokenService.add_refresh_token_to_db(mock_db, raw_token, user_id)

            assert result is None
            mock_db.rollback.assert_awaited_once()

    async def test_use_refresh_token(self, mock_db, mock_token):
        with patch('app.database.services.refresh_token_service.log') as mock_log:
            mock_db.add = MagicMock()
            mock_db.commit = AsyncMock()
            mock_db.refresh = AsyncMock()

            await RefreshTokenService.use_refresh_token(mock_db, mock_token)

            assert mock_token.used is True
            mock_db.add.assert_called_once_with(mock_token)
            mock_db.commit.assert_awaited_once()
            mock_db.refresh.assert_awaited_once_with(mock_token)
            mock_log.info.assert_called_once()

    async def test_validate_refresh_token_found(self, mock_db, mock_token):
        token_hash = "somehash"
        user_id = 1
        execute_result = MagicMock()
        execute_result.scalar_one_or_none.return_value = mock_token
        mock_db.execute = AsyncMock(return_value=execute_result)
        
        with patch('app.database.services.refresh_token_service.log'):
            token = await RefreshTokenService.validate_refresh_token(mock_db, token_hash, user_id)
            assert token == mock_token
            mock_db.execute.assert_awaited_once()


    async def test_validate_refresh_token_not_found(self, mock_db):
        token_hash = "notfound"
        user_id = 1
        
        execute_result = MagicMock()
        execute_result.scalar_one_or_none.return_value = None
        
        mock_db.execute = AsyncMock(return_value=execute_result)
        
        with patch('app.database.services.refresh_token_service.log'):
            token = await RefreshTokenService.validate_refresh_token(mock_db, token_hash, user_id)
            assert token is None
            mock_db.execute.assert_awaited_once()


    async def test_revoke_user_tokens_success(self, mock_db):
        user_id = 1
        revoked_count = 3
        mock_result = AsyncMock()
        mock_result.rowcount = revoked_count
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_db.commit = AsyncMock()
        with patch('app.database.services.refresh_token_service.log') as mock_log:
            result = await RefreshTokenService.revoke_user_tokens(mock_db, user_id)
            assert result == revoked_count
            mock_db.execute.assert_awaited_once()
            mock_db.commit.assert_awaited_once()
            mock_log.info.assert_called_once()

    async def test_revoke_user_tokens_no_tokens_found(self, mock_db):
        user_id = 1
        revoked_count = 0
        mock_result = AsyncMock()
        mock_result.rowcount = revoked_count
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_db.commit = AsyncMock()
        with patch('app.database.services.refresh_token_service.log') as mock_log:
            result = await RefreshTokenService.revoke_user_tokens(mock_db, user_id)
            assert result == revoked_count
            mock_db.execute.assert_awaited_once()
            mock_db.commit.assert_awaited_once()
            mock_log.info.assert_called_once()
