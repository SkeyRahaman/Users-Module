from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.config import Config
from app.database.models import UserGroup


class UserGroupService:
    """Service layer for managing User ↔ Group relationships."""

    @staticmethod
    async def assign_user_group(
        db: AsyncSession,
        user_id: int,
        group_id: int,
        valid_from: datetime | None = None,
        valid_until: datetime | None = None,
        created_by: int | None = None
    ) -> UserGroup:
        """
        Assign a user to a group.
        If already exists and not deleted → update validity.
        If exists but deleted → restore and update validity.
        Defaults validity to now + Config.DEFAULT_USER_GROUP_VALIDITY days if valid_until not passed.
        """
        if valid_until is None:
            valid_until = datetime.now(timezone.utc) + timedelta(days=Config.DEFAULT_USER_GROUP_VALIDITY)
        if valid_from is None:
            valid_from = datetime.now(timezone.utc)

        result = await db.execute(
            select(UserGroup).where(
                UserGroup.user_id == user_id,
                UserGroup.group_id == group_id
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            existing.is_deleted = False
            existing.valid_from = valid_from
            existing.valid_until = valid_until
            existing.created_by = created_by
            user_group = existing
        else:
            user_group = UserGroup(
                user_id=user_id,
                group_id=group_id,
                valid_from=valid_from,
                valid_until=valid_until,
                created_by=created_by
            )
            db.add(user_group)

        try:
            await db.commit()
            await db.refresh(user_group)
            return user_group
        except IntegrityError:
            await db.rollback()
            return None

    @staticmethod
    async def remove_user_group(db: AsyncSession, user_id: int, group_id: int) -> bool:
        """Soft-delete a user-group link."""
        result = await db.execute(
            select(UserGroup).where(
                UserGroup.user_id == user_id,
                UserGroup.group_id == group_id,
                UserGroup.is_deleted == False
            )
        )
        user_group = result.scalar_one_or_none()
        if not user_group:
            return False

        user_group.is_deleted = True
        try:
            await db.commit()
            return True
        except IntegrityError:
            await db.rollback()
            return False

    @staticmethod
    async def extend_validity(
        db: AsyncSession,
        user_id: int,
        group_id: int,
        new_valid_until: datetime
    ) -> bool:
        """Extend the validity period for a user-group link."""
        result = await db.execute(
            select(UserGroup).where(
                UserGroup.user_id == user_id,
                UserGroup.group_id == group_id,
                UserGroup.is_deleted == False
            )
        )
        user_group = result.scalar_one_or_none()
        if not user_group:
            return False

        user_group.valid_until = new_valid_until
        try:
            await db.commit()
            return True
        except IntegrityError:
            await db.rollback()
            return False

    @staticmethod
    async def expire_user_group(db: AsyncSession, user_id: int, group_id: int) -> bool:
        """Expire a user-group link immediately."""
        result = await db.execute(
            select(UserGroup).where(
                UserGroup.user_id == user_id,
                UserGroup.group_id == group_id,
                UserGroup.is_deleted == False
            )
        )
        user_group = result.scalar_one_or_none()
        if not user_group:
            return False

        user_group.valid_until = datetime.now(timezone.utc)
        try:
            await db.commit()
            return True
        except IntegrityError:
            await db.rollback()
            return False

    @staticmethod
    async def check_user_group_exists(db: AsyncSession, user_id: int, group_id: int) -> bool:
        """Check if an active user-group link exists."""
        result = await db.execute(
            select(UserGroup).where(
                UserGroup.user_id == user_id,
                UserGroup.group_id == group_id,
                UserGroup.is_deleted == False
            )
        )
        return result.scalar_one_or_none() is not None
