from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped, mapped_column
from typing import TYPE_CHECKING

from .mixins import AuditMixin, ValidityMixin
from . import Base

if TYPE_CHECKING:
    from . import User, Group

class UserGroup(Base, AuditMixin, ValidityMixin):
    __tablename__ = "users_groups"

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    group_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("groups.id", ondelete="CASCADE"), primary_key=True
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User", foreign_keys=[user_id], back_populates="user_groups", lazy="selectin"
    )
    group: Mapped["Group"] = relationship(
        "Group", foreign_keys=[group_id], back_populates="group_users", lazy="selectin"
    )

    def __repr__(self) -> str:
        return (
            f"<UserGroup user_id={self.user_id} "
            f"group_id={self.group_id} created_by={self.created_by} "
            f"is_deleted={self.is_deleted}>"
        )
