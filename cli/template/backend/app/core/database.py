"""Database configuration and initialization."""

from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise

from app.core.config import settings

TORTOISE_ORM = {
    "connections": {"default": settings.database_url},
    "apps": {
        "models": {
            "models": [
                "app.users.models",
                "app.billing.models",
            ],
            "default_connection": "default",
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
