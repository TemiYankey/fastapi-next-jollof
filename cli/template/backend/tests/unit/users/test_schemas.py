"""Tests for user schemas."""

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.users.schemas import (
    CompleteUserProfileSchema,
    ProfileUpdateSchema,
    UserCreate,
    UserProfileSchema,
    UserResponse,
    UserUpdate,
)


class TestUserResponse:
    """Tests for UserResponse schema."""

    def test_valid_user_response(self):
        """Test valid user response."""
        now = datetime.now(timezone.utc)

        response = UserResponse(
            id="user-123",
            email="test@example.com",
            full_name="Test User",
            created_at=now,
            last_login=now,
        )

        assert response.id == "user-123"
        assert response.email == "test@example.com"
        assert response.full_name == "Test User"
        assert response.created_at == now
        assert response.last_login == now

    def test_user_response_optional_last_login(self):
        """Test user response with optional last_login."""
        now = datetime.now(timezone.utc)

        response = UserResponse(
            id="user-123",
            email="test@example.com",
            full_name="Test User",
            created_at=now,
        )

        assert response.last_login is None

    def test_user_response_missing_required_fields(self):
        """Test user response missing required fields."""
        with pytest.raises(ValidationError):
            UserResponse(
                id="user-123",
                # Missing email, full_name, created_at
            )


class TestUserCreate:
    """Tests for UserCreate schema."""

    def test_valid_user_create(self):
        """Test valid user creation schema."""
        user_create = UserCreate(
            email="new@example.com",
            full_name="New User",
            supabase_id="supabase-id-123",
        )

        assert user_create.email == "new@example.com"
        assert user_create.full_name == "New User"
        assert user_create.supabase_id == "supabase-id-123"

    def test_user_create_missing_fields(self):
        """Test user creation with missing fields."""
        with pytest.raises(ValidationError):
            UserCreate(
                email="test@example.com",
                # Missing full_name and supabase_id
            )


class TestUserUpdate:
    """Tests for UserUpdate schema."""

    def test_user_update_with_name(self):
        """Test user update with full name."""
        update = UserUpdate(full_name="Updated Name")

        assert update.full_name == "Updated Name"

    def test_user_update_empty(self):
        """Test user update with no fields."""
        update = UserUpdate()

        assert update.full_name is None


class TestUserProfileSchema:
    """Tests for UserProfileSchema."""

    def test_profile_default_values(self):
        """Test profile schema default values."""
        profile = UserProfileSchema()

        assert profile.id is None
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
        """Test profile schema with all fields."""
        profile = UserProfileSchema(
            id="profile-123",
            bio="A developer bio",
            phone="+1234567890",
            location="New York",
            avatar_url="https://example.com/avatar.jpg",
            avatar_version=5,
            website_url="https://mysite.com",
            linkedin_url="https://linkedin.com/in/test",
            github_url="https://github.com/test",
            current_position="Developer",
            company="Tech Inc",
            theme="dark",
        )

        assert profile.id == "profile-123"
        assert profile.bio == "A developer bio"
        assert profile.theme == "dark"


class TestProfileUpdateSchema:
    """Tests for ProfileUpdateSchema."""

    def test_empty_update(self):
        """Test empty profile update."""
        update = ProfileUpdateSchema()

        assert update.full_name is None
        assert update.phone is None
        assert update.location is None
        assert update.bio is None
        assert update.theme is None

    def test_partial_update(self):
        """Test partial profile update."""
        update = ProfileUpdateSchema(
            full_name="New Name",
            theme="dark",
        )

        assert update.full_name == "New Name"
        assert update.theme == "dark"
        assert update.phone is None  # Not updated

    def test_full_update(self):
        """Test full profile update."""
        update = ProfileUpdateSchema(
            full_name="Full Update",
            phone="+1234567890",
            location="Lagos",
            website_url="https://site.com",
            linkedin_url="https://linkedin.com/in/user",
            github_url="https://github.com/user",
            bio="Updated bio",
            current_position="Manager",
            company="Big Corp",
            theme="light",
        )

        assert update.full_name == "Full Update"
        assert update.phone == "+1234567890"
        assert update.location == "Lagos"
        assert update.website_url == "https://site.com"
        assert update.linkedin_url == "https://linkedin.com/in/user"
        assert update.github_url == "https://github.com/user"
        assert update.bio == "Updated bio"
        assert update.current_position == "Manager"
        assert update.company == "Big Corp"
        assert update.theme == "light"


class TestCompleteUserProfileSchema:
    """Tests for CompleteUserProfileSchema."""

    def test_complete_profile_required_fields(self):
        """Test complete profile with required fields only."""
        now = datetime.now(timezone.utc)

        profile = CompleteUserProfileSchema(
            id="user-123",
            email="test@example.com",
            full_name="Test User",
            created_at=now,
        )

        assert profile.id == "user-123"
        assert profile.email == "test@example.com"
        assert profile.full_name == "Test User"
        assert profile.created_at == now
        # Check defaults
        assert profile.bio is None
        assert profile.avatar_version == 1
        assert profile.theme == "system"

    def test_complete_profile_all_fields(self):
        """Test complete profile with all fields."""
        now = datetime.now(timezone.utc)

        profile = CompleteUserProfileSchema(
            id="user-123",
            email="test@example.com",
            full_name="Test User",
            created_at=now,
            bio="My bio",
            phone="+1234567890",
            location="London",
            avatar_url="https://cdn.com/avatar.jpg",
            avatar_version=3,
            website_url="https://mysite.com",
            linkedin_url="https://linkedin.com/in/me",
            github_url="https://github.com/me",
            current_position="CTO",
            company="Startup",
            theme="dark",
        )

        assert profile.bio == "My bio"
        assert profile.phone == "+1234567890"
        assert profile.avatar_version == 3
        assert profile.theme == "dark"

    def test_complete_profile_missing_required(self):
        """Test complete profile missing required fields."""
        with pytest.raises(ValidationError):
            CompleteUserProfileSchema(
                id="user-123",
                # Missing email, full_name, created_at
            )
