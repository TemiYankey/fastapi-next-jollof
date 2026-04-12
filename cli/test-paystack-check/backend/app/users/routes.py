"""User routes - all operations for the authenticated user."""

import logging
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request

from app.core.rate_limiter import GENERAL_LIMIT, limiter
from app.users.auth import get_current_user, get_or_create_current_user
from app.users.models import User
from app.users.schemas import (
    CompleteUserProfileSchema,
    ProfileUpdateSchema,
    UserResponse,
)

router = APIRouter(prefix="/me", tags=["User"])
logger = logging.getLogger("app.users")


@router.get("", response_model=UserResponse)
@limiter.limit(GENERAL_LIMIT)
async def get_me(
    request: Request,
    current_user: User = Depends(get_or_create_current_user),
):
    """Get current user information. Creates user in DB if not exists."""
    now = datetime.now(timezone.utc)
    should_update = current_user.last_login is None or (
        now - current_user.last_login
    ) > timedelta(hours=1)

    if should_update:
        current_user.last_login = now
        await current_user.save()

    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        full_name=current_user.full_name,
        created_at=current_user.created_at,
        last_login=current_user.last_login,
    )


@router.get("/dashboard")
@limiter.limit(GENERAL_LIMIT)
async def get_dashboard(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    """Get user dashboard data."""
    return {
        "user": {
            "id": str(current_user.id),
            "email": current_user.email,
            "full_name": current_user.full_name,
        },
        "stats": {
            "member_since": current_user.created_at.isoformat(),
            "last_login": current_user.last_login.isoformat()
            if current_user.last_login
            else None,
        },
    }


@router.get("/profile", response_model=CompleteUserProfileSchema)
@limiter.limit(GENERAL_LIMIT)
async def get_profile(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    """Get complete user profile with all related data."""
    profile = current_user.profile
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return CompleteUserProfileSchema(
        id=str(current_user.id),
        email=current_user.email,
        full_name=current_user.full_name,
        created_at=current_user.created_at,
        bio=profile.bio,
        phone=profile.phone,
        location=profile.location,
        avatar_url=profile.avatar_url,
        avatar_version=profile.avatar_version,
        website_url=profile.website_url,
        linkedin_url=profile.linkedin_url,
        github_url=profile.github_url,
        current_position=profile.current_position,
        company=profile.company,
        theme=profile.theme,
    )


@router.put("/profile", response_model=CompleteUserProfileSchema)
@limiter.limit(GENERAL_LIMIT)
async def update_profile(
    request: Request,
    profile_data: ProfileUpdateSchema,
    current_user: User = Depends(get_current_user),
):
    """Update user profile."""
    profile = current_user.profile
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Update user fields
    if profile_data.full_name is not None:
        current_user.full_name = profile_data.full_name
        await current_user.save()

    # Update profile fields
    update_fields = [
        "phone",
        "location",
        "website_url",
        "linkedin_url",
        "github_url",
        "bio",
        "current_position",
        "company",
        "theme",
    ]

    for field in update_fields:
        value = getattr(profile_data, field, None)
        if value is not None:
            setattr(profile, field, value)

    await profile.save()

    return CompleteUserProfileSchema(
        id=str(current_user.id),
        email=current_user.email,
        full_name=current_user.full_name,
        created_at=current_user.created_at,
        bio=profile.bio,
        phone=profile.phone,
        location=profile.location,
        avatar_url=profile.avatar_url,
        avatar_version=profile.avatar_version,
        website_url=profile.website_url,
        linkedin_url=profile.linkedin_url,
        github_url=profile.github_url,
        current_position=profile.current_position,
        company=profile.company,
        theme=profile.theme,
    )


@router.delete("/account")
@limiter.limit(GENERAL_LIMIT)
async def delete_account(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    """Delete user account and all associated data."""
    await current_user.delete()
    return {"success": True}
