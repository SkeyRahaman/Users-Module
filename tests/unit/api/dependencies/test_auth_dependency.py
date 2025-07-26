import pytest
from datetime import timedelta
from jose import jwt
from fastapi import HTTPException

from app.api.dependencies.auth import create_access_token, get_current_user
from app.config import Config
from app.database.user import User
from app.services.user_service import UserService

class TestAuth:

    @pytest.fixture(autouse=True)
    def _setup_dummy_user(self):
        self.dummy_user = User(
            id=1,
            firstname="John",
            lastname="Doe",
            middlename=None,
            username="johndoe",
            email="john@example.com",
            password="hashedpassword",
            is_active=True,
            is_verified=True,
            is_deleted=False,
        )

    @pytest.fixture
    def token(self):
        return create_access_token(
            data={"sub": self.dummy_user.username},
            expire_delta=timedelta(minutes=15)
        )

    def test_create_access_token_encodes_payload_correctly(self, token):
        decoded = jwt.decode(token, Config.SECRET_KEY, algorithms=[Config.TOKEN_ALGORITHM])
        assert decoded.get("sub") == self.dummy_user.username
        assert "exp" in decoded

    def test_get_current_user_valid_token(self, mocker, token, db_session):
        mocker.patch.object(UserService, "get_user_by_username", return_value=self.dummy_user)

        user = get_current_user(token=token, db=db_session)

        assert user.username == self.dummy_user.username
        assert user.email == self.dummy_user.email

    def test_get_current_user_invalid_token_raises(self):
        invalid_token = "this.is.invalid.token"
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(token=invalid_token, db=None)

        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in str(exc_info.value.detail)

    def test_get_current_user_user_not_found(self, mocker, token, db_session):
        mocker.patch.object(UserService, "get_user_by_username", return_value=None)

        with pytest.raises(HTTPException) as exc_info:
            get_current_user(token=token, db=db_session)

        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in str(exc_info.value.detail)
