import pytest
import uuid
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import Role, User, Group, Permission, UserRole, GroupRole, RolePermission

pytestmark = pytest.mark.asyncio


class TestRoleModel:

    async def test_create_role_minimal(self, db_session: AsyncSession):
        """Test creating a Role with minimal required data."""
        role = Role(
            name="role_" + uuid.uuid4().hex[:6]
        )
        db_session.add(role)
        await db_session.commit()
        await db_session.refresh(role)

        assert role.id is not None
        assert role.is_active is True
        assert role.is_deleted is False
        assert role.created is not None
        assert role.updated is not None

    async def test_role_name_unique(self, db_session: AsyncSession, test_role: Role):
        """Test that Role.name is unique."""
        dup_role = Role(
            name=test_role.name
        )
        db_session.add(dup_role)
        with pytest.raises(IntegrityError):
            await db_session.commit()
        await db_session.rollback()

    async def test_role_users_and_groups(self, db_session: AsyncSession, test_role: Role, test_user: User, test_group: Group, test_permission: Permission):
        """
        Test reading back relationships from Role:
        - role_users -> should link to UserRole and User
        - role_groups -> should link to GroupRole and Group
        """
        user_role = UserRole(user=test_user, role=test_role)
        group_role = GroupRole(group=test_group, role=test_role)
        role_permissions = RolePermission(role=test_role, permission=test_permission)

        db_session.add_all([user_role, group_role, role_permissions])
        await db_session.commit()
        await db_session.refresh(test_role, ["role_users", "role_groups", "role_permissions"])

        # Verify user_roles relationship
        assert len(test_role.role_users) == 1
        assert test_role.role_users[0].user.username == test_user.username

        # Verify group_roles relationship
        assert len(test_role.role_groups) == 1
        assert test_role.role_groups[0].group.name == test_group.name

        assert len(test_role.role_permissions) == 1
        assert test_role.role_permissions[0].permission.name == test_permission.name
