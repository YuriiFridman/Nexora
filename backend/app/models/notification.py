from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class NotificationLevel(str, enum.Enum):
    all_messages = "all_messages"
    only_mentions = "only_mentions"
    nothing = "nothing"
    default = "default"


class GuildNotificationSetting(Base):
    __tablename__ = "guild_notification_settings"
    __table_args__ = (UniqueConstraint("user_id", "guild_id"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    guild_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("guilds.id", ondelete="CASCADE"), nullable=False, index=True)
    level: Mapped[NotificationLevel] = mapped_column(Enum(NotificationLevel), default=NotificationLevel.default, nullable=False)
    muted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)


class ChannelNotificationSetting(Base):
    __tablename__ = "channel_notification_settings"
    __table_args__ = (UniqueConstraint("user_id", "channel_id"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    channel_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("channels.id", ondelete="CASCADE"), nullable=False, index=True)
    level: Mapped[NotificationLevel] = mapped_column(Enum(NotificationLevel), default=NotificationLevel.default, nullable=False)
    muted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
