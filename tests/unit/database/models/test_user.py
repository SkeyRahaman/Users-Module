import pytest
import uuid
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import User, Role, Group, UserRole, UserGroup, PasswordResetToken

pytestmark = pytest.mark.asyncio  # marks all tests as async


class TestUserModel:

    async def test_create_user_minimal(self, db_session: AsyncSession):
        user = User(
            firstname="Shakib",
            lastname="Mondal",
            username="shakib_" + uuid.uuid4().hex[:6],
            email=f"shakib_{uuid.uuid4().hex[:6]}@example.com",
            password="hashedpassword"
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        assert user.id is not None
        assert not user.is_deleted
        assert user.is_active is True
        assert user.is_verified is False
        assert user.created is not None
        assert user.updated is not None

    async def test_username_email_unique(self, db_session: AsyncSession, test_user: User):
        user = User(
            firstname="C",
            lastname="D",
            username=test_user.username,
            email=test_user.email,
            password="p"
        )

        db_session.add(user)
        with pytest.raises(IntegrityError):
            await db_session.commit()
        await db_session.rollback()

    async def test_user_roles_and_groups(self, db_session: AsyncSession, test_user: User, test_role: Role, test_group: Group):
        user_role = UserRole(user=test_user, role=test_role)
        user_group = UserGroup(user=test_user, group=test_group)

        db_session.add_all([user_role, user_group])
        await db_session.commit()
        await db_session.refresh(test_user, ["user_roles", "user_groups"])

        assert len(test_user.user_roles) == 1
        assert test_user.user_roles[0].role.name == test_role.name
        assert len(test_user.user_groups) == 1
        assert test_user.user_groups[0].group.name == test_group.name

    async def test_user_password_reset_token(self, test_user_with_password_reset_token: PasswordResetToken):
        test_user, token = test_user_with_password_reset_token
        assert test_user.password_reset_tokens[0].token_hash == token.token_hash
        assert test_user.password_reset_tokens[0].user_id == test_user.id
        
    async def test_user_refresh_token(self, test_user_with_refresh_token):
        test_user, token = test_user_with_refresh_token
        assert test_user.refresh_tokens[0].refresh_token_hash == token.refresh_token_hash
        assert test_user.refresh_tokens[0].user_id == test_user.id