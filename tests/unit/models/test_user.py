import pytest
from app.database.user import User
from app.database.role import Role
from app.database.group import Group
from sqlalchemy.exc import IntegrityError


class TestUserModel:
    def test_create_user_minimal(self, db_session):
        user = User(
            firstname="Shakib",
            lastname="Mondal",
            username="shakib",
            email="shakib@example.com",
            password="hashedpassword"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert user.id is not None
        assert user.is_active is True
        assert user.is_verified is False

    def test_username_email_unique(self, db_session):
        user1 = User(
            firstname="A", lastname="B", username="same", email="same@example.com", password="p"
        )
        user2 = User(
            firstname="C", lastname="D", username="same", email="same@example.com", password="p"
        )
        db_session.add(user1)
        db_session.commit()
        db_session.add(user2)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_user_roles_and_groups(self, db_session):
        role = Role(name="admin")
        group = Group(name="devs")
        user = User(
            firstname="Shakib",
            lastname="Mondal",
            username="shakib2",
            email="shakib2@example.com",
            password="hashedpassword",
            roles=[role],
            groups=[group]
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert len(user.roles) == 1
        assert user.roles[0].name == "admin"
        assert len(user.groups) == 1
        assert user.groups[0].name == "devs"
