"""Application configuration."""

import os

from pydantic_settings import SettingsConfigDict

from app.base.config import BaseAppSettings


class Settings(BaseAppSettings):
    """Application settings."""

    # App
    app_name: str = "Test Paystack Check"
    app_description: str = "A production-ready FastAPI + Next.js application"
    debug: bool = False
    environment: str = "development"
    allowed_hosts: list[str] = ["*"]

    # Theme/Branding (hex color for email templates)
    primary_color: str = "#6366f1"

    # Database
    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/test_paystack_check"

    # Supabase Auth
    supabase_url: str = ""
    supabase_public_key: str = ""
    supabase_secret_key: str = ""
    supabase_jwt_secret: str = ""

    # Google OAuth (optional)
    google_oauth_client_id: str = ""
    google_oauth_client_secret: str = ""

    # Payment - Paystack
    paystack_secret_key: str = ""
    paystack_public_key: str = ""
    paystack_webhook_secret: str = ""

    # Email - Resend
    resend_api_key: str = ""
    from_email: str = ""
    from_name: str = ""

    # Security
    secret_key: str = ""
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # CORS
    cors_allowed_origins: str = ""

    # Redis
    redis_url: str = "redis://localhost:6379"

    # Sentry (optional)
    sentry_dsn: str = ""

    model_config = SettingsConfigDict(
        env_file=[
            os.environ.get("APP_ENV_FILE", ".env"),  # Override: APP_ENV_FILE=.env.test for tests
            ".env.local",  # Local overrides (gitignored)
            ".env",  # Default
        ],
        env_file_encoding="utf-8",
    )

    @property
    def is_testing(self) -> bool:
        """Check if running in test environment."""
        return self.environment in ("testing", "test")

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"


def get_settings() -> Settings:
    """
    Get the appropriate settings based on environment.

    Returns TestSettings if ENVIRONMENT=testing, otherwise Settings.
    TestSettings is in app.base.testing.config to keep test code separate.
    """
    env = os.environ.get("ENVIRONMENT", "development")
    if env in ("testing", "test"):
        from app.base.testing.config import TestSettings

        return TestSettings()
    return Settings()


# Global settings instance
settings = get_settings()
