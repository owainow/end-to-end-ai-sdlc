"""Get Forecast use case implementation."""

from src.application.interfaces import CachePort, ForecastProviderPort, LoggerPort
from src.domain.entities import ForecastData, WeatherRequest


class GetForecastUseCase:
    """Use case for retrieving forecast data with caching."""

    def __init__(
        self,
        forecast_provider: ForecastProviderPort,
        cache: CachePort,
        logger: LoggerPort,
        cache_ttl_seconds: int = 1800,
    ) -> None:
        """Initialize the use case."""
        self._provider = forecast_provider
        self._cache = cache
        self._logger = logger
        self._cache_ttl = cache_ttl_seconds

    async def execute(self, request: WeatherRequest) -> ForecastData:
        """Execute the get forecast use case."""
        cache_key = f"forecast:{request.cache_key}"

        cached_data = self._cache.get(cache_key)
        if isinstance(cached_data, ForecastData):
            self._logger.debug(
                "Forecast cache hit",
                city=request.city,
                units=request.units.value,
                cache_key=cache_key,
            )
            return cached_data

        self._logger.debug(
            "Forecast cache miss, fetching from provider",
            city=request.city,
            units=request.units.value,
        )

        forecast_data = await self._provider.get_forecast(request)
        self._cache.set(cache_key, forecast_data, self._cache_ttl)
        self._logger.info(
            "Forecast data fetched and cached",
            city=forecast_data.city_name,
            country=forecast_data.country,
            units=forecast_data.units.value,
            cache_ttl=self._cache_ttl,
            days=len(forecast_data.days),
        )

        return forecast_data
