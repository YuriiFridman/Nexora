from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel


class UserOut(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    username: str
    email: str
    display_name: str
    avatar_url: str | None
    is_active: bool
    created_at: datetime
    status: str = "offline"
    custom_status: str | None = None
    bio: str | None = None


class UserUpdateRequest(BaseModel):
    display_name: str | None = None
    avatar_url: str | None = None
    status: str | None = None
    custom_status: str | None = None
    bio: str | None = None
