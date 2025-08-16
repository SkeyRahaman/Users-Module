from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped, mapped_column

from .mixins import AuditMixin, ValidityMixin
from . import Base

class RolePermission(Base, AuditMixin, ValidityMixin):
    __tablename__ = "roles_permissions"

    role_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True
    )
    permission_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True
    )

    # Relationships
    role: Mapped["Role"] = relationship(
        "Role", foreign_keys=[role_id], back_populates="role_permissions", lazy="selectin"
    )
    permission: Mapped["Permission"] = relationship(
        "Permission",
        foreign_keys=[permission_id],
        back_populates="permission_roles",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<RolePermission role_id={self.role_id} "
            f"permission_id={self.permission_id} created_by={self.created_by} "
            f"is_deleted={self.is_deleted}>"
        )
