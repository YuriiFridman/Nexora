from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.channel import ChannelType, OverwriteTargetType


class CategoryCreate(BaseModel):
    name: str
    position: int = 0


class CategoryUpdate(BaseModel):
    name: str | None = None
    position: int | None = None


class CategoryOut(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    guild_id: uuid.UUID
    name: str
    position: int
    created_at: datetime


class ChannelCreate(BaseModel):
    name: str
    type: ChannelType = ChannelType.text
    category_id: uuid.UUID | None = None
    position: int = 0
    topic: str | None = None
    is_nsfw: bool = False
    slowmode_delay: int = 0
    bitrate: int = 64000
    user_limit: int = 0


class ChannelUpdate(BaseModel):
    name: str | None = None
    category_id: uuid.UUID | None = None
    position: int | None = None
    topic: str | None = None
    is_nsfw: bool | None = None
    slowmode_delay: int | None = None
    bitrate: int | None = None
    user_limit: int | None = None


class ChannelOut(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    guild_id: uuid.UUID | None
    category_id: uuid.UUID | None
    name: str
    type: ChannelType
    position: int
    topic: str | None
    is_nsfw: bool
    created_at: datetime
    slowmode_delay: int = 0
    bitrate: int = 64000
    user_limit: int = 0
    parent_id: uuid.UUID | None = None


class OverwriteUpsert(BaseModel):
    target_type: OverwriteTargetType
    allow: int = 0
    deny: int = 0


class OverwriteOut(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    channel_id: uuid.UUID
    target_type: OverwriteTargetType
    target_id: uuid.UUID
    allow: int
    deny: int
