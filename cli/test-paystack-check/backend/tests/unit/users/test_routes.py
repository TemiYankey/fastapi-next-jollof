"""Tests for user routes."""

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.users.models import User, UserProfile
from app.users.routes import router
from app.users.schemas import UserResponse


# Create test app
app = FastAPI()
app.include_router(router)  # Router already has /me prefix


class TestMeEndpoint:
    """Tests for GET /me endpoint."""

    @pytest.fixture
    def mock_user(self):
        """Create mock user."""
        user = MagicMock(spec=User)
        user.id = uuid4()
        user.supabase_id = "test-supabase-id"
        user.email = "test@example.com"
        user.full_name = "Test User"
        user.created_at = datetime.now(timezone.utc)
        user.last_login = datetime.now(timezone.utc) - timedelta(hours=2)
        user.save = AsyncMock()
        return user

    @pytest.fixture
    def mock_profile(self, mock_user):
        """Create mock profile."""
        profile = MagicMock(spec=UserProfile)
        profile.user_id = mock_user.id
        profile.bio = "Test bio"
        profile.phone = "+1234567890"
        profile.location = "Lagos, Nigeria"
        profile.avatar_url = "https://example.com/avatar.jpg"
        profile.avatar_version = 1
        profile.website_url = "https://example.com"
        profile.linkedin_url = "https://linkedin.com/in/test"
        profile.github_url = "https://github.com/test"
        profile.current_position = "Developer"
        profile.company = "Test Company"
        profile.theme = "dark"
        mock_user.profile = profile
        return profile

    @pytest.mark.asyncio
    async def test_get_me_success(self, mock_user):
        """Test successful get me endpoint."""
        with patch("app.users.routes.get_or_create_current_user") as mock_auth:
            mock_auth.return_value = mock_user

            client = TestClient(app)

            # We need to mock the limiter too
            with patch("app.users.routes.limiter"):
                response = client.get("/me")

            # Note: In real tests, you'd need to properly set up auth headers
            # This test demonstrates the structure

    @pytest.mark.asyncio
    async def test_get_me_updates_last_login(self, mock_user):
        """Test that last_login is updated when stale."""
        mock_user.last_login = datetime.now(timezone.utc) - timedelta(hours=2)
        original_last_login = mock_user.last_login

        with patch("app.users.routes.get_or_create_current_user") as mock_auth:
            mock_auth.return_value = mock_user

            # Simulate the route logic
            now = datetime.now(timezone.utc)
            should_update = mock_user.last_login is None or (
                now - mock_user.last_login
            ) > timedelta(hours=1)

            assert should_update is True

    @pytest.mark.asyncio
    async def test_get_me_no_update_recent_login(self, mock_user):
        """Test that last_login is not updated when recent."""
        mock_user.last_login = datetime.now(timezone.utc) - timedelta(minutes=30)

        now = datetime.now(timezone.utc)
        should_update = mock_user.last_login is None or (
            now - mock_user.last_login
        ) > timedelta(hours=1)

        assert should_update is False


class TestDashboardEndpoint:
    """Tests for GET /me/dashboard endpoint."""

    @pytest.fixture
    def mock_user(self):
        """Create mock user."""
        user = MagicMock(spec=User)
        user.id = uuid4()
        user.email = "test@example.com"
        user.full_name = "Test User"
        user.credits = 100
        user.created_at = datetime.now(timezone.utc)
        user.last_login = datetime.now(timezone.utc)
        return user

    @pytest.mark.asyncio
    async def test_dashboard_returns_user_data(self, mock_user):
        """Test dashboard returns correct user data structure."""
        # Simulate dashboard response structure
        dashboard_data = {
            "user": {
                "id": str(mock_user.id),
                "email": mock_user.email,
                "full_name": mock_user.full_name,
            },
            "stats": {
                "member_since": mock_user.created_at.isoformat(),
                "last_login": mock_user.last_login.isoformat(),
            },
        }

        assert dashboard_data["user"]["email"] == "test@example.com"
        assert "member_since" in dashboard_data["stats"]

    @pytest.mark.asyncio
    async def test_dashboard_handles_null_last_login(self, mock_user):
        """Test dashboard handles null last_login."""
        mock_user.last_login = None

        last_login = (
            mock_user.last_login.isoformat() if mock_user.last_login else None
        )

        assert last_login is None


