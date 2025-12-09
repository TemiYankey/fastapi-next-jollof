"""Test factories for users module."""

from datetime import datetime, timezone
from unittest.mock import MagicMock


class UserFactory:
    """Factory for creating User test objects."""

    @staticmethod
    def create(
        id: str = "user-123-uuid",
        email: str = "test@example.com",
        full_name: str = "Test User",
        is_active: bool = True,
        last_login: datetime | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> MagicMock:
        """Create a User mock with defaults."""
        user = MagicMock()
        user.id = id
        user.email = email
        user.full_name = full_name
        user.is_active = is_active
        user.last_login = last_login or datetime.now(timezone.utc)
        user.created_at = created_at or datetime.now(timezone.utc)
        user.updated_at = updated_at or datetime.now(timezone.utc)
        return user

    @staticmethod
    def create_new_user(
        id: str = "new-user-456",
        email: str = "newuser@example.com",
        full_name: str = "New User",
    ) -> MagicMock:
        """Create a new user without last_login."""
        return UserFactory.create(
            id=id,
            email=email,
            full_name=full_name,
            last_login=None,
        )


class UserProfileFactory:
    """Factory for creating UserProfile test objects."""

    @staticmethod
    def create(
        id: str = "profile-123-uuid",
        user_id: str = "user-123-uuid",
        bio: str | None = "Test bio",
        phone: str | None = "+1234567890",
        location: str | None = "Lagos, Nigeria",
        theme: str = "system",
        email_notifications: bool = True,
        marketing_emails: bool = False,
    ) -> MagicMock:
        """Create a UserProfile mock with defaults."""
        profile = MagicMock()
        profile.id = id
        profile.user_id = user_id
        profile.bio = bio
        profile.phone = phone
        profile.location = location
        profile.theme = theme
        profile.email_notifications = email_notifications
        profile.marketing_emails = marketing_emails
        return profile


class TokenPayloadFactory:
    """Factory for creating JWT token payloads."""

    @staticmethod
    def create(
        sub: str = "user-123-uuid",
        email: str = "test@example.com",
        exp: int | None = None,
    ) -> dict:
        """Create a token payload with defaults."""
        import time

        return {
            "sub": sub,
            "email": email,
            "exp": exp or int(time.time()) + 3600,  # 1 hour from now
        }
