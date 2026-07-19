import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.role import RoleCreate, RoleUpdate
from app.database.services.role_service import RoleService
from app.database.models import Role, Permission, Group, User


@pytest.mark.asyncio
class TestRoleService:

    async def test_create_role_success(self, db_session: AsyncSession):
        role_data = RoleCreate(name="Admin", description="Admin role")
        role = await RoleService.create_role(db_session, role_data)

        assert role is not None
        assert isinstance(role, Role)
        assert role.name == "Admin"

    async def test_create_role_duplicate_name(self, db_session: AsyncSession, test_role: Role):
        dup_data = RoleCreate(name=test_role.name, description="Duplicate name")
        result = await RoleService.create_role(db_session, dup_data)
        assert result is None

    async def test_get_role_by_id_and_name(self, db_session: AsyncSession, test_role: Role):
        by_id = await RoleService.get_role_by_id(db_session, test_role.id)
        assert by_id.id == test_role.id

        by_name = await RoleService.get_role_by_name(db_session, test_role.name)
        assert by_name.name == test_role.name

    async def test_update_role(self, db_session: AsyncSession, test_role: Role):
        update_data = RoleUpdate(description="Updated description")
        updated = await RoleService.update_role(db_session, test_role.id, update_data)

        assert updated is not None
        assert updated.description == "Updated description"

    async def test_check_name_exists(self, db_session: AsyncSession, test_role: Role):
        assert await RoleService.check_name_exists(db_session, test_role.name) is True
        assert await RoleService.check_name_exists(db_session, "NoSuchRole") is False

    async def test_get_all_roles(self, db_session: AsyncSession, test_role: Role):
        roles = await RoleService.get_all_roles(db_session, skip=0, limit=10, sort_by="name", sort_order="asc")
        assert isinstance(roles, list)
        assert any(r.id == test_role.id for r in roles)

    async def test_delete_role(self, db_session: AsyncSession, test_role: Role):
        result = await RoleService.delete_role(db_session, test_role.id)
        assert result is True
        deleted = await RoleService.get_role_by_id(db_session, test_role.id)
        assert deleted is None

    # ---------- New Feature Tests ----------

    async def test_get_all_permissions_for_role(self, db_session: AsyncSession, test_link_role_permission):
        role, permission = test_link_role_permission
        permissions = await RoleService.get_all_permissions_for_role(db_session, role.id)

        assert isinstance(permissions, list)
        assert any(isinstance(p, Permission) and p.id == permission.id for p in permissions)

    async def test_get_all_groups_for_role(self, db_session: AsyncSession, test_link_group_role):
        group, role = test_link_group_role
        groups = await RoleService.get_all_groups_for_role(db_session, role.id)

        assert isinstance(groups, list)
        assert any(isinstance(g, Group) and g.id == group.id for g in groups)

    async def test_get_all_users_for_role_direct(self, db_session: AsyncSession, test_link_user_role):
        user, role = test_link_user_role
        users = await RoleService.get_all_users_for_role(db_session, role.id)

        assert isinstance(users, list)
        assert any(isinstance(u, User) and u.id == user.id for u in users)

    async def test_get_all_users_for_role_via_group(self, db_session: AsyncSession, test_link_user_group_role):
        user, group, role = test_link_user_group_role
        users = await RoleService.get_all_users_for_role(db_session, role.id)

        assert isinstance(users, list)
        assert any(isinstance(u, User) and u.id == user.id for u in users)
