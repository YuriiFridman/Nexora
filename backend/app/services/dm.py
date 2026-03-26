from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.channel import Channel, ChannelType
from app.models.dm import DmParticipant, DmThread


async def get_dm_or_404(db: AsyncSession, dm_id: uuid.UUID, user_id: uuid.UUID) -> DmThread:
    result = await db.execute(
        select(DmThread)
        .where(DmThread.id == dm_id)
        .options(selectinload(DmThread.participants))
    )
    dm = result.scalar_one_or_none()
    if dm is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="DM thread not found")
    participant_ids = [p.user_id for p in dm.participants]
    if user_id not in participant_ids:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a participant")
    return dm


async def create_dm(db: AsyncSession, initiator_id: uuid.UUID, user_ids: list[uuid.UUID]) -> DmThread:
    all_ids = list({initiator_id, *user_ids})
    channel_type = ChannelType.dm if len(all_ids) == 2 else ChannelType.group_dm

    channel = Channel(type=channel_type, name="dm", position=0)
    db.add(channel)
    await db.flush()

    dm = DmThread(channel_id=channel.id)
    db.add(dm)
    await db.flush()

    for uid in all_ids:
        db.add(DmParticipant(dm_thread_id=dm.id, user_id=uid))

    await db.commit()
    await db.refresh(dm)
    return dm
