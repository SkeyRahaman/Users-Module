import pytest
from app.database.user import User
from app.database.role import Role
from app.database.group import Group
from sqlalchemy.exc import IntegrityError

class TestGroupModel:

    def test_create_group_minimal(self, db_session):
        group = Group(name="engineering")
        db_session.add(group)
        db_session.commit()
        db_session.refresh(group)

        assert group.id is not None
        assert group.name == "engineering"
        assert group.is_deleted is False
        assert group.created is not None
        assert group.updated is not None
        assert group.updated == group.created

    def test_group_name_unique_constraint(self, db_session):
        g1 = Group(name="finance")
        g2 = Group(name="finance")  # duplicate name

        db_session.add(g1)
        db_session.commit()

        db_session.add(g2)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_group_with_users(self, db_session):
        group = Group(name="hr")
        user = User(
            firstname="Shakib",
            lastname="Mondal",
            username="shakib4",
            email="shakib4@example.com",
            password="securepass"
        )

        group.users.append(user)
        db_session.add(group)
        db_session.commit()
        db_session.refresh(group)

        assert len(group.users) == 1
        assert group.users[0].username == "shakib4"

    def test_group_with_roles(self, db_session):
        group = Group(name="devops")
        role = Role(name="infra")

        group.roles.append(role)
        db_session.add(group)
        db_session.commit()
        db_session.refresh(group)

        assert len(group.roles) == 1
        assert group.roles[0].name == "infra"
