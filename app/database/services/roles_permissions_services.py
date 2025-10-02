from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.database.models import RolePermission, Role, Permission


class RolePermissionService:
    """Service layer for managing Role ↔ Permission relationships."""

    @staticmethod
    async def assign_role_permission(
        db: AsyncSession,
        role_id: int,
        permission_id: int,
        created_by: int | None = None
    ) -> RolePermission:
        """
        Assign a permission to a role.
        If exists and is not deleted → update metadata.
        If exists but deleted → restore (mark is_deleted=False).
        """
        result = await db.execute(
            select(RolePermission).where(
                RolePermission.role_id == role_id,
                RolePermission.permission_id == permission_id
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            existing.is_deleted = False
            existing.created_by = created_by
            role_permission = existing
        else:
            # Check if role and permission exist
            role_result = await db.execute(select(Role).where(Role.id == role_id))
            permission_result = await db.execute(select(Permission).where(Permission.id == permission_id))
            role = role_result.scalar_one_or_none()
            permission = permission_result.scalar_one_or_none()
            if not role or not permission:
                return None
            role_permission = RolePermission(
                role_id=role_id,
                permission_id=permission_id,
                created_by=created_by
            )
            db.add(role_permission)

        try:
            await db.commit()
            await db.refresh(role_permission)
            return role_permission
        except IntegrityError:
            await db.rollback()
            return None

    @staticmethod
    async def remove_role_permission(db: AsyncSession, role_id: int, permission_id: int) -> bool:
        """Soft delete a role-permission mapping."""
        result = await db.execute(
            select(RolePermission).where(
                RolePermission.role_id == role_id,
                RolePermission.permission_id == permission_id,
                RolePermission.is_deleted == False
            )
        )
        rp = result.scalar_one_or_none()
        if not rp:
            return False

        rp.is_deleted = True
        try:
            await db.commit()
            return True
        except IntegrityError:
            await db.rollback()
            return False

    @staticmethod
    async def check_role_permission_exists(db: AsyncSession, role_id: int, permission_id: int) -> bool:
        """Return True if an active role-permission mapping exists."""
        result = await db.execute(
            select(RolePermission).where(
                RolePermission.role_id == role_id,
                RolePermission.permission_id == permission_id,
                RolePermission.is_deleted == False
            )
        )
        return result.scalar_one_or_none() is not None
    
    @staticmethod
    async def get_all_permissions_for_role(db: AsyncSession, role_id: int) -> list[RolePermission]:
        """Fetch all active permissions assigned to a role."""
        #check if role exists
        role_result = await db.execute(select(Role).where(Role.id == role_id))
        role = role_result.scalar_one_or_none()
        if not role:
            return None
        result = await db.execute(
            select(Permission)
            .join(RolePermission, Permission.id == RolePermission.permission_id)
            .where(
                RolePermission.role_id == role_id,
                RolePermission.is_deleted == False
            )
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_all_roles_for_permission(db: AsyncSession, permission_id: int) -> list[Role]:
        """Fetch all active roles assigned to a permission."""
        #check if permission exists
        perm_result = await db.execute(select(Permission).where(Permission.id == permission_id))
        permission = perm_result.scalar_one_or_none()
        if not permission:
            return None
        result = await db.execute(
            select(Role)
            .join(RolePermission, Role.id == RolePermission.role_id)
            .where(
                RolePermission.permission_id == permission_id,
                RolePermission.is_deleted == False
            )
        )
        return result.scalars().all()
