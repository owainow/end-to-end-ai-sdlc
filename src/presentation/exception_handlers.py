"""Global exception handlers for FastAPI."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.domain.exceptions import (
    CityNotFoundError,
    InvalidCityNameError,
    RateLimitExceededError,
    WeatherAppError,
    WeatherProviderError,
)
from src.presentation.dependencies import get_logger


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers on the FastAPI app.

    Args:
        app: The FastAPI application instance.
    """

    @app.exception_handler(CityNotFoundError)
    async def city_not_found_handler(
        request: Request, exc: CityNotFoundError
    ) -> JSONResponse:
        """Handle city not found errors."""
        get_logger().warning("City not found", city=exc.city, path=request.url.path)
        return JSONResponse(
            status_code=404,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "retry_after": None,
                }
            },
        )

    @app.exception_handler(InvalidCityNameError)
    async def invalid_city_name_handler(
        request: Request, exc: InvalidCityNameError
    ) -> JSONResponse:
        """Handle invalid city name errors."""
        get_logger().warning(
            "Invalid city name", city=exc.city, reason=exc.reason, path=request.url.path
        )
        return JSONResponse(
            status_code=400,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "retry_after": None,
                }
            },
        )

    @app.exception_handler(RateLimitExceededError)
    async def rate_limit_handler(
        request: Request, exc: RateLimitExceededError
    ) -> JSONResponse:
        """Handle rate limit exceeded errors."""
        get_logger().warning(
            "Rate limit exceeded",
            retry_after=exc.retry_after_seconds,
            path=request.url.path,
        )
        return JSONResponse(
            status_code=429,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "retry_after": exc.retry_after_seconds,
                }
            },
            headers={"Retry-After": str(exc.retry_after_seconds)},
        )

    @app.exception_handler(WeatherProviderError)
    async def weather_provider_handler(
        request: Request, exc: WeatherProviderError
    ) -> JSONResponse:
        """Handle weather provider errors."""
        get_logger().error(
            "Weather provider error",
            provider=exc.provider,
            error=exc.message,
            path=request.url.path,
        )
        return JSONResponse(
            status_code=502,
            content={
                "error": {
                    "code": exc.code,
                    "message": "Weather service temporarily unavailable",
                    "retry_after": 30,
                }
            },
        )

    @app.exception_handler(WeatherAppError)
    async def weather_app_error_handler(
        request: Request, exc: WeatherAppError
    ) -> JSONResponse:
        """Handle generic weather app errors."""
        get_logger().error(
            "Application error", code=exc.code, error=exc.message, path=request.url.path
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "retry_after": None,
                }
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """Handle unhandled exceptions."""
        get_logger().error(
            "Unhandled exception",
            error=str(exc),
            error_type=type(exc).__name__,
            path=request.url.path,
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred",
                    "retry_after": None,
                }
            },
        )
