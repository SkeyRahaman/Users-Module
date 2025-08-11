import pytest
from fastapi import HTTPException, status
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session

from app.api.routers import users as users_router
from app.schemas.user import UserCreate, UserUpdate, UserOut
from app.database.models import User
from app.database.services.user_service import UserService

@pytest.fixture
def mock_current_user():
    user = MagicMock(spec=User)
    user.id = 1
    user.firstname = "test"
    user.lastname = "user"
    user.username = "testuser"
    user.email = "test@example.com"
    user.is_active = True
    return user

# ---- Tests ----
class TestUserRouter:
    # 🔸 POST /users/
    def test_create_user_success(self, db_session):
        test_data = UserCreate(
            firstname = "test",
            lastname = "user",
            username="newuser",
            email="new@example.com",
            password="secure123"
        )
        mock_user = MagicMock()
        mock_user.username = "newuser"
        
        with patch.object(UserService, "create_user", return_value=mock_user):
            response = users_router.create_user(test_data, db_session)
            assert response.username == "newuser"
            UserService.create_user.assert_called_once_with(db_session, test_data)

    # 🔸 GET /users/me
    def test_get_me(self, mock_current_user):
        response = users_router.get_me(mock_current_user)
        assert response == mock_current_user

    # 🔸 PUT /users/me
    def test_update_me(self, db_session, mock_current_user):
        update_data = UserUpdate(email="updated@example.com")
        updated_user = MagicMock()
        updated_user.email = "updated@example.com"
        
        with patch.object(UserService, "update_user", return_value=updated_user):
            response = users_router.update_me(update_data, db_session, mock_current_user)
            assert response.email == "updated@example.com"
            UserService.update_user.assert_called_once_with(
                db_session, mock_current_user.id, update_data
            )

    # 🔸 DELETE /users/me
    def test_delete_me(self, db_session, mock_current_user):
        with patch.object(UserService, "delete_user") as mock_delete:
            response = users_router.delete_me(db_session, mock_current_user)
            assert response == {"Message": "User Deleted."}
            mock_delete.assert_called_once_with(db_session, mock_current_user.id)

    # 🔸 GET /users/{id}
    def test_get_user_by_id(self, db_session, mock_current_user):
        test_user = MagicMock()
        test_user.id = 2
        
        with patch.object(UserService, "get_user_by_id", return_value=test_user):
            response = users_router.get_user_by_id(2, db_session, mock_current_user)
            assert response.id == 2
            UserService.get_user_by_id.assert_called_once_with(db_session, 2)

    # ---- Error Cases ----
    def test_create_user_duplicate_email(self, db_session):
        test_data = UserCreate(
            firstname="nrw",
            lastname="usesr",
            username="newuser",
            email="duplicate@example.com",
            password="secure123"
        )
        with patch.object(
                UserService,
                "create_user",
                side_effect=HTTPException(status_code=400, detail="Email already exists")
            ), pytest.raises(HTTPException) as exc_info:
            users_router.create_user(test_data, db_session)
            
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST

    def test_get_nonexistent_user(self, db_session, mock_current_user):
        with pytest.raises(HTTPException) as exc_info:
            response = users_router.get_user_by_id(999, db_session, mock_current_user)
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND