from __future__ import annotations

import uuid

from fastapi import APIRouter, status
from sqlalchemy import select

from app.deps import CurrentUser, DbDep
from app.models.notification import ChannelNotificationSetting, GuildNotificationSetting, NotificationLevel
from app.schemas.notification import ChannelNotificationSettingOut, GuildNotificationSettingOut, NotificationSettingUpdate
from app.services.channel import get_channel_or_404
from app.services.guild import get_guild_or_404

router = APIRouter(tags=["notifications"])


@router.get("/guilds/{guild_id}/notification-settings", response_model=GuildNotificationSettingOut)
async def get_guild_notification_settings(guild_id: uuid.UUID, db: DbDep, current_user: CurrentUser):
    await get_guild_or_404(db, guild_id)
    result = await db.execute(
        select(GuildNotificationSetting).where(
            GuildNotificationSetting.user_id == current_user.id,
            GuildNotificationSetting.guild_id == guild_id,
        )
    )
    setting = result.scalar_one_or_none()
    if setting is None:
        setting = GuildNotificationSetting(user_id=current_user.id, guild_id=guild_id)
        db.add(setting)
        await db.commit()
        await db.refresh(setting)
    return GuildNotificationSettingOut.model_validate(setting)


@router.put("/guilds/{guild_id}/notification-settings", response_model=GuildNotificationSettingOut)
async def update_guild_notification_settings(guild_id: uuid.UUID, body: NotificationSettingUpdate, db: DbDep, current_user: CurrentUser):
    await get_guild_or_404(db, guild_id)
    result = await db.execute(
        select(GuildNotificationSetting).where(
            GuildNotificationSetting.user_id == current_user.id,
            GuildNotificationSetting.guild_id == guild_id,
        )
    )
    setting = result.scalar_one_or_none()
    if setting is None:
        setting = GuildNotificationSetting(user_id=current_user.id, guild_id=guild_id)
        db.add(setting)

    if body.level is not None:
        setting.level = NotificationLevel(body.level)
    if body.muted is not None:
        setting.muted = body.muted

    await db.commit()
    await db.refresh(setting)
    return GuildNotificationSettingOut.model_validate(setting)


@router.get("/channels/{channel_id}/notification-settings", response_model=ChannelNotificationSettingOut)
async def get_channel_notification_settings(channel_id: uuid.UUID, db: DbDep, current_user: CurrentUser):
    await get_channel_or_404(db, channel_id)
    result = await db.execute(
        select(ChannelNotificationSetting).where(
            ChannelNotificationSetting.user_id == current_user.id,
            ChannelNotificationSetting.channel_id == channel_id,
        )
    )
    setting = result.scalar_one_or_none()
    if setting is None:
        setting = ChannelNotificationSetting(user_id=current_user.id, channel_id=channel_id)
        db.add(setting)
        await db.commit()
        await db.refresh(setting)
    return ChannelNotificationSettingOut.model_validate(setting)


@router.put("/channels/{channel_id}/notification-settings", response_model=ChannelNotificationSettingOut)
async def update_channel_notification_settings(channel_id: uuid.UUID, body: NotificationSettingUpdate, db: DbDep, current_user: CurrentUser):
    await get_channel_or_404(db, channel_id)
    result = await db.execute(
        select(ChannelNotificationSetting).where(
            ChannelNotificationSetting.user_id == current_user.id,
            ChannelNotificationSetting.channel_id == channel_id,
        )
    )
    setting = result.scalar_one_or_none()
    if setting is None:
        setting = ChannelNotificationSetting(user_id=current_user.id, channel_id=channel_id)
        db.add(setting)

    if body.level is not None:
        setting.level = NotificationLevel(body.level)
    if body.muted is not None:
        setting.muted = body.muted

    await db.commit()
    await db.refresh(setting)
    return ChannelNotificationSettingOut.model_validate(setting)
