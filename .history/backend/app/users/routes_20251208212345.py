"""User authentication routes using SQLAlchemy 2.0."""

import logging
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rate_limiter import AUTH_LIMIT, GENERAL_LIMIT, limiter
from app.users.auth import get_current_user, get_or_create_current_user
from app.users.models import User, UserProfile
from app.users.schemas import (
    CompleteUserProfileSchema,
    ProfileUpdateSchema,
    UserResponse,
)

router = APIRouter()
logger = logging.getLogger("app.users")


# Root /me endpoint - all sub-routes are nested under this
me_router = APIRouter(prefix="/me", tags=["User"])


@me_router.get("", response_model=UserResponse)
@limiter.limit(AUTH_LIMIT)
async def get_me(
    request: Request,
    current_user: User = Depends(get_or_create_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current user information. Creates user in DB if not exists."""
    now = datetime.now(timezone.utc)
    should_update = current_user.last_login is None or (
        now - current_user.last_login
    ) > timedelta(hours=1)

    if should_update:
        current_user.last_login = now

    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        full_name=current_user.full_name,
        created_at=current_user.created_at,
        last_login=current_user.last_login,
    )


@me_router.get("/dashboard")
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
            "credits": current_user.credits,
        },
        "stats": {
            "credits_balance": current_user.credits,
            "member_since": current_user.created_at.isoformat(),
            "last_login": current_user.last_login.isoformat()
            if current_user.last_login
            else None,
        },
    }


@me_router.get("/profile", response_model=CompleteUserProfileSchema)
@limiter.limit(GENERAL_LIMIT)
async def get_profile(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
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


@me_router.put("/profile", response_model=CompleteUserProfileSchema)
@limiter.limit(GENERAL_LIMIT)
async def update_profile(
    request: Request,
    profile_data: ProfileUpdateSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update user profile."""
    profile = current_user.profile
    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)

    # Update user fields
    if profile_data.full_name is not None:
        current_user.full_name = profile_data.full_name

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


@me_router.delete("/delete-account")
@limiter.limit(AUTH_LIMIT)
async def delete_account(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete user account and all associated data."""
    await db.delete(current_user)
    await db.flush()
    return {"success": True}


# Include the /me router
router.include_router(me_router)
