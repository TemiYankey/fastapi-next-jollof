"""Tests for JWT decoder (users/jwt_decoder.py)."""

import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from jose import jwt

from app.users.jwt_decoder import JWTDecoder


class TestJWTDecoderInit:
    """Tests for JWTDecoder initialization."""

    def test_default_initialization(self):
        """Test decoder initializes with default settings."""
        with patch("app.users.jwt_decoder.settings") as mock_settings:
            mock_settings.supabase_jwt_secret = "test-secret"

            decoder = JWTDecoder()

            assert decoder.jwt_secret == "test-secret"
            assert "RS256" in decoder.algorithms
            assert "ES256" in decoder.algorithms

    def test_custom_jwt_secret(self):
        """Test decoder with custom JWT secret."""
        decoder = JWTDecoder(jwt_secret="custom-secret")

        assert decoder.jwt_secret == "custom-secret"


class TestGetJWKS:
    """Tests for get_jwks method."""

    @pytest.mark.asyncio
    async def test_get_jwks_from_cache(self):
        """Test getting JWKS from Redis cache."""
        mock_jwks = {"keys": [{"kid": "key1", "kty": "RSA"}]}

        with patch("app.users.jwt_decoder.redis_service") as mock_redis:
            mock_redis.get_json = AsyncMock(return_value=mock_jwks)

            decoder = JWTDecoder()
            result = await decoder.get_jwks()

            assert result == mock_jwks
            mock_redis.get_json.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_jwks_cache_miss_fetches_from_supabase(self):
        """Test fetching JWKS from Supabase on cache miss."""
        mock_jwks = {"keys": [{"kid": "key1", "kty": "RSA"}]}

        with patch("app.users.jwt_decoder.redis_service") as mock_redis:
            mock_redis.get_json = AsyncMock(return_value=None)
            mock_redis.set_json = AsyncMock(return_value=True)

            with patch("app.users.jwt_decoder.httpx") as mock_httpx:
                mock_response = MagicMock()
                mock_response.json.return_value = mock_jwks
                mock_response.raise_for_status = MagicMock()
                mock_httpx.get.return_value = mock_response

                with patch("app.users.jwt_decoder.settings") as mock_settings:
                    mock_settings.supabase_url = "https://test.supabase.co"

                    decoder = JWTDecoder()
                    result = await decoder.get_jwks()

                    assert result == mock_jwks
                    mock_redis.set_json.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_jwks_bypass_cache(self):
        """Test bypassing cache to fetch fresh JWKS."""
        mock_jwks = {"keys": [{"kid": "key1", "kty": "RSA"}]}

        with patch("app.users.jwt_decoder.redis_service") as mock_redis:
            mock_redis.set_json = AsyncMock(return_value=True)

            with patch("app.users.jwt_decoder.httpx") as mock_httpx:
                mock_response = MagicMock()
                mock_response.json.return_value = mock_jwks
                mock_response.raise_for_status = MagicMock()
                mock_httpx.get.return_value = mock_response

                with patch("app.users.jwt_decoder.settings") as mock_settings:
                    mock_settings.supabase_url = "https://test.supabase.co"

                    decoder = JWTDecoder()
                    result = await decoder.get_jwks(bypass_cache=True)

                    assert result == mock_jwks
                    # Should not call get_json when bypassing
                    mock_redis.get_json.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_jwks_empty_keys(self):
        """Test handling of empty JWKS keys."""
        with patch("app.users.jwt_decoder.redis_service") as mock_redis:
            mock_redis.get_json = AsyncMock(return_value=None)

            with patch("app.users.jwt_decoder.httpx") as mock_httpx:
                mock_response = MagicMock()
                mock_response.json.return_value = {"keys": []}
                mock_response.raise_for_status = MagicMock()
                mock_httpx.get.return_value = mock_response

                with patch("app.users.jwt_decoder.settings") as mock_settings:
                    mock_settings.supabase_url = "https://test.supabase.co"

                    decoder = JWTDecoder()
                    result = await decoder.get_jwks()

                    assert result == {}

    @pytest.mark.asyncio
    async def test_get_jwks_fetch_failure_uses_stale_cache(self):
        """Test using stale cache when fetch fails."""
        mock_jwks = '{"keys": [{"kid": "stale-key"}]}'

        with patch("app.users.jwt_decoder.redis_service") as mock_redis:
            mock_redis.get_json = AsyncMock(return_value=None)
            mock_redis.get = AsyncMock(return_value=mock_jwks)

            with patch("app.users.jwt_decoder.httpx") as mock_httpx:
                mock_httpx.get.side_effect = Exception("Network error")

                with patch("app.users.jwt_decoder.settings") as mock_settings:
                    mock_settings.supabase_url = "https://test.supabase.co"

                    decoder = JWTDecoder()
                    result = await decoder.get_jwks()

                    assert result["keys"][0]["kid"] == "stale-key"

    @pytest.mark.asyncio
    async def test_get_jwks_total_failure(self):
        """Test when both fetch and cache fail."""
        with patch("app.users.jwt_decoder.redis_service") as mock_redis:
            mock_redis.get_json = AsyncMock(return_value=None)
            mock_redis.get = AsyncMock(side_effect=Exception("Redis error"))

            with patch("app.users.jwt_decoder.httpx") as mock_httpx:
                mock_httpx.get.side_effect = Exception("Network error")

                with patch("app.users.jwt_decoder.settings") as mock_settings:
                    mock_settings.supabase_url = "https://test.supabase.co"

                    decoder = JWTDecoder()
                    result = await decoder.get_jwks()

                    assert result == {}


