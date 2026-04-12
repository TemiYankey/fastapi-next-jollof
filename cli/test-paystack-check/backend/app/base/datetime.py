"""Datetime utilities for timezone-aware operations."""

from datetime import datetime, timezone


def utcnow() -> datetime:
    """
    Get current UTC time as timezone-aware datetime.

    Returns timezone-aware datetime instead of deprecated datetime.utcnow().
    Use this throughout the app for consistency.

    Returns:
        datetime: Current UTC time with timezone info
    """
    return datetime.now(timezone.utc)
