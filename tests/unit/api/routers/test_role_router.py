import pytest
from fastapi import HTTPException, status
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.routers import roles as role_router
from app.database.services import RoleService, UserRoleService, GroupRoleService, RolePermissionService
from app.schemas.role import RoleCreate, RoleUpdate
from app.schemas import AddRoleToGroupForRole, AddRoleToUserForRole, AddPermissionToRoleForRole


@pytest.mark.asyncio
class Testrole_router:

    async def test_create_role_success(self, mock_db, mock_role):
        with patch.object(RoleService, "create_role", new_callable=AsyncMock, return_value=mock_role):
            role_data = RoleCreate(
                name="test_role",
                description="Test description"
            )
            result = await role_router.create_role(role_data, mock_db, MagicMock())
            assert result.id == 1
            assert result.name == "test_role"
            RoleService.create_role.assert_awaited_once_with(mock_db, role_data)

    async def test_create_role_duplicate(self, mock_db):
        with patch.object(RoleService, "create_role", new_callable=AsyncMock, return_value=None):
            role_data = RoleCreate(
                name="duplicate",
                description="Should fail"
            )
            with pytest.raises(HTTPException) as exc_info:
                await role_router.create_role(role_data, mock_db, MagicMock())
            assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
            assert "already exists" in exc_info.value.detail

    async def test_get_role_success(self, mock_db, mock_role):
        with patch.object(RoleService, "get_role_by_id", new_callable=AsyncMock, return_value=mock_role):
            result = await role_router.get_role(1, mock_db, MagicMock())
            assert result.id == 1
            assert result.name == "test_role"
            RoleService.get_role_by_id.assert_awaited_once_with(mock_db, 1)

    async def test_get_role_not_found(self, mock_db):
        with patch.object(RoleService, "get_role_by_id", new_callable=AsyncMock, return_value=None):
            with pytest.raises(HTTPException) as exc_info:
                await role_router.get_role(999, mock_db, MagicMock())
            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    async def test_update_role_success(self, mock_db, mock_role):
        update_data = RoleUpdate(description="Updated description")
        with patch.object(RoleService, "update_role", new_callable=AsyncMock, return_value=mock_role):
            result = await role_router.update_role(1, update_data, mock_db, MagicMock())
            assert result.id == 1
            assert result.description == "Test description"  # Mock returns original
            RoleService.update_role.assert_awaited_once_with(mock_db, 1, update_data)

    async def test_update_role_not_found(self, mock_db):
        update_data = RoleUpdate(description="Should fail")
        with patch.object(RoleService, "update_role", new_callable=AsyncMock, return_value=None):
            with pytest.raises(HTTPException) as exc_info:
                await role_router.update_role(999, update_data, mock_db, MagicMock())
            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    async def test_delete_role_success(self, mock_db):
        with patch.object(RoleService, "delete_role", new_callable=AsyncMock, return_value=True):
            result = await role_router.delete_role(1, mock_db, MagicMock())
            assert result["message"] == "Role deleted"
            RoleService.delete_role.assert_awaited_once_with(mock_db, 1)

    async def test_delete_role_not_found(self, mock_db):
        with patch.object(RoleService, "delete_role", new_callable=AsyncMock, return_value=False):
            with pytest.raises(HTTPException) as exc_info:
                await role_router.delete_role(999, mock_db, MagicMock())
            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_all_roles(self, mock_db, mock_role):
        with patch.object(RoleService, "get_all_roles", new_callable=AsyncMock, return_value=[mock_role]):
            result = await role_router.get_all_roles(0, 10, "created", "desc", mock_db, MagicMock())
            assert len(result) == 1
            assert result[0].name == "test_role"
            RoleService.get_all_roles.assert_awaited_once()

    async def test_get_all_roles_pagination(self, mock_db, mock_role):
        mock_roles = [mock_role] * 5
        with patch.object(RoleService, "get_all_roles", new_callable=AsyncMock, return_value=mock_roles):
            result = await role_router.get_all_roles(skip=2, limit=5, db=mock_db, _=MagicMock())
            assert len(result) == 5
            RoleService.get_all_roles.assert_awaited_once_with(
                mock_db,
                skip=2,
                limit=5,
                sort_by="created",
                sort_order="desc"
            )

    async def test_get_all_roles_sorting(self, mock_db, mock_role):
        mock_roles = [mock_role] * 3
        with patch.object(RoleService, "get_all_roles", new_callable=AsyncMock, return_value=mock_roles):
            result = await role_router.get_all_roles(
                skip=0,
                limit=10,
                sort_by="name",
                sort_order="asc",
                db=mock_db,
                _=MagicMock()
            )
            assert len(result) == 3
            RoleService.get_all_roles.assert_awaited_once_with(
                mock_db,
                skip=0,
                limit=10,
                sort_by="name",
                sort_order="asc"
            )

    async def test_assign_role_to_user_success(self, mock_db, mock_current_user):
        with patch.object(UserRoleService, "assign_user_role", new_callable=AsyncMock, return_value=True):
            request_data = AddRoleToUserForRole(user_id=1)
            result = await role_router.assign_role_to_user(1, request_data, mock_db, mock_current_user)
            assert result["message"] == "Role assigned to user"
            UserRoleService.assign_user_role.assert_awaited_once()

    async def test_assign_role_to_user_failure(self, mock_db, mock_current_user):
        with patch.object(UserRoleService, "assign_user_role", new_callable=AsyncMock, return_value=False):
            request_data = AddRoleToUserForRole(user_id=1)
            with pytest.raises(HTTPException) as excinfo:
                await role_router.assign_role_to_user(1, request_data, mock_db, mock_current_user)
            assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST

    async def test_remove_role_from_user_success(self, mock_db):
        with patch.object(UserRoleService, "remove_user_role", new_callable=AsyncMock, return_value=True):
            result = await role_router.remove_role_from_user(1, 1, mock_db, MagicMock())
            assert result["message"] == "Role removed from user"
            UserRoleService.remove_user_role.assert_awaited_once()

    async def test_remove_role_from_user_failure(self, mock_db):
        with patch.object(UserRoleService, "remove_user_role", new_callable=AsyncMock, return_value=False):
            with pytest.raises(HTTPException) as excinfo:
                await role_router.remove_role_from_user(1, 1, mock_db, MagicMock())
            assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST

    async def test_get_users_for_role_success(self, mock_db):
        mock_users = [MagicMock(id=1), MagicMock(id=2)]
        with patch.object(UserRoleService, "get_all_users_for_role", new_callable=AsyncMock, return_value=mock_users):
            result = await role_router.get_users_for_role(1, mock_db, MagicMock())
            assert len(result) == 2
            UserRoleService.get_all_users_for_role.assert_awaited_once()

    async def test_get_users_for_role_not_found(self, mock_db):
        with patch.object(UserRoleService, "get_all_users_for_role", new_callable=AsyncMock, return_value=None):
            with pytest.raises(HTTPException) as excinfo:
                await role_router.get_users_for_role(999, mock_db, MagicMock())
            assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND

    async def test_assign_role_to_group_success(self, mock_db, mock_current_user):
        with patch.object(GroupRoleService, "assign_group_role", new_callable=AsyncMock, return_value=True):
            request_data = AddRoleToGroupForRole(group_id=1)
            result = await role_router.assign_role_to_group(1, request_data, mock_db, mock_current_user)
            assert result["message"] == "Role assigned to group"
            GroupRoleService.assign_group_role.assert_awaited_once()

    async def test_assign_role_to_group_failure(self, mock_db, mock_current_user):
        with patch.object(GroupRoleService, "assign_group_role", new_callable=AsyncMock, return_value=False):
            request_data = AddRoleToGroupForRole(group_id=1)
            with pytest.raises(HTTPException) as excinfo:
                await role_router.assign_role_to_group(1, request_data, mock_db, mock_current_user)
            assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST

    async def test_remove_role_from_group_success(self, mock_db):
        with patch.object(GroupRoleService, "remove_group_role", new_callable=AsyncMock, return_value=True):
            result = await role_router.remove_role_from_group(1, 1, mock_db, MagicMock())
            assert result["message"] == "Role removed from group"
            GroupRoleService.remove_group_role.assert_awaited_once()

    async def test_remove_role_from_group_failure(self, mock_db):
        with patch.object(GroupRoleService, "remove_group_role", new_callable=AsyncMock, return_value=False):
            with pytest.raises(HTTPException) as excinfo:
                await role_router.remove_role_from_group(1, 1, mock_db, MagicMock())
            assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST

    async def test_get_groups_for_role_success(self, mock_db):
        mock_groups = [MagicMock(id=1), MagicMock(id=2)]
        with patch.object(GroupRoleService, "get_all_groups_for_role", new_callable=AsyncMock, return_value=mock_groups):
            result = await role_router.get_groups_for_role(1, mock_db, MagicMock())
            assert len(result) == 2
            GroupRoleService.get_all_groups_for_role.assert_awaited_once()

    async def test_get_groups_for_role_not_found(self, mock_db):
        with patch.object(GroupRoleService, "get_all_groups_for_role", new_callable=AsyncMock, return_value=None):
            with pytest.raises(HTTPException) as excinfo:
                await role_router.get_groups_for_role(999, mock_db, MagicMock())
            assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND

    async def test_add_permission_to_role_success(self, mock_db, mock_current_user):
        with patch.object(RolePermissionService, "assign_role_permission", new_callable=AsyncMock, return_value=True):
            request_data = AddPermissionToRoleForRole(permission_id=1)
            result = await role_router.add_permission_to_role(1, request_data, mock_db, mock_current_user)
            assert result["message"] == "Permission added to role"
            RolePermissionService.assign_role_permission.assert_awaited_once()

    async def test_add_permission_to_role_failure(self, mock_db, mock_current_user):
        with patch.object(RolePermissionService, "assign_role_permission", new_callable=AsyncMock, return_value=False):
            request_data = AddPermissionToRoleForRole(permission_id=1)
            with pytest.raises(HTTPException) as excinfo:
                await role_router.add_permission_to_role(1, request_data, mock_db, mock_current_user)
            assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST

    async def test_remove_permission_from_role_success(self, mock_db):
        with patch.object(RolePermissionService, "remove_role_permission", new_callable=AsyncMock, return_value=True):
            result = await role_router.remove_permission_from_role(1, 1, mock_db, MagicMock())
            assert result["message"] == "Permission removed from role"
            RolePermissionService.remove_role_permission.assert_awaited_once()

    async def test_remove_permission_from_role_failure(self, mock_db):
        with patch.object(RolePermissionService, "remove_role_permission", new_callable=AsyncMock, return_value=False):
            with pytest.raises(HTTPException) as excinfo:
                await role_router.remove_permission_from_role(1, 1, mock_db, MagicMock())
            assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST

    async def test_get_permissions_for_role_success(self, mock_db):
        mock_permissions = [MagicMock(id=1), MagicMock(id=2)]
        with patch.object(RolePermissionService, "get_all_permissions_for_role", new_callable=AsyncMock, return_value=mock_permissions):
            result = await role_router.get_permissions_for_role(1, mock_db, MagicMock())
            assert len(result) == 2
            RolePermissionService.get_all_permissions_for_role.assert_awaited_once()

    async def test_get_permissions_for_role_not_found(self, mock_db):
        with patch.object(RolePermissionService, "get_all_permissions_for_role", new_callable=AsyncMock, return_value=None):
            with pytest.raises(HTTPException) as excinfo:
                await role_router.get_permissions_for_role(999, mock_db, MagicMock())
            assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND
