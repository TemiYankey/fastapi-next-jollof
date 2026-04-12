"""
Rate limiting configuration using SlowAPI with Redis backend.

Production-ready rate limits to prevent abuse:
- Auth endpoints: Strict limits to prevent brute force
- Payment endpoints: Strict limits to prevent fraud
- General API: Reasonable limits for normal usage
"""

import logging

from fastapi import Request, Response
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.responses import JSONResponse

from app.base.testing.utils import is_testing_environment
from app.core.config import settings

logger = logging.getLogger("app.rate_limiter")

# Disable rate limiting during tests
_is_testing = is_testing_environment()


def get_user_identifier(request: Request) -> str:
    """
    Get identifier for rate limiting.
    Uses user ID if authenticated, otherwise falls back to IP address.
    """
    # Try to get user from request state (set by auth middleware)
    user = getattr(request.state, "user", None)
    if user and hasattr(user, "id"):
        return f"user:{user.id}"

    # Fall back to IP address
    return get_remote_address(request)


def get_ip_address(request: Request) -> str:
    """Always use IP address for rate limiting (for auth endpoints)."""
    return get_remote_address(request)


# Initialize limiter with Redis storage
# Falls back to memory if Redis URL not configured
# Disabled during tests to avoid rate limit interference
storage_uri = settings.redis_url if settings.redis_url else "memory://"

limiter = Limiter(
    key_func=get_user_identifier,
    storage_uri=storage_uri,
    strategy="fixed-window",
    enabled=not _is_testing,
)

# Create a separate limiter for auth routes (always use IP)
auth_limiter = Limiter(
    key_func=get_ip_address,
    storage_uri=storage_uri,
    strategy="fixed-window",
    enabled=not _is_testing,
)


async def rate_limit_exceeded_handler(
    request: Request, exc: RateLimitExceeded
) -> Response:
    """Custom handler for rate limit exceeded errors."""
    logger.warning(
        f"Rate limit exceeded: {exc.detail} - "
        f"IP: {get_remote_address(request)} - "
        f"Path: {request.url.path}"
    )

    return JSONResponse(
        status_code=429,
        content={
            "detail": "Too many requests. Please slow down and try again later.",
            "retry_after": exc.detail.split("per")[1].strip()
            if "per" in exc.detail
            else "1 minute",
        },
        headers={
            "Retry-After": "60",
            "X-RateLimit-Limit": exc.detail,
        },
    )


# =============================================================================
# Rate Limit Constants
# =============================================================================
# Note: Supabase handles auth rate limiting (login, signup, password reset).
# These limits are for your API endpoints only.

# General API endpoints - generous for authenticated users
GENERAL_LIMIT = "200/minute"

# Checkout/payment creation - stricter to prevent duplicate orders
CHECKOUT_LIMIT = "20/minute"

# Public endpoints (pricing, plans, etc.) - generous
PUBLIC_LIMIT = "200/minute"

# File uploads - moderate
UPLOAD_LIMIT = "30/minute"

# Webhooks - NO rate limiting (signature verification is sufficient)
# Payment providers retry on failure, so don't block them
