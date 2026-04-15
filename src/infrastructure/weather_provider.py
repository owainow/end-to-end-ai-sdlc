"""OpenWeatherMap API client implementation."""

from collections import Counter, defaultdict
from datetime import UTC, datetime
from typing import Any

import httpx

from src.application.interfaces import ForecastProviderPort, WeatherProviderPort
from src.domain.entities import ForecastData, ForecastDay, WeatherData, WeatherRequest
from src.domain.exceptions import (
    CityNotFoundError,
    RateLimitExceededError,
    WeatherProviderError,
)
from src.domain.value_objects import Coordinates, UnitSystem


class OpenWeatherMapClient(WeatherProviderPort, ForecastProviderPort):
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
        params = self._build_params(request)

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(
                    f"{self._base_url}/weather",
                    params=params,
                )

                if response.status_code == 404:
                    location = (
                        f"{request.coordinates}"
                        if request.coordinates
                        else request.city
                    )
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

    async def get_forecast(self, request: WeatherRequest) -> ForecastData:
        """Fetch weather forecast data from OpenWeatherMap."""
        params = self._build_params(request)

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(
                    f"{self._base_url}/forecast",
                    params=params,
                )

                if response.status_code == 404:
                    location = (
                        f"{request.coordinates}"
                        if request.coordinates
                        else request.city
                    )
                    raise CityNotFoundError(location)

                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", "60"))
                    raise RateLimitExceededError(retry_after)

                if response.status_code != 200:
                    raise WeatherProviderError(
                        f"API returned status {response.status_code}: {response.text}"
                    )

                data = response.json()
                return self._parse_forecast_response(data, request.units)

        except httpx.TimeoutException as e:
            raise WeatherProviderError(f"Request timed out: {e}") from e
        except httpx.RequestError as e:
            raise WeatherProviderError(f"Request failed: {e}") from e

    def _build_params(self, request: WeatherRequest) -> dict[str, str | float]:
        """Build OpenWeatherMap request params for city or coordinates."""
        if request.coordinates:
            return {
                "lat": request.coordinates.latitude,
                "lon": request.coordinates.longitude,
                "units": request.units.value,
                "appid": self._api_key,
            }
        return {
            "q": request.city,
            "units": request.units.value,
            "appid": self._api_key,
        }

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

    def _parse_forecast_response(
        self, data: dict[str, Any], units: UnitSystem
    ) -> ForecastData:
        """Parse OpenWeatherMap forecast response into ForecastData entity."""
        city = data["city"]
        coordinates = Coordinates(
            latitude=city["coord"]["lat"],
            longitude=city["coord"]["lon"],
        )

        daily_entries: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
        for entry in data.get("list", []):
            dt_txt = entry.get("dt_txt")
            if not dt_txt:
                continue
            day_key = dt_txt.split(" ")[0]
            daily_entries[day_key].append(entry)

        days: list[ForecastDay] = []
        for index, day_key in enumerate(sorted(daily_entries)[:5]):
            entries = daily_entries[day_key]
            temps = [entry.get("main", {}).get("temp", 0.0) for entry in entries]
            humidities = [
                entry.get("main", {}).get("humidity", 0) for entry in entries
            ]
            wind_speeds = [entry.get("wind", {}).get("speed", 0.0) for entry in entries]

            weather_modes = Counter(
                (
                    weather.get("icon", ""),
                    weather.get("description", ""),
                )
                for weather in (
                    entry.get("weather", [{}])[0] for entry in entries
                )
            )
            mode_icon, mode_description = (
                weather_modes.most_common(1)[0][0] if weather_modes else ("", "")
            )

            date_value = datetime.strptime(day_key, "%Y-%m-%d").date()
            day_label = "Today" if index == 0 else date_value.strftime("%a")
            avg_humidity = (
                int(round(sum(humidities) / len(humidities))) if humidities else 0
            )

            days.append(
                ForecastDay(
                    date=date_value,
                    day_label=day_label,
                    temp_high=max(temps) if temps else 0.0,
                    temp_low=min(temps) if temps else 0.0,
                    humidity=avg_humidity,
                    wind_speed=max(wind_speeds) if wind_speeds else 0.0,
                    description=mode_description,
                    icon_code=mode_icon,
                    units=units,
                )
            )

        return ForecastData(
            city_name=city["name"],
            country=city["country"],
            coordinates=coordinates,
            days=days,
            units=units,
            timestamp=datetime.now(UTC),
        )
