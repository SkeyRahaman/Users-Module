import asyncio
import logging
from unittest.mock import AsyncMock
import pytest
from fastapi import status
from httpx import AsyncClient
from app.config import Config
from app.main import app
from app.database.models import User
from app.database.services.password_reset_token_service import PasswordResetTokenService
from app.database.services.refresh_token_service import RefreshTokenService

@pytest.mark.asyncio
@pytest.mark.usefixtures("setup_database", "override_get_db")
class TestAuthRouter:

    async def test_get_token_success(self, client: AsyncClient, test_user: User):
        response = await client.post(
            app.url_path_for("token"),
            data={"username": test_user.username, "password": Config.TEST_USER["password"]},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user_name"] == test_user.username

    async def test_get_token_invalid_credentials(self, client: AsyncClient):
        response = await client.post(
            app.url_path_for("token"),
            data={"username": "wronguser", "password": "wrongpass"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_token_inactive_user(self, db_session, client: AsyncClient, test_user: User):
        test_user.is_deleted = True
        db_session.add(test_user)
        await db_session.commit()
        await db_session.refresh(test_user)

        response = await client.post(
            app.url_path_for("token"),
            data={"username": test_user.username, "password": Config.TEST_USER["password"]},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "inactive user" in response.json()["detail"].lower()

    async def test_request_password_reset_existing_email(self, client: AsyncClient, test_user: User):
        response = await client.post(
            app.url_path_for("request_password_reset"),
            json={"email": test_user.email},
        )
        assert response.status_code == status.HTTP_200_OK
        assert "password reset email" in response.json()["message"].lower()

    async def test_request_password_reset_non_existing_email(self, client: AsyncClient):
        response = await client.post(
            app.url_path_for("request_password_reset"),
            json={"email": "nonexisting@example.com"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert "password reset email" in response.json()["message"].lower()

    async def test_confirm_password_reset_success(self, client: AsyncClient, db_session, test_user: User):
        token = await PasswordResetTokenService.create_password_reset_token(db_session, test_user.id)

        response = await client.post(
            app.url_path_for("confirm_password_reset"),
            json={"token": token.token_hash, "new_password": "NewPass123!"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert "password has been reset" in response.json()["message"].lower()

    async def test_confirm_password_reset_invalid_token(self, client: AsyncClient):
        response = await client.post(
            app.url_path_for("confirm_password_reset"),
            json={"token": "invalidtoken", "new_password": "password"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "invalid or expired token" in response.json()["detail"].lower()

    async def test_confirm_password_reset_update_failure(self, client: AsyncClient, db_session, test_user: User, monkeypatch):
        # This single monkeypatch here mocks a failure updating password in DB
        monkeypatch.setattr(
            "app.database.services.user_service.UserService.update_user_password",
            AsyncMock(return_value=False)
        )

        token = await PasswordResetTokenService.create_password_reset_token(db_session, test_user.id)
        response = await client.post(
            app.url_path_for("confirm_password_reset"),
            json={"token": token.token_hash, "new_password": "NewPass123!"},
        )
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "failed to reset password" in response.json()["detail"].lower()

    async def test_token_refresh_success(self, client: AsyncClient, test_user: User, caplog):
        # Obtain refresh token with login or set valid token in DB directly for tests
        login_response = await client.post(
            app.url_path_for("token"),
            data={"username": test_user.username, "password": Config.TEST_USER["password"]},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        await asyncio.sleep(1)
        refresh_token = login_response.json().get("refresh_token")
        assert refresh_token is not None
        response = await client.post(
            app.url_path_for("refresh_access_token"),
            data={"refresh_token": refresh_token},
        )
        assert response.status_code == status.HTTP_200_OK

    async def test_logout_success(self, client: AsyncClient, test_user: User):
        await asyncio.sleep(1)
        login_response = await client.post(
            app.url_path_for("token"),
            data={"username": test_user.username, "password": Config.TEST_USER["password"]},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        print(login_response.json())
        access_token = login_response.json().get("access_token")
        assert access_token is not None

        response = await client.post(
            app.url_path_for("logout"),
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert "successfully logged out" in response.json()["message"].lower()

    async def test_logout_all_tokens_revoked(self, client: AsyncClient, db_session, test_user: User):
        # Similar as logout_success but with tokens already revoked scenario
        await asyncio.sleep(1)
        login_response = await client.post(
            app.url_path_for("token"),
            data={"username": test_user.username, "password": Config.TEST_USER["password"]},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        access_token = login_response.json().get("access_token")
        assert access_token is not None

        await RefreshTokenService.revoke_user_tokens(db_session, test_user.id)

        response = await client.post(
            app.url_path_for("logout"),
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "all refresh tokens already revoked" in response.json()["detail"].lower()
