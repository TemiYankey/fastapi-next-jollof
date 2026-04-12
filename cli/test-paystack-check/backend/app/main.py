"""Main FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from starlette.middleware.sessions import SessionMiddleware

from app.core.config import settings
from app.core.constants import (
    API_DESCRIPTION,
    API_TITLE,
)
from app.core.database import init_db
from app.core.logger import log_validation_error, setup_logging
from app.core.rate_limiter import limiter, rate_limit_exceeded_handler
from app.core.redis import redis_service
from app.core.router import api_router

setup_logging()

logger = logging.getLogger("app")

# Initialize Sentry (Production Only)
if settings.environment == "production" and settings.sentry_dsn:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration
    from sentry_sdk.integrations.starlette import StarletteIntegration

    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.environment,
        integrations=[
            FastApiIntegration(transaction_style="endpoint"),
            StarletteIntegration(transaction_style="endpoint"),
            LoggingIntegration(
                level=logging.INFO,
                event_level=logging.ERROR,
            ),
        ],
        traces_sample_rate=0.1,
        profiles_sample_rate=0.1,
        ignore_errors=[KeyboardInterrupt],
        before_send=lambda event, hint: (
            None
            if "transaction" in event
            and event["transaction"] in ["/health", "/api/health"]
            else event
        ),
    )
    logger.info("Sentry initialized for production error tracking")
elif settings.environment == "production":
    logger.warning("Sentry DSN not configured for production environment")
else:
    logger.info(f"Sentry disabled for {settings.environment} environment")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.

    Handles startup and shutdown events in a single context.
    Everything before yield runs on startup, after yield runs on shutdown.
    """
    # Startup
    try:
        await redis_service.connect()
        logger.info("Redis connected successfully")
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
        if not settings.debug:
            raise

    yield  # Application runs here

    # Shutdown
    try:
        await redis_service.disconnect()
        logger.info("Redis disconnected")
    except Exception as e:
        logger.error(f"Redis disconnect error: {e}")


# Create FastAPI app with lifespan
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.environment != "production" else None,
    redoc_url="/redoc" if settings.environment != "production" else None,
)

# Initialize Tortoise ORM
init_db(app)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# Session middleware
if not settings.secret_key:
    raise RuntimeError("SECRET_KEY environment variable must be set")
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)

# CORS middleware
if not settings.cors_allowed_origins:
    raise RuntimeError("CORS_ALLOWED_ORIGINS environment variable must be set")

cors_origins = [
    origin.strip()
    for origin in settings.cors_allowed_origins.split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept", "X-Requested-With"],
)


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle 422 validation errors with detailed logging."""
    await log_validation_error(request, exc)

    errors = exc.errors()

    if settings.environment == "production":
        return JSONResponse(
            status_code=422,
            content={
                "detail": "An error occurred while processing your request. Please try again.",
            },
        )
    else:
        return JSONResponse(
            status_code=422,
            content={
                "detail": "An error occurred while processing your request. Please try again.",
                "errors": errors,
            },
        )


# Include API router
app.include_router(api_router)


@app.get("/api/health")
async def api_health_check():
    """API health check endpoint."""
    return {"status": "healthy", "app": settings.app_name}


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info",
    )
