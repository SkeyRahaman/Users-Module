import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.database.models import RolePermission, Role, Permission, User

pytestmark = pytest.mark.asyncio  # all tests are async

class TestRolePermissionModel:

    async def test_create_rolepermission_minimal(self, db_session: AsyncSession, test_role: Role, test_permission: Permission):
        """Test creating a RolePermission association with minimal required data."""
        rp = RolePermission(role=test_role, permission=test_permission)
        db_session.add(rp)
        await db_session.commit()
        await db_session.refresh(rp)

        assert rp.role_id == test_role.id
        assert rp.permission_id == test_permission.id
        assert rp.is_deleted is False
        assert rp.created_at is not None
        assert rp.updated_at is not None
        # Relationship checks
        assert rp.role.name == test_role.name
        assert rp.permission.name == test_permission.name

    async def test_duplicate_rolepermission_not_allowed(self, db_session: AsyncSession, test_role: Role, test_permission: Permission):
        """Test that the same role-permission pair can't be added twice due to composite PK."""
        rp1 = RolePermission(role=test_role, permission=test_permission)
        rp2 = RolePermission(role=test_role, permission=test_permission)

        db_session.add_all([rp1, rp2])
        with pytest.raises(IntegrityError):
            await db_session.commit()
        await db_session.rollback()

    async def test_soft_delete_rolepermission(self, db_session: AsyncSession, test_role: Role, test_permission: Permission):
        """Test setting is_deleted to True instead of deleting the row."""
        rp = RolePermission(role=test_role, permission=test_permission)
        db_session.add(rp)
        await db_session.commit()
        await db_session.refresh(rp)

        rp.is_deleted = True
        await db_session.commit()
        await db_session.refresh(rp)

        assert rp.is_deleted is True

    async def test_creator_relationship(self, db_session: AsyncSession, test_role: Role, test_permission: Permission, test_user: User):
        """Test creator relationship is set and loaded."""
        rp = RolePermission(role=test_role, permission=test_permission, created_by=test_user.id)
        db_session.add(rp)
        await db_session.commit()
        await db_session.refresh(rp)
        assert rp.creator.id == test_user.id

