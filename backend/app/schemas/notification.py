from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel


class NotificationSettingOut(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    user_id: uuid.UUID
    level: str
    muted: bool
    created_at: datetime


class GuildNotificationSettingOut(NotificationSettingOut):
    guild_id: uuid.UUID


class ChannelNotificationSettingOut(NotificationSettingOut):
    channel_id: uuid.UUID


class NotificationSettingUpdate(BaseModel):
    level: str | None = None
    muted: bool | None = None
