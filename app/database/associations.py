from sqlalchemy import (Column, DateTime, ForeignKey, Integer, Table)
from sqlalchemy.sql import func
from ..database import Base

# Association tables for many-to-many relationships
user_role = Table(
    'user_role',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id', ondelete="CASCADE")),
    Column('role_id', Integer, ForeignKey('roles.id', ondelete="CASCADE")),
    Column('created', DateTime(timezone=True), server_default=func.now())
)

user_group = Table(
    'user_group',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id', ondelete="CASCADE")),
    Column('group_id', Integer, ForeignKey('groups.id', ondelete="CASCADE")),
    Column('created', DateTime(timezone=True), server_default=func.now())
)

role_permission = Table(
    'role_permission',
    Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id', ondelete="CASCADE")),
    Column('permission_id', Integer, ForeignKey('permissions.id', ondelete="CASCADE")),
    Column('created', DateTime(timezone=True), server_default=func.now())
)

group_role = Table(
    'group_role',
    Base.metadata,
    Column('group_id', Integer, ForeignKey('groups.id', ondelete="CASCADE")),
    Column('role_id', Integer, ForeignKey('roles.id', ondelete="CASCADE")),
    Column('created', DateTime(timezone=True), server_default=func.now())
)
