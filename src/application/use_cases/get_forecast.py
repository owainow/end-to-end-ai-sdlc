"""Get Forecast use case implementation."""

from src.application.interfaces import CachePort, ForecastProviderPort, LoggerPort
from src.domain.entities import ForecastData, WeatherRequest


class GetForecastUseCase:
    """Use case for retrieving 5-day forecast data with caching."""

    def __init__(
        self,
        forecast_provider: ForecastProviderPort,
        cache: CachePort,
        logger: LoggerPort,
        cache_ttl_seconds: int = 1800,
    ) -> None:
        """Initialize the use case.

        Args:
            forecast_provider: The forecast data provider.
            cache: The cache implementation.
            logger: The logger implementation.
            cache_ttl_seconds: Cache TTL in seconds (default 30 minutes).
        """
        self._provider = forecast_provider
        self._cache = cache
        self._logger = logger
        self._cache_ttl = cache_ttl_seconds

    async def execute(self, request: WeatherRequest) -> ForecastData:
        """Execute the get forecast use case.

        Args:
            request: The weather request.

        Returns:
            ForecastData with daily forecasts.

        Raises:
            CityNotFoundError: If city not found.
            WeatherProviderError: If provider fails.
            RateLimitExceededError: If rate limited.
        """
        cache_key = request.forecast_cache_key

        # Try cache first
        cached_data = self._cache.get(cache_key)
        if cached_data is not None:
            self._logger.debug(
                "Forecast cache hit",
                city=request.city,
                units=request.units.value,
                cache_key=cache_key,
            )
            return cached_data  # type: ignore[return-value]

        self._logger.debug(
            "Forecast cache miss, fetching from provider",
            city=request.city,
            units=request.units.value,
        )

        # Fetch from provider
        forecast_data = await self._provider.get_forecast(request)

        # Cache the result
        self._cache.set(cache_key, forecast_data, self._cache_ttl)
        self._logger.info(
            "Forecast data fetched and cached",
            city=forecast_data.city_name,
            country=forecast_data.country,
            days=len(forecast_data.days),
            units=forecast_data.units.value,
            cache_ttl=self._cache_ttl,
        )

        return forecast_data
