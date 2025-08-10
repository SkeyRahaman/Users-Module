from sqlalchemy import (
    Column, Integer, Boolean, DateTime, ForeignKey
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from . import Base


class RolePermission(Base):
    __tablename__ = 'roles_permissions'

    role_id = Column(Integer, ForeignKey('roles.id', ondelete="CASCADE"), primary_key=True)
    permission_id = Column(Integer, ForeignKey('permissions.id', ondelete="CASCADE"), primary_key=True)

    # Audit/Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(),
                        onupdate=func.now(), nullable=False)
    created_by = Column(Integer, ForeignKey('users.id', ondelete="SET NULL"), nullable=True)

    # Soft delete flag
    is_deleted = Column(Boolean, default=False, nullable=False)

    # Relationships
    role = relationship("Role", foreign_keys=[role_id], back_populates="role_permissions", lazy="selectin")
    permission = relationship("Permission", foreign_keys=[permission_id], back_populates="permission_roles", lazy="selectin")
    creator = relationship("User", foreign_keys=[created_by], lazy="joined")

    def __repr__(self):
        return (f"<RolePermission role_id={self.role_id} "
                f"permission_id={self.permission_id} created_by={self.created_by} "
                f"is_deleted={self.is_deleted}>")
