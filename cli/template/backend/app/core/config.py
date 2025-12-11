"""Application configuration."""

import os

from pydantic_settings import SettingsConfigDict

from app.base.config import BaseAppSettings


class Settings(BaseAppSettings):
    """Application settings."""

    # App - CUSTOMIZE THESE FOR YOUR PROJECT
    app_name: str = "Jollof App"
    app_description: str = "A production-ready FastAPI + Next.js boilerplate"
    debug: bool = False
    environment: str = "development"  # development, staging, production, testing
    allowed_hosts: list[str] = ["*"]

    # Theme/Branding - CUSTOMIZE FOR YOUR PROJECT
    primary_color: str = "#6366f1"  # Indigo
    secondary_color: str = "#ec4899"  # Pink

    # Database
    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/jollofdb"

    # Supabase Auth
    supabase_url: str = ""
    supabase_public_key: str = ""
    supabase_secret_key: str = ""
    supabase_jwt_secret: str = ""

    # Google OAuth (optional)
    google_oauth_client_id: str = ""
    google_oauth_client_secret: str = ""

    # Payment - Nomba (Nigeria) - TESTED
    nomba_client_id: str = ""
    nomba_client_secret: str = ""
    nomba_account_id: str = ""
    nomba_webhook_secret: str = ""

    # Payment - Stripe (Global)
    stripe_secret_key: str = ""
    stripe_publishable_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_currency: str = "usd"

    # Payment - Paystack (Africa)
    paystack_secret_key: str = ""
    paystack_public_key: str = ""
    paystack_webhook_secret: str = ""

    # Default payment provider: nomba, paystack, stripe
    default_payment_provider: str = "nomba"

    # Email - Resend (recommended)
    resend_api_key: str = ""
    from_email: str = ""
    from_name: str = ""  # Email sender name

    # Email - Brevo (alternative)
    brevo_api_key: str = ""

    # Default email provider: resend, brevo
    default_email_provider: str = "resend"

    # Security
    secret_key: str = ""
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # CORS - comma-separated origins (e.g., "http://localhost:3000,https://yourapp.com")
    cors_allowed_origins: str = ""

    # Redis
    redis_url: str = "redis://localhost:6379"

    # Sentry (Error Tracking - Production Only)
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
