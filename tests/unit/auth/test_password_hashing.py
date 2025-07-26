import pytest
from passlib.exc import UnknownHashError
from app.auth.password import PasswordHasher  # Adjust import path

class TestPasswordHasher:
    # ---- Positive Tests ----
    def test_get_password_hash_returns_string(self):
        hashed = PasswordHasher.get_password_hash("secure123")
        assert isinstance(hashed, str)
        assert hashed.startswith("$2b$")  # BCrypt format

    def test_verify_password_correct(self):
        plain_password = "secure123"
        hashed = PasswordHasher.get_password_hash(plain_password)
        assert PasswordHasher.verify_password(plain_password, hashed) is True

    # ---- Negative Tests ----
    def test_verify_password_incorrect(self):
        hashed = PasswordHasher.get_password_hash("secure123")
        assert PasswordHasher.verify_password("wrong_password", hashed) is False

    def test_verify_password_empty_input(self):
        hashed = PasswordHasher.get_password_hash("secure123")
        assert PasswordHasher.verify_password("", hashed) is False

    # ---- Edge Cases ----
    def test_verify_password_invalid_hash_format(self):
        with pytest.raises(UnknownHashError):
            PasswordHasher.verify_password("secure123", "not_a_real_hash")

    @pytest.mark.parametrize("password", [
        "",                          # Empty
        "a" * 100,                  # Very long
        "👀unicode_password🚀",     # Unicode
        "  whitespace  ",           # Whitespace
    ])
    def test_hash_and_verify_varied_inputs(self, password):
        hashed = PasswordHasher.get_password_hash(password)
        assert PasswordHasher.verify_password(password, hashed) is True