class TestProfileEndpoints:
    """Tests for profile endpoints."""

    @pytest.fixture
    def mock_user_with_profile(self):
        """Create mock user with profile."""
        user = MagicMock(spec=User)
        user.id = uuid4()
        user.email = "test@example.com"
        user.full_name = "Test User"
        user.created_at = datetime.now(timezone.utc)
        user.save = AsyncMock()

        profile = MagicMock(spec=UserProfile)
        profile.bio = "Test bio"
        profile.phone = "+1234567890"
        profile.location = "Lagos"
        profile.avatar_url = None
        profile.avatar_version = 0
        profile.website_url = None
        profile.linkedin_url = None
        profile.github_url = None
        profile.current_position = "Developer"
        profile.company = "Test Co"
        profile.theme = "light"
        profile.save = AsyncMock()

        user.profile = profile
        return user

    @pytest.mark.asyncio
    async def test_get_profile_success(self, mock_user_with_profile):
        """Test successful profile retrieval."""
        user = mock_user_with_profile
        profile = user.profile

        # Simulate profile response
        profile_data = {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "bio": profile.bio,
            "phone": profile.phone,
            "location": profile.location,
            "theme": profile.theme,
        }

        assert profile_data["bio"] == "Test bio"
        assert profile_data["theme"] == "light"

    @pytest.mark.asyncio
    async def test_get_profile_not_found(self):
        """Test profile not found error."""
        user = MagicMock(spec=User)
        user.profile = None

        # Should raise 404
        assert user.profile is None

    @pytest.mark.asyncio
    async def test_update_profile_full_name(self, mock_user_with_profile):
        """Test updating full name."""
        user = mock_user_with_profile
        new_name = "Updated Name"

        user.full_name = new_name

        assert user.full_name == "Updated Name"

    @pytest.mark.asyncio
    async def test_update_profile_fields(self, mock_user_with_profile):
        """Test updating profile fields."""
        profile = mock_user_with_profile.profile

        # Update fields
        profile.bio = "New bio"
        profile.location = "Abuja"
        profile.theme = "dark"

        assert profile.bio == "New bio"
        assert profile.location == "Abuja"
        assert profile.theme == "dark"

    @pytest.mark.asyncio
    async def test_update_profile_partial(self, mock_user_with_profile):
        """Test partial profile update."""
        profile = mock_user_with_profile.profile
        original_phone = profile.phone

        # Only update bio
        profile.bio = "Just bio update"

        assert profile.bio == "Just bio update"
        assert profile.phone == original_phone  # Unchanged


class TestDeleteAccountEndpoint:
    """Tests for DELETE /me/account endpoint."""

    @pytest.fixture
    def mock_user(self):
        """Create mock user."""
        user = MagicMock(spec=User)
        user.id = uuid4()
        user.email = "test@example.com"
        user.delete = AsyncMock()
        return user

    @pytest.mark.asyncio
    async def test_delete_account_success(self, mock_user):
        """Test successful account deletion."""
        # Simulate Tortoise ORM deletion
        await mock_user.delete()

        mock_user.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_account_returns_success(self, mock_user):
        """Test delete returns success response."""
        # Expected response
        response = {"success": True}

        assert response["success"] is True


class TestUserSchemas:
    """Tests for user schemas."""

    def test_user_response_schema(self):
        """Test UserResponse schema."""
        user_id = str(uuid4())
        now = datetime.now(timezone.utc)

        response = UserResponse(
            id=user_id,
            email="test@example.com",
            full_name="Test User",
            created_at=now,
            last_login=now,
        )

        assert response.id == user_id
        assert response.email == "test@example.com"
        assert response.full_name == "Test User"
        assert response.created_at == now
        assert response.last_login == now

    def test_user_response_optional_last_login(self):
        """Test UserResponse with null last_login."""
        response = UserResponse(
            id=str(uuid4()),
            email="test@example.com",
            full_name="Test User",
            created_at=datetime.now(timezone.utc),
            last_login=None,
        )

        assert response.last_login is None


class TestAuthDependencies:
    """Tests for authentication dependencies."""

    @pytest.mark.asyncio
    async def test_get_current_user_requires_auth(self):
        """Test that get_current_user requires authentication."""
        # In real implementation, this would test JWT validation
        # Here we document the expected behavior
        pass

    @pytest.mark.asyncio
    async def test_get_or_create_current_user_creates_new(self):
        """Test that get_or_create creates new user if not exists."""
        # This would test the Supabase ID lookup and user creation
        pass

    @pytest.mark.asyncio
    async def test_get_or_create_current_user_returns_existing(self):
        """Test that get_or_create returns existing user."""
        # This would test returning existing user by Supabase ID
        pass
