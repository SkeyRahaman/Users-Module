from typing import List
from sqlalchemy.orm import Mapped, relationship

from . import Base
from .mixins import TablenameMixin, TimestampMixin, StatusMixin, NamedEntityMixin

class Group(Base, TablenameMixin, TimestampMixin, StatusMixin, NamedEntityMixin):

    # Relationships
    group_users: Mapped[List["UserGroup"]] = relationship(
        back_populates="group",
        foreign_keys="[UserGroup.group_id]",
        lazy="selectin",
    )
    group_roles: Mapped[List["GroupRole"]] = relationship(
        back_populates="group",
        foreign_keys="[GroupRole.group_id]",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Group {self.name}>"
