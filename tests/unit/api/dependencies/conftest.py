from unittest.mock import MagicMock
import pytest

@pytest.fixture(scope="class")
def test_user():
    return {"username": "testuser"}

@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def mock_current_user():
    user = MagicMock()
    user.id = 1
    user.username = "testuser"
    user.is_deleted = False
    return user
