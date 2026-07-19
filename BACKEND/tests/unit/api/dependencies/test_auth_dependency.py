import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import timedelta
from fastapi import HTTPException, status

from app.api.dependencies.auth import create_access_token, get_current_user, require_permission, create_refresh_token, authenticate_refresh_token
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

        decoded = JWTManager.decode_access_token(token, audience="audience")
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

    async def test_permission_granted(self, monkeypatch, mock_db, mock_current_user):
        """Should pass if required permission is present"""
        # Patch UserService.get_all_permissions_for_user to return needed permission
        monkeypatch.setattr(
            "app.database.services.user_service.UserService.get_all_permissions_for_user",
            AsyncMock(return_value=["sample:perm", "users:read"])
        )

        # Get the dependency function to test
        dep = require_permission("users:read").dependency

        # The dependency returns a callable, call it with injected params
        await dep(
            db=mock_db,
            current_user=mock_current_user
        )  # No exception: passed

    async def test_permission_missing(self, monkeypatch, mock_db, mock_current_user):
        """Should raise HTTPException if permission is missing"""
        monkeypatch.setattr(
            "app.database.services.user_service.UserService.get_all_permissions_for_user",
            AsyncMock(return_value=["other:perm"])
        )
        dep = require_permission("users:read").dependency

        with pytest.raises(HTTPException) as exc_info:
            await dep(
                db=mock_db,
                current_user=mock_current_user
            )
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "Missing required permission" in exc_info.value.detail

    async def test_permission_handles_empty_list(self, monkeypatch, mock_db, mock_current_user):
        """Should raise if user has no permissions at all"""
        monkeypatch.setattr(
            "app.database.services.user_service.UserService.get_all_permissions_for_user",
            AsyncMock(return_value=[])
        )
        dep = require_permission("users:read").dependency

        with pytest.raises(HTTPException) as exc_info:
            await dep(
                db=mock_db,
                current_user=mock_current_user
            )
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN

    async def test_permission_handles_none(self, monkeypatch, mock_db, mock_current_user):
        """Gracefully handle None returned as permissions (treated as missing)"""
        monkeypatch.setattr(
            "app.database.services.user_service.UserService.get_all_permissions_for_user",
            AsyncMock(return_value=None)
        )
        dep = require_permission("users:read").dependency
        with pytest.raises(HTTPException) as exc_info:
            await dep(
                db=mock_db,
                current_user=mock_current_user
            )
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN

    async def test_create_refresh_token_and_decode(self, test_user):
        payload = {"sub": test_user["username"]}
        token = create_refresh_token(payload, expire_delta=timedelta(minutes=5))
        decoded = JWTManager.decode_refresh_token(token, audience="audience")
        assert decoded["sub"] == test_user["username"]

    async def test_authenticate_refresh_token_success(self, monkeypatch, mock_db, mock_current_user):
        refresh_token = create_refresh_token({"sub": mock_current_user.username}, expire_delta=timedelta(minutes=5))
        monkeypatch.setattr(JWTManager, "decode_refresh_token", lambda t, audience=None: {"sub": mock_current_user.username})
        async def fake_get_user_by_username(db, username):
            return mock_current_user
        monkeypatch.setattr(UserService, "get_user_by_username", fake_get_user_by_username)
        mock_entry = MagicMock()
        mock_entry.revoked = False
        mock_entry.used = False
        async def fake_validate(db, tokenhash, user_id):
            return mock_entry
        monkeypatch.setattr(
            "app.database.services.refresh_token_service.RefreshTokenService.validate_refresh_token", fake_validate
        )
        user = await authenticate_refresh_token(refresh_token, db=mock_db)
        assert user.username == mock_current_user.username

    async def test_authenticate_refresh_token_expired(self, mock_db):
        expired_token = create_refresh_token({"sub": "expireduser"}, expire_delta=timedelta(minutes=-1))
        with pytest.raises(HTTPException) as exc_info:
            await authenticate_refresh_token(expired_token, db=mock_db)
        assert exc_info.value.status_code == 401
        assert "expired" in exc_info.value.detail.lower()

    async def test_authenticate_refresh_token_revoked(self, monkeypatch, mock_db, mock_current_user):
        mock_current_user.username = "revokeduser"
        refresh_token = create_refresh_token({"sub": mock_current_user.username}, expire_delta=timedelta(minutes=5))
        monkeypatch.setattr(JWTManager, "decode_refresh_token", lambda t, audience=None: {"sub": mock_current_user.username})
    
