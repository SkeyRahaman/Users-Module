from unittest.mock import AsyncMock, MagicMock
import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
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

    async def test_activate_user_success(self, db_session: AsyncSession, test_user: User):
        test_user.is_active = False
        db_session.add(test_user)
        await db_session.commit()
        await db_session.refresh(test_user)

        result = await UserService.activate_user(db_session, test_user.id)
        assert result is True
        await db_session.refresh(test_user)
        assert test_user.is_active is True

    async def test_activate_user_already_active(self, db_session: AsyncSession, test_user: User):
        result = await UserService.activate_user(db_session, test_user.id)
        assert result is False

    async def test_activate_user_not_found(self, db_session: AsyncSession):
        result = await UserService.activate_user(db_session, 999)
        assert result is False

    async def test_activate_user_commit_error(self, db_session: AsyncSession):
        user = User(id=1, is_active=False, is_deleted=False)
        # Mock result from db.execute()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = user
        db_session.execute = AsyncMock(return_value=mock_result)
        db_session.commit = AsyncMock(side_effect=IntegrityError('msg', 'params', 'orig'))
        db_session.rollback = AsyncMock()

        result = await UserService.activate_user(db_session, user.id)
        assert result is False
        db_session.rollback.assert_awaited_once()
        
    async def test_deactivate_user_success(self, db_session: AsyncSession, test_user: User):
        test_user.is_active = True
        db_session.add(test_user)
        await db_session.commit()
        await db_session.refresh(test_user)

        result = await UserService.deactivate_user(db_session, test_user.id)
        assert result is True
        await db_session.refresh(test_user)
        assert test_user.is_active is False

    async def test_deactivate_user_already_inactive(self, db_session: AsyncSession, test_user: User):
        test_user.is_active = False
        db_session.add(test_user)
        await db_session.commit()
        await db_session.refresh(test_user)

        result = await UserService.deactivate_user(db_session, test_user.id)
        assert result is False

    async def test_deactivate_user_not_found(self, db_session: AsyncSession):
        result = await UserService.deactivate_user(db_session, 999)
        assert result is False

    async def test_deactivate_user_commit_error(self, db_session: AsyncSession):
        user = User(id=1, is_active=True, is_deleted=False)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = user
        db_session.execute = AsyncMock(return_value=mock_result)
        db_session.commit = AsyncMock(side_effect=SQLAlchemyError())
        db_session.rollback = AsyncMock()

        result = await UserService.deactivate_user(db_session, user.id)
        assert result is False
        db_session.rollback.assert_awaited_once()
       
    async def test_update_user_password_success(self, db_session: AsyncSession, test_user: User):
        old_hash = test_user.password
        result = await UserService.update_user_password(db_session, test_user.id, "newpassword123")
        assert result is True
        await db_session.refresh(test_user)
        assert test_user.password != old_hash

    async def test_update_user_password_user_not_found(self, db_session: AsyncSession):
        result = await UserService.update_user_password(db_session, 999, "somepassword")
        assert result is False

    async def test_update_user_password_commit_error(self, db_session: AsyncSession):
        user = User(id=1, is_deleted=False)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = user
        db_session.execute = AsyncMock(return_value=mock_result)
        db_session.commit = AsyncMock(side_effect=IntegrityError('msg', 'params', 'orig'))
        db_session.rollback = AsyncMock()
        result = await UserService.update_user_password(db_session, user.id, "pw")
        assert result is False
        db_session.rollback.assert_awaited_once()

    async def test_get_user_by_email_found(self, db_session: AsyncSession, test_user: User):
        found = await UserService.get_user_by_email(db_session, test_user.email)
        assert found is not None
        assert found.id == test_user.id

    async def test_get_user_by_email_not_found(self, db_session: AsyncSession):
        found = await UserService.get_user_by_email(db_session, "nonexistent@email.com")
        assert found is None

    async def test_reset_user_password_success(self, db_session: AsyncSession, mocker, test_user: User):
        # Patch dependencies
        token_obj = MagicMock()
        token_obj.token_hash = "dummy-token"
        mocker.patch("app.database.services.user_service.PasswordResetTokenService.create_password_reset_token", AsyncMock(return_value=token_obj))
        mock_email = AsyncMock(return_value=True)
        mocker.patch("app.database.services.user_service.EmailService.send_password_rest_email", mock_email)
        result = await UserService.reset_user_password(db_session, test_user.id)
        assert result is True
        mock_email.assert_awaited_once()

    async def test_reset_user_password_token_fail(self, db_session: AsyncSession, mocker, test_user: User):
        # Token creation fails
        mocker.patch("app.database.services.user_service.PasswordResetTokenService.create_password_reset_token", AsyncMock(return_value=None))
        result = await UserService.reset_user_password(db_session, test_user.id)
        assert result is None

    async def test_reset_user_password_email_fail(self, db_session: AsyncSession, mocker, test_user: User):
        token_obj = MagicMock()
        token_obj.token_hash = "dummy-token"
        mocker.patch("app.database.services.user_service.PasswordResetTokenService.create_password_reset_token", AsyncMock(return_value=token_obj))
        mocker.patch("app.database.services.user_service.EmailService.send_password_rest_email", AsyncMock(return_value=False))
        result = await UserService.reset_user_password(db_session, test_user.id)
        assert result is False