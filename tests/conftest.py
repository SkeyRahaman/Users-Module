import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base
from app.config import Config
from app.database.user import User
from app.auth.password import PasswordHasher
from app.api.dependencies.database import get_db

# Database engine setup
engine = create_engine(
    Config.TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestSessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)

def setup_database():
    """Initialize test database schema"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

# Session fixtures
@pytest.fixture(scope="function")
def db_session():
    """Function-scoped database session"""
    setup_database()
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="module")
def db_session_module():
    """Module-scoped database session"""
    setup_database()
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Test client fixture
@pytest.fixture(scope="function")
def client(db_session):
    """Test client with database dependency override"""
    def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)

# Test user fixture
@pytest.fixture(scope="function")
def test_user(db_session):
    """Test user fixture with automatic cleanup"""
    hashed_password = PasswordHasher.get_password_hash("secure123")
    user = User(
        firstname="fname1",
        lastname="lname1",
        username="test_username",
        email="username@example.com",
        password=hashed_password,
        is_active=True
    )
    
    db_session.add(user)
    db_session.commit()
    
    yield user
    
    db_session.delete(user)
    db_session.commit()

@pytest.fixture
def test_token(client: TestClient, test_user: User):
    """Fixture to get auth token for test user"""
    response = client.post(
        app.url_path_for("token"),
        data={
            "username": test_user.username,
            "password": "secure123",
            "grant_type": "password"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    return response.json()["access_token"]