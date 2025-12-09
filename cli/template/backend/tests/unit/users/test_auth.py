"""Tests for authentication utilities (users/auth.py)."""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from app.users.auth import (
    _decode_token,
    _get_existing_user_from_token,
    _get_or_create_user_from_token,
    get_current_user,
    get_current_user_optional,
    get_or_create_current_user,
)

from .factories import UserFactory


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
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db.execute = AsyncMock(return_value=mock_result)

        with patch("app.users.auth._decode_token") as mock_decode:
            mock_decode.return_value = {"id": "supabase-123", "email": "test@example.com"}

            result = await _get_existing_user_from_token("token", mock_db)

            assert result == mock_user

    @pytest.mark.asyncio
    async def test_get_existing_user_not_found(self):
        """Test when user not found in database."""
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        with patch("app.users.auth._decode_token") as mock_decode:
            mock_decode.return_value = {"id": "supabase-123", "email": "test@example.com"}

            with pytest.raises(HTTPException) as exc:
                await _get_existing_user_from_token("token", mock_db)

            assert exc.value.status_code == 401
            assert exc.value.detail == "User not found"

    @pytest.mark.asyncio
    async def test_get_existing_user_inactive(self):
        """Test when user is inactive."""
        mock_user = UserFactory.create(is_active=False)
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db.execute = AsyncMock(return_value=mock_result)

        with patch("app.users.auth._decode_token") as mock_decode:
            mock_decode.return_value = {"id": "supabase-123", "email": "test@example.com"}

            with pytest.raises(HTTPException) as exc:
                await _get_existing_user_from_token("token", mock_db)

            assert exc.value.status_code == 403
            assert "deactivated" in exc.value.detail

    @pytest.mark.asyncio
    async def test_get_existing_user_without_profile(self):
        """Test getting user without loading profile."""
        mock_user = UserFactory.create()
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db.execute = AsyncMock(return_value=mock_result)

        with patch("app.users.auth._decode_token") as mock_decode:
            mock_decode.return_value = {"id": "supabase-123", "email": "test@example.com"}

            result = await _get_existing_user_from_token("token", mock_db, with_profile=False)

            assert result == mock_user

    @pytest.mark.asyncio
    async def test_get_existing_user_generic_exception(self):
        """Test handling of generic exception."""
        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(side_effect=Exception("Database error"))

        with patch("app.users.auth._decode_token") as mock_decode:
            mock_decode.return_value = {"id": "supabase-123", "email": "test@example.com"}

            with pytest.raises(HTTPException) as exc:
                await _get_existing_user_from_token("token", mock_db)

            assert exc.value.status_code == 401
            assert exc.value.detail == "Authentication failed"


