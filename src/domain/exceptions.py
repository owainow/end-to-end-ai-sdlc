"""Domain-specific exceptions for the Weather App."""


class WeatherAppError(Exception):
    """Base exception for all weather app errors."""

    def __init__(self, message: str, code: str = "WEATHER_ERROR") -> None:
        self.message = message
        self.code = code
        super().__init__(self.message)


class CityNotFoundError(WeatherAppError):
    """Raised when a city cannot be found."""

    def __init__(self, city: str) -> None:
        self.city = city
        super().__init__(
            message=f"City not found: {city}",
            code="CITY_NOT_FOUND",
        )


class InvalidCityNameError(WeatherAppError):
    """Raised when city name validation fails."""

    def __init__(self, city: str, reason: str) -> None:
        self.city = city
        self.reason = reason
        super().__init__(
            message=f"Invalid city name '{city}': {reason}",
            code="INVALID_CITY_NAME",
        )


class WeatherProviderError(WeatherAppError):
    """Raised when the weather provider fails."""

    def __init__(self, message: str, provider: str = "OpenWeatherMap") -> None:
        self.provider = provider
        super().__init__(
            message=f"Weather provider error ({provider}): {message}",
            code="PROVIDER_ERROR",
        )


class RateLimitExceededError(WeatherAppError):
    """Raised when rate limit is exceeded."""

    def __init__(self, retry_after_seconds: int = 60) -> None:
        self.retry_after_seconds = retry_after_seconds
        super().__init__(
            message=f"Rate limit exceeded. Retry after {retry_after_seconds} seconds.",
            code="RATE_LIMIT_EXCEEDED",
        )


class CacheError(WeatherAppError):
    """Raised when cache operations fail."""

    def __init__(self, operation: str, message: str) -> None:
        self.operation = operation
        super().__init__(
            message=f"Cache {operation} failed: {message}",
            code="CACHE_ERROR",
        )
