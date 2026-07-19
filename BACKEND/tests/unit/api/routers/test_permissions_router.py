import pytest
from fastapi import HTTPException, status
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.api.routers import permissions as permission_router
from app.database.services import PermissionService, RolePermissionService
from app.schemas import PermissionCreate, PermissionUpdate, AddPermissionToRoleForPermission, RoleOut

@pytest.mark.asyncio
class Testpermission_router:

    async def test_create_permission_success(self, mock_db, mock_permission):
        with patch.object(PermissionService, "create_permission", new_callable=AsyncMock, return_value=mock_permission):
            permission_data = PermissionCreate(
                name="test_permission",
                description="Test description"
            )
            response = await permission_router.create_permission(permission_data, mock_db, MagicMock())
            assert response.id == 1
            assert response.name == "test_permission"
            PermissionService.create_permission.assert_awaited_once_with(mock_db, permission_data)

    async def test_create_permission_duplicate(self, mock_db):
        with patch.object(PermissionService, "create_permission", new_callable=AsyncMock, return_value=None):
            permission_data = PermissionCreate(
                name="duplicate",
                description="Should fail"
            )
            with pytest.raises(HTTPException) as exc_info:
                await permission_router.create_permission(permission_data, mock_db, MagicMock())
            assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
            assert "already exists" in exc_info.value.detail

    async def test_get_permission_success(self, mock_db, mock_permission):
        with patch.object(PermissionService, "get_permission_by_id", new_callable=AsyncMock, return_value=mock_permission):
            response = await permission_router.get_permission(1, mock_db, MagicMock())
            assert response.id == 1
            assert response.name == "test_permission"
            PermissionService.get_permission_by_id.assert_awaited_once_with(mock_db, 1)

    async def test_get_permission_not_found(self, mock_db):
        with patch.object(PermissionService, "get_permission_by_id", new_callable=AsyncMock, return_value=None):
            with pytest.raises(HTTPException) as exc_info:
                await permission_router.get_permission(999, mock_db, MagicMock())
            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    async def test_update_permission_success(self, mock_db, mock_permission):
        update_data = PermissionUpdate(description="Updated description")
        with patch.object(PermissionService, "update_permission", new_callable=AsyncMock, return_value=mock_permission):
            response = await permission_router.update_permission(1, update_data, mock_db, MagicMock())
            assert response.id == 1
            assert response.description == "Test description"  # mock returns original
            PermissionService.update_permission.assert_awaited_once_with(mock_db, 1, update_data)

    async def test_update_permission_not_found(self, mock_db):
        update_data = PermissionUpdate(description="Should fail")
        with patch.object(PermissionService, "update_permission", new_callable=AsyncMock, return_value=None):
            with pytest.raises(HTTPException) as exc_info:
                await permission_router.update_permission(999, update_data, mock_db, MagicMock())
            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    async def test_delete_permission_success(self, mock_db):
        with patch.object(PermissionService, "delete_permission", new_callable=AsyncMock, return_value=True):
            response = await permission_router.delete_permission(1, mock_db, MagicMock())
            assert response["message"] == "Permission deleted"
            PermissionService.delete_permission.assert_awaited_once_with(mock_db, 1)

    async def test_delete_permission_not_found(self, mock_db):
        with patch.object(PermissionService, "delete_permission", new_callable=AsyncMock, return_value=False):
            with pytest.raises(HTTPException) as exc_info:
                await permission_router.delete_permission(999, mock_db, MagicMock())
            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_all_permissions(self, mock_db, mock_permission):
        with patch.object(PermissionService, "get_all_permissions", new_callable=AsyncMock, return_value=[mock_permission]):
            response = await permission_router.get_all_permissions(0, 10, "created", "desc", mock_db, MagicMock())
            assert len(response) == 1
            assert response[0].name == "test_permission"
            PermissionService.get_all_permissions.assert_awaited_once()

    async def test_get_all_permissions_pagination(self, mock_db, mock_permission):
        mock_permissions = [mock_permission] * 5
        with patch.object(PermissionService, "get_all_permissions", new_callable=AsyncMock, return_value=mock_permissions):
            response = await permission_router.get_all_permissions(skip=2, limit=5, db=mock_db, _=MagicMock())
            assert len(response) == 5
            PermissionService.get_all_permissions.assert_awaited_once_with(
                mock_db,
                skip=2,
                limit=5,
                sort_by="created",
                sort_order="desc"
            )

    async def test_get_all_permissions_sorting(self, mock_db, mock_permission):
        mock_permissions = [mock_permission] * 3
        with patch.object(PermissionService, "get_all_permissions", new_callable=AsyncMock, return_value=mock_permissions):
            response = await permission_router.get_all_permissions(
                skip=0,
                limit=10,
                sort_by="name",
                sort_order="asc",
                db=mock_db,
                _=MagicMock()
            )
            assert len(response) == 3
            PermissionService.get_all_permissions.assert_awaited_once_with(
                mock_db,
                skip=0,
                limit=10,
                sort_by="name",
                sort_order="asc"
            )

    async def test_add_permission_to_role_success(self, mock_db):
        with patch.object(
            RolePermissionService, "assign_role_permission", new_callable=AsyncMock
        ) as mock_assign:
            mock_assign.return_value = True
            request_data = AddPermissionToRoleForPermission(role_id=1)
            response = await permission_router.add_permission_to_role(
                permission_id=1, request_data=request_data, db=mock_db, current_user=MagicMock(id=123)
            )
            assert response['message'] == "Permission added to role"
            mock_assign.assert_awaited_once_with(db=mock_db, permission_id=1, role_id=1, created_by=123)

    async def test_add_permission_to_role_failure(self, mock_db):
        with patch.object(
            RolePermissionService, "assign_role_permission", new_callable=AsyncMock
        ) as mock_assign:
            mock_assign.return_value = False
            request_data = AddPermissionToRoleForPermission(role_id=2)
            with pytest.raises(HTTPException) as excinfo:
                await permission_router.add_permission_to_role(
                    permission_id=1, request_data=request_data, db=mock_db, current_user=MagicMock(id=123)
                )
            assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST
            assert "Failed to add permission to role" in excinfo.value.detail

    async def test_remove_permission_from_role_success(self, mock_db):
        with patch.object(
            RolePermissionService, "remove_role_permission", new_callable=AsyncMock
        ) as mock_remove:
            mock_remove.return_value = True
            response = await permission_router.remove_permission_from_role(
                permission_id=1, role_id=1, db=mock_db, _=MagicMock()
            )
            assert response["message"] == "Permission removed from role"
            mock_remove.assert_awaited_once_with(db=mock_db, permission_id=1, role_id=1)

    async def test_remove_permission_from_role_failure(self, mock_db):
        with patch.object(
            RolePermissionService, "remove_role_permission", new_callable=AsyncMock
        ) as mock_remove:
            mock_remove.return_value = False
            with pytest.raises(HTTPException) as excinfo:
                await permission_router.remove_permission_from_role(
                    permission_id=1, role_id=1, db=mock_db, _=MagicMock()
                )
            assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST
            assert "Failed to remove permission from role" in excinfo.value.detail

    async def test_list_roles_for_permission_success(self, mock_db):
        mock_roles = [RoleOut(id=1, name="Admin", created = datetime.now()), RoleOut(id=2, name="User", created = datetime.now())]
        with patch.object(
            RolePermissionService, "get_all_roles_for_permission", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = mock_roles
            response = await permission_router.list_roles_for_permission(
                permission_id=1, db=mock_db, _=MagicMock()
            )
            assert isinstance(response, list)
            assert response[0].id == 1
            assert response[1].name == "User"
            mock_get.assert_awaited_once_with(db=mock_db, permission_id=1)

    async def test_list_roles_for_permission_not_found(self, mock_db):
        with patch.object(
            RolePermissionService, "get_all_roles_for_permission", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = None
            with pytest.raises(HTTPException) as excinfo:
                await permission_router.list_roles_for_permission(
                    permission_id=999, db=mock_db, _=MagicMock()
                )
            assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND
            assert "Permission not found" in excinfo.value.detail