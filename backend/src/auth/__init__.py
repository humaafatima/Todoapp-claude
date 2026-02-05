"""Authentication module for JWT handling."""

from src.auth.middleware import get_current_user

__all__ = ["get_current_user"]
