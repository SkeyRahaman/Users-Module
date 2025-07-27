from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Text
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .associations import user_role, role_permission, group_role
from ..database import Base

class Role(Base):
    """User roles with associated permissions."""
    
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    
    # Status
    is_deleted = Column(Boolean, default=False)
    
    # Timestamps
    created = Column(DateTime(timezone=True), server_default=func.now())
    updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    users = relationship(
        "User",
        secondary=user_role,
        back_populates="roles"
    )
    permissions = relationship(
        "Permission",
        secondary=role_permission,
        back_populates="roles"
    )
    groups = relationship(
        "Group",
        secondary=group_role,
        back_populates="roles"
    )
