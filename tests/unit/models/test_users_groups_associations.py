import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.database import UserGroup, User, Group

pytestmark = pytest.mark.asyncio  # all tests in this module are async


class TestUserGroupModel:

    async def test_create_usergroup_minimal(self, db_session: AsyncSession, test_user: User, test_group: Group):
        """Test creating a UserGroup association with minimal data."""
        usergroup = UserGroup(user=test_user, group=test_group)
        db_session.add(usergroup)
        await db_session.commit()
        await db_session.refresh(usergroup)

        # Basic field checks
        assert usergroup.user_id == test_user.id
        assert usergroup.group_id == test_group.id
        assert usergroup.is_deleted is False
        assert usergroup.created_at is not None
        assert usergroup.updated_at is not None

        # Relationship checks
        assert usergroup.user.username == test_user.username
        assert usergroup.group.name == test_group.name

    async def test_duplicate_usergroup_not_allowed(self, db_session: AsyncSession, test_user: User, test_group: Group):
        """Test that the same user-group pair can't be added twice due to composite PK."""
        ug1 = UserGroup(user=test_user, group=test_group)
        ug2 = UserGroup(user=test_user, group=test_group)

        db_session.add_all([ug1, ug2])
        with pytest.raises(IntegrityError):
            await db_session.commit()
        await db_session.rollback()

    async def test_soft_delete_usergroup(self, db_session: AsyncSession, test_user: User, test_group: Group):
        """Test setting is_deleted to True instead of deleting the row."""
        usergroup = UserGroup(user=test_user, group=test_group)
        db_session.add(usergroup)
        await db_session.commit()
        await db_session.refresh(usergroup)

        # Soft delete
        usergroup.is_deleted = True
        await db_session.commit()
        await db_session.refresh(usergroup)

        assert usergroup.is_deleted is True
