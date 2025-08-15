import pytest
from fastapi import HTTPException, status
from unittest.mock import AsyncMock, MagicMock, patch

from app.api.routers import users as users_router
from app.schemas.user import UserCreate, UserUpdate
from app.database.services.user_service import UserService


@pytest.mark.asyncio
class TestUserRouter:
    # 🔸 POST /users/
    @pytest.mark.asyncio
    async def test_create_user_success(self, mock_db):
        test_data = UserCreate(
            firstname="test",
            lastname="user",
            username="newuser",
            email="new@example.com",
            password="secure123"
        )
        mock_user = MagicMock()
        mock_user.username = "newuser"

        with patch.object(UserService, "create_user", new_callable=AsyncMock, return_value=mock_user):
            response = await users_router.create_user(test_data, mock_db)
            assert response.username == "newuser"
            UserService.create_user.assert_awaited_once_with(mock_db, test_data)

    # 🔸 GET /users/me
    async def test_get_me(self, mock_current_user):
        response = await users_router.get_me(mock_current_user)
        assert response == mock_current_user

    # 🔸 PUT /users/me
    async def test_update_me(self, mock_db, mock_current_user):
        update_data = UserUpdate(email="updated@example.com")
        updated_user = MagicMock()
        updated_user.email = "updated@example.com"

        with patch.object(UserService, "update_user", new_callable=AsyncMock, return_value=updated_user):
            response = await users_router.update_me(update_data, mock_db, mock_current_user)
            assert response.email == "updated@example.com"
            UserService.update_user.assert_awaited_once_with(mock_db, mock_current_user.id, update_data)

    # 🔸 DELETE /users/me
    async def test_delete_me(self, mock_db, mock_current_user):
        with patch.object(UserService, "delete_user", new_callable=AsyncMock) as mock_delete:
            response = await users_router.delete_me(mock_db, mock_current_user)
            assert response == {"Message": "User Deleted."}
            mock_delete.assert_awaited_once_with(mock_db, mock_current_user.id)

    # 🔸 GET /users/{id}
    async def test_get_user_by_id(self, mock_db, mock_current_user):
        test_user = MagicMock()
        test_user.id = 2

        with patch.object(UserService, "get_user_by_id", new_callable=AsyncMock, return_value=test_user):
            response = await users_router.get_user_by_id(2, mock_db, mock_current_user)
            assert response.id == 2
            UserService.get_user_by_id.assert_awaited_once_with(mock_db, 2)

    # ---- Error Cases ----
    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(self, mock_db):
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
            new_callable=AsyncMock,
            side_effect=HTTPException(status_code=400, detail="Email already exists")
        ), pytest.raises(HTTPException) as exc_info:
            await users_router.create_user(test_data, mock_db)

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.asyncio
    async def test_get_nonexistent_user(self, mock_db, mock_current_user):
        with patch.object(
            UserService,
            "get_user_by_id",
            new_callable=AsyncMock,
            return_value=None
        ):
            with pytest.raises(HTTPException) as exc_info:
                await users_router.get_user_by_id(999, mock_db, mock_current_user)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
