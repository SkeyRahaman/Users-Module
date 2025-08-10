from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from . import Base

class User(Base):

    __tablename__ = 'users'

    # User's data
    id = Column(Integer, primary_key=True, autoincrement=True)
    firstname = Column(String(50), nullable=False)
    middlename = Column(String(50), nullable=True)
    lastname = Column(String(50), nullable=False)
    username = Column(String(30), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    
    # Status flags
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    
    # Timestamps
    created = Column(DateTime(timezone=True), server_default=func.now())
    updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    #relationships
    user_roles = relationship("UserRole", foreign_keys="[UserRole.user_id]", back_populates="user", lazy="selectin")
    user_groups = relationship("UserGroup", foreign_keys="[UserGroup.user_id]", back_populates="user", lazy="selectin")

    def __repr__(self):
        return f"<User {self.username}>"
