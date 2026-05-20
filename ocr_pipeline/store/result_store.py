"""
Result store abstraction.

If REDIS_URL starts with "memory://" (the default for local dev),
an in-process dict is used — no Redis installation required.
Otherwise a real Redis connection is established using the provided URL.
"""

import json
import asyncio
from datetime import datetime
from typing import Any, Optional

from config import settings
from utils.logger import get_logger

logger = get_logger(__name__)

# ── In-memory fallback ────────────────────────────────────────────────────────

_MEMORY_STORE: dict[str, str] = {}


class _MemoryStore:
    """Thread-safe, asyncio-friendly dict-backed store."""

    async def set(self, key: str, value: str, ex: int) -> None:
        _MEMORY_STORE[key] = value

    async def get(self, key: str) -> Optional[str]:
        return _MEMORY_STORE.get(key)

    async def delete(self, key: str) -> None:
        _MEMORY_STORE.pop(key, None)

    async def close(self) -> None:
        pass


# ── JSON serialisation helpers ────────────────────────────────────────────────

def _serialise(obj: Any) -> str:
    """Serialise a job dict to JSON, converting bytes and datetimes."""
    def default(o):
        if isinstance(o, bytes):
            return None          # never persist raw PDF bytes
        if isinstance(o, datetime):
            return o.isoformat()
        raise TypeError(f"Object of type {type(o)} is not JSON serialisable")

    return json.dumps(obj, default=default)


def _deserialise(raw: str) -> dict:
    return json.loads(raw)


# ── Public ResultStore ────────────────────────────────────────────────────────

class ResultStore:

    def __init__(self):
        self._client = None

    async def _get_client(self):
        if self._client is not None:
            return self._client

        if settings.REDIS_URL.startswith("memory://"):
            logger.info("ResultStore: using in-memory store (no Redis)")
            self._client = _MemoryStore()
        else:
            import redis.asyncio as aioredis
            logger.info(f"ResultStore: connecting to Redis at {settings.REDIS_URL}")
            self._client = await aioredis.from_url(
                settings.REDIS_URL, decode_responses=True
            )

        return self._client

    async def save(self, job_id: str, job: dict) -> None:
        client = await self._get_client()

        # Strip binary PDF bytes before saving
        safe = {k: v for k, v in job.items() if k != "pdf_bytes"}
        payload = _serialise(safe)

        await client.set(f"job:{job_id}", payload, ex=settings.RESULT_TTL_SECONDS)
        logger.debug(f"Saved job {job_id} to store")

    async def get(self, job_id: str) -> Optional[dict]:
        client = await self._get_client()
        raw = await client.get(f"job:{job_id}")
        if raw is None:
            return None
        return _deserialise(raw)

    async def delete(self, job_id: str) -> None:
        client = await self._get_client()
        await client.delete(f"job:{job_id}")

    # Store the raw PDF bytes separately in memory (not persisted to Redis)
    # so the process endpoint can retrieve them within the same process lifetime.
    _pdf_cache: dict[str, bytes] = {}

    def cache_pdf(self, job_id: str, pdf_bytes: bytes) -> None:
        self._pdf_cache[job_id] = pdf_bytes

    def get_pdf(self, job_id: str) -> Optional[bytes]:
        return self._pdf_cache.get(job_id)
