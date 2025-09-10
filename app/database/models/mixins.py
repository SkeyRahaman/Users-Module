from sqlalchemy.orm import Mapped, mapped_column, declared_attr, relationship
from sqlalchemy import Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from typing import Optional, TYPE_CHECKING
from datetime import datetime, timezone

if TYPE_CHECKING:
    from . import User

class TablenameMixin:
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + "s" 

class NamedEntityMixin:
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

class TimestampMixin:
    created: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

class StatusMixin:
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)

class AuditMixin:
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    created_by: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    @declared_attr
    def creator(cls) -> Mapped[Optional["User"]]:
        return relationship(
            "User",
            foreign_keys=[cls.created_by],
            lazy="selectin",
        )
    
class ValidityMixin:
    valid_from: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)
    valid_until: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)

class TokenMetadataMixin:
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