class TestGetSigningKey:
    """Tests for get_signing_key method."""

    @pytest.mark.asyncio
    async def test_get_signing_key_success(self):
        """Test getting signing key for valid token."""
        mock_jwks = {"keys": [{"kid": "test-kid", "kty": "RSA", "n": "xxx", "e": "AQAB"}]}

        # Create a mock token with proper header
        with patch.object(jwt, "get_unverified_header") as mock_header:
            mock_header.return_value = {"alg": "RS256", "kid": "test-kid"}

            decoder = JWTDecoder()

            with patch.object(decoder, "get_jwks", return_value=mock_jwks):
                result = await decoder.get_signing_key("mock-token")

                assert result["kid"] == "test-kid"

    @pytest.mark.asyncio
    async def test_get_signing_key_missing_kid(self):
        """Test handling token without key ID."""
        with patch.object(jwt, "get_unverified_header") as mock_header:
            mock_header.return_value = {"alg": "RS256"}  # No kid

            decoder = JWTDecoder()
            result = await decoder.get_signing_key("mock-token")

            assert result is None

    @pytest.mark.asyncio
    async def test_get_signing_key_unsupported_algorithm(self):
        """Test handling unsupported algorithm."""
        with patch.object(jwt, "get_unverified_header") as mock_header:
            mock_header.return_value = {"alg": "HS256", "kid": "test-kid"}

            decoder = JWTDecoder()
            result = await decoder.get_signing_key("mock-token")

            assert result is None

    @pytest.mark.asyncio
    async def test_get_signing_key_unknown_kid_retry(self):
        """Test retrying with fresh JWKS for unknown key ID."""
        cached_jwks = {"keys": [{"kid": "old-kid", "kty": "RSA"}]}
        fresh_jwks = {"keys": [{"kid": "new-kid", "kty": "RSA"}]}

        with patch.object(jwt, "get_unverified_header") as mock_header:
            mock_header.return_value = {"alg": "RS256", "kid": "new-kid"}

            decoder = JWTDecoder()

            call_count = 0

            async def mock_get_jwks(bypass_cache=False):
                nonlocal call_count
                call_count += 1
                if bypass_cache:
                    return fresh_jwks
                return cached_jwks

            with patch.object(decoder, "get_jwks", side_effect=mock_get_jwks):
                result = await decoder.get_signing_key("mock-token")

                assert result["kid"] == "new-kid"
                assert call_count == 2  # Called twice: cache then fresh

    @pytest.mark.asyncio
    async def test_get_signing_key_unknown_kid_not_in_fresh(self):
        """Test when key ID not found even after refresh."""
        mock_jwks = {"keys": [{"kid": "other-kid", "kty": "RSA"}]}

        with patch.object(jwt, "get_unverified_header") as mock_header:
            mock_header.return_value = {"alg": "RS256", "kid": "unknown-kid"}

            decoder = JWTDecoder()

            with patch.object(decoder, "get_jwks", return_value=mock_jwks):
                result = await decoder.get_signing_key("mock-token")

                assert result is None

    @pytest.mark.asyncio
    async def test_get_signing_key_exception(self):
        """Test handling exception during key retrieval."""
        with patch.object(jwt, "get_unverified_header") as mock_header:
            mock_header.side_effect = Exception("Invalid token")

            decoder = JWTDecoder()
            result = await decoder.get_signing_key("invalid-token")

            assert result is None


