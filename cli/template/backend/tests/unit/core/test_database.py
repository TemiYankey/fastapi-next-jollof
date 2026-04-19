"""Tests for database module (core/database.py)."""

from unittest.mock import MagicMock, patch

import pytest

from app.core.database import TORTOISE_ORM, init_db


class TestTortoiseOrmConfig:
    """Tests for TORTOISE_ORM configuration."""

    def test_config_has_connections(self):
        """Test config has connections defined."""
        assert "connections" in TORTOISE_ORM
        assert "default" in TORTOISE_ORM["connections"]

    def test_config_has_apps(self):
        """Test config has apps defined."""
        assert "apps" in TORTOISE_ORM
        assert "users" in TORTOISE_ORM["apps"]
        assert "billing" in TORTOISE_ORM["apps"]

    def test_users_app_has_models_list(self):
        """Test users app has models list."""
        users_app = TORTOISE_ORM["apps"]["users"]
        assert "models" in users_app
        assert isinstance(users_app["models"], list)

    def test_models_includes_user_models(self):
        """Test models includes user models."""
        models = TORTOISE_ORM["apps"]["users"]["models"]
        assert "app.users.models" in models

    def test_models_includes_billing_models(self):
        """Test models includes billing models."""
        models = TORTOISE_ORM["apps"]["billing"]["models"]
        assert "app.billing.models" in models

    def test_default_connection_set(self):
        """Test default connection is set."""
        users_app = TORTOISE_ORM["apps"]["users"]
        assert users_app["default_connection"] == "default"
        billing_app = TORTOISE_ORM["apps"]["billing"]
        assert billing_app["default_connection"] == "default"


class TestInitDb:
    """Tests for init_db function."""

    def test_init_db_calls_register_tortoise(self):
        """Test init_db calls register_tortoise with correct args."""
        mock_app = MagicMock()

        with patch("app.core.database.register_tortoise") as mock_register:
            init_db(mock_app)

            mock_register.assert_called_once()
            call_args = mock_register.call_args

            # Verify app is passed
            assert call_args[0][0] == mock_app

            # Verify config is passed
            assert "config" in call_args[1]
            assert call_args[1]["config"] == TORTOISE_ORM

            # Verify generate_schemas is True
            assert call_args[1]["generate_schemas"] is True

            # Verify exception handlers are added
            assert call_args[1]["add_exception_handlers"] is True
