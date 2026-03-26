from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.moderation import ActionType
from app.schemas.user import UserOut


class KickRequest(BaseModel):
    user_id: uuid.UUID
    reason: str | None = None


class BanRequest(BaseModel):
    user_id: uuid.UUID
    reason: str | None = None


class MuteRequest(BaseModel):
    user_id: uuid.UUID
    reason: str | None = None


class ModerationActionOut(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    guild_id: uuid.UUID
    actor_id: uuid.UUID | None
    target_id: uuid.UUID | None
    action_type: ActionType
    reason: str | None
    created_at: datetime


class GuildBanOut(BaseModel):
    model_config = {"from_attributes": True}

    guild_id: uuid.UUID
    user_id: uuid.UUID
    reason: str | None
    created_at: datetime
    user: UserOut | None = None
