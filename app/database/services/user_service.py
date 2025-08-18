from sqlalchemy import asc, desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.database.models import User, Role, Group, Permission, RolePermission, UserRole, UserGroup, GroupRole
from app.schemas.user import UserCreate, UserUpdate
from app.auth.password_hash import PasswordHasher

class UserService:

    @staticmethod
    async def create_user(db: AsyncSession, user_data: UserCreate) -> User | None:
        if await UserService.check_username_exists(db, user_data.username):
            return None

        if await UserService.check_email_exists(db, user_data.email):
            return None

        hashed_password = PasswordHasher.get_password_hash(user_data.password)
        user = User(
            firstname=user_data.firstname,
            middlename=user_data.middlename,
            lastname=user_data.lastname,
            username=user_data.username,
            email=user_data.email,
            password=hashed_password,
        )
        db.add(user)
        try:
            await db.commit()
            await db.refresh(user)
            return user
        except IntegrityError:
            await db.rollback()
            return None

    @staticmethod
    async def update_user(db: AsyncSession, user_id: int, user_data: UserUpdate) -> User | None:
        result = await db.execute(
            select(User).where(User.id == user_id, User.is_deleted == False)
        )
        user = result.scalar_one_or_none()
        if not user:
            return None

        for field, value in user_data.model_dump(exclude_unset=True).items():
            if field == "password" and value:
                setattr(user, field, PasswordHasher.get_password_hash(value))
            else:
                setattr(user, field, value)

        try:
            await db.commit()
            await db.refresh(user)
            return user
        except IntegrityError:
            await db.rollback()
            return None

    @staticmethod
    async def delete_user(db: AsyncSession, user_id: int) -> bool:
        result = await db.execute(
            select(User).where(User.id == user_id, User.is_deleted == False)
        )
        user = result.scalar_one_or_none()
        if not user:
            return False

        user.is_deleted = True
        try:
            await db.commit()
            return True
        except IntegrityError:
            await db.rollback()
            return False

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
        result = await db.execute(
            select(User).where(User.id == user_id, User.is_deleted == False)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
        result = await db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all_users(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 10,
        sort_by: str = "created",
        sort_order: str = "desc"
    ) -> list[User]:
        if not hasattr(User, sort_by):
            return []

        order_by_clause = (
            desc(getattr(User, sort_by))
            if sort_order == "desc"
            else asc(getattr(User, sort_by))
        )

        result = await db.execute(
            select(User)
            .where(User.is_deleted == False)
            .order_by(order_by_clause)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def check_username_exists(db: AsyncSession, username: str) -> bool:
        result = await db.execute(
            select(User).where(User.username == username, User.is_deleted == False)
        )
        return result.scalar_one_or_none() is not None

    @staticmethod
    async def check_email_exists(db: AsyncSession, email: str) -> bool:
        result = await db.execute(
            select(User).where(User.email == email, User.is_deleted == False)
        )
        return result.scalar_one_or_none() is not None

    @staticmethod
    async def get_all_groups_for_user(db: AsyncSession, user_id: int) -> list[Group]:
        """
        Returns all non-deleted groups that the user is directly assigned to.
        """
        result = await db.execute(
            select(Group)
            .join(UserGroup, UserGroup.group_id == Group.id)
            .where(
                UserGroup.user_id == user_id,
                UserGroup.is_deleted == False,
                Group.is_deleted == False
            )
        )
        return result.scalars().all()

    @staticmethod
    async def get_all_roles_for_user(db: AsyncSession, user_id: int) -> list[Role]:
        """
        Returns all roles for the user:
        - Direct roles from UserRole
        - Roles from groups via UserGroup -> GroupRole
        Removes duplicates.
        """
        # Direct roles
        direct_roles_query = (
            select(Role)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(
                UserRole.user_id == user_id,
                UserRole.is_deleted == False,
                Role.is_deleted == False
            )
        )

        # Roles via groups
        group_roles_query = (
            select(Role)
            .join(GroupRole, GroupRole.role_id == Role.id)
            .join(UserGroup, UserGroup.group_id == GroupRole.group_id)
            .where(
                UserGroup.user_id == user_id,
                UserGroup.is_deleted == False,
                GroupRole.is_deleted == False,
                Role.is_deleted == False
            )
        )

        # Execute queries
        direct_roles_result = await db.execute(direct_roles_query)
        group_roles_result = await db.execute(group_roles_query)

        # Combine and ensure unique Role IDs
        all_roles = {role.id: role for role in (direct_roles_result.scalars().all() + group_roles_result.scalars().all())}

        return list(all_roles.values())
    
    @staticmethod
    async def get_all_permissions_for_user(db: AsyncSession, user_id: int) -> list[Permission]:
        roles = await UserService.get_all_roles_for_user(db, user_id)
        if not roles:
            return []

        role_ids = [role.id for role in roles]
        result = await db.execute(
            select(Permission)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .where(
                RolePermission.role_id.in_(role_ids),
                RolePermission.is_deleted == False,
                Permission.is_deleted == False,
            )
        )
        return list({permission.id: permission for permission in result.scalars().all()}.values())
