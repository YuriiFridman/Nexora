from __future__ import annotations

from pathlib import Path
from typing import Protocol

import aiofiles

from app.config import settings


class StorageBackend(Protocol):
    async def upload(self, key: str, data: bytes, content_type: str) -> str: ...
    async def get_url(self, key: str) -> str: ...
    async def delete(self, key: str) -> None: ...


class LocalStorageBackend:
    """Stores files in a local directory. Suitable for development."""

    def __init__(self, base_path: str = settings.STORAGE_LOCAL_PATH, base_url: str = "/uploads") -> None:
        self.base_path = Path(base_path)
        self.base_url = base_url
        self.base_path.mkdir(parents=True, exist_ok=True)

    async def upload(self, key: str, data: bytes, content_type: str) -> str:
        file_path = self.base_path / key
        file_path.parent.mkdir(parents=True, exist_ok=True)
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(data)
        return self.base_url.rstrip("/") + "/" + key

    async def get_url(self, key: str) -> str:
        return self.base_url.rstrip("/") + "/" + key

    async def delete(self, key: str) -> None:
        file_path = self.base_path / key
        if file_path.exists():
            file_path.unlink()


class S3StorageBackend:
    """Stores files in an S3-compatible service (e.g., AWS S3, Cloudflare R2)."""

    def __init__(self) -> None:
        try:
            import aioboto3  # type: ignore[import]
        except ImportError as exc:
            raise RuntimeError("aioboto3 is required for S3 storage. Install with: pip install aioboto3") from exc

        import aioboto3

        self._session = aioboto3.Session(
            aws_access_key_id=settings.STORAGE_S3_ACCESS_KEY,
            aws_secret_access_key=settings.STORAGE_S3_SECRET_KEY,
            region_name=settings.STORAGE_S3_REGION,
        )
        self._bucket = settings.STORAGE_S3_BUCKET
        self._endpoint = settings.STORAGE_S3_ENDPOINT or None

    async def upload(self, key: str, data: bytes, content_type: str) -> str:
        async with self._session.client("s3", endpoint_url=self._endpoint) as s3:  # type: ignore[attr-defined]
            await s3.put_object(Bucket=self._bucket, Key=key, Body=data, ContentType=content_type)
        return await self.get_url(key)

    async def get_url(self, key: str) -> str:
        if self._endpoint:
            return f"{self._endpoint.rstrip('/')}/{self._bucket}/{key}"
        return f"https://{self._bucket}.s3.amazonaws.com/{key}"

    async def delete(self, key: str) -> None:
        async with self._session.client("s3", endpoint_url=self._endpoint) as s3:  # type: ignore[attr-defined]
            await s3.delete_object(Bucket=self._bucket, Key=key)


def get_storage_backend() -> StorageBackend:
    if settings.STORAGE_BACKEND == "s3":
        return S3StorageBackend()
    return LocalStorageBackend()


storage: StorageBackend = get_storage_backend()
