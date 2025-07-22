# tests/integration/test_user_group_role_permission.py

import pytest
from app.database.user import User
from app.database.group import Group
from app.database.role import Role
from app.database.permission import Permission


class TestUserGroupRolePermissionIntegration:

    def test_user_group_role_permission_graph(self, db_session):
        # Step 1: Create a user
        user = User(
            firstname="Shakib",
            lastname="Mondal",
            username="shakib_user",
            email="shakib_user@example.com",
            password="supersecret"
        )

        # Step 2: Create a group and add user to group
        group = Group(name="engineering")
        group.users.append(user)

        # Step 3: Create a role and assign to group
        role = Role(name="developer")
        group.roles.append(role)

        # Step 4: Create permission and assign to role
        permission = Permission(name="deploy_app")
        role.permissions.append(permission)

        # Commit everything
        db_session.add(group)
        db_session.commit()
        db_session.refresh(user)

        # Step 5: Assert relationships across layers
        assert len(user.groups) == 1
        assert user.groups[0].name == "engineering"

        assert len(user.groups[0].roles) == 1
        assert user.groups[0].roles[0].name == "developer"

        assert len(user.groups[0].roles[0].permissions) == 1
        assert user.groups[0].roles[0].permissions[0].name == "deploy_app"

        # Optional: Cross-check reverse relationship
        assert permission.roles[0].name == "developer"
        assert role.groups[0].name == "engineering"
        assert group.users[0].username == "shakib_user"
