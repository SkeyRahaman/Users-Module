import pytest
from fastapi import HTTPException, status
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.api.routers import groups as group_router
from app.database.services import GroupService, UserGroupService, GroupRoleService
from app.schemas.group import GroupCreate, GroupUpdate

@pytest.mark.asyncio
class Testgroup_router:

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

    async def test_assign_role_to_group_success(self, mock_db, mock_current_user):
        group_id = 1
        role_id = 42
        mockrequest = MagicMock()
        mockrequest.role_id = role_id
        mockrequest.valid_from = None
        mockrequest.valid_until = None
        with patch.object(GroupRoleService, "assign_group_role", new_callable=AsyncMock, return_value=True) as mockassign:
            response = await group_router.assign_role_to_group(group_id, mockrequest, mock_db, mock_current_user)
            assert response["message"] == "Role assigned to group successfully"
            assert response["group_id"] == group_id
            assert response["role_id"] == role_id
            mockassign.assert_awaited_once_with(db=mock_db, group_id=1, role_id=42, valid_from=None, valid_until=None,created_by=1)

    async def test_assign_role_to_group_failure(self, mock_db, mock_current_user):
        group_id = 99
        role_id = 101
        mockrequest = MagicMock()
        mockrequest.role_id = role_id
        mockrequest.valid_from = None
        mockrequest.valid_until = None
        with patch.object(GroupRoleService, "assign_group_role", new_callable=AsyncMock, return_value=False):
            with pytest.raises(HTTPException) as excinfo:
                await group_router.assign_role_to_group(group_id, mockrequest, mock_db, mock_current_user)
            assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST
            assert "Failed to assign role to group" in excinfo.value.detail

    async def test_remove_role_from_group_success(self, mock_db, mock_current_user):
        group_id = 5
        role_id = 55
        with patch.object(GroupRoleService, "remove_group_role", new_callable=AsyncMock, return_value=True) as mockremove:
            response = await group_router.remove_role_from_group(group_id, role_id, mock_db, mock_current_user)
            assert response["message"] == "Role removed from group successfully"
            mockremove.assert_awaited_once_with(db=mock_db, group_id=5, role_id=55)

    async def test_remove_role_from_group_failure(self, mock_db, mock_current_user):
        group_id = 111
        role_id = 105
        with patch.object(GroupRoleService, "remove_group_role", new_callable=AsyncMock, return_value=False):
            with pytest.raises(HTTPException) as excinfo:
                await group_router.remove_role_from_group(group_id, role_id, mock_db, mock_current_user)
            assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST
            assert "Failed to remove role from group" in excinfo.value.detail

    async def test_get_roles_of_group_success(self, mock_db):
        group_id = 22
        mockroles = [MagicMock(id=1), MagicMock(id=2)]
        with patch.object(GroupRoleService, "get_all_roles_for_group", new_callable=AsyncMock, return_value=mockroles) as mockget:
            response = await group_router.get_roles_of_group(group_id, mock_db, MagicMock())
            assert isinstance(response, list)
            assert response[0].id == 1
            mockget.assert_awaited_once_with(db=mock_db, group_id=22)

    async def test_get_roles_of_group_not_found(self, mock_db):
        group_id = 999
        with patch.object(GroupRoleService, "get_all_roles_for_group", new_callable=AsyncMock, return_value=None):
            with pytest.raises(HTTPException) as excinfo:
                await group_router.get_roles_of_group(group_id, mock_db, MagicMock())
            assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND
            assert "Group not found or no roles assigned" in excinfo.value.detail

    async def test_get_users_of_group_success(self, mock_db):
        group_id = 11
        mockusers = [MagicMock(id=1), MagicMock(id=2)]
        with patch.object(UserGroupService, "get_all_users_for_group", new_callable=AsyncMock, return_value=mockusers) as mockget:
            response = await group_router.get_users_of_group(group_id, mock_db, MagicMock())
            assert isinstance(response, list)
            assert response[0].id == 1
            mockget.assert_awaited_once_with(db=mock_db, group_id=11)

    async def test_get_users_of_group_not_found(self, mock_db):
        group_id = 888
        with patch.object(UserGroupService, "get_all_users_for_group", new_callable=AsyncMock, return_value=None):
            with pytest.raises(HTTPException) as excinfo:
                await group_router.get_users_of_group(group_id, mock_db, MagicMock())
            assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND
            assert "Group not found or no users assigned" in excinfo.value.detail

    async def test_get_group_by_name_success(self, mock_db):
        name = "admins"
        mockgroup = MagicMock()
        mockgroup.id = 9
        mockgroup.name = name
        mockgroup.created = datetime.now()
        with patch.object(GroupService, "get_group_by_name", new_callable=AsyncMock, return_value=mockgroup):
            response = await group_router.get_group_by_name(name, mock_db, name)
            assert response.name == name
            assert response.id == 9

    async def test_get_group_by_name_not_found(self, mock_db):
        name = "nonexistent"
        with patch.object(GroupService, "get_group_by_name", new_callable=AsyncMock, return_value=None):
            with pytest.raises(HTTPException) as excinfo:
                await group_router.get_group_by_name(name, mock_db, MagicMock())
            assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND
            assert "Group not found" in excinfo.value.detail
