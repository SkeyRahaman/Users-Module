import pytest_asyncio
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

from app.config import Config
from app.database import Base, User, Role, Permission, Group

engine = create_async_engine(
    Config.TEST_DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in Config.TEST_DATABASE_URL else {},
    future=True,
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)


@pytest_asyncio.fixture
async def db_session():
    """Create all tables before tests and drop after tests for async DB."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession):
    """Create a random test user."""
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
    yield user


@pytest_asyncio.fixture
async def test_role(db_session: AsyncSession):
    """Create a random test role."""
    role = Role(
        name="role_" + uuid.uuid4().hex[:6]
    )
    db_session.add(role)
    await db_session.commit()
    await db_session.refresh(role)
    yield role


@pytest_asyncio.fixture
async def test_permission(db_session: AsyncSession):
    """Create a random test permission."""
    permission = Permission(
        name="perm_" + uuid.uuid4().hex[:6]
    )
    db_session.add(permission)
    await db_session.commit()
    await db_session.refresh(permission)
    yield permission


@pytest_asyncio.fixture
async def test_group(db_session: AsyncSession):
    """Create a random test group."""
    group = Group(
        name="group_" + uuid.uuid4().hex[:6]
    )
    db_session.add(group)
    await db_session.commit()
    await db_session.refresh(group)
    yield group
