import pytest

@pytest.fixture(scope="class")
def jwt_data():
    """Fixture providing common JWT test data."""
    return {
        "payload": {"sub": "test_user"},
        "issuer": "your-issuer-identifier",
        "audience": "your-audience-identifier"
    }