from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel


class WebhookOut(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    guild_id: uuid.UUID
    channel_id: uuid.UUID
    creator_id: uuid.UUID | None
    name: str
    avatar_url: str | None
    created_at: datetime


class WebhookCreate(BaseModel):
    channel_id: uuid.UUID
    name: str
    avatar_url: str | None = None


class WebhookUpdate(BaseModel):
    name: str | None = None
    avatar_url: str | None = None


class WebhookExecute(BaseModel):
    content: str
    username: str | None = None
    avatar_url: str | None = None
