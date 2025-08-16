from typing import List
from sqlalchemy.orm import Mapped, relationship
from typing import TYPE_CHECKING

from . import Base
from .mixins import TimestampMixin, StatusMixin, NamedEntityMixin, TablenameMixin
if TYPE_CHECKING:
    from . import UserRole, GroupRole, RolePermission

class Role(Base, TablenameMixin, NamedEntityMixin, TimestampMixin, StatusMixin):

    role_users: Mapped[List["UserRole"]] = relationship(
        back_populates="role",
        foreign_keys="[UserRole.role_id]",
        lazy="selectin",
    )
    role_groups: Mapped[List["GroupRole"]] = relationship(
        back_populates="role",
        foreign_keys="[GroupRole.role_id]",
        lazy="selectin",
    )
    role_permissions: Mapped[List["RolePermission"]] = relationship(
        back_populates="role",
        foreign_keys="[RolePermission.role_id]",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Role {self.name}>"
