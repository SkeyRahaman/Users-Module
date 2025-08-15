from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.config import Config
from sqlalchemy.orm import declarative_base

engine = create_async_engine(Config.DATABASE_URL)
SessionLocal = async_sessionmaker(autoflush=False, autocommit = False, bind=engine)

async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

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
