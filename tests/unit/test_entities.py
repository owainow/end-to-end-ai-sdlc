"""Unit tests for domain entities."""

from datetime import UTC, date, datetime

import pytest

from src.domain.entities import ForecastData, ForecastDay, WeatherData, WeatherRequest
from src.domain.value_objects import Coordinates, UnitSystem


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
        with pytest.raises(
            ValueError, match="Either city name or coordinates must be provided"
        ):
            WeatherRequest(city="")

    def test_whitespace_city_raises_error(self) -> None:
        """Test that whitespace-only city raises ValueError."""
        with pytest.raises(
            ValueError, match="Either city name or coordinates must be provided"
        ):
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
        with pytest.raises(
            ValueError, match="Either city name or coordinates must be provided"
        ):
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
        request = WeatherRequest(
            city="London", coordinates=coords, units=UnitSystem.METRIC
        )
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


class TestForecastDay:
    """Tests for ForecastDay entity."""

    def test_temperature_displays_metric(self) -> None:
        """Test high/low temperature display for metric units."""
        day = ForecastDay(
            date=date(2026, 4, 15),
            day_label="Today",
            temp_high=16.3,
            temp_low=8.4,
            humidity=70,
            wind_speed=5.2,
            description="clear sky",
            icon_code="01d",
            units=UnitSystem.METRIC,
        )

        assert day.temp_high_display == "16.3°C"
        assert day.temp_low_display == "8.4°C"

    def test_wind_speed_display_imperial(self) -> None:
        """Test wind speed display for imperial units."""
        day = ForecastDay(
            date=date(2026, 4, 16),
            day_label="Thu",
            temp_high=61.0,
            temp_low=49.5,
            humidity=65,
            wind_speed=10.8,
            description="few clouds",
            icon_code="02d",
            units=UnitSystem.IMPERIAL,
        )

        assert day.wind_speed_display == "10.8 mph"


class TestForecastData:
    """Tests for ForecastData entity."""

    def test_forecast_data_fields(self) -> None:
        """Test creating forecast data with day list."""
        days = [
            ForecastDay(
                date=date(2026, 4, 15),
                day_label="Today",
                temp_high=16.3,
                temp_low=8.4,
                humidity=70,
                wind_speed=5.2,
                description="clear sky",
                icon_code="01d",
                units=UnitSystem.METRIC,
            )
        ]
        forecast = ForecastData(
            city_name="London",
            country="GB",
            coordinates=Coordinates(latitude=51.5074, longitude=-0.1278),
            days=days,
            units=UnitSystem.METRIC,
            timestamp=datetime.now(UTC),
        )

        assert forecast.city_name == "London"
        assert len(forecast.days) == 1
