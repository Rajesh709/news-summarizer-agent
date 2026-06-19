import os
from typing import Optional
import redis.asyncio as aioredis
from langchain_community.chat_message_histories import RedisChatMessageHistory
from app.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


def get_redis_url() -> str:
    # Railway provides REDIS_URL directly — use it if available
    redis_url = os.getenv("REDIS_URL") or os.getenv("REDIS_PRIVATE_URL")
    if redis_url:
        return redis_url
    # Fallback: build from individual settings (local dev)
    s = get_settings()
    if s.redis_password:
        return f"redis://:{s.redis_password}@{s.redis_host}:{s.redis_port}/{s.redis_db}"
    return f"redis://{s.redis_host}:{s.redis_port}/{s.redis_db}"


def get_session_history(session_id: str) -> RedisChatMessageHistory:
    settings = get_settings()
    return RedisChatMessageHistory(
        session_id=session_id,
        url=get_redis_url(),
        ttl=settings.redis_ttl,
        key_prefix="news_agent:chat:",
    )


class RedisMemoryManager:
    def __init__(self) -> None:
        self._redis = aioredis.from_url(get_redis_url(), decode_responses=True)
        settings = get_settings()
        self._ttl = settings.redis_ttl

    async def clear_session(self, session_id: str) -> None:
        pattern = f"news_agent:*:{session_id}*"
        keys = await self._redis.keys(pattern)
        if keys:
            await self._redis.delete(*keys)

    async def ping(self) -> bool:
        try:
            return await self._redis.ping()
        except Exception:
            return False

    async def close(self) -> None:
        await self._redis.aclose()
