"""Unit tests for city boundary validation rules and query parameter handling."""

import pytest
from fastapi import HTTPException

from src.presentation.dependencies import (
    validate_city_name,
    validate_weather_query_params,
)


class TestCityNameValidation:
    """Unit tests for validate_city_name rule function."""

    @pytest.mark.parametrize(
        "valid_city,expected",
        [
            ("London", "London"),
            ("New York", "New York"),
            ("São Paulo", "São Paulo"),
            ("München", "München"),
            ("Saint-Étienne", "Saint-Étienne"),
            ("Tokyo", "Tokyo"),
            ("Malmö", "Malmö"),
            ("København", "København"),
            ("7th District", "7th District"),
            ("Sector 7", "Sector 7"),
        ],
    )
    def test_valid_city_names(self, valid_city: str, expected: str) -> None:
        """Test that valid city names pass validation."""
        assert validate_city_name(valid_city) == expected

    @pytest.mark.parametrize(
        "city_with_whitespace,expected",
        [
            (" London ", "London"),
            ("   São Paulo  ", "São Paulo"),
            ("\tTokyo\n", "Tokyo"),
        ],
    )
    def test_whitespace_trimming(self, city_with_whitespace: str, expected: str) -> None:
        """Test that leading and trailing whitespace is trimmed."""
        assert validate_city_name(city_with_whitespace) == expected

    @pytest.mark.parametrize("empty_input", ["", "   ", "\t\n"])
    def test_empty_city_raises_422(self, empty_input: str) -> None:
        """Test that empty or whitespace-only city names raise HTTP 422."""
        with pytest.raises(HTTPException) as exc_info:
            validate_city_name(empty_input)

        assert exc_info.value.status_code == 422
        assert exc_info.value.detail["message"] == "City name cannot be empty"
        assert exc_info.value.detail["target"] == "city"

    def test_overlong_city_raises_422(self) -> None:
        """Test that city names over 100 characters raise HTTP 422."""
        long_city = "a" * 101
        with pytest.raises(HTTPException) as exc_info:
            validate_city_name(long_city)

        assert exc_info.value.status_code == 422
        assert exc_info.value.detail["message"] == "City name must not exceed 100 characters"
        assert exc_info.value.detail["target"] == "city"

    def test_overlong_city_trimmed_length_check(self) -> None:
        """Test that city length is checked after whitespace trimming."""
        # 100 'a's padded with whitespace is valid after trimming
        valid_padded = "   " + ("a" * 100) + "   "
        assert len(validate_city_name(valid_padded)) == 100

        # 101 'a's padded with whitespace fails after trimming
        invalid_padded = "   " + ("a" * 101) + "   "
        with pytest.raises(HTTPException) as exc_info:
            validate_city_name(invalid_padded)
        assert exc_info.value.status_code == 422

    @pytest.mark.parametrize(
        "invalid_symbolic_input",
        [
            "12345",
            "123-456",
            "123 456",
            "!!!",
            "@#$%^&*",
            "123.456",
            "---",
        ],
    )
    def test_numeric_or_symbolic_city_raises_422(self, invalid_symbolic_input: str) -> None:
        """Test that strings without alphabetic characters raise HTTP 422."""
        with pytest.raises(HTTPException) as exc_info:
            validate_city_name(invalid_symbolic_input)

        assert exc_info.value.status_code == 422
        assert (
            exc_info.value.detail["message"]
            == "City name must contain letters and cannot consist only of numbers or special characters"
        )
        assert exc_info.value.detail["target"] == "city"


class TestWeatherQueryParamsValidation:
    """Unit tests for validate_weather_query_params dependency."""

    def test_valid_city_query(self) -> None:
        """Test valid city query parameter."""
        city, lat, lon = validate_weather_query_params(city="London")
        assert city == "London"
        assert lat is None
        assert lon is None

    def test_valid_coordinates_query(self) -> None:
        """Test valid coordinates query without city."""
        city, lat, lon = validate_weather_query_params(lat=51.5074, lon=-0.1278)
        assert city is None
        assert lat == 51.5074
        assert lon == -0.1278

    def test_missing_both_city_and_coordinates_raises_422(self) -> None:
        """Test that omitting both city and coordinates raises HTTP 422."""
        with pytest.raises(HTTPException) as exc_info:
            validate_weather_query_params(city=None, lat=None, lon=None)

        assert exc_info.value.status_code == 422
        assert (
            exc_info.value.detail["message"]
            == "Either city or coordinates (lat and lon) must be provided"
        )
        assert exc_info.value.detail["target"] == "city"

    @pytest.mark.parametrize(
        "lat_val,lon_val",
        [
            (51.5074, None),
            (None, -0.1278),
        ],
    )
    def test_incomplete_coordinates_raises_422(
        self, lat_val: float | None, lon_val: float | None
    ) -> None:
        """Test that providing lat without lon or lon without lat raises HTTP 422."""
        with pytest.raises(HTTPException) as exc_info:
            validate_weather_query_params(city=None, lat=lat_val, lon=lon_val)

        assert exc_info.value.status_code == 422
        assert (
            exc_info.value.detail["message"]
            == "Both lat and lon must be provided together, or neither"
        )
        assert exc_info.value.detail["target"] == "coordinates"

    def test_city_validation_runs_first_when_both_city_and_coords_provided(self) -> None:
        """Test that invalid city is rejected even if valid coordinates are supplied."""
        with pytest.raises(HTTPException) as exc_info:
            validate_weather_query_params(city="12345", lat=51.5074, lon=-0.1278)

        assert exc_info.value.status_code == 422
        assert (
            exc_info.value.detail["message"]
            == "City name must contain letters and cannot consist only of numbers or special characters"
        )
        assert exc_info.value.detail["target"] == "city"

    def test_valid_city_and_valid_coordinates_query(self) -> None:
        """Test that both valid city and valid coordinates pass validation."""
        city, lat, lon = validate_weather_query_params(
            city="London", lat=51.5074, lon=-0.1278
        )
        assert city == "London"
        assert lat == 51.5074
        assert lon == -0.1278
