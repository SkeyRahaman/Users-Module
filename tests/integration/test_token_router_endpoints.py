import pytest
from fastapi import status
from httpx import AsyncClient

from app.main import app
from app.database.models import User
from app.config import Config

@pytest.mark.asyncio
@pytest.mark.usefixtures("setup_database", "override_get_db")
class TestAuthRouter:

    async def test_get_token_success(self, client: AsyncClient, test_user):
        # Act: request token with valid credentials for test_user
        response = await client.post(
            app.url_path_for("token"),
            data={"username": test_user.username, "password": Config.TEST_USER['password']},
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
            data={"username": test_user.username, "password": Config.TEST_USER['password']},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Inactive user." in response.json()["detail"]
