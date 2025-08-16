from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped, mapped_column
from typing import TYPE_CHECKING

from .mixins import AuditMixin, ValidityMixin
from . import Base
if TYPE_CHECKING:
    from . import Group, Role

class GroupRole(Base, AuditMixin, ValidityMixin):
    __tablename__ = "groups_roles"

    group_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("groups.id", ondelete="CASCADE"), primary_key=True
    )
    role_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True
    )

    # Relationships
    group: Mapped["Group"] = relationship(
        "Group", foreign_keys=[group_id], back_populates="group_roles", lazy="selectin"
    )
    role: Mapped["Role"] = relationship(
        "Role", foreign_keys=[role_id], back_populates="role_groups", lazy="selectin"
    )

    def __repr__(self) -> str:
        return (
            f"<GroupRole group_id={self.group_id} "
            f"role_id={self.role_id} created_by={self.created_by} "
            f"is_deleted={self.is_deleted}>"
        )
