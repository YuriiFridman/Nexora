from __future__ import annotations

import itertools

import pytest
from httpx import AsyncClient

from tests.conftest import auth_headers, create_test_user

_counter = itertools.count(1)


async def setup_guild(client: AsyncClient):
    n = next(_counter)
    token, user = await create_test_user(client, username=f"guildowner{n}", email=f"guildowner{n}@example.com")
    response = await client.post("/api/v1/guilds/", json={"name": "Test Guild"}, headers=auth_headers(token))
    assert response.status_code == 201
    return token, user, response.json()


@pytest.mark.asyncio
async def test_create_guild(client: AsyncClient):
    token, _, guild = await setup_guild(client)
    assert guild["name"] == "Test Guild"
    assert "id" in guild


@pytest.mark.asyncio
async def test_get_guild(client: AsyncClient):
    token, _, guild = await setup_guild(client)
    guild_id = guild["id"]
    response = await client.get(f"/api/v1/guilds/{guild_id}", headers=auth_headers(token))
    assert response.status_code == 200
    assert response.json()["id"] == guild_id


@pytest.mark.asyncio
async def test_list_guilds(client: AsyncClient):
    token, _, guild = await setup_guild(client)
    response = await client.get("/api/v1/guilds/", headers=auth_headers(token))
    assert response.status_code == 200
    ids = [g["id"] for g in response.json()]
    assert guild["id"] in ids


@pytest.mark.asyncio
async def test_update_guild(client: AsyncClient):
    token, _, guild = await setup_guild(client)
    guild_id = guild["id"]
    response = await client.patch(f"/api/v1/guilds/{guild_id}", json={"name": "Updated Guild"}, headers=auth_headers(token))
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Guild"


@pytest.mark.asyncio
async def test_invite_flow(client: AsyncClient):
    owner_token, _, guild = await setup_guild(client)
    guild_id = guild["id"]

    # Get the first channel to use in invite
    _channels_resp = await client.get(f"/api/v1/guilds/{guild_id}/channels", headers=auth_headers(owner_token))
    # There may be no channels yet; create one
    ch_resp = await client.post(
        f"/api/v1/guilds/{guild_id}/channels",
        json={"name": "general", "type": "text"},
        headers=auth_headers(owner_token),
    )
    assert ch_resp.status_code == 201
    channel_id = ch_resp.json()["id"]

    # Create invite
    inv_resp = await client.post(
        "/api/v1/invites/",
        json={"guild_id": guild_id, "channel_id": channel_id},
        headers=auth_headers(owner_token),
    )
    assert inv_resp.status_code == 201
    code = inv_resp.json()["code"]

    # Register a second user
    token2, _ = await create_test_user(client, username="joiner", email="joiner@example.com")

    # Get invite info
    info_resp = await client.get(f"/api/v1/invites/{code}", headers=auth_headers(token2))
    assert info_resp.status_code == 200

    # Accept invite
    accept_resp = await client.post(f"/api/v1/invites/{code}/accept", headers=auth_headers(token2))
    assert accept_resp.status_code == 200

    # Verify membership
    _members_resp = await client.get(f"/api/v1/guilds/{guild_id}/members", headers=auth_headers(owner_token))
    assert str(accept_resp.json()["guild_id"]) == guild_id


@pytest.mark.asyncio
async def test_delete_guild(client: AsyncClient):
    token, _, guild = await setup_guild(client)
    guild_id = guild["id"]
    response = await client.delete(f"/api/v1/guilds/{guild_id}", headers=auth_headers(token))
    assert response.status_code == 204
