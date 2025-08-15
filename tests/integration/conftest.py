import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from app.database.models import Base, User, Group, Role, Permission
from app.auth.jwt import JWTManager
from app.auth.password_hash import PasswordHasher
from app.main import app
from app.api.dependencies.database import get_db
from app.config import Config

TEST_DATABASE_URL = "sqlite:///./test_db.db"

# Create engine and sessionmaker for tests
engine = create_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

TEST_ASYNC_DATABASE_URL = "sqlite+aiosqlite:///test_async_db.db"

async_engine = create_async_engine(TEST_ASYNC_DATABASE_URL, echo=False)
AsyncTestingSessionLocal = sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False
)

@pytest_asyncio.fixture
async def setup_database():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await async_engine.dispose()

@pytest_asyncio.fixture
async def db_session():
    async with AsyncTestingSessionLocal() as session:
        yield session
        await session.rollback()

@pytest_asyncio.fixture
async def override_get_db(db_session):
    async def _override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.pop(get_db, None)

@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession):
    user = User(
        firstname=Config.TEST_USER["firstname"],
        lastname=Config.TEST_USER["lastname"],
        username=Config.TEST_USER['username'],
        email=Config.TEST_USER['email'],
        password=PasswordHasher.get_password_hash(Config.TEST_USER['password']),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    yield user
    await db_session.delete(user)
    await db_session.commit()

@pytest_asyncio.fixture
async def token(test_user):
    return JWTManager.encode(data={"sub": test_user.username})

@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest_asyncio.fixture
async def test_group(db_session: AsyncSession):
    group = Group(
        name = "Test Group"
    )
    db_session.add(group)
    await db_session.commit()
    await db_session.refresh(group)
    yield group
    await db_session.delete(group)
    await db_session.commit()

@pytest_asyncio.fixture
async def test_role(db_session: AsyncSession):
    role = Role(
        name = "Test role"
    )
    db_session.add(role)
    await db_session.commit()
    await db_session.refresh(role)
    yield role
    await db_session.delete(role)
    await db_session.commit()

@pytest_asyncio.fixture
async def test_permission(db_session: AsyncSession):
    permission = Permission(
        name = "Test permission"
    )
    db_session.add(permission)
    await db_session.commit()
    await db_session.refresh(permission)
    yield permission
    await db_session.delete(permission)
    await db_session.commit()
