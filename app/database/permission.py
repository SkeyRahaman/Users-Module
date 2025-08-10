from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Text
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from . import Base

class Permission(Base):
    
    __tablename__ = 'permissions'

    # Permission's data
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    
    # Status flags
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    
    # Timestamps
    created = Column(DateTime(timezone=True), server_default=func.now())
    updated = Column(DateTime(timezone=True), server_default=func.now(),onupdate=func.now())

    #relationships
    permission_roles = relationship("RolePermission", foreign_keys="[RolePermission.permission_id]", back_populates="permission")

    def __repr__(self):
        return f"<Permission {self.name}>"
    