"""Unit tests for domain entities."""

from datetime import UTC, datetime

import pytest

from src.domain.entities import (
    DailyForecast,
    ForecastData,
    ForecastRequest,
    RawForecastInterval,
    WeatherData,
    WeatherRequest,
)
from src.domain.value_objects import Coordinates, UnitSystem, WeatherCondition


class TestCoordinates:
    """Tests for Coordinates value object."""

    def test_valid_coordinates(self) -> None:
        """Test creating valid coordinates."""
        coords = Coordinates(latitude=51.5074, longitude=-0.1278)
        assert coords.latitude == 51.5074
        assert coords.longitude == -0.1278

    def test_invalid_latitude_too_high(self) -> None:
        """Test that latitude > 90 raises ValueError."""
        with pytest.raises(ValueError, match="Latitude must be between"):
            Coordinates(latitude=91.0, longitude=0.0)

    def test_invalid_latitude_too_low(self) -> None:
        """Test that latitude < -90 raises ValueError."""
        with pytest.raises(ValueError, match="Latitude must be between"):
            Coordinates(latitude=-91.0, longitude=0.0)

    def test_invalid_longitude_too_high(self) -> None:
        """Test that longitude > 180 raises ValueError."""
        with pytest.raises(ValueError, match="Longitude must be between"):
            Coordinates(latitude=0.0, longitude=181.0)

    def test_invalid_longitude_too_low(self) -> None:
        """Test that longitude < -180 raises ValueError."""
        with pytest.raises(ValueError, match="Longitude must be between"):
            Coordinates(latitude=0.0, longitude=-181.0)

    def test_coordinates_string_representation(self) -> None:
        """Test string representation of coordinates."""
        coords = Coordinates(latitude=51.5074, longitude=-0.1278)
        assert str(coords) == "(51.5074, -0.1278)"


class TestWeatherRequest:
    """Tests for WeatherRequest entity."""

    def test_valid_request(self) -> None:
        """Test creating a valid weather request."""
        request = WeatherRequest(city="London")
        assert request.city == "London"
        assert request.units == UnitSystem.METRIC

    def test_request_with_imperial_units(self) -> None:
        """Test request with imperial units."""
        request = WeatherRequest(city="New York", units=UnitSystem.IMPERIAL)
        assert request.units == UnitSystem.IMPERIAL

    def test_empty_city_raises_error(self) -> None:
        """Test that empty city raises ValueError."""
        with pytest.raises(ValueError, match="Either city name or coordinates must be provided"):
            WeatherRequest(city="")

    def test_whitespace_city_raises_error(self) -> None:
        """Test that whitespace-only city raises ValueError."""
        with pytest.raises(ValueError, match="Either city name or coordinates must be provided"):
            WeatherRequest(city="   ")

    def test_long_city_raises_error(self) -> None:
        """Test that city > 100 chars raises ValueError."""
        with pytest.raises(ValueError, match="cannot exceed 100 characters"):
            WeatherRequest(city="a" * 101)

    def test_cache_key_generation(self) -> None:
        """Test cache key generation is consistent."""
        request1 = WeatherRequest(city="London", units=UnitSystem.METRIC)
        request2 = WeatherRequest(city="LONDON", units=UnitSystem.METRIC)
        request3 = WeatherRequest(city="London", units=UnitSystem.IMPERIAL)

        # Same city (case-insensitive), same units = same key
        assert request1.cache_key == request2.cache_key
        # Different units = different key
        assert request1.cache_key != request3.cache_key

    def test_request_with_coordinates(self) -> None:
        """Test creating a request with coordinates."""
        coords = Coordinates(latitude=51.5074, longitude=-0.1278)
        request = WeatherRequest(coordinates=coords, units=UnitSystem.METRIC)
        assert request.coordinates == coords
        assert request.units == UnitSystem.METRIC

    def test_empty_city_and_no_coordinates_raises_error(self) -> None:
        """Test that request without city or coordinates raises ValueError."""
        with pytest.raises(ValueError, match="Either city name or coordinates must be provided"):
            WeatherRequest(city="", coordinates=None)

    def test_cache_key_with_coordinates(self) -> None:
        """Test cache key generation for coordinate-based requests."""
        coords1 = Coordinates(latitude=51.5074, longitude=-0.1278)
        coords2 = Coordinates(latitude=51.507401, longitude=-0.127801)
        request1 = WeatherRequest(coordinates=coords1, units=UnitSystem.METRIC)
        request2 = WeatherRequest(coordinates=coords2, units=UnitSystem.METRIC)

        # Coordinates rounded to 2 decimal places should match
        assert request1.cache_key == request2.cache_key
        assert "coords:51.51,-0.13" in request1.cache_key

    def test_coordinates_preferred_over_city(self) -> None:
        """Test that coordinates can be provided with or without city."""
        coords = Coordinates(latitude=51.5074, longitude=-0.1278)
        request = WeatherRequest(city="London", coordinates=coords, units=UnitSystem.METRIC)
        assert request.coordinates == coords
        # Cache key should use coordinates
        assert "coords:" in request.cache_key


