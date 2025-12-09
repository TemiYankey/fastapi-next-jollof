import json
import logging
import time
from typing import Any, Dict, Optional

import httpx
from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError

from app.core.config import settings
from app.core.redis import redis_service

logger = logging.getLogger("app.users.jwt")


class JWTDecoder:
    """Decode and validate JWT tokens locally."""

    def __init__(self, jwt_secret: Optional[str] = None):
        """
        Initialize JWT decoder.

        Args:
            jwt_secret: JWT secret for verification (defaults to settings)
        """
        self.jwt_secret = jwt_secret or settings.supabase_jwt_secret
        self.algorithms = [
            "RS256",
            "ES256",
        ]  # Support both symmetric and asymmetric
        self.jwks_redis_key = "supabase:jwks"  # Redis key for JWKS cache

    async def get_jwks(self, bypass_cache: bool = False) -> Dict[str, Any]:
        """
        Fetch JWKS from Redis cache or Supabase discovery endpoint.
        Strategy: Use Redis cache with 24-hour TTL, refetch on failure.

        Args:
            bypass_cache: If True, skip cache and fetch fresh from Supabase
        """
        try:
            # Skip cache if bypass requested
            if not bypass_cache:
                # Try to get from Redis first
                jwks = await redis_service.get_json(self.jwks_redis_key)
                if jwks:
                    logger.debug("Using cached JWKS from Redis")
                    return jwks

            # Cache miss, expired, or bypass requested - fetch from Supabase
            cache_status = "JWKS cache miss" if not bypass_cache else "Bypassing cache"
            logger.info(f"{cache_status}, fetching from Supabase...")
            jwks_url = f"{settings.supabase_url}/auth/v1/.well-known/jwks.json"
            response = httpx.get(jwks_url, timeout=10)
            response.raise_for_status()

            jwks = response.json()

            if jwks and jwks.get("keys"):
                # Cache in Redis for 24 hours (86400 seconds)
                await redis_service.set_json(self.jwks_redis_key, jwks, expire=86400)
                logger.info(f"Cached {len(jwks['keys'])} JWKS keys for 24 hours")
                return jwks
            else:
                logger.warning("Invalid JWKS response - no keys found")
                return {}

        except Exception as e:
            logger.error(f"Failed to fetch JWKS: {str(e)}")

            # Try one more time from Redis (in case of network failure)
            try:
                cached_data = await redis_service.get(self.jwks_redis_key)
                if cached_data:
                    logger.info("Using stale Redis cache due to fetch failure")
                    return json.loads(cached_data)
            except Exception:
                pass

            logger.error("No JWKS available - both fetch and cache failed")
            return {}

    async def get_signing_key(
        self, token: str, retry_on_unknown_kid: bool = True
    ) -> Optional[str]:
        """
        Get the appropriate signing key for token verification with enhanced security.

        Args:
            token: JWT token string
            retry_on_unknown_kid: Whether to refetch JWKS if key ID is unknown
        """
        try:
            header = jwt.get_unverified_header(token)
            alg = header.get("alg")
            kid = header.get("kid")

            # Check if we have a key ID (required for JWKS lookup)
            if not kid:
                logger.warning("JWT missing key ID (kid) - potential security issue")
                return None

            # Check if algorithm is supported
            if alg not in ["RS256", "ES256"]:
                logger.warning(f"Unsupported JWT algorithm: {alg}")
                return None

            # Get cached JWKS
            jwks = await self.get_jwks()
            if not jwks.get("keys"):
                logger.error("No JWKS keys available")
                return None

            # Look for the key with matching kid
            matching_key = None
            for key in jwks["keys"]:
                if key.get("kid") == kid:
                    matching_key = key
                    break

            if matching_key:
                # Found the key in cache - return JWK for verification
                logger.debug(f"Found cached key for kid: {kid}")
                return matching_key

            # Unknown key ID - could be legitimate rotation or attack
            if retry_on_unknown_kid:
                logger.warning(
                    f"Unknown key ID '{kid}' in cached JWKS - refetching to verify legitimacy"
                )

                # Force refresh from Supabase to check for new keys
                fresh_jwks = await self.get_jwks(bypass_cache=True)

                if fresh_jwks and fresh_jwks.get("keys"):
                    # Check if the unknown kid exists in fresh keys
                    for key in fresh_jwks["keys"]:
                        if key.get("kid") == kid:
                            # Legitimate new key - already cached by get_jwks()
                            logger.info(f"Verified new key: {kid}")
                            return key

                    # Key ID not found in fresh JWKS either
                    logger.error(
                        f"SECURITY ALERT: Invalid key ID '{kid}' not found in Supabase JWKS - possible JWT attack attempt"
                    )
                    logger.error(f"Token header: {header}")
                    return None
                else:
                    logger.error(
                        "Failed to fetch fresh JWKS for unknown key validation"
                    )
                    return None
            else:
                # Already retried or retry disabled
                logger.error(
                    f"Key ID '{kid}' not found after refresh - rejecting token"
                )
                return None

        except Exception as e:
            logger.error(f"Error getting signing key: {str(e)}", exc_info=True)
            return None

    async def decode_token(
        self, token: str, verify_exp: bool = True, verify_signature: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Decode and validate a JWT token.

        Args:
            token: JWT token string
            verify_exp: Whether to verify expiration
            verify_signature: Whether to verify signature

        Returns:
            Decoded token payload or None if invalid
        """
        try:
            # Remove 'Bearer ' prefix if present
            if token.startswith("Bearer "):
                token = token[7:]

            # Get the appropriate signing key (legacy secret or public key)
            signing_key = await self.get_signing_key(token)
            if not signing_key:
                logger.warning("Could not determine signing key for token")
                return None

            # Decode token with dynamic key
            payload = jwt.decode(
                token,
                signing_key,
                algorithms=self.algorithms,
                options={
                    "verify_signature": verify_signature,
                    "verify_exp": verify_exp,
                    "verify_aud": False,  # Don't verify audience for now
                    "verify_iss": False,  # Don't verify issuer for now
                    "leeway": 60,  # 60 second clock tolerance
                },
            )

            return payload

        except ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except JWTError as e:
            logger.warning(f"Invalid token: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error decoding token: {str(e)}")
            return None

    async def get_user_from_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Extract user information from token.

        Args:
            token: JWT token string

        Returns:
            User information dict or None
        """
        payload = await self.decode_token(token)
        if not payload:
            return None

        # Extract user data from Supabase JWT structure
        user_data = {
            "id": payload.get("sub"),  # Subject is user ID
            "email": payload.get("email"),
            "email_verified": payload.get("email_confirmed_at") is not None,
            "phone": payload.get("phone"),
            "app_metadata": payload.get("app_metadata", {}),
            "user_metadata": payload.get("user_metadata", {}),
            "role": payload.get("role", "authenticated"),
            "aal": payload.get("aal"),  # Auth assurance level
            "session_id": payload.get("session_id"),
            "exp": payload.get("exp"),  # Expiration timestamp
            "iat": payload.get("iat"),  # Issued at timestamp
        }

        # Add user metadata fields if they exist
        if "user_metadata" in payload:
            metadata = payload["user_metadata"]
            user_data["full_name"] = metadata.get("full_name")
            user_data["avatar_url"] = metadata.get("avatar_url")
        else:
            user_data["full_name"] = None
            user_data["avatar_url"] = None

        return user_data

    async def is_token_expired(self, token: str) -> bool:
        """
        Check if token is expired.

        Args:
            token: JWT token string

        Returns:
            True if expired, False otherwise
        """
        payload = await self.decode_token(token, verify_exp=False)
        if not payload:
            return True

        exp = payload.get("exp")
        if not exp:
            return True

        return time.time() > exp

    async def get_token_remaining_time(self, token: str) -> Optional[int]:
        """
        Get remaining time before token expires.

        Args:
            token: JWT token string

        Returns:
            Seconds until expiration or None if invalid
        """
        payload = await self.decode_token(token, verify_exp=False)
        if not payload:
            return None

        exp = payload.get("exp")
        if not exp:
            return None

        remaining = exp - time.time()
        return max(0, int(remaining))

    async def validate_token(self, token: str) -> bool:
        """
        Validate token is properly signed and not expired.

        Args:
            token: JWT token string

        Returns:
            True if valid, False otherwise
        """
        result = await self.decode_token(token)
        return result is not None


# Global decoder instance
jwt_decoder = JWTDecoder()
