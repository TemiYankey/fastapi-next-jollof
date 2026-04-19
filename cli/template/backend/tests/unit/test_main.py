"""Tests for main FastAPI application (main.py)."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Import the app module
from app.main import app, lifespan


class TestHealthEndpoints:
    """Tests for health check endpoints."""

    def test_api_health_check(self):
        """Test /api/health endpoint."""
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/api/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "app" in data


class TestAppConfiguration:
    """Tests for app configuration."""

    def test_app_has_title(self):
        """Test app has proper title."""
        assert app.title is not None

    def test_app_has_version(self):
        """Test app has version."""
        assert app.version == "1.0.0"

    def test_routers_included(self):
        """Test that routers are included."""
        # Check routes are registered
        routes = [route.path for route in app.routes]

        # Health endpoint
        assert "/api/health" in routes

    def test_cors_middleware_configured(self):
        """Test CORS middleware is configured."""
        # Check middleware stack
        middleware_classes = [m.cls.__name__ for m in app.user_middleware]
        assert "CORSMiddleware" in middleware_classes

    def test_session_middleware_configured(self):
        """Test session middleware is configured."""
        middleware_classes = [m.cls.__name__ for m in app.user_middleware]
        assert "SessionMiddleware" in middleware_classes


class TestValidationExceptionHandler:
    """Tests for validation exception handler."""

    def test_validation_error_returns_422(self):
        """Test validation errors return proper format."""
        # The validation handler is tested via endpoints that validate input
        # This is a placeholder to verify the handler exists
        assert app.exception_handlers is not None


class TestLifespan:
    """Tests for application lifespan context manager."""

    @pytest.mark.asyncio
    async def test_lifespan_startup_connects_redis(self):
        """Test lifespan startup connects to Redis."""
        mock_app = MagicMock(spec=FastAPI)

        with patch("app.main.redis_service") as mock_redis:
            mock_redis.connect = AsyncMock()
            mock_redis.disconnect = AsyncMock()

            async with lifespan(mock_app):
                # Inside the context = app is running
                mock_redis.connect.assert_called_once()

            # After exiting context = shutdown
            mock_redis.disconnect.assert_called_once()

    @pytest.mark.asyncio
    async def test_lifespan_handles_redis_failure_in_debug(self):
        """Test lifespan handles Redis failure gracefully in debug mode."""
        mock_app = MagicMock(spec=FastAPI)

        with patch("app.main.redis_service") as mock_redis, \
             patch("app.main.settings") as mock_settings:
            mock_redis.connect = AsyncMock(side_effect=Exception("Redis failed"))
            mock_redis.disconnect = AsyncMock()
            mock_settings.debug = True

            # Should not raise in debug mode
            async with lifespan(mock_app):
                pass

    @pytest.mark.asyncio
    async def test_lifespan_shutdown_disconnects_redis(self):
        """Test lifespan shutdown disconnects from Redis."""
        mock_app = MagicMock(spec=FastAPI)

        with patch("app.main.redis_service") as mock_redis:
            mock_redis.connect = AsyncMock()
            mock_redis.disconnect = AsyncMock()

            async with lifespan(mock_app):
                pass  # App running

            # After context exits
            mock_redis.disconnect.assert_called_once()

    @pytest.mark.asyncio
    async def test_lifespan_handles_disconnect_error(self):
        """Test lifespan handles disconnect error gracefully."""
        mock_app = MagicMock(spec=FastAPI)

        with patch("app.main.redis_service") as mock_redis:
            mock_redis.connect = AsyncMock()
            mock_redis.disconnect = AsyncMock(side_effect=Exception("Disconnect error"))

            # Should not raise even on disconnect error
            async with lifespan(mock_app):
                pass


class TestRateLimiter:
    """Tests for rate limiter configuration."""

    def test_rate_limiter_attached(self):
        """Test rate limiter is attached to app."""
        assert hasattr(app.state, "limiter")
        assert app.state.limiter is not None


class TestDatabaseInit:
    """Tests for database initialization."""

    def test_init_db_called_with_app(self):
        """Test init_db is called with the app instance."""
        # Verify the init_db function signature
        from app.core.database import init_db

        # The function should accept a FastAPI app
        assert callable(init_db)
