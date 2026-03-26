from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.deps import CurrentUser, DbDep
from app.models.guild import GuildMember
from app.models.invite import Invite
from app.schemas.invite import InviteCreate, InviteOut
from app.services.guild import require_member
from app.ws.events import WSEvent
from app.ws.manager import manager

router = APIRouter(prefix="/invites", tags=["invites"])


async def _get_invite_with_guild(db, code: str) -> Invite | None:
    result = await db.execute(
        select(Invite).where(Invite.code == code).options(selectinload(Invite.guild))
    )
    return result.scalar_one_or_none()


@router.post("/", response_model=InviteOut, status_code=status.HTTP_201_CREATED)
async def create_invite(body: InviteCreate, db: DbDep, current_user: CurrentUser):
    await require_member(db, body.guild_id, current_user.id)

    expires_at = None
    if body.expires_in:
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=body.expires_in)

    code = secrets.token_urlsafe(8)[:8]
    invite = Invite(
        code=code,
        guild_id=body.guild_id,
        channel_id=body.channel_id,
        creator_id=current_user.id,
        max_uses=body.max_uses,
        expires_at=expires_at,
    )
    db.add(invite)
    await db.commit()

    invite = await _get_invite_with_guild(db, code)
    out = InviteOut.model_validate(invite)
    await manager.broadcast_to_guild(body.guild_id, WSEvent.INVITE_CREATE, out.model_dump(mode="json"))
    return out


@router.get("/{code}", response_model=InviteOut)
async def get_invite(code: str, db: DbDep, _: CurrentUser):
    invite = await _get_invite_with_guild(db, code)
    if invite is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invite not found")
    if invite.expires_at and invite.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Invite has expired")
    return InviteOut.model_validate(invite)


@router.post("/{code}/accept", status_code=status.HTTP_200_OK)
async def accept_invite(code: str, db: DbDep, current_user: CurrentUser):
    result = await db.execute(select(Invite).where(Invite.code == code))
    invite = result.scalar_one_or_none()
    if invite is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invite not found")
    if invite.expires_at and invite.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Invite has expired")
    if invite.max_uses and invite.uses >= invite.max_uses:
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Invite has reached its max uses")

    # Check if already a member
    existing = await db.execute(
        select(GuildMember).where(GuildMember.guild_id == invite.guild_id, GuildMember.user_id == current_user.id)
    )
    if existing.scalar_one_or_none() is None:
        db.add(GuildMember(guild_id=invite.guild_id, user_id=current_user.id))
        invite.uses += 1
        await db.commit()

        await manager.broadcast_to_guild(
            invite.guild_id,
            WSEvent.GUILD_MEMBER_ADD,
            {"guild_id": str(invite.guild_id), "user_id": str(current_user.id)},
        )

    return {"guild_id": str(invite.guild_id)}


@router.delete("/{code}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_invite(code: str, db: DbDep, current_user: CurrentUser):
    result = await db.execute(select(Invite).where(Invite.code == code))
    invite = result.scalar_one_or_none()
    if invite is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invite not found")

    await require_member(db, invite.guild_id, current_user.id)
    await db.delete(invite)
    await db.commit()
    await manager.broadcast_to_guild(invite.guild_id, WSEvent.INVITE_DELETE, {"code": code})
