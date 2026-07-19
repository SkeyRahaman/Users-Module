from sqlalchemy import asc, desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.database.models import (
    Permission, Role, Group, User,
    RolePermission, GroupRole, UserRole, UserGroup
)
from app.schemas.permission import PermissionCreate, PermissionUpdate


class PermissionService:

    # ---------- CRUD ----------

    @staticmethod
    async def create_permission(db: AsyncSession, permission_data: PermissionCreate) -> Permission | None:
        if await PermissionService.check_name_exists(db, permission_data.name):
            return None

        permission = Permission(
            name=permission_data.name,
            description=permission_data.description
        )
        db.add(permission)
        try:
            await db.commit()
            await db.refresh(permission)
            return permission
        except IntegrityError:
            await db.rollback()
            return None

    @staticmethod
    async def update_permission(db: AsyncSession, permission_id: int, permission_data: PermissionUpdate) -> Permission | None:
        result = await db.execute(
            select(Permission).where(
                Permission.id == permission_id,
                Permission.is_deleted == False
            )
        )
        permission = result.scalar_one_or_none()
        if not permission:
            return None

        for field, value in permission_data.model_dump(exclude_unset=True).items():
            setattr(permission, field, value)

        try:
            await db.commit()
            await db.refresh(permission)
            return permission
        except IntegrityError:
            await db.rollback()
            return None

    @staticmethod
    async def delete_permission(db: AsyncSession, permission_id: int) -> bool:
        result = await db.execute(
            select(Permission).where(
                Permission.id == permission_id,
                Permission.is_deleted == False
            )
        )
        permission = result.scalar_one_or_none()
        if not permission:
            return False

        permission.is_deleted = True
        try:
            await db.commit()
            return True
        except IntegrityError:
            await db.rollback()
            return False

    @staticmethod
    async def get_permission_by_id(db: AsyncSession, permission_id: int) -> Permission | None:
        result = await db.execute(
            select(Permission).where(
                Permission.id == permission_id,
                Permission.is_deleted == False
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_permission_by_name(db: AsyncSession, name: str) -> Permission | None:
        result = await db.execute(
            select(Permission).where(
                Permission.name == name,
                Permission.is_deleted == False
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all_permissions(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 10,
        sort_by: str = "created",
        sort_order: str = "desc"
    ) -> list[Permission]:
        if not hasattr(Permission, sort_by):
            return []

        order_by_clause = desc(getattr(Permission, sort_by)) if sort_order == "desc" else asc(getattr(Permission, sort_by))

        result = await db.execute(
            select(Permission)
            .where(Permission.is_deleted == False)
            .order_by(order_by_clause)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def check_name_exists(db: AsyncSession, name: str) -> bool:
        result = await db.execute(
            select(Permission).where(
                Permission.name == name,
                Permission.is_deleted == False
            )
        )
        return result.scalar_one_or_none() is not None

    # ---------- Relationship helpers ----------

    @staticmethod
    async def get_all_roles_for_permission(db: AsyncSession, permission_id: int) -> list[Role]:
        """All roles that have this permission."""
        result = await db.execute(
            select(Role)
            .join(RolePermission, RolePermission.role_id == Role.id)
            .where(
                RolePermission.permission_id == permission_id,
                RolePermission.is_deleted == False,
                Role.is_deleted == False
            )
        )
        return result.scalars().all()

    @staticmethod
    async def get_all_groups_for_permission(db: AsyncSession, permission_id: int) -> list[Group]:
        """All groups that indirectly have this permission via roles."""
        result = await db.execute(
            select(Group)
            .join(GroupRole, GroupRole.group_id == Group.id)
            .join(Role, Role.id == GroupRole.role_id)
            .join(RolePermission, RolePermission.role_id == Role.id)
            .where(
                RolePermission.permission_id == permission_id,
                GroupRole.is_deleted == False,
                RolePermission.is_deleted == False,
                Group.is_deleted == False
            )
        )
        return result.scalars().all()

    @staticmethod
    async def get_all_users_for_permission(db: AsyncSession, permission_id: int) -> list[User]:
        """All unique active users with this permission (direct role or via group roles)."""
        # Direct via UserRole
        direct_users_q = (
            select(User)
            .join(UserRole, UserRole.user_id == User.id)
            .join(Role, Role.id == UserRole.role_id)
            .join(RolePermission, RolePermission.role_id == Role.id)
            .where(
                RolePermission.permission_id == permission_id,
                RolePermission.is_deleted == False,
                UserRole.is_deleted == False,
                User.is_deleted == False
            )
        )

        # Via GroupRole → UserGroup
        group_users_q = (
            select(User)
            .join(UserGroup, UserGroup.user_id == User.id)
            .join(GroupRole, GroupRole.group_id == UserGroup.group_id)
            .join(Role, Role.id == GroupRole.role_id)
            .join(RolePermission, RolePermission.role_id == Role.id)
            .where(
                RolePermission.permission_id == permission_id,
                GroupRole.is_deleted == False,
                UserGroup.is_deleted == False,
                RolePermission.is_deleted == False,
                User.is_deleted == False
            )
        )

        direct_users = (await db.execute(direct_users_q)).scalars().all()
        group_users = (await db.execute(group_users_q)).scalars().all()

        # Deduplicate by user.id
        return list({u.id: u for u in (direct_users + group_users)}.values())
