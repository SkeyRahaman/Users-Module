import pytest
import uuid
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import Group, User, UserGroup, GroupRole, Role

pytestmark = pytest.mark.asyncio  # mark all tests as async


class TestGroupModel:

    async def test_create_group_minimal(self, db_session: AsyncSession):
        """Test creating a Group with minimal data."""
        group = Group(
            name="group_" + uuid.uuid4().hex[:6]
        )
        db_session.add(group)
        await db_session.commit()
        await db_session.refresh(group)

        assert group.id is not None
        assert group.is_active is True
        assert group.is_deleted is False
        assert group.created is not None
        assert group.updated is not None

    async def test_group_name_unique(self, db_session: AsyncSession, test_group: Group):
        """Test uniqueness constraint on Group.name."""
        dup_group = Group(
            name=test_group.name
        )
        db_session.add(dup_group)
        with pytest.raises(IntegrityError):
            await db_session.commit()
        await db_session.rollback()

    async def test_group_users_and_roles(self, db_session: AsyncSession, test_group: Group, test_user: User, test_role: Role):
        """
        Verify group_users and group_roles relationships.
        """
        user_group = UserGroup(user=test_user, group=test_group)
        group_role = GroupRole(group=test_group, role=test_role)

        db_session.add_all([user_group, group_role])
        await db_session.commit()
        await db_session.refresh(test_group, ["group_users", "group_roles"])

        # Check group_users relationship
        assert len(test_group.group_users) == 1
        assert test_group.group_users[0].user.username == test_user.username

        # Check group_roles relationship
        assert len(test_group.group_roles) == 1
        assert test_group.group_roles[0].role.name == test_role.name
