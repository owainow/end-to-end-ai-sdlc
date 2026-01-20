"""Unit tests for domain exceptions."""


from src.domain.exceptions import (
    CacheError,
    CityNotFoundError,
    InvalidCityNameError,
    RateLimitExceededError,
    WeatherAppError,
    WeatherProviderError,
)


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
        assert error.code == "INVALID_CITY_NAME"


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
