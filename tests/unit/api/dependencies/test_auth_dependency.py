import pytest
from unittest.mock import MagicMock
from datetime import timedelta
from fastapi import HTTPException

from app.api.dependencies.auth import create_access_token, get_current_user
from app.auth.jwt import JWTManager
from app.database.services.user_service import UserService

@pytest.fixture(scope="class")
def test_user():
    return {"username": "testuser"}

@pytest.mark.asyncio
class TestAuthDeps:
    async def test_create_access_token_and_decode(self, test_user):
        """create_access_token should return a JWT that decodes back to the original payload"""
        payload = {"sub": test_user["username"]}
        token = create_access_token(payload, expire_delta=timedelta(minutes=5))

        decoded = JWTManager.decode(token, audience="your-audience-identifier")
        assert decoded["sub"] == test_user["username"]

    async def test_get_current_user_success(self, monkeypatch, test_user):
        """get_current_user should return a valid user object if token is valid"""

        # Mock DB and service
        mock_db = MagicMock()
        mock_user = MagicMock()
        mock_user.username = test_user["username"]

        async def fake_get_user_by_username(db, username):
            return mock_user

        monkeypatch.setattr(UserService, "get_user_by_username", fake_get_user_by_username)

        # Create & validate
        token = create_access_token({"sub": test_user["username"]})
        user = await get_current_user(token=token, db=mock_db)

        assert user.username == test_user["username"]

    async def test_get_current_user_expired_token(self, monkeypatch, test_user):
        """Should raise HTTPException when token is expired"""
        expired_token = create_access_token(
            {"sub": test_user["username"]},
            expire_delta=timedelta(minutes=-6)
        )

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token=expired_token, db=MagicMock())
        assert exc_info.value.status_code == 401
        assert "expired" in exc_info.value.detail.lower()

    async def test_get_current_user_invalid_token(self):
        """Should raise HTTPException when token is invalid (corrupted)"""
        invalid_token = "this.is.not.a.valid.jwt"

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token=invalid_token, db=MagicMock())
        assert exc_info.value.status_code == 401

    async def test_get_current_user_user_not_found(self, monkeypatch, test_user):
        """Should raise HTTPException if user not found in DB"""
        async def fake_get_user_by_username(*args, **kwargs):
            return None
        monkeypatch.setattr(UserService, "get_user_by_username", fake_get_user_by_username)

        token = create_access_token({"sub": test_user["username"]})
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token=token, db=MagicMock())
        assert exc_info.value.status_code == 401
