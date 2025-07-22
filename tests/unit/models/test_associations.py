# tests/models/test_associations.py

import pytest
from app.database.user import User
from app.database.role import Role
from app.database.group import Group
from app.database.permission import Permission


class TestAssociationTables:

    def test_user_role_association(self, db_session):
        user = User(
            firstname="Shakib",
            lastname="Mondal",
            username="shakib5",
            email="shakib5@example.com",
            password="hashed"
        )
        role = Role(name="superadmin")

        user.roles.append(role)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert len(user.roles) == 1
        assert user.roles[0].name == "superadmin"
        assert role.users[0].username == "shakib5"

    def test_user_group_association(self, db_session):
        user = User(
            firstname="Rahul",
            lastname="Singh",
            username="rahul1",
            email="rahul@example.com",
            password="pw"
        )
        group = Group(name="support")

        user.groups.append(group)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert len(user.groups) == 1
        assert user.groups[0].name == "support"
        assert group.users[0].username == "rahul1"

    def test_role_permission_association(self, db_session):
        role = Role(name="moderator")
        permission = Permission(name="ban_users")

        role.permissions.append(permission)
        db_session.add(role)
        db_session.commit()
        db_session.refresh(role)

        assert len(role.permissions) == 1
        assert role.permissions[0].name == "ban_users"
        assert permission.roles[0].name == "moderator"

    def test_group_role_association(self, db_session):
        group = Group(name="marketing")
        role = Role(name="seo_specialist")

        group.roles.append(role)
        db_session.add(group)
        db_session.commit()
        db_session.refresh(group)

        assert len(group.roles) == 1
        assert group.roles[0].name == "seo_specialist"
        assert role.groups[0].name == "marketing"
