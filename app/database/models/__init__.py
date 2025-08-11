from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import Config

engine = create_engine(Config.DATABASE_URL)
SessionLocal = sessionmaker(autoflush=False, autocommit = False, bind=engine)

Base = declarative_base()

#tables
from .user import User
from .group import Group
from .role import Role
from .permission import Permission
from .users_roles_association import UserRole
from .users_groups_associations import UserGroup
from .groups_roles_associations import GroupRole
from .roles_permissions_associations import RolePermission
