from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.channel import Channel, ChannelOverwrite, OverwriteTargetType


async def get_channel_or_404(db: AsyncSession, channel_id: uuid.UUID) -> Channel:
    result = await db.execute(select(Channel).where(Channel.id == channel_id))
    channel = result.scalar_one_or_none()
    if channel is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")
    return channel


async def upsert_overwrite(
    db: AsyncSession,
    channel_id: uuid.UUID,
    target_id: uuid.UUID,
    target_type: OverwriteTargetType,
    allow: int,
    deny: int,
) -> ChannelOverwrite:
    result = await db.execute(
        select(ChannelOverwrite).where(
            ChannelOverwrite.channel_id == channel_id,
            ChannelOverwrite.target_id == target_id,
        )
    )
    overwrite = result.scalar_one_or_none()
    if overwrite is None:
        overwrite = ChannelOverwrite(
            channel_id=channel_id,
            target_id=target_id,
            target_type=target_type,
            allow=allow,
            deny=deny,
        )
        db.add(overwrite)
    else:
        overwrite.allow = allow
        overwrite.deny = deny
    await db.commit()
    await db.refresh(overwrite)
    return overwrite
