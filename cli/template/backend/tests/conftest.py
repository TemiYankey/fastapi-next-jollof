"""
Pytest configuration and shared test setup.

This file is for:
- Environment setup (must run before app imports)
- Session-scoped fixtures (event loop, database)
- Pytest hooks and plugins

For test data/mocks, use factories in each test module's factories.py
"""

import os
from collections.abc import Generator

import pytest

# =============================================================================
# ENVIRONMENT SETUP - Must run before any app imports
# =============================================================================
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["SUPABASE_URL"] = "https://test.supabase.co"
os.environ["SUPABASE_PUBLIC_KEY"] = "test-public-key"
os.environ["SUPABASE_SECRET_KEY"] = "test-secret-key"
os.environ["SUPABASE_JWT_SECRET"] = "test-jwt-secret"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing"
os.environ["RESEND_API_KEY"] = "re_test_key"
os.environ["BREVO_API_KEY"] = "xkeysib_test_key"
os.environ["FROM_EMAIL"] = "test@example.com"
os.environ["FROM_NAME"] = "Test App"
os.environ["REDIS_URL"] = "redis://localhost:6379"


# =============================================================================
# SESSION-SCOPED FIXTURES
# =============================================================================
@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests."""
    import asyncio

    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
