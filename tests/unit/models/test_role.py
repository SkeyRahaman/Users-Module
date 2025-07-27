import pytest
from app.database.user import User
from app.database.role import Role
from app.database.group import Group
from app.database.permission import Permission
from sqlalchemy.exc import IntegrityError


class TestRoleModel:

    
    def test_create_role_minimal(self, db_session):
        role = Role(name="admin")
        db_session.add(role)
        db_session.commit()
        db_session.refresh(role)

        assert role.id is not None
        assert role.name == "admin"
        assert role.is_deleted is False
        assert role.created is not None
        assert role.updated is not None
        assert role.created == role.updated

    def test_unique_role_name_constraint(self, db_session):
        r1 = Role(name="moderator")
        r2 = Role(name="moderator")  # Duplicate name

        db_session.add(r1)
        db_session.commit()

        db_session.add(r2)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_role_with_users(self, db_session):
        role = Role(name="manager")
        user = User(
            firstname="Shakib",
            lastname="Mondal",
            username="shakib3",
            email="shakib3@example.com",
            password="hashed"
        )

        role.users.append(user)
        db_session.add(role)
        db_session.commit()
        db_session.refresh(role)

        assert len(role.users) == 1
        assert role.users[0].username == "shakib3"

    def test_role_with_permissions(self, db_session):
        role = Role(name="editor")
        perm = Permission(name="edit_articles", description="Edit articles")

        role.permissions.append(perm)
        db_session.add(role)
        db_session.commit()
        db_session.refresh(role)

        assert len(role.permissions) == 1
        assert role.permissions[0].name == "edit_articles"

    def test_role_with_groups(self, db_session):
        role = Role(name="trainer")
        group = Group(name="hr")

        role.groups.append(group)
        db_session.add(role)
        db_session.commit()
        db_session.refresh(role)

        assert len(role.groups) == 1
        assert role.groups[0].name == "hr"
