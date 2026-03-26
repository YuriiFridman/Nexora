from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, status

from app.config import settings
from app.deps import CurrentUser, DbDep
from app.models.message import Attachment
from app.services.storage import storage

router = APIRouter(prefix="/attachments", tags=["attachments"])


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_attachment(file: UploadFile, db: DbDep, current_user: CurrentUser):
    data = await file.read()
    if len(data) > settings.MAX_ATTACHMENT_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds max size of {settings.MAX_ATTACHMENT_SIZE} bytes",
        )

    ext = Path(file.filename or "file").suffix
    key = f"attachments/{current_user.id}/{uuid.uuid4()}{ext}"
    url = await storage.upload(key, data, file.content_type or "application/octet-stream")

    attachment = Attachment(
        filename=file.filename or "file",
        content_type=file.content_type or "application/octet-stream",
        size=len(data),
        storage_key=key,
        url=url,
    )
    db.add(attachment)
    await db.commit()
    await db.refresh(attachment)

    return {"attachment_id": str(attachment.id), "url": attachment.url}
