from __future__ import annotations

import uuid

from fastapi import APIRouter, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.deps import CurrentUser, DbDep
from app.models.moderation import ActionType, GuildBan, ModerationAction
from app.schemas.moderation import BanRequest, GuildBanOut, KickRequest, ModerationActionOut, MuteRequest
from app.services.guild import get_guild_or_404, require_permission
from app.services.moderation import ban_member, kick_member, log_action, unban_member
from app.services.permissions import Permissions

router = APIRouter(tags=["moderation"])


@router.post("/guilds/{guild_id}/moderation/kick", status_code=status.HTTP_204_NO_CONTENT)
async def kick(guild_id: uuid.UUID, body: KickRequest, db: DbDep, current_user: CurrentUser):
    guild = await get_guild_or_404(db, guild_id)
    await require_permission(db, guild, current_user, Permissions.KICK_MEMBERS)
    await kick_member(db, guild, current_user, body.user_id, body.reason)


@router.post("/guilds/{guild_id}/moderation/ban", response_model=GuildBanOut, status_code=status.HTTP_201_CREATED)
async def ban(guild_id: uuid.UUID, body: BanRequest, db: DbDep, current_user: CurrentUser):
    guild = await get_guild_or_404(db, guild_id)
    await require_permission(db, guild, current_user, Permissions.BAN_MEMBERS)
    ban_record = await ban_member(db, guild, current_user, body.user_id, body.reason)
    return GuildBanOut.model_validate(ban_record)


@router.delete("/guilds/{guild_id}/moderation/ban/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unban(guild_id: uuid.UUID, user_id: uuid.UUID, db: DbDep, current_user: CurrentUser):
    guild = await get_guild_or_404(db, guild_id)
    await require_permission(db, guild, current_user, Permissions.BAN_MEMBERS)
    await unban_member(db, guild, current_user, user_id)


@router.get("/guilds/{guild_id}/moderation/bans", response_model=list[GuildBanOut])
async def list_bans(guild_id: uuid.UUID, db: DbDep, current_user: CurrentUser):
    guild = await get_guild_or_404(db, guild_id)
    await require_permission(db, guild, current_user, Permissions.BAN_MEMBERS)
    result = await db.execute(
        select(GuildBan).where(GuildBan.guild_id == guild_id).options(selectinload(GuildBan.user))
    )
    return [GuildBanOut.model_validate(b) for b in result.scalars().all()]


@router.post("/guilds/{guild_id}/moderation/mute", status_code=status.HTTP_204_NO_CONTENT)
async def mute(guild_id: uuid.UUID, body: MuteRequest, db: DbDep, current_user: CurrentUser):
    """Records a mute moderation action. In a full implementation this would assign a muted role."""
    guild = await get_guild_or_404(db, guild_id)
    await require_permission(db, guild, current_user, Permissions.MUTE_MEMBERS)
    await log_action(db, guild_id, current_user.id, ActionType.mute, body.user_id, body.reason)
    await db.commit()


@router.get("/guilds/{guild_id}/moderation/audit-log", response_model=list[ModerationActionOut])
async def audit_log(
    guild_id: uuid.UUID,
    db: DbDep,
    current_user: CurrentUser,
    limit: int = 50,
    before: uuid.UUID | None = None,
):
    guild = await get_guild_or_404(db, guild_id)
    await require_permission(db, guild, current_user, Permissions.VIEW_AUDIT_LOG)

    query = (
        select(ModerationAction)
        .where(ModerationAction.guild_id == guild_id)
        .order_by(ModerationAction.created_at.desc())
        .limit(min(limit, 100))
    )
    if before:
        subq = select(ModerationAction.created_at).where(ModerationAction.id == before).scalar_subquery()
        query = query.where(ModerationAction.created_at < subq)

    result = await db.execute(query)
    return [ModerationActionOut.model_validate(a) for a in result.scalars().all()]
