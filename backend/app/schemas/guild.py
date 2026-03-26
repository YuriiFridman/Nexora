from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel

from app.schemas.user import UserOut


class GuildCreate(BaseModel):
    name: str


class GuildUpdate(BaseModel):
    name: str | None = None
    icon_url: str | None = None


class GuildOut(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    name: str
    owner_id: uuid.UUID
    icon_url: str | None
    created_at: datetime


class GuildMemberOut(BaseModel):
    model_config = {"from_attributes": True}

    guild_id: uuid.UUID
    user_id: uuid.UUID
    joined_at: datetime
    nickname: str | None
    user: UserOut
