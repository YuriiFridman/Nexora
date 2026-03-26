from __future__ import annotations

import secrets
import uuid

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.deps import CurrentUser, DbDep
from app.models.webhook import Webhook
from app.schemas.webhook import WebhookCreate, WebhookExecute, WebhookOut, WebhookUpdate
from app.services.channel import get_channel_or_404
from app.services.guild import get_guild_or_404, require_member
from app.ws.events import WSEvent
from app.ws.manager import manager

router = APIRouter(tags=["webhooks"])


@router.get("/guilds/{guild_id}/webhooks", response_model=list[WebhookOut])
async def list_guild_webhooks(guild_id: uuid.UUID, db: DbDep, current_user: CurrentUser):
    await require_member(db, guild_id, current_user.id)
    result = await db.execute(select(Webhook).where(Webhook.guild_id == guild_id))
    return [WebhookOut.model_validate(w) for w in result.scalars().all()]


@router.post("/guilds/{guild_id}/webhooks", response_model=WebhookOut, status_code=status.HTTP_201_CREATED)
async def create_webhook(guild_id: uuid.UUID, body: WebhookCreate, db: DbDep, current_user: CurrentUser):
    await require_member(db, guild_id, current_user.id)
    channel = await get_channel_or_404(db, body.channel_id)
    if channel.guild_id != guild_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Channel does not belong to this guild")

    token = secrets.token_urlsafe(96)
    webhook = Webhook(
        guild_id=guild_id,
        channel_id=body.channel_id,
        creator_id=current_user.id,
        name=body.name,
        token=token,
        avatar_url=body.avatar_url,
    )
    db.add(webhook)
    await db.commit()
    await db.refresh(webhook)

    payload = WebhookOut.model_validate(webhook).model_dump(mode="json")
    await manager.broadcast_to_guild(guild_id, WSEvent.WEBHOOK_CREATE, payload)

    return WebhookOut.model_validate(webhook)


@router.get("/webhooks/{webhook_id}", response_model=WebhookOut)
async def get_webhook(webhook_id: uuid.UUID, db: DbDep, current_user: CurrentUser):
    result = await db.execute(select(Webhook).where(Webhook.id == webhook_id))
    webhook = result.scalar_one_or_none()
    if webhook is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Webhook not found")
    await require_member(db, webhook.guild_id, current_user.id)
    return WebhookOut.model_validate(webhook)


@router.patch("/webhooks/{webhook_id}", response_model=WebhookOut)
async def update_webhook(webhook_id: uuid.UUID, body: WebhookUpdate, db: DbDep, current_user: CurrentUser):
    result = await db.execute(select(Webhook).where(Webhook.id == webhook_id))
    webhook = result.scalar_one_or_none()
    if webhook is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Webhook not found")
    await require_member(db, webhook.guild_id, current_user.id)

    if body.name is not None:
        webhook.name = body.name
    if body.avatar_url is not None:
        webhook.avatar_url = body.avatar_url
    await db.commit()
    await db.refresh(webhook)
    return WebhookOut.model_validate(webhook)


@router.delete("/webhooks/{webhook_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_webhook(webhook_id: uuid.UUID, db: DbDep, current_user: CurrentUser):
    result = await db.execute(select(Webhook).where(Webhook.id == webhook_id))
    webhook = result.scalar_one_or_none()
    if webhook is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Webhook not found")
    await require_member(db, webhook.guild_id, current_user.id)
    await db.delete(webhook)
    await db.commit()


@router.post("/webhooks/{webhook_id}/{webhook_token}", status_code=status.HTTP_204_NO_CONTENT)
async def execute_webhook(webhook_id: uuid.UUID, webhook_token: str, body: WebhookExecute, db: DbDep):
    result = await db.execute(select(Webhook).where(Webhook.id == webhook_id, Webhook.token == webhook_token))
    webhook = result.scalar_one_or_none()
    if webhook is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Webhook not found")

    from app.models.message import Message

    display_name = body.username or webhook.name
    msg = Message(
        channel_id=webhook.channel_id,
        author_id=None,
        content=body.content,
    )
    db.add(msg)
    await db.commit()

    from app.schemas.message import MessageOut
    from app.services.message import get_message_or_404

    msg = await get_message_or_404(db, msg.id)
    payload = MessageOut.model_validate(msg).model_dump(mode="json")
    payload["webhook_name"] = display_name
    if body.avatar_url:
        payload["webhook_avatar_url"] = body.avatar_url

    await manager.broadcast_to_guild(webhook.guild_id, WSEvent.MESSAGE_CREATE, payload)
