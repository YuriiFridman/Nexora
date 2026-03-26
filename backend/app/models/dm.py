from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class DmThread(Base):
    __tablename__ = "dm_threads"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    channel_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("channels.id", ondelete="CASCADE"), nullable=False, unique=True)
    name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    channel: Mapped = relationship("Channel")
    participants: Mapped[list[DmParticipant]] = relationship("DmParticipant", back_populates="dm_thread", cascade="all, delete-orphan")


class DmParticipant(Base):
    __tablename__ = "dm_participants"

    dm_thread_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("dm_threads.id", ondelete="CASCADE"), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    dm_thread: Mapped[DmThread] = relationship("DmThread", back_populates="participants")
    user: Mapped = relationship("User")
