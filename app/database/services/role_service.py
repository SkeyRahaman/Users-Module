from sqlalchemy import asc, desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.database.models import (
    Role, Permission, RolePermission,
    Group, GroupRole,
    User, UserRole, UserGroup
)
from app.schemas.role import RoleCreate, RoleUpdate


class RoleService:

    # -------- CRUD -------- #

    @staticmethod
    async def create_role(db: AsyncSession, role_data: RoleCreate) -> Role | None:
        if await RoleService.check_name_exists(db, role_data.name):
            return None

        role = Role(name=role_data.name, description=role_data.description)
        db.add(role)
        try:
            await db.commit()
            await db.refresh(role)
            return role
        except IntegrityError:
            await db.rollback()
            return None

    @staticmethod
    async def update_role(db: AsyncSession, role_id: int, role_data: RoleUpdate) -> Role | None:
        result = await db.execute(
            select(Role).where(Role.id == role_id, Role.is_deleted == False)
        )
        role = result.scalar_one_or_none()
        if not role:
            return None

        for field, value in role_data.model_dump(exclude_unset=True).items():
            setattr(role, field, value)

        try:
            await db.commit()
            await db.refresh(role)
            return role
        except IntegrityError:
            await db.rollback()
            return None

    @staticmethod
    async def delete_role(db: AsyncSession, role_id: int) -> bool:
        result = await db.execute(
            select(Role).where(Role.id == role_id, Role.is_deleted == False)
        )
        role = result.scalar_one_or_none()
        if not role:
            return False

        role.is_deleted = True
        try:
            await db.commit()
            return True
        except IntegrityError:
            await db.rollback()
            return False

    @staticmethod
    async def get_role_by_id(db: AsyncSession, role_id: int) -> Role | None:
        result = await db.execute(
            select(Role).where(Role.id == role_id, Role.is_deleted == False)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_role_by_name(db: AsyncSession, name: str) -> Role | None:
        result = await db.execute(
            select(Role).where(Role.name == name, Role.is_deleted == False)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all_roles(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 10,
        sort_by: str = "created",
        sort_order: str = "desc"
    ) -> list[Role]:
        if not hasattr(Role, sort_by):
            return []

        order_by_clause = desc(getattr(Role, sort_by)) if sort_order == "desc" else asc(getattr(Role, sort_by))

        result = await db.execute(
            select(Role)
            .where(Role.is_deleted == False)
            .order_by(order_by_clause)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def check_name_exists(db: AsyncSession, name: str) -> bool:
        result = await db.execute(
            select(Role).where(Role.name == name, Role.is_deleted == False)
        )
        return result.scalar_one_or_none() is not None

    @staticmethod
    async def get_all_permissions_for_role(db: AsyncSession, role_id: int) -> list[Permission]:
        """
        Returns all non-deleted permissions directly linked to a role.
        """
        result = await db.execute(
            select(Permission)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .where(
                RolePermission.role_id == role_id,
                RolePermission.is_deleted == False,
                Permission.is_deleted == False
            )
        )
        return result.scalars().all()

    @staticmethod
    async def get_all_groups_for_role(db: AsyncSession, role_id: int) -> list[Group]:
        """
        Returns all non-deleted groups directly linked to a role.
        """
        result = await db.execute(
            select(Group)
            .join(GroupRole, GroupRole.group_id == Group.id)
            .where(
                GroupRole.role_id == role_id,
                GroupRole.is_deleted == False,
                Group.is_deleted == False
            )
        )
        return result.scalars().all()

    @staticmethod
    async def get_all_users_for_role(db: AsyncSession, role_id: int) -> list[User]:
        """
        Returns all unique users for a role:
        - Direct via UserRole
        - Indirect via GroupRole -> UserGroup
        """
        # Direct users
        direct_users_query = (
            select(User)
            .join(UserRole, UserRole.user_id == User.id)
            .where(
                UserRole.role_id == role_id,
                UserRole.is_deleted == False,
                User.is_deleted == False
            )
        )

        # Users via groups
        indirect_users_query = (
            select(User)
            .join(UserGroup, UserGroup.user_id == User.id)
            .join(GroupRole, GroupRole.group_id == UserGroup.group_id)
            .where(
                GroupRole.role_id == role_id,
                UserGroup.is_deleted == False,
                GroupRole.is_deleted == False,
                User.is_deleted == False
            )
        )

        direct_users = (await db.execute(direct_users_query)).scalars().all()
        indirect_users = (await db.execute(indirect_users_query)).scalars().all()

        # Deduplicate by user ID
        all_users = {u.id: u for u in (direct_users + indirect_users)}
        return list(all_users.values())
