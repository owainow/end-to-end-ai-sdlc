# Implementation Plan: 5-Day Weather Forecast Endpoint

**Branch**: `006-add-a-5-day-forecast` | **Date**: 2026-08-19 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/006-add-a-5-day-forecast/spec.md`

## Summary

Add a 5-day weather forecast endpoint (`GET /api/v1/weather/{city}/forecast`) returning an array of exactly 5 consecutive local calendar days, each with daily high/low temperatures, condition summary, and icon code.

The architecture strictly adheres to Clean Architecture with inward-only dependencies:
1. **Infrastructure Layer**: `OpenWeatherMapClient` implements `WeatherProviderPort.get_forecast_raw` to fetch raw 3-hour interval forecast payloads (`RawForecastData` / `RawForecastInterval`) and timezone offset (`timezone_offset: int`) from the OpenWeatherMap `/data/2.5/forecast` endpoint without executing business aggregation.
2. **Application Layer**: `GetForecastUseCase` coordinates 15-minute caching (`InMemoryCache`), checks cache by key `forecast:{city_lower}:{units}`, calls `WeatherProviderPort.get_forecast_raw` on miss, and executes the business aggregation logic:
   - Groups 3-hour intervals by local calendar date (`YYYY-MM-DD`) using the city's UTC timezone offset (`timezone_offset` in seconds).
   - Validates that the provider payload spans at least 5 distinct local calendar days; if `< 5` days are returned, raises `WeatherProviderError` (mapped to HTTP 502 `PROVIDER_ERROR`).
   - Slices the first 5 chronological local calendar days (`sorted_dates[:5]`).
   - Computes daily extreme temperatures (`temp_min = min(temps)`, `temp_max = max(temps)`).
   - Selects condition summary and icon code using second-precision distance from 12:00:00 local time (`abs((local_dt.hour * 3600 + local_dt.minute * 60 + local_dt.second) - 43200)`), breaking ties deterministically by choosing the earlier interval (`local_dt`).
   - Constructs the `ForecastData` domain entity and writes it to the TTL cache.
3. **Domain Layer**: Defines `ForecastRequest`, `DailyForecast`, `ForecastData`, `RawForecastData`, and `RawForecastInterval`. `ForecastData` enforces an invariant requiring exactly 5 `DailyForecast` entries.
4. **Presentation Layer**: Exposes `GET /api/v1/weather/{city}/forecast` via FastAPI, validating path/query parameters, translating `ForecastData` to `ForecastResponse` (`DailyForecastResponse`), and utilizing global exception handlers for RFC-compliant structured error bodies.

## Technical Context

**Language/Version**: Python 3.11+ (CPython)  
**Primary Dependencies**: FastAPI (>=0.109.0), Uvicorn (>=0.27.0), HTTPX (>=0.26.0), Pydantic v2 (>=2.5.0), pydantic-settings (>=2.1.0), Structlog (>=24.1.0)  
**Storage**: In-memory TTL cache (`InMemoryCache` with 900s expiration); no relational or persistent database  
**Testing**: Pytest (>=7.4.0) with `pytest-asyncio` and `pytest-cov` (target: >=80% coverage on business logic)  
**Target Platform**: Linux (Azure Container Apps / Docker `python:3.11-slim`)  
**Project Type**: Single API web-service with static client assets  
**Performance Goals**: <50ms p95 latency for cached forecast queries, <1500ms p95 latency for uncached queries  
**Constraints**: 900-second cache TTL, strict 5-day daily forecast length, inward-only architectural dependency flow, strict Mypy typing (`strict = true`), Ruff linting with 100-character line limit  
**Scale/Scope**: Public weather API endpoint supporting metric and imperial unit conversions

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle / Rule | Status | Evidence / Compliance Strategy |
|---|---|---|
| **I. Clean Architecture** | ✅ PASS | Strict layer separation: Domain entities (`ForecastData`, `DailyForecast`, `RawForecastData`) have no dependencies. Application layer (`GetForecastUseCase`) holds all grouping, tie-breaking, and validation logic. Infrastructure (`OpenWeatherMapClient`) only adapts raw HTTP responses to domain transfer objects without aggregation. Presentation layer (`weather_router`, `ForecastResponse`) handles routing and serialization. |
| **II. API-First Design & Standards** | ✅ PASS | Route versioned at `/api/v1/weather/{city}/forecast`. Response schema follows snake_case naming (`city`, `country`, `coordinates`, `daily_forecasts`, `temp_min`, `temp_max`, `condition`, `icon_code`, `units`, `timestamp`). Standard error format `{"error": {"code": str, "message": str, "retry_after": int | null}}` with typed error codes (`CITY_NOT_FOUND`, `INVALID_CITY_NAME`, `PROVIDER_ERROR`, `RATE_LIMIT_EXCEEDED`). |
| **III. Tech Stack Constraints** | ✅ PASS | Python 3.11+, FastAPI, HTTPX, Pydantic v2, Structlog, `InMemoryCache`. No new unvetted external dependencies. |
| **IV. Testing Bar (>=80% Coverage)** | ✅ PASS | Unit tests for `ForecastRequest` validation, `ForecastData` invariant validation, and `GetForecastUseCase` (grouping, tie-breaking across fractional timezones, caching, error handling). Integration tests via HTTPX ASGI client for `GET /api/v1/weather/{city}/forecast` (200, 400, 404, 422, 429, 502). |
| **V. Static Typing & Linting** | ✅ PASS | Full explicit type annotations passing Mypy in `strict = true` mode. Code conforms to Ruff rules (`E`, `W`, `F`, `I`, `B`, `C4`, `UP`, `ARG`, `SIM`) with 100-char line limit. |

**Gate Status**: ✅ All gates pass.

## Project Structure

### Documentation (this feature)

```text
specs/006-add-a-5-day-forecast/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (OpenAPI spec)
│   └── openapi.yaml
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
src/
├── domain/
│   ├── entities.py             # ForecastRequest, DailyForecast, ForecastData, RawForecastData, RawForecastInterval
│   ├── exceptions.py           # CityNotFoundError, InvalidCityNameError, WeatherProviderError, RateLimitExceededError
│   └── value_objects.py        # Coordinates, UnitSystem
├── application/
│   ├── interfaces.py           # WeatherProviderPort, CachePort (generic/typed for WeatherData | ForecastData), LoggerPort
│   └── use_cases/
│       ├── get_weather.py      # Existing current weather use case
│       └── get_forecast.py     # New GetForecastUseCase (grouping, tie-breaking, 5-day validation)
├── infrastructure/
│   ├── cache.py                # InMemoryCache (supports caching ForecastData alongside WeatherData)
│   ├── config.py               # Settings (API keys, base URL, cache TTL)
│   ├── logging.py              # StructlogAdapter
│   └── weather_provider.py     # OpenWeatherMapClient (implements get_forecast_raw -> RawForecastData)
├── presentation/
│   ├── dependencies.py         # get_forecast_use_case dependency injector
│   ├── exception_handlers.py   # Exception handlers mapping domain errors to HTTP JSON responses
│   ├── middleware.py           # RequestLoggingMiddleware
│   ├── routers/
│   │   ├── health.py           # Health and readiness routes
│   │   └── weather.py          # GET /weather and new GET /weather/{city}/forecast route
│   └── schemas.py              # DailyForecastResponse, ForecastResponse, ErrorResponse
└── main.py                     # FastAPI application setup and router mounting

