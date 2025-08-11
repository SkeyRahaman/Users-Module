from sqlalchemy import asc, desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.database.models import (
    Group, Role, User, Permission,
    GroupRole, UserGroup, RolePermission
)
from app.schemas.group import GroupCreate, GroupUpdate


class GroupService:
    """Async service layer for group operations"""

    # ---------- CRUD ----------

    @staticmethod
    async def create_group(db: AsyncSession, group_data: GroupCreate) -> Group | None:
        """Create a new group if name doesn't already exist"""
        if await GroupService.check_name_exists(db, group_data.name):
            return None

        group = Group(
            name=group_data.name,
            description=group_data.description
        )
        db.add(group)
        try:
            await db.commit()
            await db.refresh(group)
            return group
        except IntegrityError:
            await db.rollback()
            return None

    @staticmethod
    async def update_group(db: AsyncSession, group_id: int, group_data: GroupUpdate) -> Group | None:
        """Update an existing group"""
        result = await db.execute(
            select(Group).where(Group.id == group_id, Group.is_deleted == False)
        )
        group = result.scalar_one_or_none()
        if not group:
            return None

        for field, value in group_data.model_dump(exclude_unset=True).items():
            setattr(group, field, value)

        try:
            await db.commit()
            await db.refresh(group)
            return group
        except IntegrityError:
            await db.rollback()
            return None

    @staticmethod
    async def delete_group(db: AsyncSession, group_id: int) -> bool:
        """Soft delete a group"""
        result = await db.execute(
            select(Group).where(Group.id == group_id, Group.is_deleted == False)
        )
        group = result.scalar_one_or_none()
        if not group:
            return False

        group.is_deleted = True
        try:
            await db.commit()
            return True
        except IntegrityError:
            await db.rollback()
            return False

    @staticmethod
    async def get_group_by_id(db: AsyncSession, group_id: int) -> Group | None:
        result = await db.execute(
            select(Group).where(Group.id == group_id, Group.is_deleted == False)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_group_by_name(db: AsyncSession, name: str) -> Group | None:
        result = await db.execute(
            select(Group).where(Group.name == name, Group.is_deleted == False)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all_groups(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 10,
        sort_by: str = "created",
        sort_order: str = "desc"
    ) -> list[Group]:
        if not hasattr(Group, sort_by):
            return []

        order_by_clause = desc(getattr(Group, sort_by)) if sort_order == "desc" else asc(getattr(Group, sort_by))

        result = await db.execute(
            select(Group)
            .where(Group.is_deleted == False)
            .order_by(order_by_clause)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def check_name_exists(db: AsyncSession, name: str) -> bool:
        result = await db.execute(
            select(Group).where(Group.name == name, Group.is_deleted == False)
        )
        return result.scalar_one_or_none() is not None

    # ---------- New helper methods ----------

    @staticmethod
    async def get_all_roles_for_group(db: AsyncSession, group_id: int) -> list[Role]:
        """Return all active roles assigned to a group."""
        result = await db.execute(
            select(Role)
            .join(GroupRole, GroupRole.role_id == Role.id)
            .where(
                GroupRole.group_id == group_id,
                GroupRole.is_deleted == False,
                Role.is_deleted == False
            )
        )
        return result.scalars().all()

    @staticmethod
    async def get_all_users_for_group(db: AsyncSession, group_id: int) -> list[User]:
        """Return all active users assigned to a group."""
        result = await db.execute(
            select(User)
            .join(UserGroup, UserGroup.user_id == User.id)
            .where(
                UserGroup.group_id == group_id,
                UserGroup.is_deleted == False,
                User.is_deleted == False
            )
        )
        return result.scalars().all()

    @staticmethod
    async def get_all_permissions_for_group(db: AsyncSession, group_id: int) -> list[Permission]:
        """Return all unique permissions for a group via its roles."""
        result = await db.execute(
            select(Permission)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .join(Role, Role.id == RolePermission.role_id)
            .join(GroupRole, GroupRole.role_id == Role.id)
            .where(
                GroupRole.group_id == group_id,
                GroupRole.is_deleted == False,
                RolePermission.is_deleted == False,
                Permission.is_deleted == False
            )
        )
        # Remove duplicates if a role is linked twice
        permissions = result.scalars().all()
        return list({p.id: p for p in permissions}.values())
