"""OpenWeatherMap API client implementation."""

from datetime import UTC, datetime
from typing import Any

import httpx

from src.application.interfaces import WeatherProviderPort
from src.domain.entities import (
    RawForecastData,
    RawForecastInterval,
    WeatherData,
    WeatherRequest,
)
from src.domain.exceptions import (
    CityNotFoundError,
    RateLimitExceededError,
    WeatherProviderError,
)
from src.domain.value_objects import Coordinates, UnitSystem


class OpenWeatherMapClient(WeatherProviderPort):
    """OpenWeatherMap API client implementing WeatherProviderPort."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.openweathermap.org/data/2.5",
        timeout_seconds: float = 10.0,
    ) -> None:
        """Initialize the client.

        Args:
            api_key: OpenWeatherMap API key.
            base_url: API base URL.
            timeout_seconds: Request timeout in seconds.
        """
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout_seconds

    async def get_weather(self, request: WeatherRequest) -> WeatherData:
        """Fetch weather data from OpenWeatherMap.

        Args:
            request: The weather request.

        Returns:
            WeatherData entity with current conditions.

        Raises:
            CityNotFoundError: If the city cannot be found.
            WeatherProviderError: If the API request fails.
            RateLimitExceededError: If rate limit is exceeded.
        """
        # Build params based on whether we have coordinates or city
        if request.coordinates:
            params = {
                "lat": request.coordinates.latitude,
                "lon": request.coordinates.longitude,
                "units": request.units.value,
                "appid": self._api_key,
            }
        else:
            params = {
                "q": request.city,
                "units": request.units.value,
                "appid": self._api_key,
            }

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(
                    f"{self._base_url}/weather",
                    params=params,
                )

                if response.status_code == 404:
                    location = f"{request.coordinates}" if request.coordinates else request.city
                    raise CityNotFoundError(location)

                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", "60"))
                    raise RateLimitExceededError(retry_after)

                if response.status_code != 200:
                    raise WeatherProviderError(
                        f"API returned status {response.status_code}: {response.text}"
                    )

                data = response.json()
                return self._parse_response(data, request.units)

        except httpx.TimeoutException as e:
            raise WeatherProviderError(f"Request timed out: {e}") from e
        except httpx.RequestError as e:
            raise WeatherProviderError(f"Request failed: {e}") from e

    def _parse_response(self, data: dict[str, Any], units: UnitSystem) -> WeatherData:
        """Parse OpenWeatherMap response into WeatherData entity.

        Args:
            data: Raw API response data.
            units: The unit system used.

        Returns:
            WeatherData entity.
        """
        coord = data["coord"]
        main = data["main"]
        wind = data.get("wind", {})
        weather = data.get("weather", [{}])[0]

        return WeatherData(
            city_name=data["name"],
            country=data["sys"]["country"],
            coordinates=Coordinates(
                latitude=coord["lat"],
                longitude=coord["lon"],
            ),
            temperature=main["temp"],
            feels_like=main["feels_like"],
            humidity=main["humidity"],
            wind_speed=wind.get("speed", 0.0),
            pressure=main["pressure"],
            visibility=data.get("visibility", 0),
            description=weather.get("description", ""),
            icon_code=weather.get("icon", ""),
            units=units,
            timestamp=datetime.now(UTC),
        )

    async def get_forecast_raw(self, city: str, units: UnitSystem) -> RawForecastData:
        """Fetch raw 5-day forecast data from OpenWeatherMap.

        Args:
            city: The city name.
            units: The temperature unit system.

        Returns:
            RawForecastData containing 3-hour intervals and timezone offset.

        Raises:
            CityNotFoundError: If the city cannot be found.
            WeatherProviderError: If the API request fails.
            RateLimitExceededError: If rate limit is exceeded.
        """
        params = {
            "q": city,
            "units": units.value,
            "appid": self._api_key,
        }

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(
                    f"{self._base_url}/forecast",
                    params=params,
                )

                if response.status_code == 404:
                    raise CityNotFoundError(city)

                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", "60"))
                    raise RateLimitExceededError(retry_after)

                if response.status_code != 200:
                    raise WeatherProviderError(
                        f"API returned status {response.status_code}: {response.text}"
                    )

                data = response.json()
                return self._parse_forecast_response(data)

        except httpx.TimeoutException as e:
            raise WeatherProviderError(f"Request timed out: {e}") from e
        except httpx.RequestError as e:
            raise WeatherProviderError(f"Request failed: {e}") from e

    def _parse_forecast_response(self, data: dict[str, Any]) -> RawForecastData:
        """Parse OpenWeatherMap 5-day forecast response into RawForecastData entity.

        Args:
            data: Raw API response data.

        Returns:
            RawForecastData entity.
        """
        city_data = data["city"]
        coord = city_data["coord"]
        timezone_offset = int(city_data.get("timezone", 0))

        intervals: list[RawForecastInterval] = []
        for item in data.get("list", []):
            dt = datetime.fromtimestamp(item["dt"], tz=UTC)
            main = item.get("main", {})
            temp = float(main.get("temp", 0.0))
            weather = item.get("weather", [{}])[0]
            condition = str(weather.get("description", ""))
            icon_code = str(weather.get("icon", ""))
            intervals.append(
                RawForecastInterval(
                    dt=dt,
                    temp=temp,
                    condition=condition,
                    icon_code=icon_code,
                )
            )

        return RawForecastData(
            city_name=city_data["name"],
            country=city_data.get("country", ""),
            coordinates=Coordinates(
                latitude=coord["lat"],
                longitude=coord["lon"],
            ),
            timezone_offset=timezone_offset,
            intervals=intervals,
        )
