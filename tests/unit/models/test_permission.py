import pytest
from app.database.role import Role
from app.database.permission import Permission
from sqlalchemy.exc import IntegrityError

class TestPermissionModel:

    def test_create_permission_minimal(self, db_session):
        perm = Permission(name="create_user")
        db_session.add(perm)
        db_session.commit()
        db_session.refresh(perm)

        assert perm.id is not None
        assert perm.name == "create_user"
        assert perm.is_deleted is False
        assert perm.created is not None
        assert perm.updated is not None
        assert perm.created == perm.updated

    def test_unique_permission_name(self, db_session):
        p1 = Permission(name="delete_post")
        p2 = Permission(name="delete_post")

        db_session.add(p1)
        db_session.commit()

        db_session.add(p2)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_permission_with_roles(self, db_session):
        role = Role(name="admin")
        perm = Permission(name="view_dashboard")

        perm.roles.append(role)
        db_session.add(perm)
        db_session.commit()
        db_session.refresh(perm)

        assert len(perm.roles) == 1
        assert perm.roles[0].name == "admin"
