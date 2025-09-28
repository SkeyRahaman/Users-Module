import pytest
from fastapi import HTTPException, status
from unittest.mock import AsyncMock, MagicMock, patch

from app.api.routers import groups as group_router
from app.database.services import GroupService, UserGroupService
from app.schemas.group import GroupCreate, GroupUpdate

@pytest.mark.asyncio
class TestGroupRouter:

    async def test_create_group_success(self, mock_db, mock_group):
        with patch.object(GroupService, "create_group", new_callable=AsyncMock, return_value=mock_group):
            group_data = GroupCreate(
                name="test_group",
                description="Test description"
            )
            response = await group_router.create_group(group_data, mock_db, MagicMock())
            assert response.id == 1
            assert response.name == "test_group"
            GroupService.create_group.assert_awaited_once_with(mock_db, group_data)

    async def test_create_group_duplicate(self, mock_db):
        with patch.object(GroupService, "create_group", new_callable=AsyncMock, return_value=None):
            group_data = GroupCreate(
                name="duplicate",
                description="Should fail"
            )
            with pytest.raises(HTTPException) as exc_info:
                await group_router.create_group(group_data, mock_db, MagicMock())
            assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
            assert "already exists" in exc_info.value.detail

    async def test_get_group_success(self, mock_db, mock_group):
        with patch.object(GroupService, "get_group_by_id", new_callable=AsyncMock, return_value=mock_group):
            response = await group_router.get_group(1, mock_db, MagicMock())
            assert response.id == 1
            assert response.name == "test_group"
            GroupService.get_group_by_id.assert_awaited_once_with(mock_db, 1)

    async def test_get_group_not_found(self, mock_db):
        with patch.object(GroupService, "get_group_by_id", new_callable=AsyncMock, return_value=None):
            with pytest.raises(HTTPException) as exc_info:
                await group_router.get_group(999, mock_db, MagicMock())
            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    async def test_update_group_success(self, mock_db, mock_group):
        update_data = GroupUpdate(description="Updated description")
        with patch.object(GroupService, "update_group", new_callable=AsyncMock, return_value=mock_group):
            response = await group_router.update_group(1, update_data, mock_db, MagicMock())
            assert response.id == 1
            assert response.description == "Test description"  # mock returns original
            GroupService.update_group.assert_awaited_once_with(mock_db, 1, update_data)

    async def test_update_group_not_found(self, mock_db):
        update_data = GroupUpdate(description="Should fail")
        with patch.object(GroupService, "update_group", new_callable=AsyncMock, return_value=None):
            with pytest.raises(HTTPException) as exc_info:
                await group_router.update_group(999, update_data, mock_db, MagicMock())
            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    async def test_delete_group_success(self, mock_db):
        with patch.object(GroupService, "delete_group", new_callable=AsyncMock, return_value=True):
            response = await group_router.delete_group(1, mock_db, MagicMock())
            assert response["message"] == "Group deleted"
            GroupService.delete_group.assert_awaited_once_with(mock_db, 1)

    async def test_delete_group_not_found(self, mock_db):
        with patch.object(GroupService, "delete_group", new_callable=AsyncMock, return_value=False):
            with pytest.raises(HTTPException) as exc_info:
                await group_router.delete_group(999, mock_db, MagicMock())
            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_all_groups(self, mock_db, mock_group):
        with patch.object(GroupService, "get_all_groups", new_callable=AsyncMock, return_value=[mock_group]):
            response = await group_router.get_all_groups(0, 10, "created", "desc", mock_db, MagicMock())
            assert len(response) == 1
            assert response[0].name == "test_group"
            GroupService.get_all_groups.assert_awaited_once()

    async def test_get_all_groups_pagination(self, mock_db, mock_group):
        mock_groups = [mock_group] * 5
        with patch.object(GroupService, "get_all_groups", new_callable=AsyncMock, return_value=mock_groups):
            response = await group_router.get_all_groups(skip=2, limit=5, db=mock_db, _=MagicMock())
            assert len(response) == 5
            GroupService.get_all_groups.assert_awaited_once_with(
                mock_db,
                skip=2,
                limit=5,
                sort_by="created",
                sort_order="desc"
            )

    async def test_get_all_groups_sorting(self, mock_db, mock_group):
        mock_groups = [mock_group] * 3
        with patch.object(GroupService, "get_all_groups", new_callable=AsyncMock, return_value=mock_groups):
            response = await group_router.get_all_groups(
                skip=0,
                limit=10,
                sort_by="name",
                sort_order="asc",
                db=mock_db,
                _=MagicMock()
            )
            assert len(response) == 3
            GroupService.get_all_groups.assert_awaited_once_with(
                mock_db,
                skip=0,
                limit=10,
                sort_by="name",
                sort_order="asc"
            )
    # 🔸 POST /users/{user_id}/add_to_group
    async def test_add_user_to_group_success(self, mock_db, mock_current_user):
        user_id = 10
        group_id = 20
        mock_request_data = MagicMock()
        mock_request_data.user_id = user_id
        with patch.object(
            UserGroupService, "assign_user_group",
            new_callable=AsyncMock, return_value=True
        ) as mock_assign:
            response = await group_router.add_user_to_group(
                group_id=group_id,
                request_data=mock_request_data,
                db=mock_db,
                current_user=mock_current_user
            )
            assert response["message"] == "User added to group successfully"
            assert response["group_id"] == group_id
            assert response["user_id"] == user_id
            mock_assign.assert_awaited_once_with(
                db=mock_db, user_id=user_id, group_id=group_id, created_by=mock_current_user.id
            )

    async def test_add_user_to_group_failure(self, mock_db, mock_current_user):
        user_id = 10
        group_id = 20
        mock_request_data = MagicMock()
        mock_request_data.user_id = user_id
        with patch.object(
            UserGroupService, "assign_user_group",
            new_callable=AsyncMock, return_value=False
        ), pytest.raises(HTTPException) as exc_info:
            await group_router.add_user_to_group(
                group_id=group_id,
                request_data=mock_request_data,
                db=mock_db,
                current_user=mock_current_user
            )
            assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
            assert "Failed to add user to group" in exc_info.value.detail

    # 🔸 POST /users/{user_id}/remove_from_group
    async def test_remove_user_from_group_success(self, mock_db, mock_current_user):
        user_id = 10
        group_id = 20
        with patch.object(
            UserGroupService, "remove_user_group",
            new_callable=AsyncMock, return_value=True
        ) as mock_remove:
            response = await group_router.remove_user_from_group(
                user_id=user_id,
                group_id=group_id,
                db=mock_db,
                _ =  mock_current_user
            )
            assert response["message"] == "User removed from group successfully"
            mock_remove.assert_awaited_once_with(
                db=mock_db, group_id=group_id, user_id=user_id
            )

    async def test_remove_user_from_group_failure(self, mock_db, mock_current_user):
        user_id = 10
        group_id = 20
        with patch.object(
            UserGroupService, "remove_user_group",
            new_callable=AsyncMock, return_value=False
        ), pytest.raises(HTTPException) as exc_info:
            await group_router.remove_user_from_group(
                user_id=user_id,
                group_id=group_id,
                db=mock_db,
                _ =  mock_current_user
            )
            assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
            assert "Failed to remove user from group" in exc_info.value.detail
