"""Tests for configuration (core/config.py)."""

import os
from unittest.mock import patch

import pytest


class TestSettings:
    """Tests for Settings configuration."""

    def test_settings_loads_from_env(self):
        """Test that settings loads from environment."""
        from app.core.config import settings

        # These are set in conftest.py
        assert settings.database_url is not None
        assert settings.supabase_url is not None

    def test_settings_has_required_fields(self):
        """Test that settings has all required fields."""
        from app.core.config import settings

        # Core settings
        assert hasattr(settings, "app_name")
        assert hasattr(settings, "environment")
        assert hasattr(settings, "debug")
        assert hasattr(settings, "primary_color")

        # Database
        assert hasattr(settings, "database_url")

        # Auth
        assert hasattr(settings, "supabase_url")
        assert hasattr(settings, "supabase_public_key")
        assert hasattr(settings, "supabase_secret_key")
        assert hasattr(settings, "supabase_jwt_secret")
        assert hasattr(settings, "secret_key")

        # Email
        assert hasattr(settings, "resend_api_key")
        assert hasattr(settings, "from_email")
        assert hasattr(settings, "from_name")

        # Payment
        assert hasattr(settings, "paystack_secret_key")
        assert hasattr(settings, "paystack_public_key")
        assert hasattr(settings, "paystack_webhook_secret")

        # Redis
        assert hasattr(settings, "redis_url")

    def test_environment_is_valid(self):
        """Test environment is a valid value."""
        from app.core.config import settings

        # Valid environment values
        valid_envs = ["development", "production", "test", "testing"]
        assert settings.environment in valid_envs

    def test_debug_is_boolean(self):
        """Test debug is a boolean value."""
        from app.core.config import settings

        assert isinstance(settings.debug, bool)

    def test_cors_allowed_origins(self):
        """Test CORS origins configuration."""
        from app.core.config import settings

        assert hasattr(settings, "cors_allowed_origins")


class TestSettingsEmailProvider:
    """Tests for email provider configuration."""

    def test_primary_color_setting(self):
        """Test primary color for email templates."""
        from app.core.config import settings

        assert hasattr(settings, "primary_color")
        assert settings.primary_color is not None


class TestSettingsValidation:
    """Tests for settings validation."""

    def test_database_url_format(self):
        """Test database URL has valid format."""
        from app.core.config import settings

        # Should be either postgres or sqlite for testing
        assert settings.database_url.startswith(("postgresql", "sqlite"))

    def test_supabase_url_is_https(self):
        """Test Supabase URL uses HTTPS."""
        from app.core.config import settings

        assert settings.supabase_url.startswith("https://")
