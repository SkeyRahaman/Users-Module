from fastapi import status
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.database.user import User
from app.main import app
from app.api.dependencies.database import get_db

class TestTokenGeneration:
    token_url = app.url_path_for("token")
    def test_successful_token_generation(self, client: TestClient, test_user: User):
        response = client.post(
            TestTokenGeneration.token_url,
            data={
                "username": "test_username",
                "password": "secure123",
                "grant_type": "password",
            },
            headers={
                "accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user_name"] == "test_username"

    def test_invalid_username(self, client: TestClient):
        response = client.post(
            TestTokenGeneration.token_url,
            data={
                "username": "nonexistent",
                "password": "anything"
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": "Invalid Credentials."}

    def test_invalid_password(self, client: TestClient, test_user: User):
        response = client.post(
            TestTokenGeneration.token_url,
            data={
                "username": "test_username",
                "password": "wrongpassword"
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": "Invalid Credentials."}

    def test_inactive_user_cannot_login(self, client: TestClient, db_session: Session, test_user: User):
        test_user.is_deleted = True
        db_session.commit()
        db_session.refresh(test_user)

        login_data = {
            "username": test_user.username,
            "password": "secure123"
        }
        
        response = client.post(
            TestTokenGeneration.token_url,
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": "Inactive user."}