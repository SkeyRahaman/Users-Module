from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from . import Base
from .mixins import AuditMixin, ValidityMixin

if TYPE_CHECKING:
    from . import User, Role


class UserRole(Base, AuditMixin, ValidityMixin):
    __tablename__ = "users_roles"

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    role_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="user_roles",
        foreign_keys=[user_id],
        lazy="selectin",
    )
    role: Mapped["Role"] = relationship(
        "Role",
        back_populates="role_users",
        foreign_keys=[role_id],
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<UserRole user_id={self.user_id} "
            f"role_id={self.role_id} created_at={self.created_at} "
            f"is_deleted={self.is_deleted}>"
        )
