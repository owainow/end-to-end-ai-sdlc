"""Presentation layer exports."""

from src.presentation.dependencies import (
    get_cache,
    get_logger,
    get_weather_provider,
    get_weather_use_case,
)
from src.presentation.exception_handlers import register_exception_handlers
from src.presentation.middleware import RequestLoggingMiddleware
from src.presentation.routers import health_router, weather_router
from src.presentation.schemas import ErrorResponse, HealthResponse, WeatherResponse

__all__ = [
    "ErrorResponse",
    "HealthResponse",
    "RequestLoggingMiddleware",
    "WeatherResponse",
    "get_cache",
    "get_logger",
    "get_weather_provider",
    "get_weather_use_case",
    "health_router",
    "register_exception_handlers",
    "weather_router",
]