class TestDecodeToken:
    """Tests for decode_token method."""

    @pytest.mark.asyncio
    async def test_decode_token_success(self):
        """Test successful token decoding."""
        mock_payload = {
            "sub": "user-123",
            "email": "test@example.com",
            "exp": int(time.time()) + 3600,
        }

        decoder = JWTDecoder()

        with patch.object(decoder, "get_signing_key", return_value={"kid": "test"}):
            with patch.object(jwt, "decode", return_value=mock_payload):
                result = await decoder.decode_token("valid-token")

                assert result == mock_payload

    @pytest.mark.asyncio
    async def test_decode_token_strips_bearer_prefix(self):
        """Test that Bearer prefix is stripped."""
        decoder = JWTDecoder()

        with patch.object(decoder, "get_signing_key", return_value={"kid": "test"}):
            with patch.object(jwt, "decode", return_value={"sub": "user"}) as mock_decode:
                await decoder.decode_token("Bearer valid-token")

                # Verify the token passed to decode doesn't have Bearer prefix
                call_args = mock_decode.call_args
                assert call_args[0][0] == "valid-token"

    @pytest.mark.asyncio
    async def test_decode_token_no_signing_key(self):
        """Test when signing key cannot be determined."""
        decoder = JWTDecoder()

        with patch.object(decoder, "get_signing_key", return_value=None):
            result = await decoder.decode_token("token-without-key")

            assert result is None

    @pytest.mark.asyncio
    async def test_decode_token_expired(self):
        """Test handling expired token."""
        from jose.exceptions import ExpiredSignatureError

        decoder = JWTDecoder()

        with patch.object(decoder, "get_signing_key", return_value={"kid": "test"}):
            with patch.object(jwt, "decode", side_effect=ExpiredSignatureError("Expired")):
                result = await decoder.decode_token("expired-token")

                assert result is None

    @pytest.mark.asyncio
    async def test_decode_token_jwt_error(self):
        """Test handling JWT error."""
        from jose import JWTError

        decoder = JWTDecoder()

        with patch.object(decoder, "get_signing_key", return_value={"kid": "test"}):
            with patch.object(jwt, "decode", side_effect=JWTError("Invalid")):
                result = await decoder.decode_token("invalid-token")

                assert result is None


class TestGetUserFromToken:
    """Tests for get_user_from_token method."""

    @pytest.mark.asyncio
    async def test_get_user_from_token_success(self):
        """Test extracting user data from token."""
        mock_payload = {
            "sub": "user-123",
            "email": "test@example.com",
            "email_confirmed_at": "2024-01-01T00:00:00Z",
            "phone": "+1234567890",
            "app_metadata": {"provider": "email"},
            "user_metadata": {"full_name": "Test User", "avatar_url": "https://example.com/avatar.jpg"},
            "role": "authenticated",
            "aal": "aal1",
            "session_id": "session-123",
            "exp": 1234567890,
            "iat": 1234567800,
        }

        decoder = JWTDecoder()

        with patch.object(decoder, "decode_token", return_value=mock_payload):
            result = await decoder.get_user_from_token("valid-token")

            assert result["id"] == "user-123"
            assert result["email"] == "test@example.com"
            assert result["email_verified"] is True
            assert result["full_name"] == "Test User"
            assert result["avatar_url"] == "https://example.com/avatar.jpg"
            assert result["role"] == "authenticated"

    @pytest.mark.asyncio
    async def test_get_user_from_token_no_metadata(self):
        """Test extracting user data without metadata."""
        mock_payload = {
            "sub": "user-123",
            "email": "test@example.com",
            "exp": 1234567890,
        }

        decoder = JWTDecoder()

        with patch.object(decoder, "decode_token", return_value=mock_payload):
            result = await decoder.get_user_from_token("valid-token")

            assert result["id"] == "user-123"
            assert result["full_name"] is None
            assert result["avatar_url"] is None

    @pytest.mark.asyncio
    async def test_get_user_from_token_invalid(self):
        """Test with invalid token."""
        decoder = JWTDecoder()

        with patch.object(decoder, "decode_token", return_value=None):
            result = await decoder.get_user_from_token("invalid-token")

            assert result is None


