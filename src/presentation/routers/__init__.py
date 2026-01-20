"""API routers."""

from src.presentation.routers.health import router as health_router
from src.presentation.routers.weather import router as weather_router

__all__ = ["health_router", "weather_router"]