class TestWeatherData:
    """Tests for WeatherData entity."""

    @pytest.fixture
    def weather_data(self) -> WeatherData:
        """Create sample weather data."""
        return WeatherData(
            city_name="London",
            country="GB",
            coordinates=Coordinates(latitude=51.5074, longitude=-0.1278),
            temperature=15.2,
            feels_like=14.8,
            humidity=72,
            wind_speed=4.5,
            pressure=1013,
            visibility=10000,
            description="scattered clouds",
            icon_code="03d",
            units=UnitSystem.METRIC,
            timestamp=datetime.now(UTC),
        )

    def test_temperature_display_metric(self, weather_data: WeatherData) -> None:
        """Test temperature display for metric units."""
        assert weather_data.temperature_display == "15.2°C"

    def test_temperature_display_imperial(self) -> None:
        """Test temperature display for imperial units."""
        data = WeatherData(
            city_name="New York",
            country="US",
            coordinates=Coordinates(latitude=40.7128, longitude=-74.006),
            temperature=59.4,
            feels_like=58.6,
            humidity=65,
            wind_speed=5.2,
            pressure=1015,
            visibility=10000,
            description="clear sky",
            icon_code="01d",
            units=UnitSystem.IMPERIAL,
            timestamp=datetime.now(UTC),
        )
        assert data.temperature_display == "59.4°F"

    def test_wind_speed_display_metric(self, weather_data: WeatherData) -> None:
        """Test wind speed display for metric units."""
        assert weather_data.wind_speed_display == "4.5 m/s"

    def test_location_display(self, weather_data: WeatherData) -> None:
        """Test location display."""
        assert weather_data.location_display == "London, GB"


class TestForecastRequest:
    """Tests for ForecastRequest entity."""

    def test_valid_request(self) -> None:
        """Test creating a valid forecast request."""
        request = ForecastRequest(city="London")
        assert request.city == "London"
        assert request.units == UnitSystem.METRIC

    def test_request_with_imperial_units(self) -> None:
        """Test forecast request with imperial units."""
        request = ForecastRequest(city="New York", units=UnitSystem.IMPERIAL)
        assert request.units == UnitSystem.IMPERIAL

    def test_empty_city_raises_invalid_city_name_error(self) -> None:
        """Test that empty city raises InvalidCityNameError."""
        from src.domain.exceptions import InvalidCityNameError

        with pytest.raises(InvalidCityNameError, match="cannot be empty or whitespace"):
            ForecastRequest(city="")

    def test_whitespace_city_raises_invalid_city_name_error(self) -> None:
        """Test that whitespace-only city raises InvalidCityNameError."""
        from src.domain.exceptions import InvalidCityNameError

        with pytest.raises(InvalidCityNameError, match="cannot be empty or whitespace"):
            ForecastRequest(city="   ")

    def test_long_city_raises_invalid_city_name_error(self) -> None:
        """Test that city > 100 chars raises InvalidCityNameError."""
        from src.domain.exceptions import InvalidCityNameError

        with pytest.raises(InvalidCityNameError, match="cannot exceed 100 characters"):
            ForecastRequest(city="a" * 101)

    def test_cache_key_generation(self) -> None:
        """Test forecast cache key generation is consistent."""
        request1 = ForecastRequest(city="London", units=UnitSystem.METRIC)
        request2 = ForecastRequest(city=" LONDON ", units=UnitSystem.METRIC)
        request3 = ForecastRequest(city="London", units=UnitSystem.IMPERIAL)

        assert request1.cache_key == "forecast:london:metric"
        assert request1.cache_key == request2.cache_key
        assert request1.cache_key != request3.cache_key
        assert request3.cache_key == "forecast:london:imperial"


