"""Tests for Redis service (core/redis.py)."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.redis import RedisService


class TestRedisServiceConnect:
    """Tests for Redis connection methods."""

    @pytest.mark.asyncio
    async def test_connect_success(self):
        """Test successful Redis connection."""
        service = RedisService()

        with patch("app.core.redis.redis.from_url") as mock_from_url:
            mock_client = AsyncMock()
            mock_client.ping = AsyncMock()
            mock_from_url.return_value = mock_client

            with patch("app.core.redis.settings") as mock_settings:
                mock_settings.redis_url = "redis://localhost:6379"

                await service.connect()

                assert service.redis_client is not None
                mock_client.ping.assert_called_once()

    @pytest.mark.asyncio
    async def test_connect_failure(self):
        """Test Redis connection failure."""
        service = RedisService()

        with patch("app.core.redis.redis.from_url") as mock_from_url:
            mock_client = AsyncMock()
            mock_client.ping = AsyncMock(side_effect=Exception("Connection refused"))
            mock_from_url.return_value = mock_client

            with patch("app.core.redis.settings") as mock_settings:
                mock_settings.redis_url = "redis://localhost:6379"

                with pytest.raises(Exception, match="Connection refused"):
                    await service.connect()

    @pytest.mark.asyncio
    async def test_disconnect(self):
        """Test Redis disconnect."""
        service = RedisService()
        service.redis_client = AsyncMock()
        service.redis_client.close = AsyncMock()

        await service.disconnect()

        service.redis_client.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_disconnect_no_client(self):
        """Test disconnect when no client exists."""
        service = RedisService()
        service.redis_client = None

        # Should not raise
        await service.disconnect()


class TestRedisServiceGet:
    """Tests for Redis GET operations."""

    @pytest.mark.asyncio
    async def test_get_success(self):
        """Test successful GET operation."""
        service = RedisService()
        service.redis_client = AsyncMock()
        service.redis_client.get = AsyncMock(return_value="test-value")

        result = await service.get("test-key")

        assert result == "test-value"
        service.redis_client.get.assert_called_once_with("test-key")

    @pytest.mark.asyncio
    async def test_get_no_client(self):
        """Test GET when no client exists."""
        service = RedisService()
        service.redis_client = None

        result = await service.get("test-key")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_exception(self):
        """Test GET exception handling."""
        service = RedisService()
        service.redis_client = AsyncMock()
        service.redis_client.get = AsyncMock(side_effect=Exception("Redis error"))

        result = await service.get("test-key")

        assert result is None


class TestRedisServiceSet:
    """Tests for Redis SET operations."""

    @pytest.mark.asyncio
    async def test_set_success(self):
        """Test successful SET operation."""
        service = RedisService()
        service.redis_client = AsyncMock()
        service.redis_client.set = AsyncMock()

        result = await service.set("test-key", "test-value")

        assert result is True
        service.redis_client.set.assert_called_once_with("test-key", "test-value", ex=None)

    @pytest.mark.asyncio
    async def test_set_with_expiration(self):
        """Test SET with expiration."""
        service = RedisService()
        service.redis_client = AsyncMock()
        service.redis_client.set = AsyncMock()

        result = await service.set("test-key", "test-value", expire=3600)

        assert result is True
        service.redis_client.set.assert_called_once_with("test-key", "test-value", ex=3600)

    @pytest.mark.asyncio
    async def test_set_no_client(self):
        """Test SET when no client exists."""
        service = RedisService()
        service.redis_client = None

        result = await service.set("test-key", "test-value")

        assert result is False

    @pytest.mark.asyncio
    async def test_set_exception(self):
        """Test SET exception handling."""
        service = RedisService()
        service.redis_client = AsyncMock()
        service.redis_client.set = AsyncMock(side_effect=Exception("Redis error"))

        result = await service.set("test-key", "test-value")

        assert result is False


class TestRedisServiceDelete:
    """Tests for Redis DELETE operations."""

    @pytest.mark.asyncio
    async def test_delete_success(self):
        """Test successful DELETE operation."""
        service = RedisService()
        service.redis_client = AsyncMock()
        service.redis_client.delete = AsyncMock(return_value=1)

        result = await service.delete("test-key")

        assert result is True

    @pytest.mark.asyncio
    async def test_delete_key_not_found(self):
        """Test DELETE when key doesn't exist."""
        service = RedisService()
        service.redis_client = AsyncMock()
        service.redis_client.delete = AsyncMock(return_value=0)

        result = await service.delete("nonexistent-key")

        assert result is False

    @pytest.mark.asyncio
    async def test_delete_no_client(self):
        """Test DELETE when no client exists."""
        service = RedisService()
        service.redis_client = None

        result = await service.delete("test-key")

        assert result is False

    @pytest.mark.asyncio
    async def test_delete_multiple_success(self):
        """Test deleting multiple keys."""
        service = RedisService()
        service.redis_client = AsyncMock()
        service.redis_client.delete = AsyncMock(return_value=3)

        result = await service.delete_multiple("key1", "key2", "key3")

        assert result == 3

    @pytest.mark.asyncio
    async def test_delete_multiple_no_keys(self):
        """Test delete_multiple with no keys."""
        service = RedisService()
        service.redis_client = AsyncMock()

        result = await service.delete_multiple()

        assert result == 0


