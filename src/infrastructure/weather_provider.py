"""OpenWeatherMap API client implementation."""

from collections import Counter
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

    async def get_forecast(self, request: WeatherRequest) -> ForecastData:
        """Fetch 5-day forecast data from OpenWeatherMap.

        Args:
            request: The weather request.

        Returns:
            ForecastData entity with daily forecasts.

        Raises:
            CityNotFoundError: If the city cannot be found.
            WeatherProviderError: If the API request fails.
            RateLimitExceededError: If rate limit is exceeded.
        """
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

    def _parse_forecast_response(
        self, data: dict[str, Any], units: UnitSystem
    ) -> ForecastData:
        """Parse OpenWeatherMap forecast response into ForecastData entity.

        Aggregates 3-hour intervals into daily summaries (up to 5 days).

        Args:
            data: Raw API forecast response data.
            units: The unit system used.

        Returns:
            ForecastData entity with aggregated daily forecasts.
        """
        city_data = data["city"]
        coord = city_data["coord"]

        # Group entries by calendar date
        daily: dict[str, list[dict[str, Any]]] = {}
        for entry in data.get("list", []):
            date_str = entry["dt_txt"].split(" ")[0]
            daily.setdefault(date_str, []).append(entry)

        days: list[ForecastDay] = []
        sorted_dates = sorted(daily.keys())
        today_str = datetime.now(UTC).strftime("%Y-%m-%d")

        for i, date_str in enumerate(sorted_dates[:5]):
            entries = daily[date_str]

            # Aggregate metrics across the day's entries
            temps = [e["main"]["temp"] for e in entries]
            humidities = [e["main"]["humidity"] for e in entries]
            wind_speeds = [e.get("wind", {}).get("speed", 0.0) for e in entries]
            icons = [e.get("weather", [{}])[0].get("icon", "") for e in entries]
            descriptions = [
                e.get("weather", [{}])[0].get("description", "") for e in entries
            ]

            # Use mode icon (most frequent), fallback to first
            icon_counter: Counter[str] = Counter(icons)
            most_common_icon = icon_counter.most_common(1)[0][0] if icons else ""

            # Use description matching the most common icon
            most_common_description = ""
            for entry in entries:
                weather_list = entry.get("weather", [{}])
                if weather_list and weather_list[0].get("icon") == most_common_icon:
                    most_common_description = weather_list[0].get("description", "")
                    break
            if not most_common_description and descriptions:
                most_common_description = descriptions[0]

            # Day label: Today for first day, abbreviated weekday for rest
            if date_str == today_str:
                day_label = "Today"
            else:
                try:
                    day_dt = datetime.strptime(date_str, "%Y-%m-%d")
                    day_label = day_dt.strftime("%a")
                except ValueError:
                    day_label = date_str

            # If sorting puts today as index 0 even if not matching today_str
            if i == 0 and day_label != "Today":
                day_label = "Today"

            days.append(
                ForecastDay(
                    date=date_str,
                    day_label=day_label,
                    temp_high=max(temps),
                    temp_low=min(temps),
                    humidity=round(sum(humidities) / len(humidities)),
                    wind_speed=max(wind_speeds),
                    description=most_common_description,
                    icon_code=most_common_icon,
                    units=units,
                )
            )

        return ForecastData(
            city_name=city_data["name"],
            country=city_data["country"],
            coordinates=Coordinates(
                latitude=coord["lat"],
                longitude=coord["lon"],
            ),
            days=days,
            units=units,
            timestamp=datetime.now(UTC),
        )
