import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import UserCreate, UserUpdate
from app.database.services.user_service import UserService
from app.database.models import User, Group, Role


@pytest.mark.asyncio
class TestUserService:

    async def test_create_user_success(self, db_session: AsyncSession):
        user_data = UserCreate(
            firstname="John",
            middlename="M",
            lastname="Doe",
            username="johndoe",
            email="john@example.com",
            password="secret123"
        )
        user = await UserService.create_user(db_session, user_data)

        assert user is not None
        assert user.username == "johndoe"
        assert user.password != "secret123"

    async def test_duplicate_username_fails(self, db_session: AsyncSession, test_user: User):
        dup_data = UserCreate(
            firstname="Another",
            middlename=None,
            lastname="User",
            username=test_user.username,  # duplicate from fixture
            email="dup@example.com",
            password="secret123"
        )
        result = await UserService.create_user(db_session, dup_data)
        assert result is None

    async def test_get_user_by_id_and_username(self, db_session: AsyncSession, test_user: User):
        found_by_id = await UserService.get_user_by_id(db_session, test_user.id)
        assert found_by_id is not None
        assert found_by_id.username == test_user.username

        found_by_username = await UserService.get_user_by_username(db_session, test_user.username)
        assert found_by_username is not None
        assert found_by_username.id == test_user.id

    async def test_update_user(self, db_session: AsyncSession, test_user: User):
        update_data = UserUpdate(firstname="UpdatedName", lastname="UpdatedLast")
        updated = await UserService.update_user(db_session, test_user.id, update_data)

        assert updated is not None
        assert updated.firstname == "UpdatedName"
        assert updated.lastname == "UpdatedLast"

    async def test_check_username_and_email_exists(self, db_session: AsyncSession, test_user: User):
        assert await UserService.check_username_exists(db_session, test_user.username) is True
        assert await UserService.check_username_exists(db_session, "nonexistent") is False
        assert await UserService.check_email_exists(db_session, test_user.email) is True
        assert await UserService.check_email_exists(db_session, "fake@email.com") is False

    async def test_get_all_users(self, db_session: AsyncSession, test_user: User):
        users = await UserService.get_all_users(db_session, skip=0, limit=10, sort_by="username", sort_order="asc")
        assert isinstance(users, list)
        assert any(u.id == test_user.id for u in users)

    async def test_delete_user(self, db_session: AsyncSession, test_user: User):
        result = await UserService.delete_user(db_session, test_user.id)
        assert result is True

        deleted_user = await UserService.get_user_by_id(db_session, test_user.id)
        assert deleted_user is None

    # ---- New Role/Group Function Tests ----

    async def test_get_all_groups_for_user(self, db_session: AsyncSession, test_link_user_group):
        user, group = test_link_user_group
        groups = await UserService.get_all_groups_for_user(db_session, user.id)

        assert isinstance(groups, list)
        assert any(isinstance(g, Group) and g.id == group.id for g in groups)

    async def test_get_all_roles_for_user_direct(self, db_session: AsyncSession, test_link_user_role):
        user, role = test_link_user_role
        roles = await UserService.get_all_roles_for_user(db_session, user.id)

        assert isinstance(roles, list)
        assert any(isinstance(r, Role) and r.id == role.id for r in roles)

    async def test_get_all_roles_for_user_via_group(self, db_session: AsyncSession, test_link_user_group_role):
        user, _, role = test_link_user_group_role
        roles = await UserService.get_all_roles_for_user(db_session, user.id)

        assert isinstance(roles, list)
        assert any(r.id == role.id for r in roles)
