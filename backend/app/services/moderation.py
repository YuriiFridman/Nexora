from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.guild import Guild, GuildMember
from app.models.moderation import ActionType, GuildBan, ModerationAction
from app.models.user import User
from app.ws.events import WSEvent
from app.ws.manager import manager


async def log_action(
    db: AsyncSession,
    guild_id: uuid.UUID,
    actor_id: uuid.UUID,
    action_type: ActionType,
    target_id: uuid.UUID | None = None,
    reason: str | None = None,
) -> ModerationAction:
    action = ModerationAction(
        guild_id=guild_id,
        actor_id=actor_id,
        target_id=target_id,
        action_type=action_type,
        reason=reason,
    )
    db.add(action)
    await db.flush()
    return action


async def kick_member(
    db: AsyncSession,
    guild: Guild,
    actor: User,
    target_id: uuid.UUID,
    reason: str | None,
) -> None:
    result = await db.execute(
        select(GuildMember).where(GuildMember.guild_id == guild.id, GuildMember.user_id == target_id)
    )
    member = result.scalar_one_or_none()
    if member is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
    if target_id == guild.owner_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot kick the guild owner")
    await db.delete(member)
    await log_action(db, guild.id, actor.id, ActionType.kick, target_id, reason)
    await db.commit()
    await manager.broadcast_to_guild(
        guild.id,
        WSEvent.GUILD_MEMBER_REMOVE,
        {"guild_id": str(guild.id), "user_id": str(target_id)},
    )


async def ban_member(
    db: AsyncSession,
    guild: Guild,
    actor: User,
    target_id: uuid.UUID,
    reason: str | None,
) -> GuildBan:
    if target_id == guild.owner_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot ban the guild owner")

    # Remove from members if present
    result = await db.execute(
        select(GuildMember).where(GuildMember.guild_id == guild.id, GuildMember.user_id == target_id)
    )
    member = result.scalar_one_or_none()
    if member:
        await db.delete(member)

    # Upsert ban
    ban_result = await db.execute(
        select(GuildBan).where(GuildBan.guild_id == guild.id, GuildBan.user_id == target_id)
    )
    ban = ban_result.scalar_one_or_none()
    if ban is None:
        ban = GuildBan(guild_id=guild.id, user_id=target_id, reason=reason)
        db.add(ban)

    await log_action(db, guild.id, actor.id, ActionType.ban, target_id, reason)
    await db.commit()
    await db.refresh(ban)
    if member:
        await manager.broadcast_to_guild(
            guild.id,
            WSEvent.GUILD_MEMBER_REMOVE,
            {"guild_id": str(guild.id), "user_id": str(target_id)},
        )
    return ban


async def unban_member(
    db: AsyncSession,
    guild: Guild,
    actor: User,
    target_id: uuid.UUID,
) -> None:
    result = await db.execute(
        select(GuildBan).where(GuildBan.guild_id == guild.id, GuildBan.user_id == target_id)
    )
    ban = result.scalar_one_or_none()
    if ban is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ban not found")
    await db.delete(ban)
    await log_action(db, guild.id, actor.id, ActionType.unban, target_id)
    await db.commit()
