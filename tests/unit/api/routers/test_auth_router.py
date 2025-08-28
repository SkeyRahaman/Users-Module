import pytest
from unittest.mock import MagicMock
from datetime import timedelta
from fastapi import HTTPException, status

from app.api.routers.auth import get_token
from app.auth.password_hash import PasswordHasher

@pytest.mark.asyncio
class TestAuthRouter:
    @pytest.fixture
    def test_user(self):
        class User:
            def __init__(self):
                self.id = 1
                self.username = "testuser"
                self.password = PasswordHasher.get_password_hash("secret")
                self.is_deleted = False
        return User()

    async def test_get_token_success(self, monkeypatch, test_user):
        # Mock UserService.get_user_by_username to return test_user
        async def _mock_get_user_by_username(*args, **kwargs):
            return test_user

        monkeypatch.setattr(
            "app.database.services.user_service.UserService.get_user_by_username",
            _mock_get_user_by_username
        )

        # Mock PasswordHasher.verify_password to return True
        monkeypatch.setattr(PasswordHasher, "verify_password", lambda plain, hashed: True)

        class Request:
            username = test_user.username
            password = "secret"

        token_response = await get_token(request=Request(), db=MagicMock())
        
        assert "access_token" in token_response
        assert token_response["token_type"] == "bearer"
        assert token_response["user_name"] == test_user.username

    async def test_get_token_invalid_user(self, monkeypatch):
        async def _mock_get_user_by_username(*args, **kwargs):
            return None

        monkeypatch.setattr(
            "app.database.services.user_service.UserService.get_user_by_username",
            _mock_get_user_by_username
        )

        class Request:
            username = "invalid"
            password = "secret"

        with pytest.raises(HTTPException) as exc_info:
            await get_token(request=Request(), db=MagicMock())
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid Credentials" in exc_info.value.detail

    async def test_get_token_inactive_user(self, monkeypatch, test_user):
        test_user.is_deleted = True
        async def _mock_get_user_by_username(*args, **kwargs):
            return test_user

        monkeypatch.setattr(
            "app.database.services.user_service.UserService.get_user_by_username",
            _mock_get_user_by_username
        )

        class Request:
            username = test_user.username
            password = "secret"

        with pytest.raises(HTTPException) as exc_info:
            await get_token(request=Request(), db=MagicMock())
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Inactive user" in exc_info.value.detail

    async def test_get_token_invalid_password(self, monkeypatch, test_user):
        async def _mock_get_user_by_username(*args, **kwargs):
            return test_user

        monkeypatch.setattr(
            "app.database.services.user_service.UserService.get_user_by_username",
            _mock_get_user_by_username
        )
        monkeypatch.setattr(PasswordHasher, "verify_password", lambda plain, hashed: False)

        class Request:
            username = test_user.username
            password = "wrongpassword"

        with pytest.raises(HTTPException) as exc_info:
            await get_token(request=Request(), db=MagicMock())
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid Credentials" in exc_info.value.detail
