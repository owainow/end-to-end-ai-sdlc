"""Unit tests for the cache implementation."""

from datetime import UTC, datetime

import pytest

from src.domain.entities import WeatherData
from src.domain.value_objects import Coordinates, UnitSystem
from src.infrastructure.cache import InMemoryCache


class TestInMemoryCache:
    """Tests for InMemoryCache."""

    @pytest.fixture
    def cache(self) -> InMemoryCache:
        """Create a fresh cache instance."""
        return InMemoryCache()

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
            weather_main="Clouds",
            units=UnitSystem.METRIC,
            timestamp=datetime.now(UTC),
        )

    def test_get_nonexistent_key(self, cache: InMemoryCache) -> None:
        """Test getting a key that doesn't exist."""
        result = cache.get("nonexistent")
        assert result is None

    def test_set_and_get(
        self, cache: InMemoryCache, weather_data: WeatherData
    ) -> None:
        """Test setting and getting a value."""
        cache.set("test_key", weather_data, ttl_seconds=300)
        result = cache.get("test_key")

        assert result is not None
        assert result.city_name == "London"
        assert result.temperature == 15.2

    def test_delete(self, cache: InMemoryCache, weather_data: WeatherData) -> None:
        """Test deleting a cached entry."""
        cache.set("delete_key", weather_data, ttl_seconds=300)
        assert cache.get("delete_key") is not None

        cache.delete("delete_key")
        assert cache.get("delete_key") is None

    def test_delete_nonexistent(self, cache: InMemoryCache) -> None:
        """Test deleting a nonexistent key (should not raise)."""
        cache.delete("nonexistent")  # Should not raise

    def test_clear(self, cache: InMemoryCache, weather_data: WeatherData) -> None:
        """Test clearing all entries."""
        cache.set("key1", weather_data, ttl_seconds=300)
        cache.set("key2", weather_data, ttl_seconds=300)

        assert cache.size == 2

        cache.clear()

        assert cache.size == 0
        assert cache.get("key1") is None
        assert cache.get("key2") is None

    def test_size(self, cache: InMemoryCache, weather_data: WeatherData) -> None:
        """Test size property."""
        assert cache.size == 0

        cache.set("key1", weather_data, ttl_seconds=300)
        assert cache.size == 1

        cache.set("key2", weather_data, ttl_seconds=300)
        assert cache.size == 2

    def test_overwrite(self, cache: InMemoryCache) -> None:
        """Test overwriting an existing key."""
        data1 = WeatherData(
            city_name="London",
            country="GB",
            coordinates=Coordinates(latitude=51.5074, longitude=-0.1278),
            temperature=15.0,
            feels_like=14.0,
            humidity=70,
            wind_speed=4.0,
            pressure=1010,
            visibility=10000,
            description="cloudy",
            icon_code="03d",
            weather_main="Clouds",
            units=UnitSystem.METRIC,
            timestamp=datetime.now(UTC),
        )
        data2 = WeatherData(
            city_name="London",
            country="GB",
            coordinates=Coordinates(latitude=51.5074, longitude=-0.1278),
            temperature=20.0,
            feels_like=19.0,
            humidity=60,
            wind_speed=3.0,
            pressure=1020,
            visibility=10000,
            description="sunny",
            icon_code="01d",
            weather_main="Clear",
            units=UnitSystem.METRIC,
            timestamp=datetime.now(UTC),
        )

        cache.set("london", data1, ttl_seconds=300)
        cache.set("london", data2, ttl_seconds=300)

        result = cache.get("london")
        assert result is not None
        assert result.temperature == 20.0
        assert result.description == "sunny"
