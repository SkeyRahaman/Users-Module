import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.database.models import User

class TestUsersRouter:
    def test_create_user_success(self, client: TestClient):
        # Get URL by route name
        url = app.url_path_for("create_user")
        
        response = client.post(
            url,
            json={
                "firstname": "Test",
                "lastname": "User",
                "username": "testuser",
                "email": "test@example.com",
                "password": "secure123"
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert "id" in response.json()

    def test_get_current_user(self, client: TestClient, test_user: User, test_token: str):
        url = app.url_path_for("get_me")
        
        response = client.get(
            url,
            headers={"Authorization": f"Bearer {test_token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["username"] == test_user.username

    def test_update_current_user(self, client: TestClient, test_user: User, test_token: str):
        url = app.url_path_for("put_me")
        
        response = client.put(
            url,
            json={"email": "updated@example.com"},
            headers={"Authorization": f"Bearer {test_token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["email"] == "updated@example.com"

    def test_delete_current_user(self, client: TestClient, test_user: User, test_token: str):
        url = app.url_path_for("delete_me")
        
        response = client.delete(
            url,
            headers={"Authorization": f"Bearer {test_token}"}
        )
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert response.json()["Message"] == "User Deleted."

    def test_get_user_by_id(self, client: TestClient, test_user: User, test_token: str):
        url = app.url_path_for("get_by_id", id=test_user.id)
        
        response = client.get(
            url,
            headers={"Authorization": f"Bearer {test_token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == test_user.id

    # Error cases
    def test_create_user_duplicate(self, client: TestClient, test_user: User):
        url = app.url_path_for("create_user")
        
        response = client.post(
            url,
            json={
                "firstname": "Test",
                "lastname": "User",
                "username": "test_username",
                "email": "username@example.com",
                "password": "secure123"
            }
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_get_nonexistent_user(self, client: TestClient, test_token: str):
        url = app.url_path_for("get_by_id", id=999999)
        
        response = client.get(
            url,
            headers={"Authorization": f"Bearer {test_token}"}
        )
        print(response.json())
        assert response.status_code == status.HTTP_404_NOT_FOUND