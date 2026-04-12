"""Redis configuration and async client setup."""

import json
import logging
from typing import Any, Dict, Optional

import redis.asyncio as redis

from app.base.datetime import utcnow
from app.core.config import settings

logger = logging.getLogger(__name__)


class RedisService:
    """Async Redis service with connection pooling."""

    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None

    async def connect(self) -> None:
        """Initialize Redis connection pool."""
        try:
            self.redis_client = redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
                max_connections=20,
                retry_on_timeout=True,
                health_check_interval=30,
            )

            # Test connection
            await self.redis_client.ping()
            logger.info("Redis connected successfully")

        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    async def disconnect(self) -> None:
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Redis disconnected")

    async def get(self, key: str) -> Optional[str]:
        """Get value by key."""
        try:
            if not self.redis_client:
                return None
            return await self.redis_client.get(key)
        except Exception as e:
            logger.error(f"Redis GET error for key {key}: {e}")
            return None

    async def set(self, key: str, value: str, expire: Optional[int] = None) -> bool:
        """Set key-value pair with optional expiration."""
        try:
            if not self.redis_client:
                return False
            await self.redis_client.set(key, value, ex=expire)
            return True
        except Exception as e:
            logger.error(f"Redis SET error for key {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete single key. Returns True if key was deleted."""
        try:
            if not self.redis_client:
                return False
            result = await self.redis_client.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"Redis DELETE error for key {key}: {e}")
            return False

    async def delete_multiple(self, *keys: str) -> int:
        """Delete multiple keys. Returns number of keys deleted."""
        try:
            if not self.redis_client or not keys:
                return 0
            return await self.redis_client.delete(*keys)
        except Exception as e:
            logger.error(f"Redis DELETE error for keys {keys}: {e}")
            return 0

    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        try:
            if not self.redis_client:
                return False
            return bool(await self.redis_client.exists(key))
        except Exception as e:
            logger.error(f"Redis EXISTS error for key {key}: {e}")
            return False

    async def keys(self, pattern: str) -> list[str]:
        """Get keys matching a pattern."""
        try:
            if not self.redis_client:
                return []
            return await self.redis_client.keys(pattern)
        except Exception as e:
            logger.error(f"Redis KEYS error for pattern {pattern}: {e}")
            return []

    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment counter."""
        try:
            if not self.redis_client:
                return None
            return await self.redis_client.incrby(key, amount)
        except Exception as e:
            logger.error(f"Redis INCR error for key {key}: {e}")
            return None

    async def set_json(
        self, key: str, data: dict, expire: Optional[int] = None
    ) -> bool:
        """Set JSON data."""
        try:
            value = json.dumps(data)
            return await self.set(key, value, expire)
        except Exception as e:
            logger.error(f"Redis SET JSON error for key {key}: {e}")
            return False

    async def get_json(self, key: str) -> Optional[dict]:
        """Get JSON data."""
        try:
            value = await self.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Redis GET JSON error for key {key}: {e}")
            return None

    async def cache_user_session(
        self, user_id: str, session_data: dict, expire: int = 1800
    ) -> bool:
        """Cache user session data (30 min default)."""
        cache_key = f"user:session:{user_id}"
        return await self.set_json(cache_key, session_data, expire)

    async def get_user_session(self, user_id: str) -> Optional[dict]:
        """Get cached user session."""
        cache_key = f"user:session:{user_id}"
        return await self.get_json(cache_key)

    async def increment_api_usage(self, user_id: str, api_type: str = "api") -> int:
        """Track API usage per user."""
        today = utcnow().strftime("%Y-%m-%d")
        cache_key = f"usage:{api_type}:{user_id}:{today}"
        count = await self.increment(cache_key)

        # Set expiration to end of day if this is the first increment
        if count == 1 and self.redis_client:
            import datetime

            tomorrow = utcnow().replace(
                hour=0, minute=0, second=0, microsecond=0
            ) + datetime.timedelta(days=1)
            expire_seconds = int((tomorrow - utcnow()).total_seconds())
            await self.redis_client.expire(cache_key, expire_seconds)

        return count or 0

    async def get_api_usage(self, user_id: str, api_type: str = "api") -> int:
        """Get daily API usage count."""
        today = utcnow().strftime("%Y-%m-%d")
        cache_key = f"usage:{api_type}:{user_id}:{today}"
        count = await self.get(cache_key)
        return int(count) if count else 0

    async def create_or_update_dictionary(
        self, key: str, value: Dict[str, Any]
    ) -> bool:
        """Create or update a dictionary."""
        data = await self.get_json(key)

        if data and not isinstance(data, dict):
            raise TypeError(f"Data for key {key} is not a dictionary")

        if data:
            data.update(value)
        else:
            data = value

        return await self.set_json(key, data, expire=3600)


# Global Redis service instance
redis_service = RedisService()