class TestIsTokenExpired:
    """Tests for is_token_expired method."""

    @pytest.mark.asyncio
    async def test_token_not_expired(self):
        """Test valid non-expired token."""
        mock_payload = {"exp": int(time.time()) + 3600}  # Expires in 1 hour

        decoder = JWTDecoder()

        with patch.object(decoder, "decode_token", return_value=mock_payload):
            result = await decoder.is_token_expired("valid-token")

            assert result is False

    @pytest.mark.asyncio
    async def test_token_expired(self):
        """Test expired token."""
        mock_payload = {"exp": int(time.time()) - 3600}  # Expired 1 hour ago

        decoder = JWTDecoder()

        with patch.object(decoder, "decode_token", return_value=mock_payload):
            result = await decoder.is_token_expired("expired-token")

            assert result is True

    @pytest.mark.asyncio
    async def test_token_no_exp(self):
        """Test token without expiration."""
        mock_payload = {"sub": "user-123"}  # No exp field

        decoder = JWTDecoder()

        with patch.object(decoder, "decode_token", return_value=mock_payload):
            result = await decoder.is_token_expired("no-exp-token")

            assert result is True

    @pytest.mark.asyncio
    async def test_invalid_token(self):
        """Test invalid token returns expired."""
        decoder = JWTDecoder()

        with patch.object(decoder, "decode_token", return_value=None):
            result = await decoder.is_token_expired("invalid-token")

            assert result is True


class TestGetTokenRemainingTime:
    """Tests for get_token_remaining_time method."""

    @pytest.mark.asyncio
    async def test_get_remaining_time(self):
        """Test getting remaining time for valid token."""
        future_time = int(time.time()) + 3600
        mock_payload = {"exp": future_time}

        decoder = JWTDecoder()

        with patch.object(decoder, "decode_token", return_value=mock_payload):
            result = await decoder.get_token_remaining_time("valid-token")

            assert result is not None
            assert result > 3500  # Should be close to 3600

    @pytest.mark.asyncio
    async def test_get_remaining_time_expired(self):
        """Test remaining time for expired token is 0."""
        past_time = int(time.time()) - 3600
        mock_payload = {"exp": past_time}

        decoder = JWTDecoder()

        with patch.object(decoder, "decode_token", return_value=mock_payload):
            result = await decoder.get_token_remaining_time("expired-token")

            assert result == 0

    @pytest.mark.asyncio
    async def test_get_remaining_time_invalid(self):
        """Test remaining time for invalid token is None."""
        decoder = JWTDecoder()

        with patch.object(decoder, "decode_token", return_value=None):
            result = await decoder.get_token_remaining_time("invalid-token")

            assert result is None


class TestValidateToken:
    """Tests for validate_token method."""

    @pytest.mark.asyncio
    async def test_validate_valid_token(self):
        """Test validating a valid token."""
        decoder = JWTDecoder()

        with patch.object(decoder, "decode_token", return_value={"sub": "user"}):
            result = await decoder.validate_token("valid-token")

            assert result is True

    @pytest.mark.asyncio
    async def test_validate_invalid_token(self):
        """Test validating an invalid token."""
        decoder = JWTDecoder()

        with patch.object(decoder, "decode_token", return_value=None):
            result = await decoder.validate_token("invalid-token")

            assert result is False