class TestRedisServiceExists:
    """Tests for Redis EXISTS operations."""

    @pytest.mark.asyncio
    async def test_exists_true(self):
        """Test EXISTS when key exists."""
        service = RedisService()
        service.redis_client = AsyncMock()
        service.redis_client.exists = AsyncMock(return_value=1)

        result = await service.exists("test-key")

        assert result is True

    @pytest.mark.asyncio
    async def test_exists_false(self):
        """Test EXISTS when key doesn't exist."""
        service = RedisService()
        service.redis_client = AsyncMock()
        service.redis_client.exists = AsyncMock(return_value=0)

        result = await service.exists("nonexistent-key")

        assert result is False

    @pytest.mark.asyncio
    async def test_exists_no_client(self):
        """Test EXISTS when no client exists."""
        service = RedisService()
        service.redis_client = None

        result = await service.exists("test-key")

        assert result is False


class TestRedisServiceKeys:
    """Tests for Redis KEYS operations."""

    @pytest.mark.asyncio
    async def test_keys_success(self):
        """Test KEYS pattern matching."""
        service = RedisService()
        service.redis_client = AsyncMock()
        service.redis_client.keys = AsyncMock(return_value=["user:1", "user:2", "user:3"])

        result = await service.keys("user:*")

        assert result == ["user:1", "user:2", "user:3"]

    @pytest.mark.asyncio
    async def test_keys_no_client(self):
        """Test KEYS when no client exists."""
        service = RedisService()
        service.redis_client = None

        result = await service.keys("user:*")

        assert result == []


class TestRedisServiceIncrement:
    """Tests for Redis INCREMENT operations."""

    @pytest.mark.asyncio
    async def test_increment_success(self):
        """Test successful increment."""
        service = RedisService()
        service.redis_client = AsyncMock()
        service.redis_client.incrby = AsyncMock(return_value=5)

        result = await service.increment("counter")

        assert result == 5

    @pytest.mark.asyncio
    async def test_increment_by_amount(self):
        """Test increment by specific amount."""
        service = RedisService()
        service.redis_client = AsyncMock()
        service.redis_client.incrby = AsyncMock(return_value=10)

        result = await service.increment("counter", amount=5)

        assert result == 10
        service.redis_client.incrby.assert_called_once_with("counter", 5)

    @pytest.mark.asyncio
    async def test_increment_no_client(self):
        """Test increment when no client exists."""
        service = RedisService()
        service.redis_client = None

        result = await service.increment("counter")

        assert result is None


