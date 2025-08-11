import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.database.models import UserRole, User, Role

pytestmark = pytest.mark.asyncio  


class TestUserRoleModel:

    async def test_create_userrole_minimal(self, db_session: AsyncSession, test_user: User, test_role: Role):
        """Test creating a UserRole association with minimal data"""
        userrole = UserRole(user=test_user, role=test_role)
        db_session.add(userrole)
        await db_session.commit()
        await db_session.refresh(userrole)

        assert userrole.user_id == test_user.id
        assert userrole.role_id == test_role.id
        assert userrole.is_deleted is False
        assert userrole.created_at is not None
        assert userrole.updated_at is not None

        # Relationship checks
        assert userrole.user.username == test_user.username
        assert userrole.role.name == test_role.name

    async def test_duplicate_userrole_not_allowed(self, db_session: AsyncSession, test_user: User, test_role: Role):
        """Test that the same user-role pair can't be added twice (composite PK)."""
        ur1 = UserRole(user=test_user, role=test_role)
        ur2 = UserRole(user=test_user, role=test_role)

        db_session.add_all([ur1, ur2])
        with pytest.raises(IntegrityError):
            await db_session.commit()
        await db_session.rollback()

    async def test_soft_delete_userrole(self, db_session: AsyncSession, test_user: User, test_role: Role):
        """Test setting is_deleted to True instead of deleting the row."""
        userrole = UserRole(user=test_user, role=test_role)
        db_session.add(userrole)
        await db_session.commit()
        await db_session.refresh(userrole)

        # Soft delete
        userrole.is_deleted = True
        await db_session.commit()
        await db_session.refresh(userrole)

        assert userrole.is_deleted is True
