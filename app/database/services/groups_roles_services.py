from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.config import Config
from app.database.models import GroupRole


class GroupRoleService:
    """Service layer for managing Group ↔ Role relationships."""

    @staticmethod
    async def assign_group_role(
        db: AsyncSession,
        group_id: int,
        role_id: int,
        valid_from: datetime | None = None,
        valid_until: datetime | None = None,
        created_by: int | None = None
    ) -> GroupRole:
        """
        Assign a role to a group.
        If already exists and not deleted → update validity.
        If exists but deleted → restore.
        Defaults validity period from Config.DEFAULT_GROUP_ROLE_VALIDITY if not provided.
        """
        if valid_until is None:
            valid_until = datetime.now(timezone.utc) + timedelta(days=Config.DEFAULT_GROUP_ROLE_VALIDITY)
        if valid_from is None:
            valid_from = datetime.now(timezone.utc)

        result = await db.execute(
            select(GroupRole).where(
                GroupRole.group_id == group_id,
                GroupRole.role_id == role_id
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            existing.is_deleted = False
            existing.valid_from = valid_from
            existing.valid_until = valid_until
            existing.created_by = created_by
            group_role = existing
        else:
            group_role = GroupRole(
                group_id=group_id,
                role_id=role_id,
                valid_from=valid_from,
                valid_until=valid_until,
                created_by=created_by
            )
            db.add(group_role)

        try:
            await db.commit()
            await db.refresh(group_role)
            return group_role
        except IntegrityError:
            await db.rollback()
            return None

    @staticmethod
    async def remove_group_role(db: AsyncSession, group_id: int, role_id: int) -> bool:
        """Soft-delete a group-role link."""
        result = await db.execute(
            select(GroupRole).where(
                GroupRole.group_id == group_id,
                GroupRole.role_id == role_id,
                GroupRole.is_deleted == False
            )
        )
        group_role = result.scalar_one_or_none()
        if not group_role:
            return False

        group_role.is_deleted = True
        try:
            await db.commit()
            return True
        except IntegrityError:
            await db.rollback()
            return False

    @staticmethod
    async def extend_validity(
        db: AsyncSession,
        group_id: int,
        role_id: int,
        new_valid_until: datetime
    ) -> bool:
        """Extend the validity period for a group-role link."""
        result = await db.execute(
            select(GroupRole).where(
                GroupRole.group_id == group_id,
                GroupRole.role_id == role_id,
                GroupRole.is_deleted == False
            )
        )
        group_role = result.scalar_one_or_none()
        if not group_role:
            return False

        group_role.valid_until = new_valid_until
        try:
            await db.commit()
            return True
        except IntegrityError:
            await db.rollback()
            return False

    @staticmethod
    async def expire_group_role(db: AsyncSession, group_id: int, role_id: int) -> bool:
        """Expire a group-role link immediately."""
        result = await db.execute(
            select(GroupRole).where(
                GroupRole.group_id == group_id,
                GroupRole.role_id == role_id,
                GroupRole.is_deleted == False
            )
        )
        group_role = result.scalar_one_or_none()
        if not group_role:
            return False

        group_role.valid_until = datetime.now(timezone.utc)
        try:
            await db.commit()
            return True
        except IntegrityError:
            await db.rollback()
            return False

    @staticmethod
    async def check_group_role_exists(db: AsyncSession, group_id: int, role_id: int) -> bool:
        """Check if an active group-role link exists."""
        result = await db.execute(
            select(GroupRole).where(
                GroupRole.group_id == group_id,
                GroupRole.role_id == role_id,
                GroupRole.is_deleted == False
            )
        )
        return result.scalar_one_or_none() is not None
