import pytest
from datetime import datetime, timedelta
from pydantic import ValidationError

from app.schemas.association_schemas import *

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

class TestAddRoleToUserForUser:
    def test_valid_input(self):
        schema = AddRoleToUserForUser(role_id=10)
        assert schema.role_id == 10
        assert schema.valid_from is None
        assert schema.valid_until is None

    def test_with_validity_fields(self):
        future = datetime.now() + timedelta(days=5)
        schema = AddRoleToUserForUser(role_id=20, valid_until=future)
        assert schema.role_id == 20
        assert schema.valid_until == future

    def test_missing_role_id_fails(self):
        with pytest.raises(ValidationError):
            AddRoleToUserForUser()

class TestAddRoleToUserForRole:
    def test_valid_input(self):
        schema = AddRoleToUserForRole(user_id=15)
        assert schema.user_id == 15
        assert schema.valid_from is None
        assert schema.valid_until is None

    def test_with_validity_fields(self):
        now = datetime.now()
        schema = AddRoleToUserForRole(user_id=7, valid_from=now)
        assert schema.user_id == 7
        assert schema.valid_from == now

    def test_missing_user_id_fails(self):
        with pytest.raises(ValidationError):
            AddRoleToUserForRole()

class TestAddRoleToGroupForGroup:
    def test_valid_input(self):
        schema = AddRoleToGroupForGroup(role_id=11)
        assert schema.role_id == 11
        assert schema.valid_from is None
        assert schema.valid_until is None

    def test_with_validity_fields(self):
        future = datetime.now() + timedelta(days=1)
        schema = AddRoleToGroupForGroup(role_id=5, valid_until=future)
        assert schema.role_id == 5
        assert schema.valid_until == future

    def test_missing_role_id_fails(self):
        with pytest.raises(ValidationError):
            AddRoleToGroupForGroup()

class TestAddRoleToGroupForRole:
    def test_valid_input(self):
        schema = AddRoleToGroupForRole(group_id=6)
        assert schema.group_id == 6
        assert schema.valid_from is None
        assert schema.valid_until is None

    def test_with_validity_fields(self):
        now = datetime.now()
        schema = AddRoleToGroupForRole(group_id=7, valid_from=now)
        assert schema.group_id == 7
        assert schema.valid_from == now

    def test_missing_group_id_fails(self):
        with pytest.raises(ValidationError):
            AddRoleToGroupForRole()

class TestAddPermissionToRoleForRole:
    def test_valid_input(self):
        schema = AddPermissionToRoleForRole(permission_id=13)
        assert schema.permission_id == 13
        assert schema.valid_from is None
        assert schema.valid_until is None

    def test_with_validity_fields(self):
        future = datetime.now() + timedelta(days=3)
        schema = AddPermissionToRoleForRole(permission_id=4, valid_until=future)
        assert schema.permission_id == 4
        assert schema.valid_until == future

    def test_missing_permission_id_fails(self):
        with pytest.raises(ValidationError):
            AddPermissionToRoleForRole()

class TestAddPermissionToRoleForPermission:
    def test_valid_input(self):
        schema = AddPermissionToRoleForPermission(role_id=8)
        assert schema.role_id == 8
        assert schema.valid_from is None
        assert schema.valid_until is None

    def test_with_validity_fields(self):
        now = datetime.now()
        schema = AddPermissionToRoleForPermission(role_id=9, valid_from=now)
        assert schema.role_id == 9
        assert schema.valid_from == now

    def test_missing_role_id_fails(self):
        with pytest.raises(ValidationError):
            AddPermissionToRoleForPermission()

