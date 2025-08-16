from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base
from .mixins import TimestampMixin, StatusMixin, TablenameMixin
if TYPE_CHECKING:
    from . import UserRole, UserGroup

class User(Base, TablenameMixin, TimestampMixin, StatusMixin):

    # User's data
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    firstname: Mapped[str] = mapped_column(String(50), nullable=False)
    middlename: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    lastname: Mapped[str] = mapped_column(String(50), nullable=False)
    username: Mapped[str] = mapped_column(String(30), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)

    # Status flags
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    user_roles: Mapped[List["UserRole"]] = relationship(
        back_populates="user",
        foreign_keys="[UserRole.user_id]",
        lazy="selectin"
    )
    user_groups: Mapped[List["UserGroup"]] = relationship(
        back_populates="user",
        foreign_keys="[UserGroup.user_id]",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<User {self.username}>"
