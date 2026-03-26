from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.conftest import auth_headers, create_test_user


@pytest.mark.asyncio
async def test_register(client: AsyncClient):
    token, user = await create_test_user(client)
    assert token
    assert user["username"] == "testuser"
    assert user["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_register_duplicate_username(client: AsyncClient):
    await create_test_user(client, username="dupeuser", email="dupe1@example.com")
    response = await client.post(
        "/api/v1/auth/register",
        json={"username": "dupeuser", "email": "dupe2@example.com", "password": "password123"},
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    await create_test_user(client, username="user_a", email="shared@example.com")
    response = await client.post(
        "/api/v1/auth/register",
        json={"username": "user_b", "email": "shared@example.com", "password": "password123"},
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_login(client: AsyncClient):
    await create_test_user(client, username="loginuser", email="login@example.com")
    response = await client.post("/api/v1/auth/login", json={"email": "login@example.com", "password": "password123"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    await create_test_user(client, username="wrongpass", email="wrongpass@example.com")
    response = await client.post("/api/v1/auth/login", json={"email": "wrongpass@example.com", "password": "wrongpassword"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/register",
        json={"username": "refreshuser", "email": "refresh@example.com", "password": "password123"},
    )
    refresh_token = response.json()["refresh_token"]

    response = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["refresh_token"] != refresh_token  # rotated


@pytest.mark.asyncio
async def test_logout(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/register",
        json={"username": "logoutuser", "email": "logout@example.com", "password": "password123"},
    )
    refresh_token = response.json()["refresh_token"]

    response = await client.post("/api/v1/auth/logout", json={"refresh_token": refresh_token})
    assert response.status_code == 204

    # Using the revoked token should fail
    response = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me(client: AsyncClient):
    token, _ = await create_test_user(client, username="meuser", email="me@example.com")
    response = await client.get("/api/v1/auth/me", headers=auth_headers(token))
    assert response.status_code == 200
    assert response.json()["username"] == "meuser"
