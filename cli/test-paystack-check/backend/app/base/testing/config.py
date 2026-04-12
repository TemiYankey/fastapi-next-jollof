"""Test configuration - Safe defaults for testing.

This module provides TestSettings with safe hardcoded defaults that
NEVER connect to production systems. Used by conftest.py.
"""

from pydantic_settings import SettingsConfigDict

from app.base.config import BaseAppSettings


class TestSettings(BaseAppSettings):
    """
    Safe settings for testing - NEVER connects to production.

    These defaults are used when running tests to ensure:
    1. Database is always SQLite in-memory (safe)
    2. Environment is always "testing"
    3. All API keys are fake test values
    4. No .env files are loaded (env_file=None)
    """

    # FORCED safe defaults for testing
    environment: str = "testing"
    debug: bool = False
    database_url: str = "sqlite+aiosqlite:///:memory:"

    # App defaults
    app_name: str = "Test App"
    app_description: str = "Test application"
    allowed_hosts: list[str] = ["*"]
    primary_color: str = "#6366f1"
    secondary_color: str = "#ec4899"

    # Test Supabase values
    supabase_url: str = "https://test.supabase.co"
    supabase_public_key: str = "test-public-key"
    supabase_secret_key: str = "test-secret-key"
    supabase_jwt_secret: str = "test-jwt-secret"

    # Test Google OAuth
    google_oauth_client_id: str = ""
    google_oauth_client_secret: str = ""

    # Test security
    secret_key: str = "test-secret-key-for-testing-only"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    cors_allowed_origins: str = "http://localhost:3000,http://localhost:8000"

    # Test email - all providers (only one will be used)
    from_email: str = "test@example.com"
    from_name: str = "Test App"
    resend_api_key: str = "re_test_key"
    brevo_api_key: str = "xkeysib_test_key"
    default_email_provider: str = "resend"

    # Test payment - Nomba
    nomba_client_id: str = "test-client-id"
    nomba_client_secret: str = "test-client-secret"
    nomba_account_id: str = "test-account-id"
    nomba_webhook_secret: str = "test-webhook-secret"

    # Test payment - Stripe
    stripe_secret_key: str = "sk_test_key"
    stripe_publishable_key: str = "pk_test_key"
    stripe_webhook_secret: str = "whsec_test_key"
    stripe_currency: str = "usd"

    # Test payment - Paystack
    paystack_secret_key: str = "sk_test_key"
    paystack_public_key: str = "pk_test_key"
    paystack_webhook_secret: str = "test-webhook-secret"
    default_payment_provider: str = "nomba"

    # Redis
    redis_url: str = "redis://localhost:6379"

    # Sentry (disabled in tests)
    sentry_dsn: str = ""

    model_config = SettingsConfigDict(
        env_file=None,  # CRITICAL: Ignore all .env files in tests
        env_file_encoding="utf-8",
    )

    @property
    def is_testing(self) -> bool:
        """Always true for TestSettings."""
        return True

    @property
    def is_production(self) -> bool:
        """Always false for TestSettings."""
        return False
