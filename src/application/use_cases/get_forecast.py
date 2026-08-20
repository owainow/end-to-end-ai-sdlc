"""Get 5-day weather forecast use case implementation."""

from datetime import UTC, datetime, timedelta, timezone

from src.application.interfaces import CachePort, LoggerPort, WeatherProviderPort
from src.domain.entities import (
    DailyForecast,
    ForecastData,
    ForecastRequest,
    RawForecastInterval,
)
from src.domain.exceptions import WeatherProviderError


class GetForecastUseCase:
    """Use case for retrieving 5-day weather forecast data with aggregation and caching."""

    def __init__(
        self,
        weather_provider: WeatherProviderPort,
        cache: CachePort,
        logger: LoggerPort,
        cache_ttl_seconds: int = 900,
    ) -> None:
        """Initialize the use case.

        Args:
            weather_provider: The weather data provider.
            cache: The cache implementation.
            logger: The logger implementation.
            cache_ttl_seconds: Cache TTL in seconds (default 15 minutes).
        """
        self._provider = weather_provider
        self._cache = cache
        self._logger = logger
        self._cache_ttl = cache_ttl_seconds

    async def execute(self, request: ForecastRequest) -> ForecastData:
        """Execute the get forecast use case.

        Args:
            request: The forecast request containing city and units.

        Returns:
            ForecastData entity containing 5 consecutive daily forecasts.

        Raises:
            CityNotFoundError: If city not found.
            WeatherProviderError: If provider fails or provides insufficient data.
            RateLimitExceededError: If rate limited.
        """
        cache_key = request.cache_key

        # Try cache first
        cached_data = self._cache.get(cache_key)
        if isinstance(cached_data, ForecastData):
            self._logger.debug(
                "Cache hit",
                city=request.city,
                units=request.units.value,
                cache_key=cache_key,
            )
            return cached_data

        self._logger.debug(
            "Cache miss, fetching from provider",
            city=request.city,
            units=request.units.value,
        )

        # Fetch raw forecast from provider
        raw_data = await self._provider.get_forecast_raw(city=request.city, units=request.units)

        # Group intervals by local calendar date (YYYY-MM-DD)
        tz = timezone(timedelta(seconds=raw_data.timezone_offset))
        grouped_days: dict[str, list[tuple[datetime, RawForecastInterval]]] = {}
        for interval in raw_data.intervals:
            local_dt = interval.dt.astimezone(tz)
            date_str = local_dt.strftime("%Y-%m-%d")
            if date_str not in grouped_days:
                grouped_days[date_str] = []
            grouped_days[date_str].append((local_dt, interval))

        if len(grouped_days) < 5:
            raise WeatherProviderError(
                f"Insufficient forecast data: expected at least 5 days, received {len(grouped_days)}"
            )

        # Select first 5 chronological local calendar days
        sorted_dates = sorted(grouped_days.keys())[:5]
        daily_forecasts: list[DailyForecast] = []

        for date_str in sorted_dates:
            day_entries = grouped_days[date_str]
            temp_min = min(entry[1].temp for entry in day_entries)
            temp_max = max(entry[1].temp for entry in day_entries)

            # Midday condition selection: closest to 12:00:00 local time (43200 seconds from midnight)
            # Tie breaking: earlier local datetime wins
            best_entry = min(
                day_entries,
                key=lambda entry: (
                    abs((entry[0].hour * 3600 + entry[0].minute * 60 + entry[0].second) - 43200),
                    entry[0],
                ),
            )

            daily_forecasts.append(
                DailyForecast(
                    date=date_str,
                    temp_min=temp_min,
                    temp_max=temp_max,
                    condition=best_entry[1].condition,
                    icon_code=best_entry[1].icon_code,
                    condition_code=best_entry[1].condition_code,
                )
            )

        forecast_data = ForecastData(
            city_name=raw_data.city_name,
            country=raw_data.country,
            coordinates=raw_data.coordinates,
            units=request.units,
            daily_forecasts=daily_forecasts,
            timestamp=datetime.now(UTC),
        )

        # Cache the result
        self._cache.set(cache_key, forecast_data, self._cache_ttl)
        self._logger.info(
            "Forecast data fetched and cached",
            city=forecast_data.city_name,
            country=forecast_data.country,
            units=forecast_data.units.value,
            days=len(forecast_data.daily_forecasts),
            cache_ttl=self._cache_ttl,
        )

        return forecast_data
