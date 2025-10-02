import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy import MetaData
from alembic.config import Config as AlembiConfig
from alembic import command
import asyncio
import os

from app.database.models import Base, User, Group, Role, Permission
from app.auth.jwt import JWTManager
from app.auth.password_hash import PasswordHasher
from app.main import app
from app.api.dependencies.database import get_db
from app.config import Config
from app.database.models import RolePermission, UserRole, GroupRole

# ------------------ DB Session Fixture ------------------
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


@pytest_asyncio.fixture
async def override_get_db(db_session):
    async def _override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.pop(get_db, None)

@pytest_asyncio.fixture(scope="function")
async def test_user(db_session: AsyncSession):
    user = User(
        firstname=Config.TEST_USER["firstname"],
        lastname=Config.TEST_USER["lastname"],
        username=f"{os.urandom(4).hex()}{Config.TEST_USER['username']}",
        email=f"{os.urandom(4).hex()}{Config.TEST_USER['email']}",
        password=PasswordHasher.get_password_hash(Config.TEST_USER['password']),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    yield user
    user.is_deleted = True
    await db_session.commit()

@pytest_asyncio.fixture
async def token(test_user):
    return JWTManager.encode_access_token(data={"sub": test_user.username})

@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest_asyncio.fixture
async def test_group(db_session: AsyncSession):
    group = Group(
        name = f"Test Group {os.urandom(4).hex()}"
    )
    db_session.add(group)
    await db_session.commit()
    await db_session.refresh(group)
    yield group
    group.is_deleted = True
    await db_session.commit()

@pytest_asyncio.fixture(scope="function")
async def test_role(db_session: AsyncSession):
    role = Role(
        name = f"Test Role {os.urandom(4).hex()}"
    )
    db_session.add(role)
    await db_session.commit()
    await db_session.refresh(role)
    yield role
    role.is_deleted = True
    await db_session.commit()

@pytest_asyncio.fixture(scope="function")
async def test_permission(db_session: AsyncSession):
    permission = Permission(
        name = f"test_permission_{os.urandom(4).hex()}",
    )
    db_session.add(permission)
    await db_session.commit()
    await db_session.refresh(permission)
    yield permission
    permission.is_deleted = True
    await db_session.commit()

@pytest_asyncio.fixture
async def test_role_permission(db_session: AsyncSession, test_role: Role, test_permission: Permission):
    role_permission = RolePermission(
        role_id = test_role.id,
        permission_id = test_permission.id,
        created_by = 1
    )
    db_session.add(role_permission)
    await db_session.commit()
    await db_session.refresh(role_permission)
    yield test_role, test_permission
    await db_session.delete(role_permission)
    await db_session.commit()

@pytest_asyncio.fixture
async def test_user_role(db_session: AsyncSession, test_user: User, test_role: Role):
    user_role = UserRole(
        user_id = test_user.id,
        role_id = test_role.id,
        created_by = 1
    )
    db_session.add(user_role)
    await db_session.commit()
    await db_session.refresh(user_role)
    yield test_user, test_role
    await db_session.delete(user_role)
    await db_session.commit()

@pytest_asyncio.fixture
async def test_group_role(db_session: AsyncSession, test_group: Group, test_role: Role):
    group_role = GroupRole(
        group_id = test_group.id,
        role_id = test_role.id,
        created_by = 1
    )
    db_session.add(group_role)
    await db_session.commit()
    await db_session.refresh(group_role)
    yield test_group, test_role
    await db_session.delete(group_role)
    await db_session.commit()

@pytest_asyncio.fixture
async def admin_user(db_session: AsyncSession):
    user = await db_session.execute(
        select(User).where(User.username == Config.ADMIN_USER['username'])
    )
    admin_user = user.scalars().first()
    if admin_user is None:
        raise RuntimeError("No admin user found in the database for tests")
    yield admin_user

@pytest_asyncio.fixture
async def admin_token():
    return JWTManager.encode_access_token(data={"sub": Config.ADMIN_USER['username']})