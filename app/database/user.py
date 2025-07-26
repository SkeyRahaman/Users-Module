from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base
from .associations import user_group, user_role


class User(Base):
    """User account model with authentication and authorization fields."""
    
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    firstname = Column(String(50), nullable=False)
    middlename = Column(String(50), nullable=True)
    lastname = Column(String(50), nullable=False)
    username = Column(String(30), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)  # Store hashed passwords only
    
    # Status flags
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    
    # Timestamps
    created = Column(DateTime(timezone=True), server_default=func.now())
    updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    roles = relationship(
        "Role",
        secondary=user_role,
        back_populates="users",
        cascade="all, delete"
    )
    groups = relationship(
        "Group",
        secondary=user_group,
        back_populates="users",
        cascade="all, delete"
    )

    def __repr__(self):
        return f"<User {self.username}>"