tests/
├── conftest.py                 # Shared fixtures (mock raw forecast payloads, mock provider, cache fixtures)
├── unit/
│   ├── test_entities.py        # WeatherData, WeatherRequest, ForecastRequest, DailyForecast, ForecastData validation
│   ├── test_use_cases.py       # Current weather use case tests
│   ├── test_forecast_use_case.py # Unit tests for GetForecastUseCase (aggregation, tie-breaking, <5 days error, cache)
│   └── test_cache.py           # Cache storage and expiration tests
└── integration/
    ├── test_api.py             # Current weather and health endpoint tests
    └── test_forecast_api.py    # Integration tests for GET /api/v1/weather/{city}/forecast (200, 400, 404, 422, 429, 502)
```

**Structure Decision**:
1. **Clean Separation of Aggregation vs. Provider Adapter**:
   - `WeatherProviderPort` defines `async def get_forecast_raw(self, city: str, units: UnitSystem) -> RawForecastData`.
   - `OpenWeatherMapClient` in `src/infrastructure/weather_provider.py` queries `/data/2.5/forecast?q={city}&units={units.value}&appid={key}`, parses HTTP errors into `CityNotFoundError`, `RateLimitExceededError`, or `WeatherProviderError`, and maps the 40 raw 3-hour data points into `RawForecastData(city_name=..., country=..., coordinates=..., timezone_offset=..., intervals=[RawForecastInterval(dt=..., temp=..., condition=..., icon_code=...)])`. It does not perform calendar day grouping or condition selection.
   - `GetForecastUseCase` in `src/application/use_cases/get_forecast.py` owns all business aggregation:
     - Converts each interval timestamp `dt` to local datetime using `timezone(timedelta(seconds=raw_data.timezone_offset))`.
     - Groups intervals by local date `YYYY-MM-DD`.
     - Checks `if len(grouped_days) < 5:` and raises `WeatherProviderError(f"Insufficient forecast data: expected at least 5 days, received {len(grouped_days)}")`.
     - Takes `sorted_dates = sorted(grouped_days.keys())[:5]`.
     - Computes daily `temp_min` and `temp_max`.
     - Selects condition and icon by minimizing second-precision distance from 12:00:00 local time:
       `key=lambda interval: (abs((interval.local_dt.hour * 3600 + interval.local_dt.minute * 60 + interval.local_dt.second) - 43200), interval.local_dt)`. This guarantees accurate midday selection for standard and fractional UTC offsets (e.g., UTC+5:30) and deterministic earlier-interval tie-breaking.
     - Instantiates `ForecastData` with 5 `DailyForecast` items and stores it in `InMemoryCache` with key `forecast:{city_lower}:{units}`.
2. **Presentation Contract**:
   - `DailyForecastResponse` schema: `date: str`, `temp_min: float`, `temp_max: float`, `condition: str`, `icon_code: str`.
   - `ForecastResponse` schema: `city: str`, `country: str`, `coordinates: dict[str, float]`, `units: UnitSystem`, `daily_forecasts: list[DailyForecastResponse]`, `timestamp: datetime`.
   - Route `GET /api/v1/weather/{city}/forecast` with path parameter `city: str` (validated 1-100 chars, whitespace trimmed) and query parameter `units: UnitSystem = UnitSystem.METRIC`.

## Complexity Tracking

> No constitution violations requiring justification. All patterns follow established Clean Architecture standards.
