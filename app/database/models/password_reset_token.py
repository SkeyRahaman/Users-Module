from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from . import Base

if TYPE_CHECKING:
    from . import User


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    
    user: Mapped["User"] = relationship("User", back_populates="password_reset_tokens", lazy="selectin")

    def is_expired(self) -> bool:
        return datetime.now() > self.expires_at
    
    def __repr__(self) -> str:
        return f"<PasswordResetToken {self.user.username}>"

    @classmethod
    def create_expiration(cls, hours: int = 1) -> datetime:
        return datetime.now(timezone.utc) + timedelta(hours=hours)
