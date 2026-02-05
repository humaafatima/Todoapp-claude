"""API v1 router - aggregates all v1 endpoints."""

from fastapi import APIRouter
from src.api.v1 import tasks

api_router = APIRouter()

# Include all v1 routers
api_router.include_router(tasks.router)
