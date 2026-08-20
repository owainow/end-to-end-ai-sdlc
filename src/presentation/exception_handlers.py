"""Global exception handlers for FastAPI."""

import uuid
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.domain.exceptions import (
    CityNotFoundError,
    InvalidCityNameError,
    RateLimitExceededError,
    WeatherAppError,
    WeatherProviderError,
)
from src.presentation.dependencies import get_logger


def _get_correlation_id(request: Request) -> str:
    """Retrieve correlation ID from request state, header, or generate new UUID."""
    correlation_id = getattr(request.state, "correlation_id", None)
    if not correlation_id:
        correlation_id = request.headers.get("x-correlation-id") or f"req-{uuid.uuid4()}"
    return str(correlation_id)


def _create_error_response(
    status_code: int,
    code: str,
    message: str,
    correlation_id: str,
    target: str | None = None,
    details: list[dict[str, Any]] | None = None,
    retry_after: int | None = None,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    """Construct a standard ErrorResponse JSONResponse."""
    content = {
        "error": {
            "code": code,
            "message": message,
            "target": target,
            "details": details if details is not None else [],
            "correlationId": correlation_id,
            "retry_after": retry_after,
        }
    }
    response_headers = {"x-correlation-id": correlation_id}
    if headers:
        response_headers.update(headers)
    return JSONResponse(
        status_code=status_code,
        content=content,
        headers=response_headers,
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers on the FastAPI app.

    Args:
        app: The FastAPI application instance.
    """

    @app.exception_handler(RequestValidationError)
    async def request_validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Handle FastAPI request parameter/body validation errors."""
        correlation_id = _get_correlation_id(request)
        get_logger().warning(
            "Request validation error",
            errors=exc.errors(),
            path=request.url.path,
            correlation_id=correlation_id,
        )

        details: list[dict[str, Any]] = []
        primary_target: str | None = None
        primary_msg: str = "Validation error"

        for err in exc.errors():
            loc = err.get("loc", ())
            field_name = str(loc[-1]) if loc else None
            msg = err.get("msg", "Invalid value")
            details.append({"target": field_name, "message": msg})
            if primary_target is None and field_name and field_name != "query":
                primary_target = field_name
                primary_msg = msg

        if len(details) == 1 and details[0].get("message"):
            primary_msg = str(details[0]["message"])

        return _create_error_response(
            status_code=422,
            code="UNPROCESSABLE_ENTITY",
            message=primary_msg,
            target=primary_target,
            details=details,
            correlation_id=correlation_id,
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        request: Request, exc: HTTPException
    ) -> JSONResponse:
        """Handle HTTP exceptions explicitly raised by application logic or dependencies."""
        correlation_id = _get_correlation_id(request)
        get_logger().warning(
            "HTTP exception",
            status_code=exc.status_code,
            detail=exc.detail,
            path=request.url.path,
            correlation_id=correlation_id,
        )

        target: str | None = None
        message: str = str(exc.detail)
        details: list[dict[str, Any]] = []

        if isinstance(exc.detail, dict):
            message = str(exc.detail.get("message", "Validation error"))
            target = exc.detail.get("target")
            details = exc.detail.get("details", [])

        code = "UNPROCESSABLE_ENTITY" if exc.status_code == 422 else (
            "VALIDATION_ERROR" if exc.status_code == 400 else (
                "NOT_FOUND" if exc.status_code == 404 else (
                    "RATE_LIMITED" if exc.status_code == 429 else "HTTP_ERROR"
                )
            )
        )

        headers = getattr(exc, "headers", None)

        return _create_error_response(
            status_code=exc.status_code,
            code=code,
            message=message,
            target=target,
            details=details,
            correlation_id=correlation_id,
            headers=headers,
        )

    @app.exception_handler(CityNotFoundError)
    async def city_not_found_handler(
        request: Request, exc: CityNotFoundError
    ) -> JSONResponse:
        """Handle city not found errors."""
        correlation_id = _get_correlation_id(request)
        get_logger().warning(
            "City not found",
            city=exc.city,
            path=request.url.path,
            correlation_id=correlation_id,
        )
        return _create_error_response(
            status_code=404,
            code=exc.code,
            message=exc.message,
            target="city",
            correlation_id=correlation_id,
        )

    @app.exception_handler(InvalidCityNameError)
    async def invalid_city_name_handler(
        request: Request, exc: InvalidCityNameError
    ) -> JSONResponse:
        """Handle invalid city name errors."""
        correlation_id = _get_correlation_id(request)
        get_logger().warning(
            "Invalid city name",
            city=exc.city,
            reason=exc.reason,
            path=request.url.path,
            correlation_id=correlation_id,
        )
        return _create_error_response(
            status_code=422,
            code="UNPROCESSABLE_ENTITY",
            message=exc.message,
            target="city",
            correlation_id=correlation_id,
        )

    @app.exception_handler(RateLimitExceededError)
    async def rate_limit_handler(
        request: Request, exc: RateLimitExceededError
    ) -> JSONResponse:
        """Handle rate limit exceeded errors."""
        correlation_id = _get_correlation_id(request)
        get_logger().warning(
            "Rate limit exceeded",
            retry_after=exc.retry_after_seconds,
            path=request.url.path,
            correlation_id=correlation_id,
        )
        return _create_error_response(
            status_code=429,
            code="RATE_LIMITED",
            message=exc.message,
            retry_after=exc.retry_after_seconds,
            correlation_id=correlation_id,
            headers={"Retry-After": str(exc.retry_after_seconds)},
        )

    @app.exception_handler(WeatherProviderError)
    async def weather_provider_handler(
        request: Request, exc: WeatherProviderError
    ) -> JSONResponse:
        """Handle weather provider errors."""
        correlation_id = _get_correlation_id(request)
        get_logger().error(
            "Weather provider error",
            provider=exc.provider,
            error=exc.message,
            path=request.url.path,
            correlation_id=correlation_id,
        )
        return _create_error_response(
            status_code=502,
            code="PROVIDER_UNAVAILABLE",
            message="Weather service temporarily unavailable",
            retry_after=30,
            correlation_id=correlation_id,
        )

    @app.exception_handler(WeatherAppError)
    async def weather_app_error_handler(
        request: Request, exc: WeatherAppError
    ) -> JSONResponse:
        """Handle generic weather app errors."""
        correlation_id = _get_correlation_id(request)
        get_logger().error(
            "Application error",
            code=exc.code,
            error=exc.message,
            path=request.url.path,
            correlation_id=correlation_id,
        )
        return _create_error_response(
            status_code=500,
            code=exc.code,
            message=exc.message,
            correlation_id=correlation_id,
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """Handle unhandled exceptions."""
        correlation_id = _get_correlation_id(request)
        get_logger().error(
            "Unhandled exception",
            error=str(exc),
            error_type=type(exc).__name__,
            path=request.url.path,
            correlation_id=correlation_id,
        )
        return _create_error_response(
            status_code=500,
            code="INTERNAL_ERROR",
            message="An unexpected error occurred",
            correlation_id=correlation_id,
        )

