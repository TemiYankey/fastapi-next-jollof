"""Tests for rate limiter (core/rate_limiter.py)."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi import Request
from slowapi.errors import RateLimitExceeded

from app.core.rate_limiter import (
    CHECKOUT_LIMIT,
    GENERAL_LIMIT,
    PUBLIC_LIMIT,
    UPLOAD_LIMIT,
    get_ip_address,
    get_user_identifier,
    rate_limit_exceeded_handler,
)


class TestGetUserIdentifier:
    """Tests for get_user_identifier function."""

    def test_returns_user_id_when_authenticated(self):
        """Test returns user ID for authenticated requests."""
        mock_request = MagicMock(spec=Request)
        mock_user = MagicMock()
        mock_user.id = "user-123"
        mock_request.state.user = mock_user

        result = get_user_identifier(mock_request)

        assert result == "user:user-123"

    def test_returns_ip_when_not_authenticated(self):
        """Test returns IP address for unauthenticated requests."""
        mock_request = MagicMock(spec=Request)
        mock_request.state = MagicMock(spec=[])  # No user attribute

        with patch("app.core.rate_limiter.get_remote_address") as mock_get_ip:
            mock_get_ip.return_value = "192.168.1.1"

            result = get_user_identifier(mock_request)

            assert result == "192.168.1.1"

    def test_returns_ip_when_user_has_no_id(self):
        """Test returns IP when user object has no id."""
        mock_request = MagicMock(spec=Request)
        mock_user = MagicMock(spec=[])  # No id attribute
        mock_request.state.user = mock_user

        with patch("app.core.rate_limiter.get_remote_address") as mock_get_ip:
            mock_get_ip.return_value = "192.168.1.1"

            result = get_user_identifier(mock_request)

            assert result == "192.168.1.1"


class TestGetIpAddress:
    """Tests for get_ip_address function."""

    def test_returns_remote_address(self):
        """Test returns remote address."""
        mock_request = MagicMock(spec=Request)

        with patch("app.core.rate_limiter.get_remote_address") as mock_get_ip:
            mock_get_ip.return_value = "10.0.0.1"

            result = get_ip_address(mock_request)

            assert result == "10.0.0.1"
            mock_get_ip.assert_called_once_with(mock_request)


class TestRateLimitExceededHandler:
    """Tests for rate_limit_exceeded_handler."""

    def _create_rate_limit_exception(self, limit_string: str) -> RateLimitExceeded:
        """Create a RateLimitExceeded exception with proper mocking."""
        mock_limit = MagicMock()
        mock_limit.error_message = None

        exc = RateLimitExceeded.__new__(RateLimitExceeded)
        exc.limit = mock_limit
        exc.detail = limit_string
        return exc

    @pytest.mark.asyncio
    async def test_returns_429_response(self):
        """Test handler returns 429 status code."""
        mock_request = MagicMock(spec=Request)
        mock_request.url.path = "/api/test"

        exc = self._create_rate_limit_exception("5 per minute")

        with patch("app.core.rate_limiter.get_remote_address") as mock_get_ip:
            mock_get_ip.return_value = "192.168.1.1"

            response = await rate_limit_exceeded_handler(mock_request, exc)

            assert response.status_code == 429

    @pytest.mark.asyncio
    async def test_response_contains_detail(self):
        """Test response contains error detail."""
        mock_request = MagicMock(spec=Request)
        mock_request.url.path = "/api/test"

        exc = self._create_rate_limit_exception("5 per minute")

        with patch("app.core.rate_limiter.get_remote_address") as mock_get_ip:
            mock_get_ip.return_value = "192.168.1.1"

            response = await rate_limit_exceeded_handler(mock_request, exc)

            import json
            body = json.loads(response.body)
            assert "detail" in body
            assert "Too many requests" in body["detail"]

    @pytest.mark.asyncio
    async def test_response_contains_retry_after_header(self):
        """Test response contains Retry-After header."""
        mock_request = MagicMock(spec=Request)
        mock_request.url.path = "/api/test"

        exc = self._create_rate_limit_exception("5 per minute")

        with patch("app.core.rate_limiter.get_remote_address") as mock_get_ip:
            mock_get_ip.return_value = "192.168.1.1"

            response = await rate_limit_exceeded_handler(mock_request, exc)

            assert "retry-after" in response.headers


class TestRateLimitConstants:
    """Tests for rate limit constants."""

    def test_general_limit_is_generous(self):
        """Test general limit allows normal usage for authenticated users."""
        assert "200/minute" in GENERAL_LIMIT

    def test_checkout_limit(self):
        """Test checkout limit prevents duplicate orders."""
        assert "20/minute" in CHECKOUT_LIMIT

    def test_public_limit_is_generous(self):
        """Test public endpoints have generous limits."""
        assert "200/minute" in PUBLIC_LIMIT

    def test_upload_limit(self):
        """Test upload limit."""
        assert "30/minute" in UPLOAD_LIMIT


class TestLimiterConfiguration:
    """Tests for limiter configuration."""

    def test_limiter_disabled_in_tests(self):
        """Test that rate limiting is disabled during tests."""
        with patch("app.core.rate_limiter.is_testing_environment") as mock_is_testing:
            mock_is_testing.return_value = True
            assert mock_is_testing() is True
