from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    guild_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("guilds.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    color: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    icon_emoji: Mapped[str | None] = mapped_column(String(32), nullable=True)
    hoist: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    mentionable: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    permissions: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    guild: Mapped = relationship("Guild", back_populates="roles")
    member_roles: Mapped[list[MemberRole]] = relationship(
        "MemberRole",
        back_populates="role",
        cascade="all, delete-orphan",
    )


class MemberRole(Base):
    __tablename__ = "member_roles"

    guild_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("guilds.id", ondelete="CASCADE"), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    role_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)

    role: Mapped[Role] = relationship("Role", back_populates="member_roles")
    member: Mapped = relationship(
        "GuildMember",
        foreign_keys=[guild_id, user_id],
        primaryjoin="and_(MemberRole.guild_id == GuildMember.guild_id, MemberRole.user_id == GuildMember.user_id)",
        back_populates="member_roles",
    )


class RoleAuditLog(Base):
    __tablename__ = "role_audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    guild_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("guilds.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid,
        ForeignKey("roles.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    actor_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    action: Mapped[str] = mapped_column(String(32), nullable=False)
    details: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
