"""Seed default data

Revision ID: 724ac70b8487
Revises: 0d4bc5398270
Create Date: 2025-08-17 19:48:27.510853

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import datetime

from app.config import Config


# revision identifiers, used by Alembic.
revision: str = '724ac70b8487'
down_revision: Union[str, Sequence[str], None] = '0d4bc5398270'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    now = datetime.datetime.now(datetime.UTC)

    groups_table = sa.table(
        "groups",
        sa.column("id", sa.Integer),
        sa.column("name", sa.String),
        sa.column("description", sa.Text),
        sa.column("is_active", sa.Boolean),
        sa.column("is_deleted", sa.Boolean),
    )

    roles_table = sa.table(
        "roles",
        sa.column("id", sa.Integer),
        sa.column("name", sa.String),
        sa.column("description", sa.Text),
        sa.column("is_active", sa.Boolean),
        sa.column("is_deleted", sa.Boolean),
    )

    permissions_table = sa.table(
        "permissions",
        sa.column("id", sa.Integer),
        sa.column("name", sa.String),
        sa.column("description", sa.Text),
        sa.column("is_active", sa.Boolean),
        sa.column("is_deleted", sa.Boolean),
    )

    users_table = sa.table(
        "users",
        sa.column("id", sa.Integer),
        sa.column("firstname", sa.String),
        sa.column("middlename", sa.String),
        sa.column("lastname", sa.String),
        sa.column("username", sa.String),
        sa.column("email", sa.String),
        sa.column("password", sa.String),
        sa.column("is_verified", sa.Boolean),
        sa.column("created", sa.DateTime(timezone=True)),
        sa.column("updated", sa.DateTime(timezone=True)),
        sa.column("is_active", sa.Boolean),
        sa.column("is_deleted", sa.Boolean),
    )

    groups_roles_table = sa.table(
        "groups_roles",
        sa.column("group_id", sa.Integer),
        sa.column("role_id", sa.Integer),
        sa.column("created_at", sa.DateTime(timezone=True)),
        sa.column("updated_at", sa.DateTime(timezone=True)),
        sa.column("created_by", sa.Integer),
        sa.column("is_deleted", sa.Boolean),
        sa.column("valid_from", sa.DateTime(timezone=True)),
        sa.column("valid_until", sa.DateTime(timezone=True)),
    )

    roles_permissions_table = sa.table(
        "roles_permissions",
        sa.column("role_id", sa.Integer),
        sa.column("permission_id", sa.Integer),
        sa.column("created_at", sa.DateTime(timezone=True)),
        sa.column("updated_at", sa.DateTime(timezone=True)),
        sa.column("created_by", sa.Integer),
        sa.column("is_deleted", sa.Boolean),
        sa.column("valid_from", sa.DateTime(timezone=True)),
        sa.column("valid_until", sa.DateTime(timezone=True)),
    )

    users_groups_table = sa.table(
        "users_groups",
        sa.column("user_id", sa.Integer),
        sa.column("group_id", sa.Integer),
        sa.column("created_at", sa.DateTime(timezone=True)),
        sa.column("updated_at", sa.DateTime(timezone=True)),
        sa.column("created_by", sa.Integer),
        sa.column("is_deleted", sa.Boolean),
        sa.column("valid_from", sa.DateTime(timezone=True)),
        sa.column("valid_until", sa.DateTime(timezone=True)),
    )

    users_roles_table = sa.table(
        "users_roles",
        sa.column("user_id", sa.Integer),
        sa.column("role_id", sa.Integer),
        sa.column("created_at", sa.DateTime(timezone=True)),
        sa.column("updated_at", sa.DateTime(timezone=True)),
        sa.column("created_by", sa.Integer),
        sa.column("is_deleted", sa.Boolean),
        sa.column("valid_from", sa.DateTime(timezone=True)),
        sa.column("valid_until", sa.DateTime(timezone=True)),
    )

    # 1. Groups: Minimal representative
    op.bulk_insert(
        groups_table,
        [
            {"id": 1, "name": "Administrators", "description": "Users with full system control.", "is_active": True, "is_deleted": False},
            {"id": 2, "name": "Managers", "description": "Manage users and resources within departments.", "is_active": True, "is_deleted": False},
            {"id": 3, "name": "Users", "description": "Regular end users.", "is_active": True, "is_deleted": False},
        ],
    )

    # 2. Roles: Key roles for demo
    op.bulk_insert(
        roles_table,
        [
            {"id": 1, "name": "System Administrator (Admin)", "description": "Highest privilege with full system access.", "is_active": True, "is_deleted": False},
            {"id": 2, "name": "Group Administrator / Manager", "description": "Manage users, groups, roles within scope.", "is_active": True, "is_deleted": False},
            {"id": 3, "name": "User", "description": "Limited permissions for regular users.", "is_active": True, "is_deleted": False},
        ],
    )

    # 3. All permissions as you require (full list)
    op.bulk_insert(
        permissions_table,
        [
            {"id": 1, "name": "create_user", "description": "Permission to create a new user", "is_active": True, "is_deleted": False},
            {"id": 2, "name": "view_user_self", "description": "Permission to view own user profile", "is_active": True, "is_deleted": False},
            {"id": 3, "name": "update_user_self", "description": "Permission to update own user profile", "is_active": True, "is_deleted": False},
            {"id": 4, "name": "delete_user_self", "description": "Permission to delete own user account", "is_active": True, "is_deleted": False},
            {"id": 5, "name": "view_user_by_id", "description": "Permission to view any user by ID", "is_active": True, "is_deleted": False},
            {"id": 6, "name": "reset_user_password", "description": "Permission to reset a user’s password", "is_active": True, "is_deleted": False},
            {"id": 7, "name": "activate_user", "description": "Permission to activate a user account", "is_active": True, "is_deleted": False},
            {"id": 8, "name": "deactivate_user", "description": "Permission to deactivate a user account", "is_active": True, "is_deleted": False},
            {"id": 9, "name": "view_user_activity", "description": "Permission to view user activity logs", "is_active": True, "is_deleted": False},
            {"id": 10, "name": "create_role", "description": "Permission to create a new role", "is_active": True, "is_deleted": False},
            {"id": 11, "name": "view_roles", "description": "Permission to view list of roles", "is_active": True, "is_deleted": False},
            {"id": 12, "name": "view_role_by_id", "description": "Permission to view role details by ID", "is_active": True, "is_deleted": False},
            {"id": 13, "name": "update_role", "description": "Permission to update existing role", "is_active": True, "is_deleted": False},
            {"id": 14, "name": "delete_role", "description": "Permission to delete a role", "is_active": True, "is_deleted": False},
            {"id": 15, "name": "create_group", "description": "Permission to create a new group", "is_active": True, "is_deleted": False},
            {"id": 16, "name": "view_groups", "description": "Permission to view list of groups", "is_active": True, "is_deleted": False},
            {"id": 17, "name": "view_group_by_id", "description": "Permission to view group details by ID", "is_active": True, "is_deleted": False},
            {"id": 18, "name": "update_group", "description": "Permission to update existing group", "is_active": True, "is_deleted": False},
            {"id": 19, "name": "delete_group", "description": "Permission to delete a group", "is_active": True, "is_deleted": False},
            {"id": 20, "name": "view_group_by_name", "description": "Permission to view group details by name", "is_active": True, "is_deleted": False},
            {"id": 21, "name": "create_permission", "description": "Permission to create new permissions", "is_active": True, "is_deleted": False},
            {"id": 22, "name": "view_permissions", "description": "Permission to view list of permissions", "is_active": True, "is_deleted": False},
            {"id": 23, "name": "view_permission_by_id", "description": "Permission to view permission details by ID", "is_active": True, "is_deleted": False},
            {"id": 24, "name": "update_permission", "description": "Permission to update existing permission", "is_active": True, "is_deleted": False},
            {"id": 25, "name": "delete_permission", "description": "Permission to delete a permission", "is_active": True, "is_deleted": False},
            {"id": 26, "name": "request_token", "description": "Permission to request authentication token", "is_active": True, "is_deleted": False},
            {"id": 27, "name": "view_health", "description": "Permission to view system health status", "is_active": True, "is_deleted": False},
            {"id": 28, "name": "view_metrics", "description": "Permission to view system metrics (if added)", "is_active": True, "is_deleted": False},
            {"id": 29, "name": "view_status", "description": "Permission to view overall service status (if added)", "is_active": True, "is_deleted": False},
            {"id": 30, "name": "assign_role_to_user", "description": "Permission to assign role to user", "is_active": True, "is_deleted": False},
            {"id": 31, "name": "assign_permission_to_role", "description": "Permission to assign permission to role", "is_active": True, "is_deleted": False},
            {"id": 32, "name": "assign_user_to_group", "description": "Permission to add user to group", "is_active": True, "is_deleted": False},
            {"id": 33, "name": "remove_user_from_group", "description": "Permission to remove user from group", "is_active": True, "is_deleted": False},
            {"id": 34, "name": "view_audit_logs", "description": "Permission to view audit and logs", "is_active": True, "is_deleted": False},
            {"id": 35, "name": "search_user", "description": "Permission to serarch user in db", "is_active": True, "is_deleted": False},
            
        ],
    )

    # 4. Users: minimal - one admin and one regular user from Config
    op.bulk_insert(
        users_table,
        [
            {
                "id": 1,
                "firstname": Config.ADMIN_USER["firstname"],
                "middlename": Config.ADMIN_USER["middlename"],
                "lastname": Config.ADMIN_USER["lastname"],
                "username": Config.ADMIN_USER["username"],
                "email": Config.ADMIN_USER["email"],
                "password": Config.ADMIN_USER["password_hash"],
                "is_verified": Config.ADMIN_USER["is_verified"],
                "created": now,
                "updated": now,
                "is_active": Config.ADMIN_USER["is_active"],
                "is_deleted": Config.ADMIN_USER["is_deleted"],
            },
            {
                "id": 2,
                "firstname": Config.NORMAL_USER["firstname"],
                "middlename": Config.NORMAL_USER["middlename"],
                "lastname": Config.NORMAL_USER["lastname"],
                "username": Config.NORMAL_USER["username"],
                "email": Config.NORMAL_USER["email"],
                "password": Config.NORMAL_USER["password_hash"],
                "is_verified": Config.NORMAL_USER["is_verified"],
                "created": now,
                "updated": now,
                "is_active": Config.NORMAL_USER["is_active"],
                "is_deleted": Config.NORMAL_USER["is_deleted"],
            },
        ],
    )


    # 5. Associations: groups_roles
    op.bulk_insert(
        groups_roles_table,
        [
            {"group_id": 1, "role_id": 1, "created_at": now, "updated_at": now, "created_by": 1, "is_deleted": False, "valid_from": None, "valid_until": None},  # Admin
            {"group_id": 2, "role_id": 2, "created_at": now, "updated_at": now, "created_by": 1, "is_deleted": False, "valid_from": None, "valid_until": None},  # Manager
            {"group_id": 3, "role_id": 3, "created_at": now, "updated_at": now, "created_by": 1, "is_deleted": False, "valid_from": None, "valid_until": None},  # User
        ],
    )

    # 6. Associations: roles_permissions — Admin gets all, Manager and User get selective (simplified example)
    admin_permissions = list(range(1, 36))  # all permission IDs 1 to 34
    # Manager gets subset (example: IDs 2, 3, 11, 15, etc.)
    manager_permissions = [2,3,11,15,16,18,22,33]
    # User gets minimal permissions (example IDs 2,3)
    user_permissions = [2,3]

    role_permission_inserts = []
    for pid in admin_permissions:
        role_permission_inserts.append({"role_id": 1, "permission_id": pid, "created_at": now, "updated_at": now, "created_by": 1, "is_deleted": False, "valid_from": None, "valid_until": None})
    for pid in manager_permissions:
        role_permission_inserts.append({"role_id": 2, "permission_id": pid, "created_at": now, "updated_at": now, "created_by": 1, "is_deleted": False, "valid_from": None, "valid_until": None})
    for pid in user_permissions:
        role_permission_inserts.append({"role_id": 3, "permission_id": pid, "created_at": now, "updated_at": now, "created_by": 1, "is_deleted": False, "valid_from": None, "valid_until": None})

    op.bulk_insert(roles_permissions_table, role_permission_inserts)

    # 7. Associations: users_groups
    op.bulk_insert(
        users_groups_table,
        [
            {"user_id": 1, "group_id": 1, "created_at": now, "updated_at": now, "created_by": 1, "is_deleted": False, "valid_from": None, "valid_until": None},  # Admin user in Administrators group
            {"user_id": 2, "group_id": 3, "created_at": now, "updated_at": now, "created_by": 1, "is_deleted": False, "valid_from": None, "valid_until": None},  # Regular user in Users group
        ],
    )

    # 8. Associations: users_roles
    op.bulk_insert(
        users_roles_table,
        [
            {"user_id": 1, "role_id": 1, "created_at": now, "updated_at": now, "created_by": 1, "is_deleted": False, "valid_from": None, "valid_until": None},  # Admin user with Admin role
            {"user_id": 2, "role_id": 3, "created_at": now, "updated_at": now, "created_by": 1, "is_deleted": False, "valid_from": None, "valid_until": None},  # Regular user with User role
        ],
    )
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute(
            """
            DO $$
            DECLARE
              rec RECORD;
            BEGIN
              FOR rec IN
                SELECT seq_ns.nspname AS seq_schema,
                       seq.relname    AS seq_name,
                       tab_ns.nspname AS table_schema,
                       tab.relname    AS table_name,
                       att.attname    AS column_name
                FROM pg_class seq
                JOIN pg_namespace seq_ns ON seq_ns.oid = seq.relnamespace
                JOIN pg_depend dep ON dep.objid = seq.oid AND dep.deptype = 'a'
                JOIN pg_class tab ON tab.oid = dep.refobjid
                JOIN pg_namespace tab_ns ON tab_ns.oid = tab.relnamespace
                JOIN pg_attribute att ON att.attrelid = tab.oid AND att.attnum = dep.refobjsubid
                WHERE seq.relkind = 'S'
              LOOP
                EXECUTE format(
                  'SELECT setval(%L, COALESCE((SELECT MAX(%I) FROM %I.%I), 0), true)',
                  format('%I.%I', rec.seq_schema, rec.seq_name),
                  rec.column_name,
                  rec.table_schema,
                  rec.table_name
                );
              END LOOP;
            END
            $$;
            """
        )


def downgrade() -> None:
    # Remove seeded user-role mappings
    op.execute("DELETE FROM users_roles WHERE user_id IN (1, 2)")

    # Remove seeded user-group mappings
    op.execute("DELETE FROM users_groups WHERE user_id IN (1, 2)")

    # Remove seeded role-permission mappings
    op.execute("DELETE FROM roles_permissions WHERE role_id IN (1, 2, 3)")

    # Remove seeded group-role mappings
    op.execute("DELETE FROM groups_roles WHERE group_id IN (1, 2, 3)")

    # Remove seeded users
    op.execute("DELETE FROM users WHERE id IN (1, 2)")

    # Remove seeded roles
    op.execute(
        "DELETE FROM roles WHERE name IN ('System Administrator (Admin)', 'Group Administrator / Manager', 'User')"
    )

    # Remove seeded permissions (all)
    permission_names = [
        "create_user", "view_user_self", "update_user_self", "delete_user_self", "view_user_by_id", "reset_user_password",
        "activate_user", "deactivate_user", "view_user_activity", "create_role", "view_roles", "view_role_by_id", "update_role",
        "delete_role", "create_group", "view_groups", "view_group_by_id", "update_group", "delete_group", "view_group_by_name",
        "create_permission", "view_permissions", "view_permission_by_id", "update_permission", "delete_permission", "request_token",
        "view_health", "view_metrics", "view_status", "assign_role_to_user", "assign_permission_to_role", "assign_user_to_group",
        "remove_user_from_group", "view_audit_logs"
    ]
    op.execute("DELETE FROM permissions WHERE name IN (" + ",".join(f"'{name}'" for name in permission_names) + ")")

    # Remove seeded groups
    op.execute(
        "DELETE FROM groups WHERE name IN ('Administrators', 'Managers', 'Users')"
    )