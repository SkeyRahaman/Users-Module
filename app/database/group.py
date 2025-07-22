from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Text
)
from sqlalchemy.orm import relationship
from ..database import Base
from sqlalchemy.sql import func
from .associations import user_group, group_role

class Group(Base):
    """User groups that can be assigned roles."""
    
    __tablename__ = 'groups'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    
    # Status
    is_deleted = Column(Boolean, default=False)
    
    # Timestamps
    created = Column(DateTime(timezone=True), server_default=func.now())
    updated = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    users = relationship(
        "User",
        secondary=user_group,
        back_populates="groups"
    )
    roles = relationship(
        "Role",
        secondary=group_role,
        back_populates="groups"
    )
