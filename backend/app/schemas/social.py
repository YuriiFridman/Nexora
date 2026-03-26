from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel

from app.schemas.user import UserOut


class FriendRequestOut(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    sender_id: uuid.UUID
    receiver_id: uuid.UUID
    status: str
    created_at: datetime
    sender: UserOut | None = None
    receiver: UserOut | None = None


class FriendRequestCreate(BaseModel):
    receiver_id: uuid.UUID