class TestRedisServiceJSON:
    """Tests for Redis JSON operations."""

    @pytest.mark.asyncio
    async def test_set_json_success(self):
        """Test setting JSON data."""
        service = RedisService()
        service.redis_client = AsyncMock()
        service.redis_client.set = AsyncMock()

        data = {"name": "test", "value": 123}
        result = await service.set_json("test-key", data)

        assert result is True
        call_args = service.redis_client.set.call_args
        assert json.loads(call_args[0][1]) == data

    @pytest.mark.asyncio
    async def test_get_json_success(self):
        """Test getting JSON data."""
        service = RedisService()
        service.redis_client = AsyncMock()
        data = {"name": "test", "value": 123}
        service.redis_client.get = AsyncMock(return_value=json.dumps(data))

        result = await service.get_json("test-key")

        assert result == data

    @pytest.mark.asyncio
    async def test_get_json_not_found(self):
        """Test getting JSON when key doesn't exist."""
        service = RedisService()
        service.redis_client = AsyncMock()
        service.redis_client.get = AsyncMock(return_value=None)

        result = await service.get_json("nonexistent-key")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_json_invalid(self):
        """Test getting invalid JSON data."""
        service = RedisService()
        service.redis_client = AsyncMock()
        service.redis_client.get = AsyncMock(return_value="not-json")

        result = await service.get_json("invalid-key")

        assert result is None


class TestRedisServiceUserSession:
    """Tests for user session caching."""

    @pytest.mark.asyncio
    async def test_cache_user_session(self):
        """Test caching user session."""
        service = RedisService()
        service.redis_client = AsyncMock()
        service.redis_client.set = AsyncMock()

        session_data = {"user_id": "123", "email": "test@example.com"}
        result = await service.cache_user_session("user-123", session_data)

        assert result is True

    @pytest.mark.asyncio
    async def test_get_user_session(self):
        """Test getting cached user session."""
        service = RedisService()
        service.redis_client = AsyncMock()
        session_data = {"user_id": "123", "email": "test@example.com"}
        service.redis_client.get = AsyncMock(return_value=json.dumps(session_data))

        result = await service.get_user_session("user-123")

        assert result == session_data


class TestRedisServiceAPIUsage:
    """Tests for API usage tracking."""

    @pytest.mark.asyncio
    async def test_increment_api_usage(self):
        """Test incrementing API usage."""
        service = RedisService()
        service.redis_client = AsyncMock()
        service.redis_client.incrby = AsyncMock(return_value=1)
        service.redis_client.expire = AsyncMock()

        result = await service.increment_api_usage("user-123")

        assert result == 1

    @pytest.mark.asyncio
    async def test_get_api_usage(self):
        """Test getting API usage count."""
        service = RedisService()
        service.redis_client = AsyncMock()
        service.redis_client.get = AsyncMock(return_value="42")

        result = await service.get_api_usage("user-123")

        assert result == 42

    @pytest.mark.asyncio
    async def test_get_api_usage_no_usage(self):
        """Test getting API usage when none exists."""
        service = RedisService()
        service.redis_client = AsyncMock()
        service.redis_client.get = AsyncMock(return_value=None)

        result = await service.get_api_usage("user-123")

        assert result == 0


class TestRedisServiceDictionary:
    """Tests for dictionary operations."""

    @pytest.mark.asyncio
    async def test_create_dictionary(self):
        """Test creating a new dictionary."""
        service = RedisService()
        service.redis_client = AsyncMock()
        service.redis_client.get = AsyncMock(return_value=None)
        service.redis_client.set = AsyncMock()

        result = await service.create_or_update_dictionary("test-key", {"name": "test"})

        assert result is True

    @pytest.mark.asyncio
    async def test_update_dictionary(self):
        """Test updating existing dictionary."""
        service = RedisService()
        service.redis_client = AsyncMock()
        existing_data = {"name": "old"}
        service.redis_client.get = AsyncMock(return_value=json.dumps(existing_data))
        service.redis_client.set = AsyncMock()

        result = await service.create_or_update_dictionary("test-key", {"value": "new"})

        assert result is True
        # Verify the merged data was saved
        call_args = service.redis_client.set.call_args
        saved_data = json.loads(call_args[0][1])
        assert saved_data["name"] == "old"
        assert saved_data["value"] == "new"

    @pytest.mark.asyncio
    async def test_update_dictionary_type_error(self):
        """Test error when existing data is not a dictionary."""
        service = RedisService()
        service.redis_client = AsyncMock()
        service.redis_client.get = AsyncMock(return_value='"not-a-dict"')

        with pytest.raises(TypeError, match="not a dictionary"):
            await service.create_or_update_dictionary("test-key", {"value": "new"})
