import pytest
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import Config
from app.database.services.users_roles_services import UserRoleService
from app.database.models import UserRole


# --- Helper to normalize DB datetime to UTC-aware ---
def to_utc_aware(dt: datetime) -> datetime:
    """
    Ensure that a datetime is timezone-aware in UTC.
    Works for SQLite (naive) and Postgres (aware) results.
    """
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


@pytest.mark.asyncio
class TestUserRoleService:

    async def test_assign_creates_new_with_default_validity(self, db_session: AsyncSession, test_user, test_role):
        before = datetime.now(timezone.utc)
        user_role = await UserRoleService.assigne_user_role(db_session, test_user.id, test_role.id)

        assert user_role is not None
        assert user_role.user_id == test_user.id
        assert user_role.role_id == test_role.id
        assert to_utc_aware(user_role.valid_from) >= before
        assert to_utc_aware(user_role.valid_until).date() == (
            before + timedelta(days=Config.DEFAULT_USER_ROLE_VALIDITY)
        ).date()
        assert user_role.is_deleted is False

    async def test_assign_existing_updates_validity(self, db_session: AsyncSession, test_link_user_role):
        user, role = test_link_user_role
        new_until = datetime.now(timezone.utc) + timedelta(days=10)

        updated = await UserRoleService.assigne_user_role(
            db_session,
            user.id,
            role.id,
            valid_from=datetime.now(timezone.utc),
            valid_until=new_until
        )

        assert to_utc_aware(updated.valid_until) == to_utc_aware(new_until)
        assert updated.is_deleted is False

    async def test_assign_restores_deleted(self, db_session: AsyncSession, test_link_user_role):
        user, role = test_link_user_role

        # mark as deleted
        await UserRoleService.remove_user_role(db_session, user.id, role.id)
        assert await UserRoleService.check_user_role_exists(db_session, user.id, role.id) is False

        restored = await UserRoleService.assigne_user_role(db_session, user.id, role.id)
        assert restored.is_deleted is False
        assert await UserRoleService.check_user_role_exists(db_session, user.id, role.id) is True

    async def test_remove_user_role(self, db_session: AsyncSession, test_link_user_role):
        user, role = test_link_user_role

        result = await UserRoleService.remove_user_role(db_session, user.id, role.id)
        assert result is True

        check = await UserRoleService.check_user_role_exists(db_session, user.id, role.id)
        assert check is False

    async def test_extend_validity(self, db_session: AsyncSession, test_link_user_role):
        user, role = test_link_user_role
        new_until = datetime.now(timezone.utc) + timedelta(days=60)

        result = await UserRoleService.extend_validity(db_session, user.id, role.id, new_until)
        assert result is True

        # Verify normalized
        ur = await db_session.get(UserRole, {"user_id": user.id, "role_id": role.id})
        assert to_utc_aware(ur.valid_until) == to_utc_aware(new_until)

    async def test_expire_user_role(self, db_session: AsyncSession, test_link_user_role):
        user, role = test_link_user_role
        before = datetime.now(timezone.utc)

        result = await UserRoleService.expire_user_role(db_session, user.id, role.id)
        assert result is True

        # Verify normalized UTC dates
        ur = await db_session.get(UserRole, {"user_id": user.id, "role_id": role.id})
        vu = to_utc_aware(ur.valid_until)
        assert vu >= before
        assert vu <= datetime.now(timezone.utc)

    async def test_check_user_role_exists_true(self, db_session: AsyncSession, test_link_user_role):
        user, role = test_link_user_role
        assert await UserRoleService.check_user_role_exists(db_session, user.id, role.id) is True

    async def test_check_user_role_exists_false(self, db_session: AsyncSession, test_user, test_role):
        assert await UserRoleService.check_user_role_exists(db_session, test_user.id, test_role.id) is False

    async def test_getallrolesforuser_returns_roles(self, db_session: AsyncSession, test_user, test_role):
        # Assign the role to user
        await UserRoleService.assigne_user_role(db_session, test_user.id, test_role.id)
        roles = await UserRoleService.get_all_roles_for_user(db_session, test_user.id)
        assert roles is not None
        assert any(role.id == test_role.id for role in roles)
    async def test_getallrolesforuser_returns_none_if_user_missing(self, db_session: AsyncSession):
        roles = await UserRoleService.get_all_roles_for_user(db_session, user_id=999999)
        assert roles is None

    async def test_getallusersforrole_returns_users(self, db_session: AsyncSession, test_user, test_role):
        await UserRoleService.assigne_user_role(db_session, test_user.id, test_role.id)
        users = await UserRoleService.get_all_users_for_role(db_session, test_role.id)
        assert users is not None
        assert any(user.id == test_user.id for user in users)

    async def test_getallusersforrole_returns_none_if_role_missing(self, db_session: AsyncSession):
        users = await UserRoleService.get_all_users_for_role(db_session, role_id=999999)
        assert users is None
