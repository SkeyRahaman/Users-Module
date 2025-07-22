from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Text
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .associations import role_permission
from ..database import Base

class Permission(Base):
    """System permissions that can be assigned to roles."""
    
    __tablename__ = 'permissions'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    
    # Status
    is_deleted = Column(Boolean, default=False)
    
    # Timestamps
    created = Column(DateTime(timezone=True), server_default=func.now())
    updated = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    roles = relationship(
        "Role",
        secondary=role_permission,
        back_populates="permissions"
    )
    