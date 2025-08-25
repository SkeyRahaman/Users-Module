import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import UserCreate, UserUpdate
from app.database.services.user_service import UserService
from app.database.models import User, Group, Role, Permission


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

    async def test_get_all_users_basic(self, db_session: AsyncSession, test_user: User):
        total, users = await UserService.get_all_users(db_session)
        assert isinstance(users, list)
        assert isinstance(total, int)
        assert total >= 1
        assert any(u.id == test_user.id for u in users)

    async def test_get_all_users_sorting(self, db_session: AsyncSession, test_user: User):
        user2 = User(
            firstname="TestFirst_" + uuid.uuid4().hex[:6],
            lastname="TestLast_" + uuid.uuid4().hex[:6],
            username="user_" + uuid.uuid4().hex[:8],
            email=f"user_{uuid.uuid4().hex[:8]}@example.com",
            password="hashedpassword"
        )
        db_session.add(user2)
        await db_session.commit()
        await db_session.refresh(user2)
        total_asc, users_asc = await UserService.get_all_users(db_session, page=1, limit=5, sort_by="email", sort_order="asc")
        total_desc, users_desc = await UserService.get_all_users(db_session, page=1, limit=5, sort_by="email", sort_order="desc")
        assert users_asc != users_desc  # Results should be different order
        emails_asc = [u.email for u in users_asc]
        assert emails_asc == sorted(emails_asc)

    async def test_get_all_users_filter_status(self, db_session: AsyncSession, test_user: User):
        status = test_user.is_active
        total, users = await UserService.get_all_users(db_session, status=status)
        assert all(u.is_active == status for u in users)

    async def test_get_all_users_filter_role(self, db_session: AsyncSession, test_link_user_role):
        test_user, test_role = test_link_user_role
        total, users = await UserService.get_all_users(db_session, role=test_role.name)
        assert all(any(r.role.name == test_role.name for r in u.user_roles) for u in users)

    async def test_get_all_users_filter_group(self, db_session: AsyncSession, test_link_user_group):
        test_user, test_group = test_link_user_group
        total, users = await UserService.get_all_users(db_session, group=test_group.name)
        assert all(any(g.group.name == test_group.name for g in u.user_groups) for u in users)

    async def test_get_all_users_search(self, db_session: AsyncSession, test_user: User):
        search_term = test_user.username[:3]  # Partial username
        total, users = await UserService.get_all_users(db_session, search=search_term)
        assert any(search_term.lower() in u.username.lower() or search_term.lower() in u.email.lower() for u in users)

    async def test_delete_user(self, db_session: AsyncSession, test_user: User):
        result = await UserService.delete_user(db_session, test_user.id)
        assert result is True

        deleted_user = await UserService.get_user_by_id(db_session, test_user.id)
        assert deleted_user is None

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
    async def test_get_all_permissions_for_user_no_roles(self, db_session: AsyncSession, test_user: User):
        permissions = await UserService.get_all_permissions_for_user(db_session, test_user.id)
        assert isinstance(permissions, list)
        assert len(permissions) == 0

    async def test_get_all_permissions_for_user_with_direct_roles(
        self, db_session: AsyncSession, test_link_user_role_permission
    ):
        user, role, permission = test_link_user_role_permission
        permissions = await UserService.get_all_permissions_for_user(db_session, user.id)
        assert isinstance(permissions, list)
        assert permission.name in permissions

    async def test_get_all_permissions_for_user_with_group_roles(self, db_session: AsyncSession, test_link_user_group_role_permission):
        user, group, role, permission = test_link_user_group_role_permission
        permissions = await UserService.get_all_permissions_for_user(db_session, user.id)
        assert isinstance(permissions, list)
        assert permission.name in permissions

    async def test_get_all_permissions_for_user_with_duplicate_permissions(self, db_session: AsyncSession, test_user: User):
        permissions = await UserService.get_all_permissions_for_user(db_session, test_user.id)
        permission_ids = [p.id for p in permissions]
        assert len(permission_ids) == len(set(permission_ids)), "Duplicate permissions found"