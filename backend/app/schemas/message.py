from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel

from app.schemas.user import UserOut


class MessageCreate(BaseModel):
    content: str
    attachment_ids: list[uuid.UUID] = []


class MessageUpdate(BaseModel):
    content: str


class AttachmentOut(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    filename: str
    content_type: str
    size: int
    url: str
    created_at: datetime


class ReactionOut(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    message_id: uuid.UUID
    user_id: uuid.UUID
    emoji: str
    created_at: datetime


class MessageOut(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    channel_id: uuid.UUID
    author_id: uuid.UUID | None
    content: str
    is_edited: bool
    created_at: datetime
    updated_at: datetime
    attachments: list[AttachmentOut] = []
    reactions: list[ReactionOut] = []
    author: UserOut | None = None
