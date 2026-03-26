from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Guild(Base):
    __tablename__ = "guilds"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    owner_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    icon_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    owner: Mapped = relationship("User", foreign_keys=[owner_id])
    members: Mapped[list[GuildMember]] = relationship("GuildMember", back_populates="guild", cascade="all, delete-orphan")
    roles: Mapped[list] = relationship("Role", back_populates="guild", cascade="all, delete-orphan")
    channels: Mapped[list] = relationship("Channel", back_populates="guild", cascade="all, delete-orphan")
    categories: Mapped[list] = relationship("Category", back_populates="guild", cascade="all, delete-orphan")
    invites: Mapped[list] = relationship("Invite", back_populates="guild", cascade="all, delete-orphan")
    bans: Mapped[list] = relationship("GuildBan", back_populates="guild", cascade="all, delete-orphan")


class GuildMember(Base):
    __tablename__ = "guild_members"

    guild_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("guilds.id", ondelete="CASCADE"), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    nickname: Mapped[str | None] = mapped_column(String(128), nullable=True)

    guild: Mapped[Guild] = relationship("Guild", back_populates="members")
    user: Mapped = relationship("User", back_populates="guild_memberships")
    member_roles: Mapped[list] = relationship("MemberRole", back_populates="member", cascade="all, delete-orphan",
                                               primaryjoin="and_(GuildMember.guild_id == foreign(MemberRole.guild_id), "
                                                           "GuildMember.user_id == foreign(MemberRole.user_id))")
