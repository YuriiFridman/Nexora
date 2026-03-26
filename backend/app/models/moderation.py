from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ActionType(str, enum.Enum):
    kick = "kick"
    ban = "ban"
    unban = "unban"
    mute = "mute"
    unmute = "unmute"
    warn = "warn"
    timeout = "timeout"


class ModerationAction(Base):
    __tablename__ = "moderation_actions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    guild_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("guilds.id", ondelete="CASCADE"), nullable=False, index=True)
    actor_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    target_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action_type: Mapped[ActionType] = mapped_column(Enum(ActionType), nullable=False)
    reason: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    guild: Mapped = relationship("Guild")
    actor: Mapped = relationship("User", foreign_keys=[actor_id])
    target: Mapped = relationship("User", foreign_keys=[target_id])


class GuildBan(Base):
    __tablename__ = "guild_bans"

    guild_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("guilds.id", ondelete="CASCADE"), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    reason: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    guild: Mapped = relationship("Guild", back_populates="bans")
    user: Mapped = relationship("User")
