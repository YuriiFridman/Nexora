from __future__ import annotations

import os

# Override DATABASE_URL before any app module is imported so SQLAlchemy uses SQLite
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

import app.database as _db_module

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Reconfigure the engine to use SQLite in-memory for the test suite
_db_module.configure_engine(TEST_DATABASE_URL)

from app.database import Base, get_db  # noqa: E402 - must come after configure
from app.main import app  # noqa: E402


@pytest_asyncio.fixture(scope="session")
async def db_engine():
    _db_module.configure_engine(TEST_DATABASE_URL)
    engine = _db_module.engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine):
    AsyncTestSession = async_sessionmaker(db_engine, expire_on_commit=False, class_=AsyncSession)
    async with AsyncTestSession() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


async def create_test_user(client: AsyncClient, username: str = "testuser", email: str = "test@example.com", password: str = "password123"):
    response = await client.post(
        "/api/v1/auth/register",
        json={"username": username, "email": email, "password": password},
    )
    assert response.status_code == 201
    data = response.json()
    return data["access_token"], data["user"]


def auth_headers(access_token: str) -> dict:
    return {"Authorization": f"Bearer {access_token}"}
