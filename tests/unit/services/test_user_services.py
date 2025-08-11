import pytest
from app.schemas.user import UserCreate, UserUpdate
from app.database.services.user_service import UserService
from app.database.models import User


class TestUserService:

    def test_create_user_success(self, db_session_module):
        user_data = UserCreate(
            firstname="John",
            middlename="M",
            lastname="Doe",
            username="johndoe",
            email="john@example.com",
            password="secret123"
        )
        user = UserService.create_user(db_session_module, user_data)

        assert user.id is not None
        assert user.username == "johndoe"
        assert user.email == "john@example.com"
        assert user.password != "secret123"  # should be hashed

    def test_duplicate_username_fails(self, db_session_module):
        user_data = UserCreate(
            firstname="Jane",
            middlename=None,
            lastname="Smith",
            username="johndoe",  # same username as before
            email="jane@example.com",
            password="secret123"
        )
        result = UserService.create_user(db_session_module, user_data)
        assert result is None 

    def test_get_user_by_id(self, db_session_module):
        user = db_session_module.query(User).filter_by(username="johndoe").first()
        result = UserService.get_user_by_id(db_session_module, user.id)
        assert result.username == "johndoe"


    def test_get_user_by_username(self, db_session_module):
        user = db_session_module.query(User).filter_by(username="johndoe").first()
        result = UserService.get_user_by_username(db_session_module, user.username)
        assert result.username == "johndoe"

    def test_update_user(self, db_session_module):
        user = db_session_module.query(User).filter_by(username="johndoe").first()
        update_data = UserUpdate(firstname="Johnny", lastname="Updated")
        updated = UserService.update_user(db_session_module, user.id, update_data)

        assert updated.firstname == "Johnny"
        assert updated.lastname == "Updated"

    def test_check_username_exists(self, db_session_module):
        assert UserService.check_username_exists(db_session_module, "johndoe") is True
        assert UserService.check_username_exists(db_session_module, "nonexistent") is False

    def test_check_email_exists(self, db_session_module):
        assert UserService.check_email_exists(db_session_module, "john@example.com") is True
        assert UserService.check_email_exists(db_session_module, "fake@email.com") is False

    def test_get_all_users(self, db_session_module):
        users = UserService.get_all_users(db_session_module, skip=0, limit=10, sort_by="username", sort_order="asc")
        assert isinstance(users, list)
        assert users[0].username == "johndoe"

    def test_delete_user(self, db_session_module):
        user = db_session_module.query(User).filter_by(username="johndoe").first()
        result = UserService.delete_user(db_session_module, user.id)
        assert result is True
         
        result = UserService.get_user_by_id(db_session_module, user.id)
        assert result is None 

