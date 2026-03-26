from __future__ import annotations

import uuid

from fastapi import APIRouter
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.deps import CurrentUser, DbDep
from app.models.voice import VoiceSession

router = APIRouter(prefix="/voice", tags=["voice"])


@router.get("/channel/{channel_id}")
async def voice_participants(channel_id: uuid.UUID, db: DbDep, _: CurrentUser):
    result = await db.execute(
        select(VoiceSession)
        .where(VoiceSession.channel_id == channel_id)
        .options(selectinload(VoiceSession.user))
    )
    sessions = result.scalars().all()
    return [
        {
            "user_id": str(s.user_id),
            "joined_at": s.joined_at.isoformat(),
            "is_muted": s.is_muted,
            "is_deafened": s.is_deafened,
        }
        for s in sessions
    ]
