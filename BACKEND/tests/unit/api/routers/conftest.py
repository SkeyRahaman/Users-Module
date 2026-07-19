import pytest
from unittest.mock import MagicMock
from app.database.models import User
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.fixture
def mock_db():
    return MagicMock(spec=AsyncSession)

@pytest.fixture
def mock_user():
    user = MagicMock(spec=User)
    user.id = 1
    user.firstname = "test"
    user.lastname = "user"
    user.username = "testuser"
    user.email = "test@example.com"
    user.is_active = True
    return user

@pytest.fixture
def mock_current_user(mock_user: User):
    return mock_user

@pytest.fixture
def mock_role():
    role = MagicMock()
    role.id = 1
    role.name = "test_role"
    role.description = "Test description"
    role.is_deleted = False
    return role

@pytest.fixture
def mock_group():
    group = MagicMock()
    group.id = 1
    group.name = "test_group"
    group.description = "Test description"
    group.is_deleted = False
    return group

@pytest.fixture
def mock_permission():
    permission = MagicMock()
    permission.id = 1
    permission.name = "test_permission"
    permission.description = "Test description"
    permission.is_deleted = False
    return permission
