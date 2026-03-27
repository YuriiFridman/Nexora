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
    combined = await get_user_permissions_mask(db, guild, user.id)
    if not (combined & permission):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")


async def get_user_permissions_mask(db: AsyncSession, guild: Guild, user_id: uuid.UUID) -> int:
    if guild.owner_id == user_id:
        return Permissions.all()

    result = await db.execute(
        select(Role)
        .join(Role.member_roles)
        .where(
            Role.guild_id == guild.id,
        )
        .filter(
            Role.member_roles.any(user_id=user_id)  # type: ignore[attr-defined]
        )
    )
    roles = result.scalars().all()

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
        return Permissions.all()
    return combined


async def get_user_top_role_position(db: AsyncSession, guild_id: uuid.UUID, user_id: uuid.UUID) -> int:
    """Get highest role position user can control in guild."""
    guild_result = await db.execute(select(Guild).where(Guild.id == guild_id))
    guild = guild_result.scalar_one_or_none()
    if guild is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guild not found")

    if guild.owner_id == user_id:
        return 10**9

    everyone_result = await db.execute(select(Role).where(Role.guild_id == guild_id, Role.is_default == True))  # noqa: E712
    everyone = everyone_result.scalar_one_or_none()
    top = everyone.position if everyone else 0

    result = await db.execute(
        select(Role)
        .join(Role.member_roles)
        .where(Role.guild_id == guild_id)
        .filter(Role.member_roles.any(user_id=user_id))  # type: ignore[attr-defined]
    )
    for role in result.scalars().all():
        if role.position > top:
            top = role.position
    return top


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
