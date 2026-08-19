# Feature Specification: 5-Day Weather Forecast

**Feature Branch**: `006-add-a-5-day-forecast`

**Created**: 2026-08-19

**Status**: Draft

**Input**: User description: "Add a 5-day forecast endpoint: GET /api/v1/weather/{city}/forecast returning a 5-day forecast (daily high/low temperatures and a condition summary per day). Follow the existing clean-architecture layering (domain entity, use case, API route), keep the response shape consistent with our API design standards (versioned path, structured error body on failure), and add unit tests for the new use case and entity validation."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Retrieve 5-Day Daily Forecast by City Name (Priority: P1)

As an API consumer or end user, I want to request a 5-day weather forecast for a specific city by name so that I can view upcoming daily weather trends including daily high/low temperatures, condition summaries, and icon codes to plan ahead.

**Why this priority**: Core value delivery for the feature. Provides multi-day forecasting capability beyond the single-day real-time weather query.

**Independent Test**: Can be fully tested by sending `GET /api/v1/weather/London/forecast` and verifying that the response contains city metadata and an array of exactly 5 consecutive daily forecasts with daily maximum temperature, minimum temperature, condition summary, and icon code.

**Acceptance Scenarios**:

1. **Given** the weather service is available, **When** a client sends `GET /api/v1/weather/London/forecast`, **Then** the system returns HTTP 200 with city name, country code, coordinates, unit system, and an array of exactly 5 consecutive daily forecast entries, each containing `date` (YYYY-MM-DD), `temp_min`, `temp_max`, `condition`, and `icon_code`.
2. **Given** an external provider payload containing 40 3-hour forecast intervals spanning 6 distinct local calendar days (due to local UTC timezone offset), **When** the forecast is aggregated, **Then** the system groups intervals by local calendar date, calculates daily `temp_min` (minimum temperature across intervals) and `temp_max` (maximum temperature across intervals), selects condition/icon from the interval closest to 12:00 local time, and returns the first 5 chronological local calendar days (`days[:5]`).
3. **Given** the weather service is available, **When** a client requests a forecast for a city that does not exist (e.g., `GET /api/v1/weather/NonExistentCityXyz/forecast`), **Then** the system returns HTTP 404 with structured error code `"CITY_NOT_FOUND"` and an informative error message.
4. **Given** a client submits a city path parameter exceeding 100 characters or containing only whitespace, **When** the domain entity validates the request, **Then** the system returns HTTP 400 with structured error code `"INVALID_CITY_NAME"` and a descriptive message.
5. **Given** the external weather provider is unreachable or returns a server error, **When** a client requests a forecast, **Then** the system returns HTTP 502 with structured error code `"PROVIDER_ERROR"`, retry-after guidance (30 seconds), and logs the failure without exposing internal stack traces.

---

### User Story 2 - Forecast Temperature Units and Query Parameter Handling (Priority: P2)

As an API consumer, I want to specify my preferred temperature unit system (`metric` for Celsius or `imperial` for Fahrenheit) via query parameter so that forecast data is presented in the desired measurement format.

**Why this priority**: Regional localization and usability requirement for consumers in different locales, built on top of the P1 forecast retrieval.

**Independent Test**: Can be tested by requesting forecasts with `?units=metric` and `?units=imperial` and verifying temperature values and units indicator in the response payload.

**Acceptance Scenarios**:

1. **Given** a valid city, **When** a client requests `GET /api/v1/weather/London/forecast?units=metric`, **Then** all temperature values (`temp_min`, `temp_max`) are returned in Celsius and `units` is set to `"metric"`.
2. **Given** a valid city, **When** a client requests `GET /api/v1/weather/London/forecast?units=imperial`, **Then** all temperature values (`temp_min`, `temp_max`) are returned in Fahrenheit and `units` is set to `"imperial"`.
3. **Given** a valid city, **When** a client requests `GET /api/v1/weather/London/forecast` without specifying the `units` parameter, **Then** the system defaults to `"metric"` (Celsius).
4. **Given** a valid city, **When** a client supplies an invalid unit parameter (e.g., `?units=kelvin`), **Then** the system rejects the request with HTTP 422 Unprocessable Entity and validation error details.

---

### User Story 3 - In-Memory Caching and Performance Optimization (Priority: P3)

