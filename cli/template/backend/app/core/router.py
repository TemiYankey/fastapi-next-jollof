"""API router configuration."""

from fastapi import APIRouter

from app.billing.routes import router as billing_router
from app.users.routes import router as users_router

# Base API router - all routes under /api
api_router = APIRouter(prefix="/api")
api_router.include_router(users_router)
api_router.include_router(billing_router)
