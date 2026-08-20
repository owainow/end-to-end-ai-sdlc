"""Unit tests for domain exceptions, schemas, and presentation exception handlers."""

import uuid
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.domain.exceptions import (
    CacheError,
    CityNotFoundError,
    InvalidCityNameError,
    RateLimitExceededError,
    WeatherAppError,
    WeatherProviderError,
)
from src.presentation.exception_handlers import (
    _get_correlation_id,
    register_exception_handlers,
)
from src.presentation.schemas import ErrorDetail, ErrorResponse


class TestWeatherAppError:
    """Tests for base WeatherAppError."""

    def test_error_with_default_code(self) -> None:
        """Test error creation with default code."""
        error = WeatherAppError("Something went wrong")
        assert error.message == "Something went wrong"
        assert error.code == "WEATHER_ERROR"
        assert str(error) == "Something went wrong"

    def test_error_with_custom_code(self) -> None:
        """Test error creation with custom code."""
        error = WeatherAppError("Custom error", code="CUSTOM_CODE")
        assert error.code == "CUSTOM_CODE"


class TestCityNotFoundError:
    """Tests for CityNotFoundError."""

    def test_city_not_found(self) -> None:
        """Test city not found error."""
        error = CityNotFoundError("InvalidCity")
        assert error.city == "InvalidCity"
        assert error.code == "CITY_NOT_FOUND"
        assert "InvalidCity" in error.message


class TestInvalidCityNameError:
    """Tests for InvalidCityNameError."""

    def test_invalid_city_name(self) -> None:
        """Test invalid city name error."""
        error = InvalidCityNameError("123City", "contains numbers")
        assert error.city == "123City"
        assert error.reason == "contains numbers"
        assert error.code == "UNPROCESSABLE_ENTITY"


class TestWeatherProviderError:
    """Tests for WeatherProviderError."""

    def test_provider_error_default(self) -> None:
        """Test provider error with default provider."""
        error = WeatherProviderError("API timeout")
        assert error.provider == "OpenWeatherMap"
        assert "OpenWeatherMap" in error.message
        assert "API timeout" in error.message

    def test_provider_error_custom_provider(self) -> None:
        """Test provider error with custom provider."""
        error = WeatherProviderError("Connection failed", provider="CustomProvider")
        assert error.provider == "CustomProvider"


class TestRateLimitExceededError:
    """Tests for RateLimitExceededError."""

    def test_rate_limit_default(self) -> None:
        """Test rate limit error with default retry time."""
        error = RateLimitExceededError()
        assert error.retry_after_seconds == 60
        assert error.code == "RATE_LIMIT_EXCEEDED"

    def test_rate_limit_custom(self) -> None:
        """Test rate limit error with custom retry time."""
        error = RateLimitExceededError(retry_after_seconds=120)
        assert error.retry_after_seconds == 120
        assert "120 seconds" in error.message


class TestCacheError:
    """Tests for CacheError."""

    def test_cache_error(self) -> None:
        """Test cache error."""
        error = CacheError("get", "Connection refused")
        assert error.operation == "get"
        assert error.code == "CACHE_ERROR"
        assert "get" in error.message
        assert "Connection refused" in error.message


class TestErrorSchemas:
    """Tests for ErrorDetail and ErrorResponse schemas."""

    def test_error_detail_schema(self) -> None:
        """Test ErrorDetail serialization."""
        detail = ErrorDetail(
            code="UNPROCESSABLE_ENTITY",
            message="City name cannot be empty",
            target="city",
            details=[],
            correlationId="req-abc-123",
        )
        data = detail.model_dump()
        assert data["code"] == "UNPROCESSABLE_ENTITY"
        assert data["message"] == "City name cannot be empty"
        assert data["target"] == "city"
        assert data["details"] == []
        assert data["correlationId"] == "req-abc-123"
        assert data["retry_after"] is None

    def test_error_response_schema(self) -> None:
        """Test ErrorResponse schema wrapping ErrorDetail."""
        detail = ErrorDetail(
            code="VALIDATION_ERROR",
            message="Invalid input",
            correlationId="req-xyz-789",
        )
        response = ErrorResponse(error=detail)
        data = response.model_dump()
        assert "error" in data
        assert data["error"]["code"] == "VALIDATION_ERROR"
        assert data["error"]["correlationId"] == "req-xyz-789"


class TestCorrelationIdHelper:
    """Tests for _get_correlation_id helper function."""

    def test_correlation_id_from_request_state(self) -> None:
        """Test retrieving correlation ID from request.state."""
        request = MagicMock(spec=Request)
        request.state.correlation_id = "req-from-state-123"
        assert _get_correlation_id(request) == "req-from-state-123"

    def test_correlation_id_from_header(self) -> None:
        """Test retrieving correlation ID from headers when request.state is empty."""
        request = MagicMock(spec=Request)
        request.state = MagicMock()
        del request.state.correlation_id
        request.headers = {"x-correlation-id": "req-from-header-456"}
        assert _get_correlation_id(request) == "req-from-header-456"

    def test_correlation_id_fallback_generation(self) -> None:
        """Test fallback generation of correlation ID if state and header are missing."""
        request = MagicMock(spec=Request)
        request.state = MagicMock()
        del request.state.correlation_id
        request.headers = {}
        cid = _get_correlation_id(request)
        assert cid.startswith("req-")
        # Ensure it's a valid UUID after prefix
        uuid_str = cid[4:]
        assert uuid.UUID(uuid_str)
