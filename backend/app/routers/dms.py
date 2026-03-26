from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.deps import CurrentUser, DbDep
from app.models.dm import DmParticipant, DmThread
from app.models.message import Message
from app.schemas.dm import DmCreate, DmParticipantAdd, DmThreadOut
from app.schemas.message import MessageCreate, MessageOut
from app.services.dm import create_dm, get_dm_or_404
from app.services.message import get_message_or_404, list_messages
from app.ws.events import WSEvent
from app.ws.manager import manager

router = APIRouter(prefix="/dms", tags=["dms"])


@router.get("/", response_model=list[DmThreadOut])
async def list_dms(db: DbDep, current_user: CurrentUser):
    result = await db.execute(
        select(DmThread)
        .join(DmParticipant, DmParticipant.dm_thread_id == DmThread.id)
        .where(DmParticipant.user_id == current_user.id)
        .options(selectinload(DmThread.participants).selectinload(DmParticipant.user))
    )
    return [DmThreadOut.model_validate(dm) for dm in result.scalars().all()]


@router.post("/", response_model=DmThreadOut, status_code=status.HTTP_201_CREATED)
async def create_dm_endpoint(body: DmCreate, db: DbDep, current_user: CurrentUser):
    dm = await create_dm(db, current_user.id, body.user_ids)
    result = await db.execute(
        select(DmThread).where(DmThread.id == dm.id).options(selectinload(DmThread.participants).selectinload(DmParticipant.user))
    )
    dm = result.scalar_one()
    out = DmThreadOut.model_validate(dm)
    for p in dm.participants:
        await manager.send_to_user(p.user_id, WSEvent.DM_THREAD_CREATE, out.model_dump(mode="json"))
    return out


@router.get("/{dm_id}/messages", response_model=list[MessageOut])
async def list_dm_messages(
    dm_id: uuid.UUID,
    db: DbDep,
    current_user: CurrentUser,
    before: uuid.UUID | None = None,
    limit: int = 50,
):
    dm = await get_dm_or_404(db, dm_id, current_user.id)
    msgs = await list_messages(db, dm.channel_id, before=before, limit=min(limit, 100))
    return [MessageOut.model_validate(m) for m in msgs]


@router.post("/{dm_id}/messages", response_model=MessageOut, status_code=status.HTTP_201_CREATED)
async def send_dm_message(dm_id: uuid.UUID, body: MessageCreate, db: DbDep, current_user: CurrentUser):
    dm = await get_dm_or_404(db, dm_id, current_user.id)

    msg = Message(channel_id=dm.channel_id, author_id=current_user.id, content=body.content)
    db.add(msg)
    await db.flush()
    await db.commit()
    msg = await get_message_or_404(db, msg.id)

    out = MessageOut.model_validate(msg)
    await manager.broadcast_to_dm(dm_id, WSEvent.DM_MESSAGE_CREATE, out.model_dump(mode="json"))
    return out


@router.post("/{dm_id}/participants", status_code=status.HTTP_201_CREATED)
async def add_participant(dm_id: uuid.UUID, body: DmParticipantAdd, db: DbDep, current_user: CurrentUser):
    await get_dm_or_404(db, dm_id, current_user.id)
    existing = await db.execute(
        select(DmParticipant).where(DmParticipant.dm_thread_id == dm_id, DmParticipant.user_id == body.user_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already a participant")

    db.add(DmParticipant(dm_thread_id=dm_id, user_id=body.user_id))
    await db.commit()
    return {"dm_thread_id": str(dm_id), "user_id": str(body.user_id)}


@router.delete("/{dm_id}/participants/me", status_code=status.HTTP_204_NO_CONTENT)
async def leave_dm(dm_id: uuid.UUID, db: DbDep, current_user: CurrentUser):
    result = await db.execute(
        select(DmParticipant).where(DmParticipant.dm_thread_id == dm_id, DmParticipant.user_id == current_user.id)
    )
    participant = result.scalar_one_or_none()
    if participant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not a participant")
    await db.delete(participant)
    await db.commit()
