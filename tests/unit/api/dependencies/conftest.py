import pytest

@pytest.fixture(scope="class")
def test_user():
    return {"username": "testuser"}
