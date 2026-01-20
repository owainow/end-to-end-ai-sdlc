"""Source package exports."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi import FastAPI

# Lazy imports to avoid loading settings at import time
__all__ = ["create_app", "get_app"]


def create_app() -> "FastAPI":
    """Create a new FastAPI application."""
    from src.main import create_app as _create_app
    return _create_app()


def get_app() -> "FastAPI":
    """Get the FastAPI application."""
    from src.main import get_app as _get_app
    return _get_app()
