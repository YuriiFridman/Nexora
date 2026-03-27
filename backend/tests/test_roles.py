from __future__ import annotations

import itertools

import pytest
from httpx import AsyncClient

from app.services.permissions import Permissions
from tests.conftest import auth_headers, create_test_user

_counter = itertools.count(1)


async def setup_guild_with_channel(client: AsyncClient):
    n = next(_counter)
    owner_token, owner = await create_test_user(
        client,
        username=f"roleowner{n}",
        email=f"roleowner{n}@example.com",
    )
    guild_resp = await client.post(
        "/api/v1/guilds/",
        json={"name": f"Roles Guild {n}"},
        headers=auth_headers(owner_token),
    )
    assert guild_resp.status_code == 201
    guild = guild_resp.json()

    channel_resp = await client.post(
        f"/api/v1/guilds/{guild['id']}/channels",
        json={"name": "general", "type": "text"},
        headers=auth_headers(owner_token),
    )
    assert channel_resp.status_code == 201
    channel = channel_resp.json()
    return owner_token, owner, guild, channel


async def invite_user_to_guild(
    client: AsyncClient,
    owner_token: str,
    guild_id: str,
    channel_id: str,
    username: str,
    email: str,
):
    token, user = await create_test_user(client, username=username, email=email)
    invite_resp = await client.post(
        "/api/v1/invites/",
        json={"guild_id": guild_id, "channel_id": channel_id},
        headers=auth_headers(owner_token),
    )
    assert invite_resp.status_code == 201
    code = invite_resp.json()["code"]
    accept_resp = await client.post(f"/api/v1/invites/{code}/accept", headers=auth_headers(token))
    assert accept_resp.status_code == 200
    return token, user


@pytest.mark.asyncio
async def test_role_name_must_be_unique_case_insensitive(client: AsyncClient):
    owner_token, _, guild, _ = await setup_guild_with_channel(client)

    first = await client.post(
        f"/api/v1/guilds/{guild['id']}/roles",
        json={
            "name": "Moderator",
            "color": 0x5865F2,
            "permissions": 0,
            "hoist": False,
            "mentionable": False,
            "position": 3,
        },
        headers=auth_headers(owner_token),
    )
    assert first.status_code == 201

    duplicate = await client.post(
        f"/api/v1/guilds/{guild['id']}/roles",
        json={
            "name": "moderator",
            "color": 0x57F287,
            "permissions": 0,
            "hoist": False,
            "mentionable": False,
            "position": 2,
        },
        headers=auth_headers(owner_token),
    )
    assert duplicate.status_code == 409


@pytest.mark.asyncio
async def test_cannot_grant_permissions_user_does_not_have(client: AsyncClient):
    owner_token, _, guild, channel = await setup_guild_with_channel(client)
    member_token, member = await invite_user_to_guild(
        client, owner_token, guild["id"], channel["id"], username="rolemember", email="rolemember@example.com"
    )

    manager_role = await client.post(
        f"/api/v1/guilds/{guild['id']}/roles",
        json={
            "name": "RoleManager",
            "color": 0x5865F2,
            "permissions": Permissions.MANAGE_ROLES,
            "hoist": True,
            "mentionable": False,
            "position": 10,
        },
        headers=auth_headers(owner_token),
    )
    assert manager_role.status_code == 201
    manager_role_id = manager_role.json()["id"]

    assign = await client.post(
        f"/api/v1/guilds/{guild['id']}/roles/{manager_role_id}/members/{member['id']}",
        headers=auth_headers(owner_token),
    )
    assert assign.status_code == 201

    forbidden = await client.post(
        f"/api/v1/guilds/{guild['id']}/roles",
        json={
            "name": "Escalation",
            "color": 0xED4245,
            "permissions": Permissions.MANAGE_ROLES | Permissions.ADMINISTRATOR,
            "hoist": False,
            "mentionable": True,
            "position": 2,
        },
        headers=auth_headers(member_token),
    )
    assert forbidden.status_code == 403


@pytest.mark.asyncio
async def test_template_bulk_assign_and_audit(client: AsyncClient):
    owner_token, _, guild, channel = await setup_guild_with_channel(client)
    _, member = await invite_user_to_guild(
        client, owner_token, guild["id"], channel["id"], username="bulkmember", email="bulkmember@example.com"
    )

    template = await client.post(
        f"/api/v1/guilds/{guild['id']}/roles/template",
        json={"template": "moderator", "position": 5},
        headers=auth_headers(owner_token),
    )
    assert template.status_code == 201
    role_id = template.json()["id"]

    bulk_assign = await client.post(
        f"/api/v1/guilds/{guild['id']}/roles/bulk-assign",
        json={"role_id": role_id, "user_ids": [member["id"]]},
        headers=auth_headers(owner_token),
    )
    assert bulk_assign.status_code == 204

    member_roles = await client.get(f"/api/v1/guilds/{guild['id']}/member-roles", headers=auth_headers(owner_token))
    assert member_roles.status_code == 200
    assert any(item["user_id"] == member["id"] and item["role_id"] == role_id for item in member_roles.json())

    audit = await client.get(f"/api/v1/guilds/{guild['id']}/roles/audit", headers=auth_headers(owner_token))
    assert audit.status_code == 200
    actions = [entry["action"] for entry in audit.json()]
    assert "create_template" in actions
    assert "bulk_assign" in actions
