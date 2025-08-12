import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.services.roles_permissions_services import RolePermissionService


@pytest.mark.asyncio
class TestRolePermissionService:

    async def test_assign_creates_new(self, db_session: AsyncSession, test_role, test_permission):
        rp = await RolePermissionService.assign_role_permission(
            db_session, test_role.id, test_permission.id
        )

        assert rp is not None
        assert rp.role_id == test_role.id
        assert rp.permission_id == test_permission.id
        assert rp.is_deleted is False

    async def test_assign_existing_does_not_duplicate(self, db_session: AsyncSession, test_link_role_permission):
        role, permission = test_link_role_permission

        rp = await RolePermissionService.assign_role_permission(db_session, role.id, permission.id)
        assert rp.is_deleted is False

    async def test_assign_restores_deleted(self, db_session: AsyncSession, test_link_role_permission):
        role, permission = test_link_role_permission

        # soft delete first
        await RolePermissionService.remove_role_permission(db_session, role.id, permission.id)
        assert await RolePermissionService.check_role_permission_exists(db_session, role.id, permission.id) is False

        restored = await RolePermissionService.assign_role_permission(db_session, role.id, permission.id)
        assert restored.is_deleted is False
        assert await RolePermissionService.check_role_permission_exists(db_session, role.id, permission.id) is True

    async def test_remove_role_permission(self, db_session: AsyncSession, test_link_role_permission):
        role, permission = test_link_role_permission
        result = await RolePermissionService.remove_role_permission(db_session, role.id, permission.id)
        assert result is True

        exists = await RolePermissionService.check_role_permission_exists(db_session, role.id, permission.id)
        assert exists is False

    async def test_check_role_permission_exists_true(self, db_session: AsyncSession, test_link_role_permission):
        role, permission = test_link_role_permission
        assert await RolePermissionService.check_role_permission_exists(db_session, role.id, permission.id) is True

    async def test_check_role_permission_exists_false(self, db_session: AsyncSession, test_role, test_permission):
        assert await RolePermissionService.check_role_permission_exists(db_session, test_role.id, test_permission.id) is False
