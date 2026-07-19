from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import Mapped, relationship, mapped_column

from app.database.models.mixins import TokenMetadataMixin
from . import Base

if TYPE_CHECKING:
    from . import User


class PasswordResetToken(Base, TokenMetadataMixin):
    __tablename__ = "password_reset_tokens"

    token_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    user: Mapped["User"] = relationship("User", back_populates="password_reset_tokens", lazy="selectin")

    def is_expired(self):
        now = datetime.now(timezone.utc)
        expires_at = self.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        return now >= expires_at
    
    def __repr__(self) -> str:
        return f"<PasswordResetToken {self.user.username}>"

    @classmethod
    def create_expiration(cls, hours: int = 1) -> datetime:
        return datetime.now(timezone.utc) + timedelta(hours=hours)
