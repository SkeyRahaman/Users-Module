from typing import TYPE_CHECKING
from datetime import datetime, timezone
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.models.mixins import TokenMetadataMixin
from . import Base

if TYPE_CHECKING:
    from . import User

class RefreshToken(TokenMetadataMixin, Base):
    __tablename__ = "refresh_tokens"

    refresh_token_hash: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    client_info: Mapped[str | None] = mapped_column(String(256), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="refresh_tokens", lazy="selectin")


    def is_expired(self):
        return datetime.now(timezone.utc) >= self.expires_at

    def is_active(self) -> bool:
        return not self.revoked and not self.used and not self.is_expired()
