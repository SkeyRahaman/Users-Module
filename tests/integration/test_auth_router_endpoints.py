from unittest.mock import AsyncMock
import pytest
from fastapi import status
from httpx import AsyncClient

from app.config import Config
from app.main import app
from app.database.models import User


@pytest.mark.asyncio
@pytest.mark.usefixtures("setup_database", "override_get_db")
class TestAuthRouter:

    async def test_get_token_success(self, client: AsyncClient, test_user):
        response = await client.post(
            app.url_path_for("token"),
            data={"username": test_user.username, "password": Config.TEST_USER['password']},  # Use actual test password from fixture
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user_name"] == test_user.username

    async def test_get_token_invalid_credentials(self, client: AsyncClient):
        response = await client.post(
            app.url_path_for("token"),
            data={"username": "wrong", "password": "wrong"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_token_inactive_user(self, db_session, client: AsyncClient, test_user: User):
        test_user.is_deleted = True
        db_session.add(test_user)
        await db_session.commit()
        await db_session.refresh(test_user)

        response = await client.post(
            app.url_path_for("token"),
            data={"username": test_user.username, "password": "test_password"},  # Use actual test password
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Inactive user." in response.json()["detail"]

    async def test_request_password_reset_existing_email(self, client: AsyncClient, test_user: User):
        response = await client.post(
            app.url_path_for("request_password_reset"),
            json={"email": test_user.email}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "password reset email" in data["message"].lower()

    async def test_request_password_reset_non_existing_email(self, client: AsyncClient):
        response = await client.post(
            app.url_path_for("request_password_reset"),
            json={"email": "nonexistingemail@example.com"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "password reset email" in data["message"].lower()

    async def test_confirm_password_reset_success(self, client: AsyncClient, db_session, test_user: User):
        # Create a valid token for the test user via PasswordResetTokenService or a fixture
        from app.database.services.password_reset_token_service import PasswordResetTokenService
        token = await PasswordResetTokenService.create_password_reset_token(db_session, test_user.id)

        response = await client.post(
            app.url_path_for("confirm_password_reset"),
            json={"token": token.token_hash, "new_password": "NewSecurePass123!"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "password has been reset" in data["message"].lower()

    async def test_confirm_password_reset_invalid_token(self, client: AsyncClient):
        response = await client.post(
            app.url_path_for("confirm_password_reset"),
            json={"token": "invalidtoken123", "new_password": "newpass123"}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "invalid or expired token" in response.json()["detail"].lower()

    async def test_confirm_password_reset_update_failure(self, client: AsyncClient, db_session, test_user: User, monkeypatch):
        from app.database.services.password_reset_token_service import PasswordResetTokenService

        token = await PasswordResetTokenService.create_password_reset_token(db_session, test_user.id)

        # Patch UserService.update_user_password to simulate failure
        from app.database.services import user_service
        monkeypatch.setattr(
            user_service.UserService,
            "update_user_password",
            AsyncMock(return_value=False)
        )

        response = await client.post(
            app.url_path_for("confirm_password_reset"),
            json={"token": token.token_hash, "new_password": "newpass123"}
        )
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "failed to reset password" in response.json()["detail"].lower()
