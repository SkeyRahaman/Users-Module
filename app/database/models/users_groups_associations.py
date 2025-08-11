from sqlalchemy import (
    Column, Integer, Boolean, DateTime, ForeignKey
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from . import Base


class UserGroup(Base):
    __tablename__ = 'users_groups'

    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), primary_key=True)
    group_id = Column(Integer, ForeignKey('groups.id', ondelete="CASCADE"), primary_key=True)

    # Audit/Metadata columns
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(Integer, ForeignKey('users.id', ondelete="SET NULL"), nullable=True)

    # Soft delete flag
    is_deleted = Column(Boolean, default=False, nullable=False)

    # Validity period
    valid_from = Column(DateTime(timezone=True), nullable=True)
    valid_until = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="user_groups", lazy="selectin")
    group = relationship("Group", foreign_keys=[group_id], back_populates="group_users", lazy="selectin")
    creator = relationship("User", foreign_keys=[created_by], lazy="joined")

    def __repr__(self):
        return (f"<UserGroup user_id={self.user_id} "
                f"group_id={self.group_id} created_by={self.created_by} "
                f"is_deleted={self.is_deleted}>")
