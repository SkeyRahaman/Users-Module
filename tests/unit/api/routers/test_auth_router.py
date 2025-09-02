import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from fastapi import HTTPException, status

from app.api.routers import auth as auth_router
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
        monkeypatch.setattr(
            "app.database.services.user_service.UserService.get_user_by_username",
            AsyncMock(return_value=test_user)
        )
        monkeypatch.setattr(PasswordHasher, "verify_password", lambda plain, hashed: True)
        monkeypatch.setattr(
            "app.api.routers.auth.create_access_token",
            lambda data: "mocked_token"
        )

        monkeypatch.setattr(
            "app.utils.logger.log.info",
            lambda *args, **kwargs: None
        )

        class Request:
            username = test_user.username
            password = "secret"

        result = await auth_router.get_token(request=Request(), db=MagicMock())
        assert result["access_token"] == "mocked_token"
        assert result["token_type"] == "bearer"
        assert result["user_name"] == test_user.username

    async def test_get_token_user_not_found(self, monkeypatch):
        monkeypatch.setattr(
            "app.database.services.user_service.UserService.get_user_by_username",
            AsyncMock(return_value=None)
        )

        class Request:
            username = "nonexistent"
            password = "secret"

        with pytest.raises(HTTPException) as exc:
            await auth_router.get_token(request=Request(), db=MagicMock())
        assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid Credentials" in exc.value.detail

    async def test_get_token_inactive_user(self, monkeypatch, test_user):
        test_user.is_deleted = True
        monkeypatch.setattr(
            "app.database.services.user_service.UserService.get_user_by_username",
            AsyncMock(return_value=test_user)
        )

        class Request:
            username = test_user.username
            password = "secret"

        with pytest.raises(HTTPException) as exc:
            await auth_router.get_token(request=Request(), db=MagicMock())
        assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Inactive user" in exc.value.detail

    async def test_get_token_invalid_password(self, monkeypatch, test_user):
        monkeypatch.setattr(
            "app.database.services.user_service.UserService.get_user_by_username",
            AsyncMock(return_value=test_user)
        )
        monkeypatch.setattr(PasswordHasher, "verify_password", lambda plain, hashed: False)

        class Request:
            username = test_user.username
            password = "wrongpass"

        with pytest.raises(HTTPException) as exc:
            await auth_router.get_token(request=Request(), db=MagicMock())
        assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid Credentials" in exc.value.detail

    async def test_request_password_reset_existing_email(self, monkeypatch):
        fake_user = MagicMock()
        fake_user.id = 1
        fake_user.email = "test@example.com"

        monkeypatch.setattr(
            "app.database.services.user_service.UserService.get_user_by_email",
            AsyncMock(return_value=fake_user)
        )
        monkeypatch.setattr(
            "app.database.services.user_service.UserService.reset_user_password",
            AsyncMock(return_value=True)
        )
        monkeypatch.setattr(
            "app.utils.logger.log.info",
            lambda *args, **kwargs: None
        )
        monkeypatch.setattr(
            "app.utils.logger.log.error",
            lambda *args, **kwargs: None
        )

        class Data:
            email = "test@example.com"

        response = await auth_router.request_password_reset(Data(), db=MagicMock())
        assert "message" in response
        assert "password reset email" in response["message"].lower()

    async def test_request_password_reset_non_existing_email(self, monkeypatch):
        monkeypatch.setattr(
            "app.database.services.user_service.UserService.get_user_by_email",
            AsyncMock(return_value=None)
        )

        class Data:
            email = "noone@example.com"

        response = await auth_router.request_password_reset(Data(), db=MagicMock())
        assert "message" in response
        assert "password reset email" in response["message"].lower()

    async def test_confirm_password_reset_success(self, monkeypatch):
        monkeypatch.setattr(
            "app.database.services.password_reset_token_service.PasswordResetTokenService.validate_token",
            AsyncMock(return_value=1)
        )
        monkeypatch.setattr(
            "app.database.services.user_service.UserService.update_user_password",
            AsyncMock(return_value=True)
        )
        monkeypatch.setattr(
            "app.utils.logger.log.info",
            lambda *args, **kwargs: None
        )

        class Data:
            token = "validtoken"
            new_password = "newsecurepassword"

        response = await auth_router.confirm_password_reset(Data(), db=MagicMock())
        assert response == {"message": "Password has been reset successfully."}

    async def test_confirm_password_reset_invalid_token(self, monkeypatch):
        monkeypatch.setattr(
            "app.database.services.password_reset_token_service.PasswordResetTokenService.validate_token",
            AsyncMock(return_value=None)
        )

        class Data:
            token = "invalidtoken"
            new_password = "whatever"

        with pytest.raises(HTTPException) as exc:
            await auth_router.confirm_password_reset(Data(), db=MagicMock())
        assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid or expired token" in exc.value.detail

    async def test_confirm_password_reset_update_failure(self, monkeypatch):
        monkeypatch.setattr(
            "app.database.services.password_reset_token_service.PasswordResetTokenService.validate_token",
            AsyncMock(return_value=1)
        )
        monkeypatch.setattr(
            "app.database.services.user_service.UserService.update_user_password",
            AsyncMock(return_value=False)
        )

        class Data:
            token = "validtoken"
            new_password = "newpassword"

        with pytest.raises(HTTPException) as exc:
            await auth_router.confirm_password_reset(Data(), db=MagicMock())
        assert exc.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Failed to reset password" in exc.value.detail
