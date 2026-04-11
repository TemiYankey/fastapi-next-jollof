"""Tests for user models."""

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

    def test_user_table_name(self):
        """Test User model has correct table name."""
        assert User._meta.db_table == "users"

    def test_user_has_required_fields(self):
        """Test User model has required fields."""
        field_names = [f.model_field_name for f in User._meta.fields_map.values()]

        assert "id" in field_names
        assert "email" in field_names
        assert "full_name" in field_names
        assert "supabase_id" in field_names
        assert "is_active" in field_names
        assert "credits" in field_names

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


class TestUserProfileModel:
    """Tests for UserProfile model."""

    def test_profile_table_name(self):
        """Test UserProfile model has correct table name."""
        assert UserProfile._meta.db_table == "user_profiles"

    def test_profile_has_required_fields(self):
        """Test UserProfile model has required fields."""
        field_names = [f.model_field_name for f in UserProfile._meta.fields_map.values()]

        assert "id" in field_names
        assert "bio" in field_names
        assert "phone" in field_names
        assert "location" in field_names
        assert "avatar_url" in field_names
        assert "theme" in field_names


class TestUserProfileRelationship:
    """Tests for User-UserProfile relationship."""

    def test_user_has_profile_relationship(self):
        """Test User model has profile relationship defined."""
        # Check that profile is defined as a type annotation
        # (fetch_fields only populated after Tortoise init)
        assert "profile" in User.__annotations__

    def test_user_has_payments_relationship(self):
        """Test User model has payments relationship defined."""
        # Check that payments is defined as a type annotation
        assert "payments" in User.__annotations__
