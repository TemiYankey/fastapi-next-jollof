"""Authentication utilities."""

from typing import Any, Dict, List, Optional

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from tortoise.exceptions import IntegrityError

from app.core.config import settings
from app.core.logger import get_logger
from app.users.jwt_decoder import jwt_decoder
from app.users.models import User, UserProfile

logger = get_logger("users.auth")
security = HTTPBearer()

# Supabase Auth API timeout
SUPABASE_AUTH_TIMEOUT = 10.0


async def _validate_with_supabase(token: str) -> Optional[Dict[str, Any]]:
    """
    Validate token with Supabase Auth API and get fresh user data.

    This makes a real API call to Supabase to:
    - Verify the session is still valid (not revoked/logged out)
    - Get fresh user data (email, metadata updates)

    Returns:
        User data dict from Supabase or None if invalid
    """
    try:
        async with httpx.AsyncClient(timeout=SUPABASE_AUTH_TIMEOUT) as client:
            response = await client.get(
                f"{settings.supabase_url}/auth/v1/user",
                headers={
                    "Authorization": f"Bearer {token}",
                    "apikey": settings.supabase_public_key,
                },
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "id": data.get("id"),
                    "email": data.get("email"),
                    "email_verified": data.get("email_confirmed_at") is not None,
                    "phone": data.get("phone"),
                    "full_name": data.get("user_metadata", {}).get("full_name"),
                    "avatar_url": data.get("user_metadata", {}).get("avatar_url"),
                    "user_metadata": data.get("user_metadata", {}),
                    "app_metadata": data.get("app_metadata", {}),
                }

            if response.status_code == 401:
                logger.warning("Supabase auth: Token invalid or session revoked")
                return None

            logger.warning(f"Supabase auth unexpected response: {response.status_code}")
            return None

    except httpx.TimeoutException:
        logger.error("Supabase auth API timeout")
        return None
    except Exception as e:
        logger.error(f"Supabase auth API error: {str(e)}")
        return None


async def _decode_token(token: str) -> dict:
    """
    Decode JWT token and return user data.

    Raises:
        HTTPException: If token is invalid
    """
    user_data = await jwt_decoder.get_user_from_token(token)

    if not user_data or not user_data.get("id"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_data


async def _get_existing_user_from_token(
    token: str, prefetch_relations: Optional[List[str]] = None
) -> User:
    """
    Get existing user from JWT token. Returns 401 if user not in DB.

    Use this for all endpoints except /me.
    """
    user_data = {}
    try:
        user_data = await _decode_token(token)
        relations = prefetch_relations or ["profile"]

        user = (
            await User.filter(supabase_id=user_data["id"])
            .prefetch_related(*relations)
            .first()
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            logger.warning(
                f"Inactive user attempted access: {user.email} (ID: {user.id})"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account has been deactivated",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error during authentication for user {user_data.get('email', 'unknown') if user_data else 'unknown'}: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def _get_or_create_user_from_token(
    token: str, prefetch_relations: Optional[List[str]] = None
) -> User:
    """
    Get or create user from Supabase-validated token. Creates user if not in DB.

    This function validates the token with Supabase Auth API to:
    - Verify the session is still valid (catches revoked sessions)
    - Get fresh user data (email changes, metadata updates)

    Use this ONLY for /me endpoint. Other endpoints use local JWT decoding.
    """
    user_data = {}
    try:
        # Validate with Supabase API (real session check)
        user_data = await _validate_with_supabase(token)

        if not user_data or not user_data.get("id"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired session",
                headers={"WWW-Authenticate": "Bearer"},
            )

        relations = prefetch_relations or ["profile"]

        user = (
            await User.filter(supabase_id=user_data["id"])
            .prefetch_related(*relations)
            .first()
        )

        if not user:
            # Derive name from email if not provided (handles None values)
            email = user_data.get("email") or ""
            full_name = user_data.get("full_name") or email.split("@")[0] or "User"

            # Check if user exists with this email but different supabase_id
            existing_user = await User.filter(email=email).first()
            if existing_user:
                logger.critical(
                    f"Account conflict: email {email} exists with supabase_id "
                    f"{existing_user.supabase_id}, attempted signup with {user_data['id']}"
                )
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="There's a problem with your account. Please contact support.",
                )

            # Create new user from Supabase data
            user = await User.create(
                supabase_id=user_data["id"],
                email=email,
                full_name=full_name,
            )
            # Create user profile
            await UserProfile.create(user=user)
            # Prefetch the profile for the response
            await user.fetch_related("profile")
            logger.info(f"Created new user with profile: {user.email} (ID: {user.id})")
        else:
            # Sync user data if changed (email from Supabase)
            needs_save = False
            if user_data.get("email") and user.email != user_data["email"]:
                logger.info(
                    f"Syncing email for user {user.id}: "
                    f"{user.email} -> {user_data['email']}"
                )
                user.email = user_data["email"]
                needs_save = True

            # Note: We intentionally do NOT sync full_name from Supabase.
            # Users can update their name in the profile page, and that should
            # be the source of truth.

            if needs_save:
                await user.save()

        if not user.is_active:
            logger.warning(
                f"Inactive user attempted access: {user.email} (ID: {user.id})"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account has been deactivated",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user

    except HTTPException:
        raise
    except IntegrityError as e:
        # Race condition: another request created the user, fetch them
        logger.warning(
            f"Race condition during user creation for {user_data.get('email', 'unknown')}, fetching existing user"
        )
        user = (
            await User.filter(supabase_id=user_data["id"])
            .prefetch_related(*(prefetch_relations or ["profile"]))
            .first()
        )
        if user:
            return user
        logger.error(
            f"Integrity error but user not found: {user_data.get('email', 'unknown')}: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(
            f"Error during authentication for user {user_data.get('email', 'unknown') if user_data else 'unknown'}: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    """
    Get current user from JWT token (lightweight). Returns 401 if user not in DB.

    Prefetches:
    - profile (basic data only)

    Use this for most endpoints that only need user.id, user.email, etc.
    Does NOT create users - use get_or_create_current_user for /me endpoint.
    """
    return await _get_existing_user_from_token(
        token=credentials.credentials,
        prefetch_relations=["profile"],
    )


async def get_or_create_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    """
    Get or create current user from JWT token.

    Creates user in DB if not exists. Use this ONLY for /me endpoint.
    All other endpoints should use get_current_user which returns 401 if user not found.
    """
    return await _get_or_create_user_from_token(
        token=credentials.credentials,
        prefetch_relations=["profile"],
    )


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[User]:
    """Get current user, return None if not authenticated or user not in DB."""
    if not credentials:
        return None

    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None
