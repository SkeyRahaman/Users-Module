from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Text
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from . import Base

class Group(Base):
    
    __tablename__ = 'groups'

    #Group data
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    
    # Status flags
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    
    # Timestamps
    created = Column(DateTime(timezone=True), server_default=func.now())
    updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    #relationships
    group_users = relationship("UserGroup", foreign_keys="[UserGroup.group_id]", back_populates="group")
    group_roles = relationship("GroupRole", foreign_keys="[GroupRole.group_id]", back_populates="group")

    def __repr__(self):
        return f"<Group {self.name}>"
