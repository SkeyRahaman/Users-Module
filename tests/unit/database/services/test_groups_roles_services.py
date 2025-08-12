import pytest
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import Config
from app.database.services.groups_roles_services import GroupRoleService
from app.database.models import GroupRole


# --- Helper to normalize DB datetime to UTC-aware for cross-DB consistency ---
def to_utc_aware(dt: datetime) -> datetime:
    """
    Ensure datetime is timezone-aware in UTC.
    Works for SQLite (naive) and Postgres (aware) results.
    """
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


@pytest.mark.asyncio
class TestGroupRoleService:

    async def test_assign_creates_new_with_default_validity(self, db_session: AsyncSession, test_group, test_role):
        before = datetime.now(timezone.utc)
        group_role = await GroupRoleService.assign_group_role(db_session, test_group.id, test_role.id)

        assert group_role is not None
        assert group_role.group_id == test_group.id
        assert group_role.role_id == test_role.id
        assert to_utc_aware(group_role.valid_from) >= before
        assert to_utc_aware(group_role.valid_until).date() == (
            before + timedelta(days=Config.DEFAULT_GROUP_ROLE_VALIDITY)
        ).date()
        assert group_role.is_deleted is False

    async def test_assign_existing_updates_validity(self, db_session: AsyncSession, test_link_group_role):
        group, role = test_link_group_role
        new_until = datetime.now(timezone.utc) + timedelta(days=10)

        updated = await GroupRoleService.assign_group_role(
            db_session,
            group.id,
            role.id,
            valid_from=datetime.now(timezone.utc),
            valid_until=new_until
        )

        assert to_utc_aware(updated.valid_until) == to_utc_aware(new_until)
        assert updated.is_deleted is False

    async def test_assign_restores_deleted(self, db_session: AsyncSession, test_link_group_role):
        group, role = test_link_group_role

        # Mark deleted
        await GroupRoleService.remove_group_role(db_session, group.id, role.id)
        assert await GroupRoleService.check_group_role_exists(db_session, group.id, role.id) is False

        restored = await GroupRoleService.assign_group_role(db_session, group.id, role.id)
        assert restored.is_deleted is False
        assert await GroupRoleService.check_group_role_exists(db_session, group.id, role.id) is True

    async def test_remove_group_role(self, db_session: AsyncSession, test_link_group_role):
        group, role = test_link_group_role

        result = await GroupRoleService.remove_group_role(db_session, group.id, role.id)
        assert result is True

        check = await GroupRoleService.check_group_role_exists(db_session, group.id, role.id)
        assert check is False

    async def test_extend_validity(self, db_session: AsyncSession, test_link_group_role):
        group, role = test_link_group_role
        new_until = datetime.now(timezone.utc) + timedelta(days=30)

        result = await GroupRoleService.extend_validity(db_session, group.id, role.id, new_until)
        assert result is True

        # Verify normalized
        gr = await db_session.get(GroupRole, {"group_id": group.id, "role_id": role.id})
        assert to_utc_aware(gr.valid_until) == to_utc_aware(new_until)

    async def test_expire_group_role(self, db_session: AsyncSession, test_link_group_role):
        group, role = test_link_group_role
        before = datetime.now(timezone.utc)

        result = await GroupRoleService.expire_group_role(db_session, group.id, role.id)
        assert result is True

        gr = await db_session.get(GroupRole, {"group_id": group.id, "role_id": role.id})
        vu = to_utc_aware(gr.valid_until)
        assert vu >= before
        assert vu <= datetime.now(timezone.utc)

    async def test_check_group_role_exists_true(self, db_session: AsyncSession, test_link_group_role):
        group, role = test_link_group_role
        assert await GroupRoleService.check_group_role_exists(db_session, group.id, role.id) is True

    async def test_check_group_role_exists_false(self, db_session: AsyncSession, test_group, test_role):
        assert await GroupRoleService.check_group_role_exists(db_session, test_group.id, test_role.id) is False
