"""User schemas."""

from datetime import datetime
from typing import Optional

from app.base.schemas import BaseAppSchema


class UserResponse(BaseAppSchema):
    """User response model."""

    id: str
    email: str
    full_name: str
    created_at: datetime
    last_login: Optional[datetime] = None


class UserCreate(BaseAppSchema):
    """User creation model."""

    email: str
    full_name: str
    supabase_id: str


class UserUpdate(BaseAppSchema):
    """User update model."""

    full_name: Optional[str] = None


class UserProfileSchema(BaseAppSchema):
    """User profile schema."""

    id: Optional[str] = None
    bio: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    avatar_url: Optional[str] = None
    avatar_version: int = 1
    website_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    current_position: Optional[str] = None
    company: Optional[str] = None
    theme: str = "system"


class ProfileUpdateSchema(BaseAppSchema):
    """Schema for updating user profile."""

    full_name: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    website_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    bio: Optional[str] = None
    current_position: Optional[str] = None
    company: Optional[str] = None
    theme: Optional[str] = None


class CompleteUserProfileSchema(BaseAppSchema):
    """Complete user profile with all related data."""

    # Basic user information
    id: str
    email: str
    full_name: str
    created_at: datetime

    # Profile information
    bio: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    avatar_url: Optional[str] = None
    avatar_version: int = 1
    website_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    current_position: Optional[str] = None
    company: Optional[str] = None
    theme: str = "system"
