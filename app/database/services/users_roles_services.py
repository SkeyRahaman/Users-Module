from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.config import Config
from app.database.models import UserRole, Role, User
from app.utils.logger import log


class UserRoleService:
    """Service layer for managing User ↔ Role relationships."""

    @staticmethod
    async def assign_user_role(
        db: AsyncSession,
        user_id: int,
        role_id: int,
        valid_from: datetime | None = None,
        valid_until: datetime | None = None,
        created_by: int | None = None
    ) -> UserRole:
        """
        Assign a role to a user.
        If exists and not deleted → update validity.
        If exists but deleted → restore and update validity.
        If no valid_until provided → defaults to now + Config.DEFAULT_USER_ROLE_VALIDITY days.
        """
        if valid_until is None:
            valid_until = datetime.now(timezone.utc) + timedelta(days=Config.DEFAULT_USER_ROLE_VALIDITY)
        if valid_from is None:
            valid_from = datetime.now(timezone.utc)

        result = await db.execute(
            select(UserRole).where(
                UserRole.user_id == user_id,
                UserRole.role_id == role_id
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            existing.is_deleted = False
            existing.valid_from = valid_from
            existing.valid_until = valid_until
            existing.created_by = created_by
            user_role = existing
        else:
            user_role = UserRole(
                user_id=user_id,
                role_id=role_id,
                valid_from=valid_from,
                valid_until=valid_until,
                created_by=created_by
            )
            db.add(user_role)

        try:
            await db.commit()
            await db.refresh(user_role)
            log.info("User role assigned", user_id=user_id, role_id=role_id)
            return user_role
        except IntegrityError:
            await db.rollback()
            log.error("Failed to assign user role", user_id=user_id, role_id=role_id)
            return None

    @staticmethod
    async def remove_user_role(db: AsyncSession, user_id: int, role_id: int) -> bool:
        """Soft-delete a user-role link."""
        result = await db.execute(
            select(UserRole).where(
                UserRole.user_id == user_id,
                UserRole.role_id == role_id,
                UserRole.is_deleted == False
            )
        )
        user_role = result.scalar_one_or_none()
        if not user_role:
            return False

        user_role.is_deleted = True
        try:
            await db.commit()
            log.info("User role deleted", user_id=user_id, role_id=role_id)
            return True
        except IntegrityError:
            await db.rollback()
            log.error("Failed to delete user role", user_id=user_id, role_id=role_id)
            return False

    @staticmethod
    async def extend_validity(
        db: AsyncSession,
        user_id: int,
        role_id: int,
        new_valid_until: datetime
    ) -> bool:
        """Extend the validity period for a user-role link."""
        result = await db.execute(
            select(UserRole).where(
                UserRole.user_id == user_id,
                UserRole.role_id == role_id,
                UserRole.is_deleted == False
            )
        )
        user_role = result.scalar_one_or_none()
        if not user_role:
            return False

        user_role.valid_until = new_valid_until
        try:
            await db.commit()
            return True
        except IntegrityError:
            await db.rollback()
            return False

    @staticmethod
    async def expire_user_role(db: AsyncSession, user_id: int, role_id: int) -> bool:
        """Expire a user-role link immediately using UTC now."""
        result = await db.execute(
            select(UserRole).where(
                UserRole.user_id == user_id,
                UserRole.role_id == role_id,
                UserRole.is_deleted == False
            )
        )
        user_role = result.scalar_one_or_none()
        if not user_role:
            return False

        user_role.valid_until = datetime.now(timezone.utc)
        try:
            await db.commit()
            log.info("User role expired", user_id=user_id, role_id=role_id)
            return True
        except IntegrityError:
            log.error("Failed to expire user role", user_id=user_id, role_id=role_id)
            await db.rollback()
            return False


    @staticmethod
    async def check_user_role_exists(db: AsyncSession, user_id: int, role_id: int) -> bool:
        result = await db.execute(
            select(UserRole).where(
                UserRole.user_id == user_id,
                UserRole.role_id == role_id,
                UserRole.is_deleted == False
            )
        )
        return result.scalar_one_or_none() is not None
    
    @staticmethod
    async def get_all_roles_for_user(db: AsyncSession, user_id: int) -> list[UserRole]:
        """Fetch all active roles assigned to a user."""
        #check if user exists
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()
        if not user:
            return None
        result = await db.execute(
            select(Role)
            .join(UserRole, Role.id == UserRole.role_id)
            .where(
                UserRole.user_id == user_id,
                UserRole.is_deleted == False,
                Role.is_deleted == False
            )
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_all_users_for_role(db: AsyncSession, role_id: int) -> list[User]:
        """Fetch all active users assigned to a role."""
        #check if role exists
        role_result = await db.execute(select(Role).where(Role.id == role_id))
        role = role_result.scalar_one_or_none()
        if not role:
            return None
        result = await db.execute(
            select(User)
            .join(UserRole, User.id == UserRole.user_id)
            .where(
                UserRole.role_id == role_id,
                UserRole.is_deleted == False,
                User.is_active == True
            )
        )
        return result.scalars().all()