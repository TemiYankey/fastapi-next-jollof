"""Authentication utilities using SQLAlchemy 2.0."""

from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.logger import get_logger
from app.users.jwt_decoder import jwt_decoder
from app.users.models import User, UserProfile

logger = get_logger("users.auth")
security = HTTPBearer()


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
    token: str,
    db: AsyncSession,
    with_profile: bool = True,
) -> User:
    """
    Get existing user from JWT token. Returns 401 if user not in DB.

    Use this for all endpoints except /me.
    """
    user_data = {}
    try:
        user_data = await _decode_token(token)

        query = select(User).where(User.supabase_id == user_data["id"])
        if with_profile:
            query = query.options(selectinload(User.profile))

        result = await db.execute(query)
        user = result.scalar_one_or_none()

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
    token: str,
    db: AsyncSession,
    with_profile: bool = True,
) -> User:
    """
    Get or create user from JWT token. Creates user if not in DB.

    Use this ONLY for /me endpoint.
    """
    user_data = {}
    try:
        user_data = await _decode_token(token)

        query = select(User).where(User.supabase_id == user_data["id"])
        if with_profile:
            query = query.options(selectinload(User.profile))

        result = await db.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            # Create new user from JWT data
            user = User(
                supabase_id=user_data["id"],
                email=user_data.get("email", ""),
                full_name=user_data.get("full_name", ""),
            )
            db.add(user)
            await db.flush()

            # Create default profile
            profile = UserProfile(user_id=user.id)
            db.add(profile)
            await db.flush()

            # Refresh to get profile relationship
            await db.refresh(user, ["profile"])

            logger.info(f"Created new user: {user.email} (ID: {user.id})")

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
        await db.rollback()
        logger.warning(
            f"Race condition during user creation for {user_data.get('email', 'unknown')}, fetching existing user"
        )
        query = select(User).where(User.supabase_id == user_data["id"])
        if with_profile:
            query = query.options(selectinload(User.profile))

        result = await db.execute(query)
        user = result.scalar_one_or_none()

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
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Get current user from JWT token (lightweight). Returns 401 if user not in DB.

    Use this for most endpoints that only need user.id, user.email, etc.
    Does NOT create users - use get_or_create_current_user for /me endpoint.
    """
    return await _get_existing_user_from_token(
        token=credentials.credentials,
        db=db,
        with_profile=True,
    )


async def get_or_create_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Get or create current user from JWT token.

    Creates user in DB if not exists. Use this ONLY for /me endpoint.
    All other endpoints should use get_current_user which returns 401 if user not found.
    """
    return await _get_or_create_user_from_token(
        token=credentials.credentials,
        db=db,
        with_profile=True,
    )


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """Get current user, return None if not authenticated or user not in DB."""
    if not credentials:
        return None

    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None
