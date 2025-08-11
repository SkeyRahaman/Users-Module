from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Text
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from . import Base

class Role(Base):
    
    __tablename__ = 'roles'

    #Role's data.
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    
    # Status flags
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    
    # Timestamps
    created = Column(DateTime(timezone=True), server_default=func.now())
    updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    #relationship
    role_users = relationship("UserRole", foreign_keys="[UserRole.role_id]", back_populates="role", lazy="selectin")
    role_groups = relationship("GroupRole", foreign_keys="[GroupRole.role_id]", back_populates="role", lazy="selectin")
    role_permissions = relationship("RolePermission", foreign_keys="[RolePermission.role_id]", back_populates="role", lazy="selectin")

    def __repr__(self):
        return f"<Role {self.name}>"
