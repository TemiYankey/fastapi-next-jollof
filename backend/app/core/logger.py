"""
Logging configuration for the application.

Production-grade logging with separate files per component:
- app.log: Main application logs
- auth.log: Authentication logs
- users.log: User management
- payments.log: Payment processing
- emails.log: Email sending
- external.log: Third-party services
- errors.log: All errors from any component
"""

import logging
from pathlib import Path

from fastapi import Request
from fastapi.exceptions import RequestValidationError

validation_logger = logging.getLogger("app.core.logger")

# Ensure logs directory exists (at backend/logs, not app/logs)
LOG_DIR = Path(__file__).parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"},
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": "INFO",
            "stream": "ext://sys.stdout",
        },
        "file_app": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "standard",
            "filename": LOG_DIR / "app.log",
            "maxBytes": 20971520,  # 20 MB
            "backupCount": 10,
            "level": "DEBUG",
        },
        "file_auth": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "standard",
            "filename": LOG_DIR / "auth.log",
            "maxBytes": 10485760,  # 10 MB
            "backupCount": 5,
            "level": "DEBUG",
        },
        "file_users": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "detailed",
            "filename": LOG_DIR / "users.log",
            "maxBytes": 10485760,  # 10 MB
            "backupCount": 5,
            "level": "DEBUG",
        },
        "file_payments": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "detailed",
            "filename": LOG_DIR / "payments.log",
            "maxBytes": 10485760,  # 10 MB
            "backupCount": 5,
            "level": "DEBUG",
        },
        "file_emails": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "detailed",
            "filename": LOG_DIR / "emails.log",
            "maxBytes": 15485760,  # 15 MB
            "backupCount": 7,
            "level": "DEBUG",
        },
        "file_external": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "standard",
            "filename": LOG_DIR / "external.log",
            "maxBytes": 10485760,  # 10 MB
            "backupCount": 5,
            "level": "WARNING",
        },
        "file_errors": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "detailed",
            "filename": LOG_DIR / "errors.log",
            "maxBytes": 20485760,  # 20 MB
            "backupCount": 15,
            "level": "ERROR",
        },
    },
    "loggers": {
        # Main app logger
        "app": {
            "handlers": ["console", "file_app", "file_errors"],
            "level": "DEBUG",
            "propagate": False,
        },
        # Auth logger
        "app.auth": {
            "handlers": ["console", "file_auth", "file_errors"],
            "level": "DEBUG",
            "propagate": False,
        },
        # Users logger
        "app.users": {
            "handlers": ["console", "file_users", "file_errors"],
            "level": "DEBUG",
            "propagate": False,
        },
        # Payments logger
        "app.payments": {
            "handlers": ["console", "file_payments", "file_errors"],
            "level": "DEBUG",
            "propagate": False,
        },
        # Emails logger
        "app.emails": {
            "handlers": ["console", "file_emails", "file_errors"],
            "level": "DEBUG",
            "propagate": False,
        },
        # External services logger
        "app.external": {
            "handlers": ["console", "file_external", "file_errors"],
            "level": "WARNING",
            "propagate": False,
        },
        # Uvicorn loggers
        "uvicorn": {
            "handlers": ["console", "file_app"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.access": {
            "handlers": ["console", "file_app"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.error": {
            "handlers": ["console", "file_app"],
            "level": "ERROR",
            "propagate": False,
        },
        # External library noise reduction
        "httpx": {
            "handlers": ["file_external"],
            "level": "WARNING",
            "propagate": False,
        },
        "httpcore": {
            "handlers": ["file_external"],
            "level": "WARNING",
            "propagate": False,
        },
        "tortoise": {
            "handlers": ["file_external"],
            "level": "WARNING",
            "propagate": False,
        },
        "asyncpg": {
            "handlers": ["file_external"],
            "level": "WARNING",
            "propagate": False,
        },
        "redis": {
            "handlers": ["file_external"],
            "level": "WARNING",
            "propagate": False,
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
}


def setup_logging():
    """Setup logging configuration for the application."""
    import logging.config

    # Ensure log directory exists
    LOG_DIR.mkdir(exist_ok=True)

    # Apply logging configuration
    logging.config.dictConfig(LOGGING_CONFIG)

    # Test that logging is working
    logger = logging.getLogger("app")
    logger.info("Logging configuration initialized successfully")


def get_logger(name: str) -> logging.Logger:
    """
    Get a properly configured logger for app components.

    Args:
        name: Component name (will be prefixed with 'app.' if not already)

    Returns:
        Configured logger instance

    Examples:
        >>> logger = get_logger("users.auth")     # -> app.users.auth
        >>> logger = get_logger("payments")       # -> app.payments
        >>> logger = get_logger("emails")         # -> app.emails
    """
    if not name.startswith("app."):
        name = f"app.{name}"

    return logging.getLogger(name)


def get_email_logger(sub_component: str = "") -> logging.Logger:
    """Get email service logger."""
    if sub_component:
        return get_logger(f"emails.{sub_component}")
    return get_logger("emails")


def get_external_logger(service_name: str) -> logging.Logger:
    """Get external service logger."""
    return get_logger(f"external.{service_name}")


async def log_validation_error(request: Request, exc: RequestValidationError):
    """Log detailed validation error information."""
    # Read request body for logging (if possible)
    request_body = None
    try:
        if hasattr(request, "_body"):
            request_body = request._body.decode("utf-8")
        elif request.method in ["POST", "PUT", "PATCH"]:
            # Try to read body if not already consumed
            body = await request.body()
            request_body = body.decode("utf-8") if body else None
    except Exception:
        request_body = "[Unable to read request body]"

    # Log validation error details
    validation_logger.error(
        f"422 Validation Error - {request.method} {request.url.path}\n"
        f"Query params: {dict(request.query_params)}\n"
        f"Raw error: {str(exc)}"
    )
