from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import BigInteger, Boolean, DateTime, Enum, ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ChannelType(str, enum.Enum):
    text = "text"
    voice = "voice"
    dm = "dm"
    group_dm = "group_dm"


class OverwriteTargetType(str, enum.Enum):
    role = "role"
    member = "member"


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    guild_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("guilds.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    guild: Mapped = relationship("Guild", back_populates="categories")
    channels: Mapped[list[Channel]] = relationship("Channel", back_populates="category")


class Channel(Base):
    __tablename__ = "channels"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    guild_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("guilds.id", ondelete="CASCADE"), nullable=True, index=True)
    category_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[ChannelType] = mapped_column(Enum(ChannelType), nullable=False, default=ChannelType.text)
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    topic: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    is_nsfw: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    guild: Mapped = relationship("Guild", back_populates="channels")
    category: Mapped[Category | None] = relationship("Category", back_populates="channels")
    messages: Mapped[list] = relationship("Message", back_populates="channel", cascade="all, delete-orphan")
    overwrites: Mapped[list[ChannelOverwrite]] = relationship("ChannelOverwrite", back_populates="channel", cascade="all, delete-orphan")
    voice_sessions: Mapped[list] = relationship("VoiceSession", back_populates="channel", cascade="all, delete-orphan")


class ChannelOverwrite(Base):
    __tablename__ = "channel_overwrites"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    channel_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("channels.id", ondelete="CASCADE"), nullable=False, index=True)
    target_type: Mapped[OverwriteTargetType] = mapped_column(Enum(OverwriteTargetType), nullable=False)
    target_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    allow: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    deny: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)

    channel: Mapped[Channel] = relationship("Channel", back_populates="overwrites")