As an API consumer, I want repeated forecast requests for the same city and unit preference to be served rapidly from cache so that response latency is minimized and external provider rate limits are preserved.

**Why this priority**: Operational reliability and efficiency requirement to protect third-party API quotas and ensure fast sub-second response times.

**Independent Test**: Can be tested by issuing two identical forecast requests sequentially; the second request should complete with near-zero latency without triggering a second outbound external provider call.

**Acceptance Scenarios**:

1. **Given** a cached forecast entry exists for a normalized city name and unit system within the 900-second (15-minute) TTL window, **When** a client requests that forecast, **Then** the cached forecast data is returned immediately without contacting the external provider.
2. **Given** external provider rate limits are exceeded (HTTP 429), **When** a client requests a forecast for an uncached city, **Then** the system returns HTTP 429 with structured error code `"RATE_LIMIT_EXCEEDED"`, an appropriate `Retry-After` header, and error body.

---

### Edge Cases

- **6 Calendar Day Window from 40 3-Hour Intervals**: OpenWeatherMap 5-day forecast returns 40 data points at 3-hour increments (120 hours). When converted to local calendar dates using the city's UTC timezone offset (`city.timezone`), the 120-hour window can cover up to 6 distinct local calendar dates (e.g. remaining evening hours of Day 0, full Days 1-4, and early morning hours of Day 5). The aggregation logic MUST sort all grouped calendar dates chronologically and select exactly the first 5 calendar dates (`days[:5]`), guaranteeing an array length of exactly 5.
- **Midday Condition Selection and Equidistant Tie-Breaking**: For each daily bucket, the representative condition summary and icon code MUST be derived from the 3-hour interval closest to 12:00 (midday) local time (minimizing `|local_hour - 12|`). If two intervals are equidistant from 12:00 local time (e.g., intervals at 09:00 and 15:00 local time, each 3 hours away), the tie MUST be broken deterministically by selecting the earlier interval (09:00).
- **Partial Current Day (Late Evening Query)**: If a query is executed late in the day such that 12:00 local time has already passed and only evening intervals remain for today (e.g. 18:00 and 21:00), the interval with the smallest absolute difference from 12:00 for that date is used (e.g. 18:00 has `|18 - 12| = 6` vs 21:00 `|21 - 12| = 9`, so 18:00 is chosen).
- **Special Characters and Diacritics in City Names**: City names containing unicode characters, accents, or spaces (e.g., "München", "São Paulo", "San Francisco") MUST be URL-decoded and supported by the provider query and cache key normalizer (`forecast:{normalized_city}:{units}`).
- **Missing or Empty City Path**: Requests to `/api/v1/weather//forecast` are rejected by the routing framework with HTTP 404 Not Found. Requests with a city parameter composed entirely of whitespace (e.g., `/api/v1/weather/%20%20/forecast`) or exceeding 100 characters fail domain validation and return HTTP 400 Bad Request with code `"INVALID_CITY_NAME"`.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose an HTTP endpoint `GET /api/v1/weather/{city}/forecast` accepting a required `city` path parameter (string, 1-100 characters) and an optional `units` query parameter (`metric` | `imperial`, defaulting to `metric`).
- **FR-002**: The system MUST fetch 3-hour forecast interval data and location timezone offset from the weather provider for the requested city.
- **FR-003**: The system MUST group all provider intervals into local calendar dates (`YYYY-MM-DD`) using the city's UTC timezone offset (`city.timezone` seconds).
- **FR-004**: The system MUST select the first 5 chronological local calendar dates (`days[:5]`) when aggregated intervals span 5 or more local calendar days, ensuring the response contains an array of exactly 5 consecutive daily forecast entries.
- **FR-005**: For each of the 5 selected days, the system MUST compute:
  - `temp_max`: The highest temperature across all 3-hour intervals on that local calendar date.
  - `temp_min`: The lowest temperature across all 3-hour intervals on that local calendar date.
  - `condition`: The weather condition summary string from the 3-hour interval on that date closest to 12:00 local time. In case of an equidistant tie (e.g. 09:00 vs 15:00), the earlier interval (09:00) MUST be selected.
  - `icon_code`: The weather icon code from the same interval selected for `condition`.
  - `date`: The local calendar date string formatted as `YYYY-MM-DD`.
