from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.guild import Guild, GuildMember
from app.models.role import Role
from app.models.user import User
from app.services.permissions import Permissions


async def get_guild_or_404(db: AsyncSession, guild_id: uuid.UUID) -> Guild:
    result = await db.execute(select(Guild).where(Guild.id == guild_id))
    guild = result.scalar_one_or_none()
    if guild is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guild not found")
    return guild


async def require_member(db: AsyncSession, guild_id: uuid.UUID, user_id: uuid.UUID) -> GuildMember:
    result = await db.execute(
        select(GuildMember).where(GuildMember.guild_id == guild_id, GuildMember.user_id == user_id)
    )
    member = result.scalar_one_or_none()
    if member is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a member of this guild")
    return member


async def require_permission(
    db: AsyncSession,
    guild: Guild,
    user: User,
    permission: int,
) -> None:
    """Raise 403 if the user lacks the given permission in the guild."""
    if guild.owner_id == user.id:
        return  # Owner has all permissions

    # Load member roles
    result = await db.execute(
        select(Role)
        .join(Role.member_roles)
        .where(
            Role.guild_id == guild.id,
        )
        .filter(
            Role.member_roles.any(user_id=user.id)  # type: ignore[attr-defined]
        )
    )
    roles = result.scalars().all()

    # Always include @everyone role
    everyone_result = await db.execute(
        select(Role).where(Role.guild_id == guild.id, Role.is_default == True)  # noqa: E712
    )
    everyone = everyone_result.scalar_one_or_none()

    combined = 0
    if everyone:
        combined |= everyone.permissions
    for role in roles:
        combined |= role.permissions

    if combined & Permissions.ADMINISTRATOR:
        return

    if not (combined & permission):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")


async def create_guild(db: AsyncSession, name: str, owner: User) -> Guild:
    guild = Guild(name=name, owner_id=owner.id)
    db.add(guild)
    await db.flush()

    # Create @everyone role
    everyone = Role(
        guild_id=guild.id,
        name="@everyone",
        permissions=Permissions.SEND_MESSAGES | Permissions.CONNECT | Permissions.SPEAK,
        is_default=True,
        position=0,
    )
    db.add(everyone)

    # Add owner as member
    member = GuildMember(guild_id=guild.id, user_id=owner.id)
    db.add(member)

    await db.commit()
    await db.refresh(guild)
    return guild
