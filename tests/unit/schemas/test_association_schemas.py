import pytest
from datetime import datetime, timedelta
from pydantic import ValidationError

from app.schemas.association_schemas import (
    ValiditySchema,
    AddUserToGroupForGroup,
    AddUserToGroupForUser,
)

class TestValiditySchema:
    def test_valid_dates(self):
        now = datetime.now()
        future = now + timedelta(days=1)
        schema = ValiditySchema(valid_from=now, valid_until=future)
        assert schema.valid_from == now
        assert schema.valid_until == future

    def test_optional_dates_none(self):
        schema = ValiditySchema()
        assert schema.valid_from is None
        assert schema.valid_until is None

class TestAddUserToGroupForGroup:
    def test_valid_input(self):
        schema = AddUserToGroupForGroup(user_id=1)
        assert schema.user_id == 1
        # Inherit validity fields
        assert schema.valid_from is None
        assert schema.valid_until is None

    def test_with_validity_fields(self):
        now = datetime.now()
        schema = AddUserToGroupForGroup(user_id=7, valid_from=now)
        assert schema.user_id == 7
        assert schema.valid_from == now

    def test_missing_user_id_fails(self):
        with pytest.raises(ValidationError):
            AddUserToGroupForGroup()  # user_id is required

class TestAddUserToGroupForUser:
    def test_valid_input(self):
        schema = AddUserToGroupForUser(group_id=4)
        assert schema.group_id == 4
        assert schema.valid_from is None
        assert schema.valid_until is None

    def test_with_validity_fields(self):
        future = datetime.now() + timedelta(days=10)
        schema = AddUserToGroupForUser(group_id=5, valid_until=future)
        assert schema.group_id == 5
        assert schema.valid_until == future

    def test_missing_group_id_fails(self):
        with pytest.raises(ValidationError):
            AddUserToGroupForUser()  # group_id is required
