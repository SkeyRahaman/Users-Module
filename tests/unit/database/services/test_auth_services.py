import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import HTTPException

from app.database.services.auth_service import AuthService 

@pytest.mark.asyncio
class TestAuthService:

    async def test_get_new_tokens_success(self):
        # Arrange
        mock_db = MagicMock()
        mock_user = MagicMock()
        mock_user.id = 123
        mock_user.username = "alice"

        example_access_token = "access.token.value"
        example_refresh_token = "refresh.token.value"
        mock_refresh_token_entry = MagicMock()

        with patch(
            "app.database.services.auth_service.create_access_token",
            return_value=example_access_token
        ) as mock_create_access_token, patch(
            "app.database.services.auth_service.create_refresh_token",
            return_value=example_refresh_token
        ) as mock_create_refresh_token, patch(
            "app.database.services.auth_service.RefreshTokenService.add_refresh_token_to_db",
            new_callable=AsyncMock,
            return_value=mock_refresh_token_entry
        ) as mock_add_refresh_token, patch(
            "app.database.services.auth_service.log"
        ) as mock_log:
            # Act
            tokens = await AuthService.get_new_tokens(mock_db, mock_user)

            # Assert
            assert tokens == {
                "access_token": example_access_token,
                "refresh_token": example_refresh_token,
                "token_type": "bearer",
                "user_name": "alice"
            }
            mock_create_access_token.assert_called_once_with(data={"sub": "alice"})
            mock_create_refresh_token.assert_called_once_with(data={"sub": "alice"})
            mock_add_refresh_token.assert_awaited_once_with(
                db=mock_db,
                raw_token=example_refresh_token,
                user_id=123,
            )
            mock_log.info.assert_called_once()
    
    async def test_get_new_tokens_refresh_token_fail(self):
        # Arrange
        mock_db = MagicMock()
        mock_user = MagicMock()
        mock_user.id = 99
        mock_user.username = "bob"
        example_access_token = "access.token.value"
        example_refresh_token = "refresh.token.value"

        with patch(
            "app.database.services.auth_service.create_access_token",
            return_value=example_access_token
        ), patch(
            "app.database.services.auth_service.create_refresh_token",
            return_value=example_refresh_token
        ), patch(
            "app.database.services.auth_service.RefreshTokenService.add_refresh_token_to_db",
            new_callable=AsyncMock,
            return_value=None
        ):
            # Act & Assert
            with pytest.raises(HTTPException) as exc:
                await AuthService.get_new_tokens(mock_db, mock_user)
            assert exc.value.status_code == 500
            assert "Failed to create refresh token" in exc.value.detail
