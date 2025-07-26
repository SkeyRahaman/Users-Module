import pytest
from pydantic import ValidationError
from datetime import datetime
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserOut,
    UserDetail
)


class TestUserCreateSchema:

    def test_valid_user_create(self):
        user = UserCreate(
            firstname="Shakib",
            lastname="Mondal",
            middlename="A.",
            username="shakib99",
            email="shakib@example.com",
            password="secret123"
        )
        assert user.firstname == "Shakib"
        assert user.password == "secret123"

    def test_missing_required_field(self):
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                lastname="Mondal",
                username="shakib99",
                email="shakib@example.com",
                password="secret123"
            )
        assert "firstname" in str(exc_info.value)

    def test_invalid_email(self):
        with pytest.raises(ValidationError):
            UserCreate(
                firstname="Shakib",
                lastname="Mondal",
                username="shakib99",
                email="invalid-email",
                password="secret123"
            )

    def test_password_min_length(self):
        with pytest.raises(ValidationError):
            UserCreate(
                firstname="Shakib",
                lastname="Mondal",
                username="shakib99",
                email="shakib@example.com",
                password="123"  # too short
            )


class TestUserUpdateSchema:

    def test_partial_update_is_allowed(self):
        update = UserUpdate(firstname="Updated")
        assert update.firstname == "Updated"
        assert update.lastname is None

    def test_invalid_username_length(self):
        with pytest.raises(ValidationError):
            UserUpdate(username="a" * 100)  # exceeds max_length 30


class TestUserOutSchema:

    def test_valid_user_output(self):
        user = UserOut(
            id=1,
            firstname="Shakib",
            middlename=None,
            lastname="Mondal",
            username="shakib99",
            email="shakib@example.com",
            is_active=True,
            is_verified=False,
            is_deleted=False,
            created=datetime.now(),
            updated=None
        )
        assert user.id == 1
        assert user.is_active


class TestUserDetailSchema:

    def test_user_detail_with_relations(self):
        detail = UserDetail(
            id=1,
            firstname="Shakib",
            middlename=None,
            lastname="Mondal",
            username="shakib99",
            email="shakib@example.com",
            is_active=True,
            is_verified=True,
            is_deleted=False,
            created=datetime.now(),
            updated=None,
            roles=["admin", "editor"],
            groups=["staff", "finance"]
        )
        assert "admin" in detail.roles
        assert "staff" in detail.groups
