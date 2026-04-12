"""Database configuration and initialization."""

from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise

from app.core.config import settings

TORTOISE_ORM = {
    "connections": {"default": settings.database_url},
    "apps": {
        "users": {
            "models": ["app.users.models"],
            "default_connection": "default",
            "migrations": "app.users.migrations",
        },
        "billing": {
            "models": ["app.billing.models"],
            "default_connection": "default",
            "migrations": "app.billing.migrations",
        },
    },
}


def init_db(app: FastAPI):
    """Initialize database with Tortoise ORM."""
    register_tortoise(
        app,
        config=TORTOISE_ORM,
        generate_schemas=True,
        add_exception_handlers=True,
    )
