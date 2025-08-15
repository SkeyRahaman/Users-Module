import pytest
from fastapi import status
from httpx import AsyncClient

from app.main import app
from app.database.models import User
from app.config import Config
from app.auth.password_hash import PasswordHasher

@pytest.mark.asyncio
@pytest.mark.usefixtures("setup_database", "override_get_db")
class TestUsersRouter:

    async def test_create_user_success(self, client: AsyncClient):
        url = app.url_path_for("create_user")

        response = await client.post(
            url,
            json={
                "firstname": Config.TEST_USER["firstname"],
                "lastname": Config.TEST_USER["lastname"],
                "username": Config.TEST_USER['username'],
                "email": Config.TEST_USER['email'],
                "password": PasswordHasher.get_password_hash(Config.TEST_USER['password']),
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert "id" in response.json()

    async def test_get_current_user(self, client: AsyncClient, test_user: User, token: str):
        url = app.url_path_for("get_me")

        response = await client.get(
            url,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["username"] == test_user.username

    async def test_update_current_user(self, client: AsyncClient, test_user: User, token: str):
        url = app.url_path_for("put_me")

        response = await client.put(
            url,
            json={"email": "updated@example.com"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["email"] == "updated@example.com"

    async def test_delete_current_user(self, client: AsyncClient, test_user: User, token: str):
        url = app.url_path_for("delete_me")

        response = await client.delete(
            url,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert response.json()["Message"] == "User Deleted."

    async def test_get_user_by_id(self, client: AsyncClient, test_user: User, token: str):
        url = app.url_path_for("get_by_id", id=test_user.id)

        response = await client.get(
            url,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == test_user.id

    # Error cases
    async def test_create_user_duplicate(self, client: AsyncClient, test_user: User):
        url = app.url_path_for("create_user")

        response = await client.post(
            url,
            json={
                "firstname": "Test",
                "lastname": "User",
                "username": test_user.username,
                "email": test_user.email,
                "password": "secure123"
            }
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_get_nonexistent_user(self, client: AsyncClient, token: str):
        url = app.url_path_for("get_by_id", id=999999)

        response = await client.get(
            url,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
