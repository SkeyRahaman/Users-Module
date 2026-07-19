import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.group import GroupCreate, GroupUpdate
from app.database.services.group_service import GroupService
from app.database.models import Group, Role, User, Permission


@pytest.mark.asyncio
class TestGroupService:

    async def test_create_group_success(self, db_session: AsyncSession):
        data = GroupCreate(name="TestGroup1", description="Desc")
        group = await GroupService.create_group(db_session, data)

        assert group is not None
        assert group.name == "TestGroup1"

    async def test_create_group_duplicate_name(self, db_session: AsyncSession, test_group: Group):
        # Attempt with an existing group's name
        data = GroupCreate(name=test_group.name, description="Duplicate")
        result = await GroupService.create_group(db_session, data)
        assert result is None

    async def test_get_group_by_id_and_name(self, db_session: AsyncSession, test_group: Group):
        by_id = await GroupService.get_group_by_id(db_session, test_group.id)
        assert by_id.id == test_group.id

        by_name = await GroupService.get_group_by_name(db_session, test_group.name)
        assert by_name.name == test_group.name

    async def test_update_group(self, db_session: AsyncSession, test_group: Group):
        update_data = GroupUpdate(description="Updated group description")
        updated = await GroupService.update_group(db_session, test_group.id, update_data)

        assert updated is not None
        assert updated.description == "Updated group description"

    async def test_check_name_exists(self, db_session: AsyncSession, test_group: Group):
        assert await GroupService.check_name_exists(db_session, test_group.name) is True
        assert await GroupService.check_name_exists(db_session, "Nonexistent") is False

    async def test_get_all_groups(self, db_session: AsyncSession, test_group: Group):
        groups = await GroupService.get_all_groups(db_session, skip=0, limit=10, sort_by="name", sort_order="asc")
        assert isinstance(groups, list)
        assert any(g.id == test_group.id for g in groups)

    async def test_delete_group(self, db_session: AsyncSession, test_group: Group):
        result = await GroupService.delete_group(db_session, test_group.id)
        assert result is True
        deleted = await GroupService.get_group_by_id(db_session, test_group.id)
        assert deleted is None

    # -------- New Method Tests --------

    async def test_get_all_roles_for_group(self, db_session: AsyncSession, test_link_group_role):
        group, role = test_link_group_role
        roles = await GroupService.get_all_roles_for_group(db_session, group.id)

        assert isinstance(roles, list)
        assert any(isinstance(r, Role) and r.id == role.id for r in roles)

    async def test_get_all_users_for_group(self, db_session: AsyncSession, test_link_user_group):
        user, group = test_link_user_group
        users = await GroupService.get_all_users_for_group(db_session, group.id)

        assert isinstance(users, list)
        assert any(isinstance(u, User) and u.id == user.id for u in users)

    async def test_get_all_permissions_for_group(self, db_session: AsyncSession, test_link_group_role_permission):
        group, role, permission = test_link_group_role_permission
        permissions = await GroupService.get_all_permissions_for_group(db_session, group.id)

        assert isinstance(permissions, list)
        assert any(isinstance(p, Permission) and p.id == permission.id for p in permissions)
