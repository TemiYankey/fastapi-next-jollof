"""Tests for authentication utilities (users/auth.py)."""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException
from tortoise.exceptions import IntegrityError

from app.users.auth import (
    _decode_token,
    _get_existing_user_from_token,
    _get_or_create_user_from_token,
    _validate_with_supabase,
    get_current_user,
    get_current_user_optional,
    get_or_create_current_user,
)

from .factories import UserFactory


class TestValidateWithSupabase:
    """Tests for _validate_with_supabase function."""

    @pytest.mark.asyncio
    async def test_validate_success(self):
        """Test successful validation with Supabase."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "supabase-123",
            "email": "test@example.com",
            "email_confirmed_at": "2024-01-01T00:00:00Z",
            "phone": "+1234567890",
            "user_metadata": {"full_name": "Test User", "avatar_url": "https://example.com/avatar.jpg"},
            "app_metadata": {},
        }

        with patch("app.users.auth.httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )

            result = await _validate_with_supabase("valid-token")

            assert result["id"] == "supabase-123"
            assert result["email"] == "test@example.com"
            assert result["email_verified"] is True
            assert result["full_name"] == "Test User"

    @pytest.mark.asyncio
    async def test_validate_unauthorized(self):
        """Test validation with invalid/revoked token."""
        mock_response = MagicMock()
        mock_response.status_code = 401

        with patch("app.users.auth.httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )

            result = await _validate_with_supabase("invalid-token")

            assert result is None

    @pytest.mark.asyncio
    async def test_validate_timeout(self):
        """Test validation timeout handling."""
        import httpx

        with patch("app.users.auth.httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                side_effect=httpx.TimeoutException("Timeout")
            )

            result = await _validate_with_supabase("token")

            assert result is None


class TestDecodeToken:
    """Tests for _decode_token function."""

    @pytest.mark.asyncio
    async def test_decode_token_success(self):
        """Test successful token decoding."""
        mock_user_data = {
            "id": "supabase-user-123",
            "email": "test@example.com",
        }

        with patch("app.users.auth.jwt_decoder") as mock_decoder:
            mock_decoder.get_user_from_token = AsyncMock(return_value=mock_user_data)

            result = await _decode_token("valid-token")

            assert result == mock_user_data
            mock_decoder.get_user_from_token.assert_called_once_with("valid-token")

    @pytest.mark.asyncio
    async def test_decode_token_returns_none(self):
        """Test token decoding when decoder returns None."""
        with patch("app.users.auth.jwt_decoder") as mock_decoder:
            mock_decoder.get_user_from_token = AsyncMock(return_value=None)

            with pytest.raises(HTTPException) as exc:
                await _decode_token("invalid-token")

            assert exc.value.status_code == 401
            assert exc.value.detail == "Invalid token"

    @pytest.mark.asyncio
    async def test_decode_token_missing_id(self):
        """Test token decoding when user data has no id."""
        mock_user_data = {"email": "test@example.com"}  # No 'id' field

        with patch("app.users.auth.jwt_decoder") as mock_decoder:
            mock_decoder.get_user_from_token = AsyncMock(return_value=mock_user_data)

            with pytest.raises(HTTPException) as exc:
                await _decode_token("token-without-id")

            assert exc.value.status_code == 401
            assert exc.value.detail == "Invalid token"


class TestGetExistingUserFromToken:
    """Tests for _get_existing_user_from_token function."""

    @pytest.mark.asyncio
    async def test_get_existing_user_success(self):
        """Test getting existing user from token."""
        mock_user = UserFactory.create()

        with patch("app.users.auth._decode_token") as mock_decode, \
             patch("app.users.auth.User") as mock_user_model:
            mock_decode.return_value = {"id": "supabase-123", "email": "test@example.com"}

            # Mock the filter chain
            mock_filter = MagicMock()
            mock_filter.prefetch_related.return_value.first = AsyncMock(return_value=mock_user)
            mock_user_model.filter.return_value = mock_filter

            result = await _get_existing_user_from_token("token")

            assert result == mock_user
            mock_user_model.filter.assert_called_once_with(supabase_id="supabase-123")

    @pytest.mark.asyncio
    async def test_get_existing_user_not_found(self):
        """Test when user not found in database."""
        with patch("app.users.auth._decode_token") as mock_decode, \
             patch("app.users.auth.User") as mock_user_model:
            mock_decode.return_value = {"id": "supabase-123", "email": "test@example.com"}

            mock_filter = MagicMock()
            mock_filter.prefetch_related.return_value.first = AsyncMock(return_value=None)
            mock_user_model.filter.return_value = mock_filter

            with pytest.raises(HTTPException) as exc:
                await _get_existing_user_from_token("token")

            assert exc.value.status_code == 401
            assert exc.value.detail == "User not found"

    @pytest.mark.asyncio
    async def test_get_existing_user_inactive(self):
        """Test when user is inactive."""
        mock_user = UserFactory.create(is_active=False)

        with patch("app.users.auth._decode_token") as mock_decode, \
             patch("app.users.auth.User") as mock_user_model:
            mock_decode.return_value = {"id": "supabase-123", "email": "test@example.com"}

            mock_filter = MagicMock()
            mock_filter.prefetch_related.return_value.first = AsyncMock(return_value=mock_user)
            mock_user_model.filter.return_value = mock_filter

            with pytest.raises(HTTPException) as exc:
                await _get_existing_user_from_token("token")

            assert exc.value.status_code == 403
            assert "deactivated" in exc.value.detail

    @pytest.mark.asyncio
    async def test_get_existing_user_custom_relations(self):
        """Test getting user with custom prefetch relations."""
        mock_user = UserFactory.create()

        with patch("app.users.auth._decode_token") as mock_decode, \
             patch("app.users.auth.User") as mock_user_model:
            mock_decode.return_value = {"id": "supabase-123", "email": "test@example.com"}

            mock_filter = MagicMock()
            mock_prefetch = MagicMock()
            mock_prefetch.first = AsyncMock(return_value=mock_user)
            mock_filter.prefetch_related.return_value = mock_prefetch
            mock_user_model.filter.return_value = mock_filter

            result = await _get_existing_user_from_token("token", prefetch_relations=["profile", "payments"])

            assert result == mock_user
            mock_filter.prefetch_related.assert_called_once_with("profile", "payments")

    @pytest.mark.asyncio
    async def test_get_existing_user_generic_exception(self):
        """Test handling of generic exception."""
        with patch("app.users.auth._decode_token") as mock_decode, \
             patch("app.users.auth.User") as mock_user_model:
            mock_decode.return_value = {"id": "supabase-123", "email": "test@example.com"}
            mock_user_model.filter.side_effect = Exception("Database error")

            with pytest.raises(HTTPException) as exc:
                await _get_existing_user_from_token("token")

            assert exc.value.status_code == 401
            assert exc.value.detail == "Authentication failed"


class TestGetOrCreateUserFromToken:
    """Tests for _get_or_create_user_from_token function."""

    @pytest.mark.asyncio
    async def test_get_existing_user(self):
        """Test getting existing user."""
        mock_user = UserFactory.create()

        with patch("app.users.auth._validate_with_supabase") as mock_validate, \
             patch("app.users.auth.User") as mock_user_model:
            mock_validate.return_value = {"id": "supabase-123", "email": "test@example.com"}

            mock_filter = MagicMock()
            mock_filter.prefetch_related.return_value.first = AsyncMock(return_value=mock_user)
            mock_user_model.filter.return_value = mock_filter

            result = await _get_or_create_user_from_token("token")

            assert result == mock_user

    @pytest.mark.asyncio
    async def test_create_new_user(self):
        """Test creating new user when not exists."""
        mock_new_user = UserFactory.create(is_active=True)

        with patch("app.users.auth._validate_with_supabase") as mock_validate, \
             patch("app.users.auth.User") as mock_user_model, \
             patch("app.users.auth.UserProfile") as mock_profile_model:
            mock_validate.return_value = {
                "id": "supabase-new-123",
                "email": "new@example.com",
                "full_name": "New User",
            }

            # First call: user not found
            mock_filter = MagicMock()
            mock_filter.prefetch_related.return_value.first = AsyncMock(return_value=None)
            mock_filter.first = AsyncMock(return_value=None)
            mock_user_model.filter.return_value = mock_filter

            # Create returns new user
            mock_user_model.create = AsyncMock(return_value=mock_new_user)
            mock_profile_model.create = AsyncMock()
            mock_new_user.fetch_related = AsyncMock()

            result = await _get_or_create_user_from_token("token")

            assert result == mock_new_user
            mock_user_model.create.assert_called_once()
            mock_profile_model.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_invalid_session(self):
        """Test when Supabase returns invalid session."""
        with patch("app.users.auth._validate_with_supabase") as mock_validate:
            mock_validate.return_value = None

            with pytest.raises(HTTPException) as exc:
                await _get_or_create_user_from_token("invalid-token")

            assert exc.value.status_code == 401
            assert "Invalid or expired session" in exc.value.detail

    @pytest.mark.asyncio
    async def test_inactive_user(self):
        """Test when user is inactive."""
        mock_user = UserFactory.create(is_active=False)

        with patch("app.users.auth._validate_with_supabase") as mock_validate, \
             patch("app.users.auth.User") as mock_user_model:
            mock_validate.return_value = {"id": "supabase-123", "email": "test@example.com"}

            mock_filter = MagicMock()
            mock_filter.prefetch_related.return_value.first = AsyncMock(return_value=mock_user)
            mock_user_model.filter.return_value = mock_filter

            with pytest.raises(HTTPException) as exc:
                await _get_or_create_user_from_token("token")

            assert exc.value.status_code == 403
            assert "deactivated" in exc.value.detail

    @pytest.mark.asyncio
    async def test_race_condition_handling(self):
        """Test handling of race condition during user creation."""
        mock_user = UserFactory.create()

        with patch("app.users.auth._validate_with_supabase") as mock_validate, \
             patch("app.users.auth.User") as mock_user_model, \
             patch("app.users.auth.UserProfile") as mock_profile_model:
            mock_validate.return_value = {"id": "supabase-123", "email": "test@example.com"}

            # First filter: user not found
            mock_filter_none = MagicMock()
            mock_filter_none.prefetch_related.return_value.first = AsyncMock(return_value=None)
            mock_filter_none.first = AsyncMock(return_value=None)

            # After IntegrityError: user found
            mock_filter_found = MagicMock()
            mock_filter_found.prefetch_related.return_value.first = AsyncMock(return_value=mock_user)

            mock_user_model.filter.side_effect = [mock_filter_none, mock_filter_none, mock_filter_found]
            mock_user_model.create = AsyncMock(side_effect=IntegrityError("Duplicate"))

            result = await _get_or_create_user_from_token("token")

            assert result == mock_user

    @pytest.mark.asyncio
    async def test_generic_exception(self):
        """Test handling of generic exception during creation."""
        with patch("app.users.auth._validate_with_supabase") as mock_validate, \
             patch("app.users.auth.User") as mock_user_model:
            mock_validate.return_value = {"id": "supabase-123", "email": "test@example.com"}
            mock_user_model.filter.side_effect = Exception("Database error")

            with pytest.raises(HTTPException) as exc:
                await _get_or_create_user_from_token("token")

            assert exc.value.status_code == 401
            assert exc.value.detail == "Authentication failed"


class TestGetCurrentUser:
    """Tests for get_current_user dependency."""

    @pytest.mark.asyncio
    async def test_get_current_user_calls_internal(self):
        """Test that get_current_user calls internal function."""
        mock_user = UserFactory.create()
        mock_credentials = MagicMock()
        mock_credentials.credentials = "test-token"

        with patch("app.users.auth._get_existing_user_from_token") as mock_get:
            mock_get.return_value = mock_user

            result = await get_current_user(mock_credentials)

            assert result == mock_user
            mock_get.assert_called_once_with(
                token="test-token",
                prefetch_relations=["profile"],
            )


class TestGetOrCreateCurrentUser:
    """Tests for get_or_create_current_user dependency."""

    @pytest.mark.asyncio
    async def test_get_or_create_current_user_calls_internal(self):
        """Test that get_or_create_current_user calls internal function."""
        mock_user = UserFactory.create()
        mock_credentials = MagicMock()
        mock_credentials.credentials = "test-token"

        with patch("app.users.auth._get_or_create_user_from_token") as mock_get:
            mock_get.return_value = mock_user

            result = await get_or_create_current_user(mock_credentials)

            assert result == mock_user
            mock_get.assert_called_once_with(
                token="test-token",
                prefetch_relations=["profile"],
            )


class TestGetCurrentUserOptional:
    """Tests for get_current_user_optional dependency."""

    @pytest.mark.asyncio
    async def test_returns_none_without_credentials(self):
        """Test returns None when no credentials provided."""
        result = await get_current_user_optional(None)

        assert result is None

    @pytest.mark.asyncio
    async def test_returns_user_with_valid_credentials(self):
        """Test returns user with valid credentials."""
        mock_user = UserFactory.create()
        mock_credentials = MagicMock()
        mock_credentials.credentials = "test-token"

        with patch("app.users.auth.get_current_user") as mock_get:
            mock_get.return_value = mock_user

            result = await get_current_user_optional(mock_credentials)

            assert result == mock_user

    @pytest.mark.asyncio
    async def test_returns_none_on_http_exception(self):
        """Test returns None when authentication fails."""
        mock_credentials = MagicMock()
        mock_credentials.credentials = "invalid-token"

        with patch("app.users.auth.get_current_user") as mock_get:
            mock_get.side_effect = HTTPException(status_code=401, detail="Invalid")

            result = await get_current_user_optional(mock_credentials)

            assert result is None
