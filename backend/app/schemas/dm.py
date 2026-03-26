from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel

from app.schemas.user import UserOut


class DmCreate(BaseModel):
    user_ids: list[uuid.UUID]


class DmParticipantAdd(BaseModel):
    user_id: uuid.UUID


class DmThreadOut(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    channel_id: uuid.UUID
    name: str | None
    created_at: datetime
    participants: list[DmParticipantOut] = []


class DmParticipantOut(BaseModel):
    model_config = {"from_attributes": True}

    dm_thread_id: uuid.UUID
    user_id: uuid.UUID
    joined_at: datetime
    user: UserOut