- **FR-006**: The system MUST return city metadata in the response, including `city` (city name), `country` (ISO country code), `coordinates` (`latitude`, `longitude`), `units` (`metric` | `imperial`), and `timestamp` (UTC ISO 8601).
- **FR-007**: The system MUST format the response properties using `snake_case` naming consistent with existing weather endpoints (`city`, `country`, `coordinates`, `daily_forecasts`, `temp_min`, `temp_max`, `condition`, `icon_code`, `units`, `timestamp`).
- **FR-008**: The system MUST cache forecast responses in the in-memory cache for 900 seconds (15 minutes) using a normalized cache key format (`forecast:{city_name_lower}:{units}`).
- **FR-009**: The system MUST validate that city names are non-empty, non-whitespace, and do not exceed 100 characters, raising `InvalidCityNameError` (HTTP 400 Bad Request with code `"INVALID_CITY_NAME"`) if validation fails.
- **FR-010**: The system MUST return HTTP 404 Not Found with code `"CITY_NOT_FOUND"` when the requested city is not found by the weather provider.
- **FR-011**: The system MUST return HTTP 422 Unprocessable Entity when an unsupported `units` query parameter value is provided.
- **FR-012**: The system MUST return HTTP 429 Too Many Requests with code `"RATE_LIMIT_EXCEEDED"` and a `Retry-After` header when external provider rate limits are exceeded.
- **FR-013**: The system MUST return HTTP 502 Bad Gateway with code `"PROVIDER_ERROR"` and a retry-after advisory of 30 seconds when the upstream weather provider fails.
- **FR-014**: All error responses MUST strictly adhere to the structured error envelope: `{"error": {"code": str, "message": str, "retry_after": int | null}}`.

### Key Entities *(include if feature involves data)*

- **ForecastRequest**: Request entity for 5-day forecast queries.
  - Attributes: `city: str` (1-100 chars, stripped), `units: UnitSystem` (default: `UnitSystem.METRIC`).
  - Validation: Non-empty string, length <= 100 characters; raises `InvalidCityNameError` upon validation failure.
  - Methods: `cache_key -> str` (`forecast:{city}:{units}`).
- **DailyForecast**: Value object representing a single day's aggregated forecast.
  - Attributes: `date: str` (ISO 8601 date `YYYY-MM-DD`), `temp_min: float`, `temp_max: float`, `condition: str`, `icon_code: str`.
- **ForecastData**: Domain entity representing the complete 5-day weather forecast.
  - Attributes: `city_name: str`, `country: str`, `coordinates: Coordinates` (`latitude: float`, `longitude: float`), `units: UnitSystem`, `daily_forecasts: list[DailyForecast]` (length exactly 5), `timestamp: datetime`.
- **ForecastResponse**: Presentation schema defining the JSON response payload.
  - Attributes: `city: str`, `country: str`, `coordinates: dict[str, float]`, `units: UnitSystem`, `daily_forecasts: list[DailyForecastResponse]`, `timestamp: datetime`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Cached 5-day forecast requests respond in under 50 milliseconds (p95); uncached requests respond in under 1.5 seconds (p95).
- **SC-002**: 100% of successful responses for valid cities return an array of exactly 5 consecutive daily forecast entries.
- **SC-003**: 100% of error responses return the standard structured error JSON format with correct HTTP status codes (400, 404, 422, 429, 502).
- **SC-004**: Unit test coverage for domain entities, aggregation logic, use cases, and route handlers exceeds the 80% coverage threshold mandated by the project constitution.
- **SC-005**: All code passes Ruff linting (`ruff check src tests`) and strict Mypy type validation (`mypy src`) without suppression or errors.

## Assumptions

- The external weather provider is OpenWeatherMap's 5 day / 3 hour forecast API (`/data/2.5/forecast`), which returns 40 data points with temperature, weather condition summaries, weather icon codes, and the city's UTC timezone offset in seconds (`city.timezone`).
- In-memory cache (`InMemoryCache`) is used with a default TTL of 900 seconds (15 minutes), matching current weather caching behavior.
- Daily temperature highs and lows represent the aggregate extreme temperatures across all 3-hour intervals recorded for that local calendar day.
- Midday weather conditions are represented by the interval closest to 12:00 local time, with earlier intervals winning equidistant ties.
