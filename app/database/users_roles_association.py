from sqlalchemy import (
    Column, Integer, Boolean, DateTime, ForeignKey
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from . import Base

class UserRole(Base):
    __tablename__ = 'users_roles'

    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), primary_key=True)
    role_id = Column(Integer, ForeignKey('roles.id', ondelete="CASCADE"), primary_key=True)

    # Audit/Metadata columns
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(Integer, ForeignKey('users.id', ondelete="SET NULL"), nullable=True)


    # Soft delete flag
    is_deleted = Column(Boolean, default=False, nullable=False)

    # Validity period for the association
    valid_from = Column(DateTime(timezone=True), nullable=True)  
    valid_until = Column(DateTime(timezone=True), nullable=True) 

    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="user_roles", lazy="selectin")
    role = relationship("Role", foreign_keys=[role_id], back_populates="role_users", lazy="selectin")
    creator = relationship("User", foreign_keys=[created_by], lazy="joined")

    def __repr__(self):
        return (f"<UserRole user_id={self.user_id} "
                f"role_id={self.role_id} created_by={self.created_at} "
                f"is_deleted={self.is_deleted}>")
