import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.permission import PermissionCreate, PermissionUpdate
from app.database.services.permission_service import PermissionService
from app.database.models import Permission, Role, Group, User


@pytest.mark.asyncio
class TestPermissionService:

    async def test_create_permission_success(self, db_session: AsyncSession):
        data = PermissionCreate(name="perm_test", description="Test permission")
        permission = await PermissionService.create_permission(db_session, data)

        assert permission is not None
        assert permission.name == "perm_test"

    async def test_create_permission_duplicate_name(self, db_session: AsyncSession, test_permission: Permission):
        dup_data = PermissionCreate(name=test_permission.name, description="Duplicate")
        result = await PermissionService.create_permission(db_session, dup_data)
        assert result is None

    async def test_get_permission_by_id_and_name(self, db_session: AsyncSession, test_permission: Permission):
        by_id = await PermissionService.get_permission_by_id(db_session, test_permission.id)
        assert by_id.id == test_permission.id

        by_name = await PermissionService.get_permission_by_name(db_session, test_permission.name)
        assert by_name.name == test_permission.name

    async def test_update_permission(self, db_session: AsyncSession, test_permission: Permission):
        update_data = PermissionUpdate(description="Updated description")
        updated = await PermissionService.update_permission(db_session, test_permission.id, update_data)

        assert updated is not None
        assert updated.description == "Updated description"

    async def test_check_name_exists(self, db_session: AsyncSession, test_permission: Permission):
        assert await PermissionService.check_name_exists(db_session, test_permission.name) is True
        assert await PermissionService.check_name_exists(db_session, "Nonexistent") is False

    async def test_get_all_permissions(self, db_session: AsyncSession, test_permission: Permission):
        permissions = await PermissionService.get_all_permissions(db_session, skip=0, limit=100, sort_by="name", sort_order="asc")
        assert isinstance(permissions, list)
        assert any(p.id == test_permission.id for p in permissions)

    async def test_delete_permission(self, db_session: AsyncSession, test_permission: Permission):
        result = await PermissionService.delete_permission(db_session, test_permission.id)
        assert result is True

        deleted = await PermissionService.get_permission_by_id(db_session, test_permission.id)
        assert deleted is None

    # New helper method tests

    async def test_get_all_roles_for_permission(self, db_session: AsyncSession, test_link_role_permission):
        role, perm = test_link_role_permission
        roles = await PermissionService.get_all_roles_for_permission(db_session, perm.id)

        assert isinstance(roles, list)
        assert any(r.id == role.id for r in roles)

    async def test_get_all_groups_for_permission(self, db_session: AsyncSession, test_link_group_role_permission):
        group, role, perm = test_link_group_role_permission
        groups = await PermissionService.get_all_groups_for_permission(db_session, perm.id)

        assert isinstance(groups, list)
        assert any(g.id == group.id for g in groups)

    async def test_get_all_users_for_permission_direct(self, db_session: AsyncSession, test_link_user_role_permission):
        user, role, perm = test_link_user_role_permission
        users = await PermissionService.get_all_users_for_permission(db_session, perm.id)

        assert isinstance(users, list)
        assert any(u.id == user.id for u in users)

    async def test_get_all_users_for_permission_via_group(self, db_session: AsyncSession, test_link_user_group_role_permission):
        user, group, role, perm = test_link_user_group_role_permission
        users = await PermissionService.get_all_users_for_permission(db_session, perm.id)

        assert isinstance(users, list)
        assert any(u.id == user.id for u in users)
