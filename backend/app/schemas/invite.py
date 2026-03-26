from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel

from app.schemas.guild import GuildOut


class InviteCreate(BaseModel):
    guild_id: uuid.UUID
    channel_id: uuid.UUID
    max_uses: int | None = None
    expires_in: int | None = None  # seconds


class InviteOut(BaseModel):
    model_config = {"from_attributes": True}

    code: str
    guild_id: uuid.UUID
    channel_id: uuid.UUID
    creator_id: uuid.UUID | None
    max_uses: int | None
    uses: int
    expires_at: datetime | None
    created_at: datetime
    guild: GuildOut | None = None
