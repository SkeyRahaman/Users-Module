from typing import List
from sqlalchemy.orm import Mapped, relationship

from . import Base
from .mixins import TimestampMixin, StatusMixin, NamedEntityMixin, TablenameMixin


class Permission(Base, TablenameMixin, TimestampMixin, StatusMixin, NamedEntityMixin):

    permission_roles: Mapped[List["RolePermission"]] = relationship(
        back_populates="permission",
        foreign_keys="[RolePermission.permission_id]",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Permission {self.name}>"
