from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


class Base(DeclarativeBase):
    __allow_unmapped__ = True


def _make_engine():
    return create_async_engine(settings.DATABASE_URL, echo=False, future=True)


def _make_session_factory(eng):
    return async_sessionmaker(eng, expire_on_commit=False, class_=AsyncSession)


# These are created lazily so that tests can override DATABASE_URL before importing this module
engine = _make_engine()
AsyncSessionLocal = _make_session_factory(engine)


def configure_engine(url: str):
    """Re-configure the engine and session factory (used by tests)."""
    global engine, AsyncSessionLocal
    engine = create_async_engine(url, echo=False, future=True)
    AsyncSessionLocal = _make_session_factory(engine)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
