"""Tests for user models."""

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from app.users.models import User, UserProfile


class TestUserModel:
    """Tests for User model."""

    def test_user_str_representation(self):
        """Test user string representation."""
        user = User(
            id=uuid4(),
            email="test@example.com",
            full_name="Test User",
            supabase_id="test-supabase-id",
        )

        result = str(user)

        assert "Test User" in result
        assert "test@example.com" in result

    def test_user_column_defaults_defined(self):
        """Test user model has defaults defined in column mapping."""
        from sqlalchemy import inspect
        mapper = inspect(User)

        # Check various columns have defaults
        credits_col = mapper.columns['credits']
        assert credits_col.default is not None
        assert credits_col.default.arg == 0

        is_active_col = mapper.columns['is_active']
        assert is_active_col.default is not None
        assert is_active_col.default.arg is True

        is_admin_col = mapper.columns['is_admin']
        assert is_admin_col.default is not None
        assert is_admin_col.default.arg is False

    def test_user_with_explicit_defaults(self):
        """Test user with explicit default values."""
        user = User(
            id=uuid4(),
            email="test@example.com",
            full_name="Test User",
            supabase_id="test-supabase-id",
            credits=0,
            is_active=True,
            is_admin=False,
            is_staff=False,
            email_notifications=True,
            marketing_emails=False,
        )

        assert user.credits == 0
        assert user.is_active is True
        assert user.is_admin is False
        assert user.is_staff is False
        assert user.email_notifications is True
        assert user.marketing_emails is False
        assert user.password is None
        assert user.last_login is None
        assert user.last_purchase_date is None
        assert user.deleted_at is None

    def test_user_tablename(self):
        """Test User model has correct table name."""
        assert User.__tablename__ == "users"

    def test_set_password(self):
        """Test password hashing."""
        user = User(
            id=uuid4(),
            email="test@example.com",
            full_name="Test User",
            supabase_id="test-supabase-id",
        )

        user.set_password("secure123")

        assert user.password is not None
        assert user.password != "secure123"
        assert len(user.password) > 20  # bcrypt hashes are long

    def test_check_password_correct(self):
        """Test password verification with correct password."""
        user = User(
            id=uuid4(),
            email="test@example.com",
            full_name="Test User",
            supabase_id="test-supabase-id",
        )

        user.set_password("secure123")

        assert user.check_password("secure123") is True

    def test_check_password_incorrect(self):
        """Test password verification with incorrect password."""
        user = User(
            id=uuid4(),
            email="test@example.com",
            full_name="Test User",
            supabase_id="test-supabase-id",
        )

        user.set_password("secure123")

        assert user.check_password("wrong") is False

    def test_check_password_no_password_set(self):
        """Test password verification when no password is set."""
        user = User(
            id=uuid4(),
            email="test@example.com",
            full_name="Test User",
            supabase_id="test-supabase-id",
        )

        assert user.check_password("any") is False

    def test_user_with_all_fields(self):
        """Test user with all fields set."""
        user_id = uuid4()
        now = datetime.now(timezone.utc)

        user = User(
            id=user_id,
            email="admin@example.com",
            full_name="Admin User",
            supabase_id="admin-supabase-id",
            credits=500,
            last_login=now,
            last_purchase_date=now,
            is_active=True,
            is_admin=True,
            is_staff=True,
            email_notifications=False,
            marketing_emails=True,
        )

        assert user.id == user_id
        assert user.email == "admin@example.com"
        assert user.credits == 500
        assert user.is_admin is True
        assert user.is_staff is True
        assert user.email_notifications is False
        assert user.marketing_emails is True


class TestUserProfileModel:
    """Tests for UserProfile model."""

    def test_profile_tablename(self):
        """Test UserProfile model has correct table name."""
        assert UserProfile.__tablename__ == "user_profiles"

    def test_profile_column_defaults_defined(self):
        """Test profile model has defaults defined in column mapping."""
        from sqlalchemy import inspect
        mapper = inspect(UserProfile)

        # Check avatar_version has default
        avatar_version_col = mapper.columns['avatar_version']
        assert avatar_version_col.default is not None
        assert avatar_version_col.default.arg == 1

        # Check theme has default
        theme_col = mapper.columns['theme']
        assert theme_col.default is not None
        assert theme_col.default.arg == "system"

    def test_profile_with_explicit_defaults(self):
        """Test profile with explicit default values."""
        profile = UserProfile(
            id=uuid4(),
            user_id=uuid4(),
            avatar_version=1,
            theme="system",
        )

        assert profile.bio is None
        assert profile.phone is None
        assert profile.location is None
        assert profile.avatar_url is None
        assert profile.avatar_version == 1
        assert profile.website_url is None
        assert profile.linkedin_url is None
        assert profile.github_url is None
        assert profile.current_position is None
        assert profile.company is None
        assert profile.theme == "system"

    def test_profile_with_all_fields(self):
        """Test profile with all fields set."""
        profile_id = uuid4()
        user_id = uuid4()

        profile = UserProfile(
            id=profile_id,
            user_id=user_id,
            bio="Software developer with 10 years experience",
            phone="+2348012345678",
            location="Lagos, Nigeria",
            avatar_url="https://cdn.example.com/avatar.jpg",
            avatar_version=3,
            website_url="https://mysite.com",
            linkedin_url="https://linkedin.com/in/testuser",
            github_url="https://github.com/testuser",
            current_position="Senior Developer",
            company="Tech Corp",
            theme="dark",
        )

        assert profile.id == profile_id
        assert profile.user_id == user_id
        assert profile.bio == "Software developer with 10 years experience"
        assert profile.phone == "+2348012345678"
        assert profile.location == "Lagos, Nigeria"
        assert profile.avatar_url == "https://cdn.example.com/avatar.jpg"
        assert profile.avatar_version == 3
        assert profile.website_url == "https://mysite.com"
        assert profile.linkedin_url == "https://linkedin.com/in/testuser"
        assert profile.github_url == "https://github.com/testuser"
        assert profile.current_position == "Senior Developer"
        assert profile.company == "Tech Corp"
        assert profile.theme == "dark"


class TestUserProfileRelationship:
    """Tests for User-UserProfile relationship."""

    def test_user_has_profile_relationship(self):
        """Test User model has profile relationship attribute."""
        user = User(
            id=uuid4(),
            email="test@example.com",
            full_name="Test User",
            supabase_id="test-supabase-id",
        )

        # Profile relationship exists (initially None)
        assert hasattr(user, "profile")

    def test_user_has_payments_relationship(self):
        """Test User model has payments relationship attribute."""
        user = User(
            id=uuid4(),
            email="test@example.com",
            full_name="Test User",
            supabase_id="test-supabase-id",
        )

        # Payments relationship exists
        assert hasattr(user, "payments")

    def test_profile_has_user_relationship(self):
        """Test UserProfile model has user relationship attribute."""
        profile = UserProfile(
            id=uuid4(),
            user_id=uuid4(),
        )

        # User relationship exists
        assert hasattr(profile, "user")
