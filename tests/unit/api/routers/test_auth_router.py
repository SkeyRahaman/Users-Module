import pytest
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from app.api.routers import auth as auth_router
from app.services.user_service import UserService
from app.auth.password import PasswordHasher

# --- Fixtures ---
@pytest.fixture
def mock_db():
    return Mock(spec=Session)

@pytest.fixture
def mock_user():
    user = Mock()
    user.username = "test_user"
    user.password = "hashed_password"
    user.is_deleted = False
    return user

# --- Tests ---
class TestTokenEndpoint:
    def test_valid_credentials_returns_token(self, mock_db, mock_user):
        # Arrange
        with patch.object(UserService, "get_user_by_username", return_value=mock_user), \
             patch.object(PasswordHasher, "verify_password", return_value=True), \
             patch("app.api.routers.auth.create_access_token", return_value="fake_token"):
           
            form_data = OAuth2PasswordRequestForm(
                username="test_user", 
                password="correct_password", 
                scope=""
            )
            
            # Act
            response = auth_router.get_token(form_data, mock_db)
            print(response)
            print({
                "access_token": "fake_token",
                "token_type": "bearer",
                "user_name": "test_user"
            })
            # Assert
            assert response == {
                "access_token": "fake_token",
                "token_type": "bearer",
                "user_name": "test_user"
            }

    def test_invalid_username_raises_401(self, mock_db):
        # Arrange
        with patch.object(UserService, "get_user_by_username", return_value=None):
            form_data = OAuth2PasswordRequestForm(
                username="wrong_user", 
                password="any_password", 
                scope=""
            )
            
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                auth_router.get_token(form_data, mock_db)
            
            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert exc_info.value.detail == "Invalid Credentials."

    def test_invalid_password_raises_401(self, mock_db, mock_user):
        # Arrange
        with patch.object(UserService, "get_user_by_username", return_value=mock_user), \
             patch.object(PasswordHasher, "verify_password", return_value=False):
            
            form_data = OAuth2PasswordRequestForm(
                username="test_user", 
                password="wrong_password", 
                scope=""
            )
            
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                auth_router.get_token(form_data, mock_db)
            
            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert exc_info.value.detail == "Invalid Credentials."
            