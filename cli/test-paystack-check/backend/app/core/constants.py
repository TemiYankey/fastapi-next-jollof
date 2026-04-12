"""Application constants."""

from app.core.config import settings

# API Info
API_TITLE = settings.app_name
API_DESCRIPTION = settings.app_description

# Startup/Shutdown Messages
STARTUP_MESSAGE = f"Starting {settings.app_name}..."
STARTUP_SUCCESS_MESSAGE = f"{settings.app_name} started successfully!"
SHUTDOWN_MESSAGE = f"Shutting down {settings.app_name}..."
SHUTDOWN_SUCCESS_MESSAGE = f"{settings.app_name} shutdown complete."
