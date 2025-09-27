import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException, status
from app.api.routers import auth as authrouter
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
        monkeypatch.setattr('app.database.services.user_service.UserService.get_user_by_username', AsyncMock(return_value=test_user))
        monkeypatch.setattr(PasswordHasher, "verify_password", lambda plain, hashed: True)
        mocked_tokens = {"access_token": "mockedtoken", "token_type": "bearer", "username": test_user.username}
        monkeypatch.setattr('app.database.services.auth_service.AuthService.get_new_tokens', AsyncMock(return_value=mocked_tokens))
        monkeypatch.setattr('app.utils.logger.log.info', lambda *args, **kwargs: None)

        class Request:
            username = test_user.username
            password = "secret"

        result = await authrouter.get_token(request=Request(), db=AsyncMock())
        assert result == mocked_tokens

    async def test_get_token_user_not_found(self, monkeypatch):
        monkeypatch.setattr('app.database.services.user_service.UserService.get_user_by_username', AsyncMock(return_value=None))

        class Request:
            username = "nonexistent"
            password = "secret"

        with pytest.raises(HTTPException) as exc:
            await authrouter.get_token(request=Request(), db=MagicMock())
        assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid credentials or inactive user" in exc.value.detail

    async def test_get_token_inactive_user(self, monkeypatch, test_user):
        test_user.is_deleted = True
        monkeypatch.setattr('app.database.services.user_service.UserService.get_user_by_username', AsyncMock(return_value=test_user))

        class Request:
            username = test_user.username
            password = "secret"

        # Use AsyncMock() for db to support await
        with pytest.raises(HTTPException) as exc:
            await authrouter.get_token(request=Request(), db=AsyncMock())
        assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "inactive user" in exc.value.detail.lower()


    async def test_get_token_invalid_password(self, monkeypatch, test_user):
        monkeypatch.setattr('app.database.services.user_service.UserService.get_user_by_username', AsyncMock(return_value=test_user))
        monkeypatch.setattr(PasswordHasher, "verify_password", lambda plain, hashed: False)

        class Request:
            username = test_user.username
            password = "wrongpass"

        with pytest.raises(HTTPException) as exc:
            await authrouter.get_token(request=Request(), db=MagicMock())
        assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid credentials" in exc.value.detail

    async def test_password_reset_request_existing_email(self, monkeypatch):
        fake_user = MagicMock()
        fake_user.id = 1
        fake_user.email = "test@example.com"
        monkeypatch.setattr('app.database.services.user_service.UserService.get_user_by_email', AsyncMock(return_value=fake_user))
        monkeypatch.setattr('app.database.services.user_service.UserService.reset_user_password', AsyncMock(return_value=True))
        monkeypatch.setattr('app.utils.logger.log.info', lambda *args, **kwargs: None)
        monkeypatch.setattr('app.utils.logger.log.error', lambda *args, **kwargs: None)

        class Data:
            email = "test@example.com"

        response = await authrouter.request_password_reset(data=Data(), db=AsyncMock())
        assert "password reset email" in response["message"].lower()

    async def test_password_reset_request_non_existing_email(self, monkeypatch):
        monkeypatch.setattr('app.database.services.user_service.UserService.get_user_by_email', AsyncMock(return_value=None))

        class Data:
            email = "noone@example.com"

        response = await authrouter.request_password_reset(data=Data(), db=AsyncMock())
        assert "password reset email" in response["message"].lower()

    async def test_password_reset_confirm_success(self, monkeypatch):
        monkeypatch.setattr('app.database.services.password_reset_token_service.PasswordResetTokenService.validate_token', AsyncMock(return_value=1))
        monkeypatch.setattr('app.database.services.user_service.UserService.update_user_password', AsyncMock(return_value=True))
        monkeypatch.setattr('app.utils.logger.log.info', lambda *args, **kwargs: None)

        class Data:
            token = "validtoken"
            new_password = "newsecurepassword"

        response = await authrouter.confirm_password_reset(data=Data(), db=AsyncMock())
        assert "password has been reset successfully" in response["message"].lower()

    async def test_password_reset_confirm_invalid_token(self, monkeypatch):
        monkeypatch.setattr('app.database.services.password_reset_token_service.PasswordResetTokenService.validate_token', AsyncMock(return_value=None))

        class Data:
            token = "invalidtoken"
            new_password = "whatever"

        with pytest.raises(HTTPException) as exc:
            await authrouter.confirm_password_reset(data=Data(), db=AsyncMock())
        assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "invalid or expired token" in exc.value.detail.lower()

    async def test_password_reset_confirm_update_failure(self, monkeypatch):
        monkeypatch.setattr('app.database.services.password_reset_token_service.PasswordResetTokenService.validate_token', AsyncMock(return_value=1))
        monkeypatch.setattr('app.database.services.user_service.UserService.update_user_password', AsyncMock(return_value=False))

        class Data:
            token = "validtoken"
            new_password = "newpassword"

        with pytest.raises(HTTPException) as exc:
            await authrouter.confirm_password_reset(data=Data(), db=AsyncMock())
        assert exc.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "failed to reset password" in exc.value.detail.lower()

    async def test_refresh_access_token_success(self, monkeypatch, test_user):
        # Patch the router's imported authenticate_refresh_token, not the original location
        monkeypatch.setattr('app.api.routers.auth.authenticate_refresh_token', AsyncMock(return_value=test_user))
        monkeypatch.setattr('app.database.services.auth_service.AuthService.get_new_tokens', AsyncMock())
        monkeypatch.setattr('app.utils.logger.log.info', lambda *a, **k: None)

        result = await authrouter.refresh_access_token(refresh_token="sometoken", db=AsyncMock())
        assert result is not None


        result = await authrouter.refresh_access_token(refresh_token="sometoken", db=AsyncMock())
        assert result is not None

    async def test_logout_success(self, monkeypatch, test_user):
        monkeypatch.setattr('app.api.dependencies.auth.get_current_user', AsyncMock(return_value=test_user))
        monkeypatch.setattr('app.database.services.refresh_token_service.RefreshTokenService.revoke_user_tokens', AsyncMock(return_value=1))
        monkeypatch.setattr('app.utils.logger.log.info', lambda *args, **kwargs: None)

        result = await authrouter.logout(db=AsyncMock(), current_user=test_user)
        assert "Successfully logged out" in result["message"]

    async def test_logout_all_tokens_revoked(self, monkeypatch, test_user):
        monkeypatch.setattr('app.api.dependencies.auth.get_current_user', AsyncMock(return_value=test_user))
        monkeypatch.setattr('app.database.services.refresh_token_service.RefreshTokenService.revoke_user_tokens', AsyncMock(return_value=0))
        monkeypatch.setattr('app.utils.logger.log.error', lambda *args, **kwargs: None)

        with pytest.raises(HTTPException) as exc:
            await authrouter.logout(db=AsyncMock(), current_user=test_user)
        assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "all refresh tokens already revoked" in exc.value.detail.lower()
