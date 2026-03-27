from __future__ import annotations

import uuid

from fastapi import APIRouter, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.deps import CurrentUser, DbDep
from app.models.moderation import ActionType, GuildBan, ModerationAction
from app.models.role import MemberRole, Role
from app.schemas.moderation import BanRequest, GuildBanOut, KickRequest, ModerationActionOut, MuteRequest
from app.services.guild import get_guild_or_404, require_member, require_permission
from app.services.moderation import ban_member, kick_member, log_action, unban_member
from app.services.permissions import Permissions
from app.ws.events import WSEvent
from app.ws.manager import manager

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
    """Mutes a member by assigning the guild's Muted role (creating it if needed)."""
    guild = await get_guild_or_404(db, guild_id)
    await require_permission(db, guild, current_user, Permissions.MUTE_MEMBERS)
    await require_member(db, guild_id, body.user_id)

    # Find or create the "Muted" role for this guild
    muted_role_result = await db.execute(
        select(Role).where(Role.guild_id == guild_id, Role.name == "Muted")
    )
    muted_role = muted_role_result.scalar_one_or_none()
    if muted_role is None:
        muted_role = Role(
            guild_id=guild_id,
            name="Muted",
            permissions=0,  # No permissions — cannot send messages
            color=0x808080,
            hoist=False,
        )
        db.add(muted_role)
        await db.flush()

    # Assign the role to the target user if not already assigned
    existing_mr = await db.execute(
        select(MemberRole).where(
            MemberRole.guild_id == guild_id,
            MemberRole.user_id == body.user_id,
            MemberRole.role_id == muted_role.id,
        )
    )
    if existing_mr.scalar_one_or_none() is None:
        db.add(MemberRole(guild_id=guild_id, user_id=body.user_id, role_id=muted_role.id))

    await log_action(db, guild_id, current_user.id, ActionType.mute, body.user_id, body.reason)
    await db.commit()

    await manager.broadcast_to_guild(
        guild_id,
        WSEvent.GUILD_MEMBER_UPDATE,
        {"guild_id": str(guild_id), "user_id": str(body.user_id), "muted": True},
    )


@router.delete("/guilds/{guild_id}/moderation/mute/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unmute(guild_id: uuid.UUID, user_id: uuid.UUID, db: DbDep, current_user: CurrentUser):
    """Removes the Muted role from a guild member."""
    guild = await get_guild_or_404(db, guild_id)
    await require_permission(db, guild, current_user, Permissions.MUTE_MEMBERS)

    muted_role_result = await db.execute(
        select(Role).where(Role.guild_id == guild_id, Role.name == "Muted")
    )
    muted_role = muted_role_result.scalar_one_or_none()
    if muted_role:
        mr_result = await db.execute(
            select(MemberRole).where(
                MemberRole.guild_id == guild_id,
                MemberRole.user_id == user_id,
                MemberRole.role_id == muted_role.id,
            )
        )
        mr = mr_result.scalar_one_or_none()
        if mr:
            await db.delete(mr)

    await log_action(db, guild_id, current_user.id, ActionType.unmute, user_id)
    await db.commit()

    await manager.broadcast_to_guild(
        guild_id,
        WSEvent.GUILD_MEMBER_UPDATE,
        {"guild_id": str(guild_id), "user_id": str(user_id), "muted": False},
    )


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
