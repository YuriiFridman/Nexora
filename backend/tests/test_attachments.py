from __future__ import annotations

import io

import pytest
from httpx import AsyncClient

from tests.conftest import auth_headers, create_test_user


@pytest.mark.asyncio
async def test_upload_attachment(client: AsyncClient):
    token, _ = await create_test_user(client, username="attuser", email="att@example.com")

    file_content = b"Hello, this is a test file."
    response = await client.post(
        "/api/v1/attachments/upload",
        files={"file": ("test.txt", io.BytesIO(file_content), "text/plain")},
        headers=auth_headers(token),
    )
    assert response.status_code == 201
    data = response.json()
    assert "attachment_id" in data
    assert "url" in data


@pytest.mark.asyncio
async def test_upload_attachment_too_large(client: AsyncClient):
    token, _ = await create_test_user(client, username="bigfileuser", email="bigfile@example.com")

    # 9MB file (over the 8MB limit)
    large_content = b"x" * (9 * 1024 * 1024)
    response = await client.post(
        "/api/v1/attachments/upload",
        files={"file": ("big.bin", io.BytesIO(large_content), "application/octet-stream")},
        headers=auth_headers(token),
    )
    assert response.status_code == 413


@pytest.mark.asyncio
async def test_attachment_linked_to_message(client: AsyncClient):
    token, _ = await create_test_user(client, username="attmsguser", email="attmsg@example.com")

    # Create guild and channel
    guild_resp = await client.post("/api/v1/guilds/", json={"name": "Attachment Guild"}, headers=auth_headers(token))
    guild_id = guild_resp.json()["id"]
    ch_resp = await client.post(
        f"/api/v1/guilds/{guild_id}/channels",
        json={"name": "attachments", "type": "text"},
        headers=auth_headers(token),
    )
    channel_id = ch_resp.json()["id"]

    # Upload attachment
    att_resp = await client.post(
        "/api/v1/attachments/upload",
        files={"file": ("note.txt", io.BytesIO(b"note content"), "text/plain")},
        headers=auth_headers(token),
    )
    attachment_id = att_resp.json()["attachment_id"]

    # Send message with attachment
    msg_resp = await client.post(
        f"/api/v1/channels/{channel_id}/messages",
        json={"content": "See attachment", "attachment_ids": [attachment_id]},
        headers=auth_headers(token),
    )
    assert msg_resp.status_code == 201
    msg_data = msg_resp.json()
    assert len(msg_data["attachments"]) == 1
    assert msg_data["attachments"][0]["id"] == attachment_id
