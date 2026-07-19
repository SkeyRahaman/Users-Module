import pytest
from pydantic import ValidationError, EmailStr
from app.schemas.auth import PasswordResetRequest, PasswordResetConfirm


class TestPasswordResetRequest:
    """Test cases for PasswordResetRequest model"""

    def test_valid_email(self):
        req = PasswordResetRequest(email="user@example.com")
        assert req.email == "user@example.com"
        assert isinstance(req.email, str)

    def test_invalid_email(self):
        with pytest.raises(ValidationError):
            PasswordResetRequest(email="not-an-email")

    def test_missing_email(self):
        with pytest.raises(ValidationError):
            PasswordResetRequest()


class TestPasswordResetConfirm:
    """Test cases for PasswordResetConfirm model"""

    def test_valid_password_reset_confirm(self):
        confirm = PasswordResetConfirm(token="sometoken123", new_password="secret1")
        assert confirm.token == "sometoken123"
        assert confirm.new_password == "secret1"

    def test_missing_token(self):
        with pytest.raises(ValidationError):
            PasswordResetConfirm(new_password="secret1")

    def test_missing_new_password(self):
        with pytest.raises(ValidationError):
            PasswordResetConfirm(token="sometoken123")

    def test_new_password_min_length(self):
        with pytest.raises(ValidationError):
            PasswordResetConfirm(token="sometoken123", new_password="123")

    def test_new_password_exact_min_length(self):
        confirm = PasswordResetConfirm(token="sometoken123", new_password="123456")
        assert confirm.new_password == "123456"
