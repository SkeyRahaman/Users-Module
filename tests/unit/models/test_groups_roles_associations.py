import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.database import GroupRole, Group, Role, User

pytestmark = pytest.mark.asyncio  # all tests in this module are async


class TestGroupRoleModel:

    async def test_create_grouprole_minimal(self, db_session: AsyncSession, test_group: Group, test_role: Role):
        """Test creating a GroupRole association with minimal required data."""
        grouprole = GroupRole(group=test_group, role=test_role)
        db_session.add(grouprole)
        await db_session.commit()
        await db_session.refresh(grouprole)

        # Basic field checks
        assert grouprole.group_id == test_group.id
        assert grouprole.role_id == test_role.id
        assert grouprole.is_deleted is False
        assert grouprole.created_at is not None
        assert grouprole.updated_at is not None

        # Relationship checks
        assert grouprole.group.name == test_group.name
        assert grouprole.role.name == test_role.name

    async def test_duplicate_grouprole_not_allowed(self, db_session: AsyncSession, test_group: Group, test_role: Role):
        """Composite PK should prevent adding same group-role twice."""
        gr1 = GroupRole(group=test_group, role=test_role)
        gr2 = GroupRole(group=test_group, role=test_role)

        db_session.add_all([gr1, gr2])
        with pytest.raises(IntegrityError):
            await db_session.commit()
        await db_session.rollback()

    async def test_soft_delete_grouprole(self, db_session: AsyncSession, test_group: Group, test_role: Role):
        """Test soft-delete behaviour using is_deleted flag."""
        grouprole = GroupRole(group=test_group, role=test_role)
        db_session.add(grouprole)
        await db_session.commit()
        await db_session.refresh(grouprole)

        # Soft delete
        grouprole.is_deleted = True
        await db_session.commit()
        await db_session.refresh(grouprole)

        assert grouprole.is_deleted is True

    async def test_creator_relationship(self, db_session: AsyncSession, test_group: Group, test_role: Role, test_user: User):
        """Test that the creator relationship works."""
        grouprole = GroupRole(group=test_group, role=test_role, created_by=test_user.id)
        db_session.add(grouprole)
        await db_session.commit()
        await db_session.refresh(grouprole)

        assert grouprole.creator.id == test_user.id