class TestGetOrCreateUserFromToken:
    """Tests for _get_or_create_user_from_token function."""

    @pytest.mark.asyncio
    async def test_get_existing_user(self):
        """Test getting existing user."""
        mock_user = UserFactory.create()
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db.execute = AsyncMock(return_value=mock_result)

        with patch("app.users.auth._decode_token") as mock_decode:
            mock_decode.return_value = {"id": "supabase-123", "email": "test@example.com"}

            result = await _get_or_create_user_from_token("token", mock_db)

            assert result == mock_user

    @pytest.mark.asyncio
    async def test_create_new_user(self):
        """Test creating new user when not exists.

        Note: This test verifies the flow where a user doesn't exist and needs to be created.
        Due to SQLAlchemy's select() requiring actual model classes, we test the flow
        by mocking at a higher level.
        """
        # Create an active user - is_active=True is required after creation
        mock_new_user = UserFactory.create(is_active=True)
        mock_db = AsyncMock()

        # First execute: check if user exists -> None (triggers creation)
        # After creation: the function refreshes and returns user
        mock_result_none = MagicMock()
        mock_result_none.scalar_one_or_none.return_value = None

        mock_db.execute = AsyncMock(return_value=mock_result_none)
        mock_db.add = MagicMock()
        mock_db.flush = AsyncMock()
        # After refresh, the newly created user should be active (takes user and optional relationship list)
        mock_db.refresh = AsyncMock(side_effect=lambda user, *args: setattr(user, 'is_active', True))

        with patch("app.users.auth._decode_token") as mock_decode:
            mock_decode.return_value = {
                "id": "supabase-new-123",
                "email": "new@example.com",
                "full_name": "New User",
            }

            # The test verifies the function is called correctly
            result = await _get_or_create_user_from_token("token", mock_db)

            # Verify decode was called
            mock_decode.assert_called_once_with("token")
            # Verify execute was called to check for existing user
            assert mock_db.execute.called
            # Verify add and flush were called to create the user
            assert mock_db.add.called
            assert mock_db.flush.called

    @pytest.mark.asyncio
    async def test_create_user_inactive(self):
        """Test creating user that becomes inactive."""
        mock_user = UserFactory.create(is_active=False)
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db.execute = AsyncMock(return_value=mock_result)

        with patch("app.users.auth._decode_token") as mock_decode:
            mock_decode.return_value = {"id": "supabase-123", "email": "test@example.com"}

            with pytest.raises(HTTPException) as exc:
                await _get_or_create_user_from_token("token", mock_db)

            assert exc.value.status_code == 403
            assert "deactivated" in exc.value.detail

    @pytest.mark.asyncio
    async def test_create_user_race_condition(self):
        """Test handling of race condition during user creation.

        When two requests try to create the same user simultaneously,
        one will get an IntegrityError. The handler should rollback
        and re-fetch the now-existing user.
        """
        mock_user = UserFactory.create()
        mock_db = AsyncMock()

        # First call: user not found -> None
        mock_result_none = MagicMock()
        mock_result_none.scalar_one_or_none.return_value = None

        # Second call (after rollback): user now exists
        mock_result_user = MagicMock()
        mock_result_user.scalar_one_or_none.return_value = mock_user

        mock_db.execute = AsyncMock(side_effect=[mock_result_none, mock_result_user])
        mock_db.add = MagicMock()
        mock_db.flush = AsyncMock(side_effect=IntegrityError("stmt", "params", "orig"))
        mock_db.rollback = AsyncMock()

        with patch("app.users.auth._decode_token") as mock_decode:
            mock_decode.return_value = {"id": "supabase-123", "email": "test@example.com"}

            result = await _get_or_create_user_from_token("token", mock_db)

            assert result == mock_user
            assert mock_db.rollback.called

    @pytest.mark.asyncio
    async def test_create_user_generic_exception(self):
        """Test handling of generic exception during creation."""
        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(side_effect=Exception("Database error"))

        with patch("app.users.auth._decode_token") as mock_decode:
            mock_decode.return_value = {"id": "supabase-123", "email": "test@example.com"}

            with pytest.raises(HTTPException) as exc:
                await _get_or_create_user_from_token("token", mock_db)

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
        mock_db = AsyncMock()

        with patch("app.users.auth._get_existing_user_from_token") as mock_get:
            mock_get.return_value = mock_user

            result = await get_current_user(mock_credentials, mock_db)

            assert result == mock_user
            mock_get.assert_called_once_with(
                token="test-token",
                db=mock_db,
                with_profile=True,
            )


class TestGetOrCreateCurrentUser:
    """Tests for get_or_create_current_user dependency."""

    @pytest.mark.asyncio
    async def test_get_or_create_current_user_calls_internal(self):
        """Test that get_or_create_current_user calls internal function."""
        mock_user = UserFactory.create()
        mock_credentials = MagicMock()
        mock_credentials.credentials = "test-token"
        mock_db = AsyncMock()

        with patch("app.users.auth._get_or_create_user_from_token") as mock_get:
            mock_get.return_value = mock_user

            result = await get_or_create_current_user(mock_credentials, mock_db)

            assert result == mock_user
            mock_get.assert_called_once_with(
                token="test-token",
                db=mock_db,
                with_profile=True,
            )


class TestGetCurrentUserOptional:
    """Tests for get_current_user_optional dependency."""

    @pytest.mark.asyncio
    async def test_returns_none_without_credentials(self):
        """Test returns None when no credentials provided."""
        mock_db = AsyncMock()

        result = await get_current_user_optional(None, mock_db)

        assert result is None

    @pytest.mark.asyncio
    async def test_returns_user_with_valid_credentials(self):
        """Test returns user with valid credentials."""
        mock_user = UserFactory.create()
        mock_credentials = MagicMock()
        mock_credentials.credentials = "test-token"
        mock_db = AsyncMock()

        with patch("app.users.auth.get_current_user") as mock_get:
            mock_get.return_value = mock_user

            result = await get_current_user_optional(mock_credentials, mock_db)

            assert result == mock_user

    @pytest.mark.asyncio
    async def test_returns_none_on_http_exception(self):
        """Test returns None when authentication fails."""
        mock_credentials = MagicMock()
        mock_credentials.credentials = "invalid-token"
        mock_db = AsyncMock()

        with patch("app.users.auth.get_current_user") as mock_get:
            mock_get.side_effect = HTTPException(status_code=401, detail="Invalid")

            result = await get_current_user_optional(mock_credentials, mock_db)

            assert result is None
