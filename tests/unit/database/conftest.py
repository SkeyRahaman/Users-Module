import pytest_asyncio
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy import MetaData
from alembic.config import Config as AlembiConfig
from alembic import command
import asyncio
from sqlalchemy.orm import sessionmaker
import hashlib
from datetime import datetime, timedelta

from app.config import Config
from app.database.models import (
    Base, User, Role, Permission, Group,
    UserRole, UserGroup, GroupRole, RolePermission, PasswordResetToken, RefreshToken
)
from app.auth.jwt import JWTManager
import os

async_engine = create_async_engine(Config.TEST_DATABASE_URL, echo=False)
AsyncTestingSessionLocal = sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False
)

async def run_migrations_on_connection(async_engine: AsyncEngine, revision):
    async with async_engine.begin() as conn:
        alembic_cfg = AlembiConfig("alembic.ini")
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, lambda: command.upgrade(alembic_cfg, revision))

@pytest_asyncio.fixture(scope="module")
async def setup_database():
    os.environ["DATABASE_URL_ALEMBIC"] = Config.TEST_DATABASE_URL_ALEMBIC
    await run_migrations_on_connection(async_engine, "head")
    yield
    async with async_engine.begin() as conn:
        meta = MetaData()
        await conn.run_sync(meta.reflect)
        await conn.run_sync(meta.drop_all)
    await async_engine.dispose()

@pytest_asyncio.fixture
async def db_session(setup_database):
    async with AsyncTestingSessionLocal() as session:
        yield session

# ------------------ Base Entity Fixtures ------------------
@pytest_asyncio.fixture(scope="function")
async def test_user(db_session: AsyncSession):
    user = User(
        firstname="TestFirst_" + uuid.uuid4().hex[:6],
        lastname="TestLast_" + uuid.uuid4().hex[:6],
        username="user_" + uuid.uuid4().hex[:8],
        email=f"user_{uuid.uuid4().hex[:8]}@example.com",
        password="hashedpassword"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest_asyncio.fixture
async def test_role(db_session: AsyncSession):
    role = Role(name="role_" + uuid.uuid4().hex[:6])
    db_session.add(role)
    await db_session.commit()
    await db_session.refresh(role)
    return role

@pytest_asyncio.fixture
async def test_permission(db_session: AsyncSession):
    permission = Permission(name="perm_" + uuid.uuid4().hex[:6])
    db_session.add(permission)
    await db_session.commit()
    await db_session.refresh(permission)
    return permission

@pytest_asyncio.fixture
async def test_group(db_session: AsyncSession):
    group = Group(name="group_" + uuid.uuid4().hex[:6])
    db_session.add(group)
    await db_session.commit()
    await db_session.refresh(group)
    return group

@pytest_asyncio.fixture
async def test_user_with_password_reset_token(db_session: AsyncSession, test_user: User):
    token = PasswordResetToken(
            user_id=test_user.id,
            token_hash=hashlib.sha256(uuid.uuid4().hex.encode()).hexdigest(),
            expires_at=datetime.now() + timedelta(minutes=10),
        )
    db_session.add(token)
    await db_session.commit()
    await db_session.refresh(token)
    await db_session.refresh(test_user)
    return test_user, token

@pytest_asyncio.fixture
async def test_user_with_refresh_token(db_session: AsyncSession, test_user: User):
    raw_token = JWTManager.encode_refresh_token(data={"sub": test_user.username})
    refresh_token = RefreshToken(
        user_id=test_user.id,
        refresh_token_hash=hashlib.sha256(raw_token.encode()).hexdigest(),
        expires_at=datetime.now() + timedelta(minutes=10),
    )
    db_session.add(refresh_token)
    await db_session.commit()
    await db_session.refresh(refresh_token)
    await db_session.refresh(test_user)
    return test_user, refresh_token


# ------------------ Generic Link Fixtures ------------------
@pytest_asyncio.fixture
async def test_link_user_role(db_session: AsyncSession, test_user, test_role):
    db_session.add(UserRole(user_id=test_user.id, role_id=test_role.id))
    await db_session.commit()
    await db_session.refresh(test_user)
    await db_session.refresh(test_role)
    return test_user, test_role

@pytest_asyncio.fixture
async def test_link_user_group(db_session: AsyncSession, test_user, test_group):
    db_session.add(UserGroup(user_id=test_user.id, group_id=test_group.id))
    await db_session.commit()
    await db_session.refresh(test_user)
    await db_session.refresh(test_group)
    return test_user, test_group

@pytest_asyncio.fixture
async def test_link_group_role(db_session: AsyncSession, test_group, test_role):
    db_session.add(GroupRole(group_id=test_group.id, role_id=test_role.id))
    await db_session.commit()
    return test_group, test_role

@pytest_asyncio.fixture
async def test_link_role_permission(db_session: AsyncSession, test_role, test_permission):
    db_session.add(RolePermission(role_id=test_role.id, permission_id=test_permission.id))
    await db_session.commit()
    return test_role, test_permission

# ------------------ Multi-Hop Link Fixtures ------------------
@pytest_asyncio.fixture
async def test_link_user_group_role(db_session: AsyncSession, test_user, test_group, test_role):
    db_session.add(UserGroup(user_id=test_user.id, group_id=test_group.id))
    db_session.add(GroupRole(group_id=test_group.id, role_id=test_role.id))
    await db_session.commit()
    return test_user, test_group, test_role

@pytest_asyncio.fixture
async def test_link_group_role_permission(db_session: AsyncSession, test_group, test_role, test_permission):
    db_session.add(GroupRole(group_id=test_group.id, role_id=test_role.id))
    db_session.add(RolePermission(role_id=test_role.id, permission_id=test_permission.id))
    await db_session.commit()
    return test_group, test_role, test_permission

@pytest_asyncio.fixture
async def test_link_user_role_permission(db_session: AsyncSession, test_user, test_role, test_permission):
    db_session.add(UserRole(user_id=test_user.id, role_id=test_role.id))
    db_session.add(RolePermission(role_id=test_role.id, permission_id=test_permission.id))
    await db_session.commit()
    return test_user, test_role, test_permission

@pytest_asyncio.fixture
async def test_link_user_group_role_permission(db_session: AsyncSession, test_user, test_group, test_role, test_permission):
    db_session.add(UserGroup(user_id=test_user.id, group_id=test_group.id))
    db_session.add(GroupRole(group_id=test_group.id, role_id=test_role.id))
    db_session.add(RolePermission(role_id=test_role.id, permission_id=test_permission.id))
    await db_session.commit()
    return test_user, test_group, test_role, test_permission
