from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class PermissionEntry(BaseModel):
    key: str
    label: str
    description: str
    value: int
    category: str
    critical: bool = False


class RoleCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    color: int = Field(default=0, ge=0, le=0xFFFFFF)
    icon_emoji: str | None = Field(default=None, max_length=32)
    hoist: bool = False
    mentionable: bool = False
    position: int = 0
    permissions: int = 0


class RoleUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    color: int | None = Field(default=None, ge=0, le=0xFFFFFF)
    icon_emoji: str | None = Field(default=None, max_length=32)
    hoist: bool | None = None
    mentionable: bool | None = None
    position: int | None = None
    permissions: int | None = None


class RoleOut(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    guild_id: uuid.UUID
    name: str
    color: int
    icon_emoji: str | None
    hoist: bool
    mentionable: bool
    position: int
    permissions: int
    is_default: bool
    created_at: datetime


class MemberRoleOut(BaseModel):
    model_config = {"from_attributes": True}

    guild_id: uuid.UUID
    user_id: uuid.UUID
    role_id: uuid.UUID


class RoleReorderItem(BaseModel):
    role_id: uuid.UUID
    position: int = Field(ge=0)


class RoleReorderPayload(BaseModel):
    items: list[RoleReorderItem]


class RoleBulkAssignPayload(BaseModel):
    role_id: uuid.UUID
    user_ids: list[uuid.UUID]


class RoleTemplateCreate(BaseModel):
    template: str
    name: str | None = Field(default=None, min_length=1, max_length=100)
    position: int = Field(default=0, ge=0)


class RoleAuditLogOut(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    guild_id: uuid.UUID
    role_id: uuid.UUID | None
    actor_id: uuid.UUID
    action: str
    details: str | None
    created_at: datetime