class TestWeatherCondition:
    """Tests for WeatherCondition enum and helpers."""

    def test_weather_condition_enum_values(self) -> None:
        """Test expected enum values exist."""
        assert WeatherCondition.CLEAR == "clear"
        assert WeatherCondition.CLOUDS == "clouds"
        assert WeatherCondition.RAIN == "rain"
        assert WeatherCondition.DRIZZLE == "drizzle"
        assert WeatherCondition.THUNDERSTORM == "thunderstorm"
        assert WeatherCondition.SNOW == "snow"
        assert WeatherCondition.MIST == "mist"
        assert WeatherCondition.UNKNOWN == "unknown"

    def test_from_string_exact_and_case_insensitive(self) -> None:
        """Test from_string handles exact matches with whitespace and case variations."""
        assert WeatherCondition.from_string("clear") == WeatherCondition.CLEAR
        assert WeatherCondition.from_string("Clear") == WeatherCondition.CLEAR
        assert WeatherCondition.from_string("  CLOUDS  ") == WeatherCondition.CLOUDS
        assert WeatherCondition.from_string("Rain") == WeatherCondition.RAIN

    def test_from_string_prose_matching(self) -> None:
        """Test from_string matches keyword in prose condition descriptions."""
        assert WeatherCondition.from_string("scattered clouds") == WeatherCondition.CLOUDS
        assert WeatherCondition.from_string("light rain") == WeatherCondition.RAIN
        assert WeatherCondition.from_string("heavy thunderstorm") == WeatherCondition.THUNDERSTORM
        assert WeatherCondition.from_string("clear sky") == WeatherCondition.CLEAR

    def test_from_string_unknown_fallback(self) -> None:
        """Test from_string falls back to UNKNOWN for unrecognizable or empty values."""
        assert WeatherCondition.from_string("unheard of weather") == WeatherCondition.UNKNOWN
        assert WeatherCondition.from_string("") == WeatherCondition.UNKNOWN
        assert WeatherCondition.from_string(None) == WeatherCondition.UNKNOWN


class TestDailyForecast:
    """Tests for DailyForecast value object."""

    def test_valid_daily_forecast(self) -> None:
        """Test creating a valid DailyForecast with auto-derived condition_code."""
        df = DailyForecast(
            date="2026-08-19",
            temp_min=14.0,
            temp_max=22.5,
            condition="clear sky",
            icon_code="01d",
        )
        assert df.date == "2026-08-19"
        assert df.temp_min == 14.0
        assert df.temp_max == 22.5
        assert df.condition == "clear sky"
        assert df.condition_code == WeatherCondition.CLEAR
        assert df.icon_code == "01d"

    def test_daily_forecast_explicit_condition_code(self) -> None:
        """Test creating DailyForecast with explicit condition_code."""
        df = DailyForecast(
            date="2026-08-19",
            temp_min=14.0,
            temp_max=22.5,
            condition="light drizzle",
            icon_code="09d",
            condition_code=WeatherCondition.DRIZZLE,
        )
        assert df.condition_code == WeatherCondition.DRIZZLE


class TestRawForecastInterval:
    """Tests for RawForecastInterval."""

    def test_raw_forecast_interval_auto_derives_condition_code(self) -> None:
        """Test RawForecastInterval auto-derives condition_code from condition."""
        interval = RawForecastInterval(
            dt=datetime.now(UTC),
            temp=20.0,
            condition="scattered clouds",
            icon_code="03d",
        )
        assert interval.condition_code == WeatherCondition.CLOUDS

    def test_raw_forecast_interval_explicit_condition_code(self) -> None:
        """Test RawForecastInterval with explicitly passed condition_code."""
        interval = RawForecastInterval(
            dt=datetime.now(UTC),
            temp=20.0,
            condition="scattered clouds",
            icon_code="03d",
            condition_code=WeatherCondition.CLOUDS,
        )
        assert interval.condition_code == WeatherCondition.CLOUDS


class TestForecastData:
    """Tests for ForecastData entity."""

    def test_valid_forecast_data(
        self, sample_coordinates: Coordinates, sample_daily_forecasts: list[DailyForecast]
    ) -> None:
        """Test creating valid ForecastData with 5 daily forecasts."""
        data = ForecastData(
            city_name="London",
            country="GB",
            coordinates=sample_coordinates,
            units=UnitSystem.METRIC,
            daily_forecasts=sample_daily_forecasts,
            timestamp=datetime.now(UTC),
        )
        assert data.city_name == "London"
        assert len(data.daily_forecasts) == 5

    def test_less_than_5_days_raises_value_error(
        self, sample_coordinates: Coordinates, sample_daily_forecasts: list[DailyForecast]
    ) -> None:
        """Test that fewer than 5 daily forecasts raises ValueError."""
        with pytest.raises(ValueError, match="ForecastData must contain exactly 5 daily forecasts"):
            ForecastData(
                city_name="London",
                country="GB",
                coordinates=sample_coordinates,
                units=UnitSystem.METRIC,
                daily_forecasts=sample_daily_forecasts[:4],
                timestamp=datetime.now(UTC),
            )

    def test_more_than_5_days_raises_value_error(
        self, sample_coordinates: Coordinates, sample_daily_forecasts: list[DailyForecast]
    ) -> None:
        """Test that more than 5 daily forecasts raises ValueError."""
        extra_day = DailyForecast(
            date="2026-08-24",
            temp_min=15.0,
            temp_max=24.0,
            condition="sunny",
            icon_code="01d",
        )
        with pytest.raises(ValueError, match="ForecastData must contain exactly 5 daily forecasts"):
            ForecastData(
                city_name="London",
                country="GB",
                coordinates=sample_coordinates,
                units=UnitSystem.METRIC,
                daily_forecasts=[*sample_daily_forecasts, extra_day],
                timestamp=datetime.now(UTC),
            )
