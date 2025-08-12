import pytest
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import Config
from app.database.services.users_groups_services import UserGroupService
from app.database.models import UserGroup

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
class TestUserGroupService:

    async def test_assign_creates_new_with_default_validity(self, db_session: AsyncSession, test_user, test_group):
        before = datetime.now(timezone.utc)
        user_group = await UserGroupService.assign_user_group(db_session, test_user.id, test_group.id)

        assert user_group is not None
        assert user_group.user_id == test_user.id
        assert user_group.group_id == test_group.id
        assert to_utc_aware(user_group.valid_from) >= before
        assert to_utc_aware(user_group.valid_until).date() == (
            before + timedelta(days=Config.DEFAULT_USER_GROUP_VALIDITY)
        ).date()
        assert user_group.is_deleted is False

    async def test_assign_existing_updates_validity(self, db_session: AsyncSession, test_link_user_group):
        user, group = test_link_user_group
        new_until = datetime.now(timezone.utc) + timedelta(days=10)

        updated = await UserGroupService.assign_user_group(
            db_session,
            user.id,
            group.id,
            valid_from=datetime.now(timezone.utc),
            valid_until=new_until
        )

        assert to_utc_aware(updated.valid_until) == to_utc_aware(new_until)
        assert updated.is_deleted is False

    async def test_assign_restores_deleted(self, db_session: AsyncSession, test_link_user_group):
        user, group = test_link_user_group

        # mark as deleted
        await UserGroupService.remove_user_group(db_session, user.id, group.id)
        assert await UserGroupService.check_user_group_exists(db_session, user.id, group.id) is False

        restored = await UserGroupService.assign_user_group(db_session, user.id, group.id)
        assert restored.is_deleted is False
        assert await UserGroupService.check_user_group_exists(db_session, user.id, group.id) is True

    async def test_remove_user_group(self, db_session: AsyncSession, test_link_user_group):
        user, group = test_link_user_group

        result = await UserGroupService.remove_user_group(db_session, user.id, group.id)
        assert result is True

        check = await UserGroupService.check_user_group_exists(db_session, user.id, group.id)
        assert check is False

    async def test_extend_validity(self, db_session: AsyncSession, test_link_user_group):
        user, group = test_link_user_group
        new_until = datetime.now(timezone.utc) + timedelta(days=60)

        result = await UserGroupService.extend_validity(db_session, user.id, group.id, new_until)
        assert result is True

        # Verify normalized
        ug = await db_session.get(UserGroup, {"user_id": user.id, "group_id": group.id})
        assert to_utc_aware(ug.valid_until) == to_utc_aware(new_until)

    async def test_expire_user_group(self, db_session: AsyncSession, test_link_user_group):
        user, group = test_link_user_group
        before = datetime.now(timezone.utc)

        result = await UserGroupService.expire_user_group(db_session, user.id, group.id)
        assert result is True

        # Verify normalized UTC dates
        ug = await db_session.get(UserGroup, {"user_id": user.id, "group_id": group.id})
        vu = to_utc_aware(ug.valid_until)
        assert vu >= before
        assert vu <= datetime.now(timezone.utc)

    async def test_check_user_group_exists_true(self, db_session: AsyncSession, test_link_user_group):
        user, group = test_link_user_group
        assert await UserGroupService.check_user_group_exists(db_session, user.id, group.id) is True

    async def test_check_user_group_exists_false(self, db_session: AsyncSession, test_user, test_group):
        assert await UserGroupService.check_user_group_exists(db_session, test_user.id, test_group.id) is False
