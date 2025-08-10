import pytest
import uuid
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import Permission, Role, RolePermission

pytestmark = pytest.mark.asyncio


class TestPermissionModel:

    async def test_create_permission_minimal(self, db_session: AsyncSession):
        """Test creation with minimal data"""
        perm = Permission(
            name="perm_" + uuid.uuid4().hex[:8]
        )
        db_session.add(perm)
        await db_session.commit()
        await db_session.refresh(perm)

        assert perm.id is not None
        assert perm.name.startswith("perm_")
        assert perm.is_active is True
        assert perm.is_deleted is False
        assert perm.created is not None
        assert perm.updated is not None

    async def test_permission_name_unique(self, db_session: AsyncSession, test_permission: Permission):
        """Test uniqueness constraint on Permission.name"""
        dup_perm = Permission(
            name=test_permission.name
        )
        db_session.add(dup_perm)
        with pytest.raises(IntegrityError):
            await db_session.commit()
        await db_session.rollback()

    async def test_permission_roles_relationship(self, db_session: AsyncSession, test_permission: Permission, test_role: Role):
        """
        Test Permission <-> RolePermission relationship
        """
        role_perm = RolePermission(permission=test_permission, role=test_role)
        db_session.add(role_perm)
        await db_session.commit()
        await db_session.refresh(test_permission, ["permission_roles"])

        assert len(test_permission.permission_roles) == 1
        assert test_permission.permission_roles[0].role.id == test_role.id
