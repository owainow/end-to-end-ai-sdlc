"""Get Weather use case implementation."""

from src.application.dto import WeatherResult
from src.application.interfaces import CachePort, LoggerPort, WeatherProviderPort
from src.domain.entities import WeatherRequest


class GetWeatherUseCase:
    """Use case for retrieving weather data with caching."""

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

    async def execute(self, request: WeatherRequest) -> WeatherResult:
        """Execute the get weather use case.

        Args:
            request: The weather request.

        Returns:
            WeatherResult containing weather data and optional easter egg identifier.

        Raises:
            CityNotFoundError: If city not found.
            WeatherProviderError: If provider fails.
            RateLimitExceededError: If rate limited.
        """
        cache_key = request.cache_key

        # Try cache first
        cached_data = self._cache.get(cache_key)
        if cached_data is not None:
            self._logger.debug(
                "Cache hit",
                city=request.city,
                units=request.units.value,
                cache_key=cache_key,
            )
            weather_data = cached_data
        else:
            self._logger.debug(
                "Cache miss, fetching from provider",
                city=request.city,
                units=request.units.value,
            )

            # Fetch from provider
            weather_data = await self._provider.get_weather(request)

            # Cache the result
            self._cache.set(cache_key, weather_data, self._cache_ttl)
            self._logger.info(
                "Weather data fetched and cached",
                city=weather_data.city_name,
                country=weather_data.country,
                temperature=weather_data.temperature,
                units=weather_data.units.value,
                cache_ttl=self._cache_ttl,
            )

        country_code = (weather_data.country or "").strip().upper()
        easter_egg = "zidane" if country_code == "FR" else None

        return WeatherResult(weather_data=weather_data, easter_egg=easter_egg)
