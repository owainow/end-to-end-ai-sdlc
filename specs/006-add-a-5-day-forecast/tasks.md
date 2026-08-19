# Tasks: 5-Day Weather Forecast Endpoint

**Input**: Design documents from `/specs/006-add-a-5-day-forecast/`  
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: Mandated by project constitution (>= 80% business logic coverage, unit tests for entities/use cases, integration tests with HTTPX ASGI client for all endpoint paths and error codes).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Single project layout: `src/` and `tests/` at repository root

---

## Phase 1: Setup (Shared Infrastructure & Test Fixtures)

**Purpose**: Test harness preparation, shared fixtures, and contract validation setup

- [ ] T001 Create shared forecast test fixtures in `tests/conftest.py` with mock raw 40-interval OpenWeatherMap 5-day forecast payloads (spanning 5 and 6 distinct local calendar days, standard and fractional UTC offsets such as UTC+5:30, and error responses).
- [ ] T002 [P] Create contract integration test in `tests/integration/test_forecast_api.py` validating route schema against `specs/006-add-a-5-day-forecast/contracts/openapi.yaml`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core domain models, port interfaces, cache typing, presentation schemas, and exception handling that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T003 Define domain entities and value objects in `src/domain/entities.py`:
  - `DailyForecast`: `date: str` (`YYYY-MM-DD`), `temp_min: float`, `temp_max: float`, `condition: str`, `icon_code: str`.
  - `ForecastData`: `city_name: str`, `country: str`, `coordinates: Coordinates`, `units: UnitSystem`, `daily_forecasts: list[DailyForecast]`, `timestamp: datetime` with invariant validation ensuring `len(daily_forecasts) == 5`.
  - `ForecastRequest`: `city: str`, `units: UnitSystem` (default: `UnitSystem.METRIC`) with validation rejecting empty/whitespace string or >100 characters by raising `InvalidCityNameError`, and property `cache_key -> str` (`forecast:{city_lower}:{units}`).
  - `RawForecastInterval`: `dt: datetime`, `temp: float`, `condition: str`, `icon_code: str`.
  - `RawForecastData`: `city_name: str`, `country: str`, `coordinates: Coordinates`, `timezone_offset: int`, `intervals: list[RawForecastInterval]`.
- [ ] T004 [P] Update application port interfaces in `src/application/interfaces.py` to add `WeatherProviderPort.get_forecast_raw(city: str, units: UnitSystem) -> RawForecastData` and update `CachePort` methods (`get(key: str) -> WeatherData | ForecastData | None`, `set(key: str, value: WeatherData | ForecastData, ttl_seconds: int) -> None`).
- [ ] T005 [P] Update `InMemoryCache` in `src/infrastructure/cache.py` to store and retrieve `WeatherData | ForecastData | None` in thread-safe memory with TTL.
- [ ] T006 [P] Update `GetWeatherUseCase` in `src/application/use_cases/get_weather.py` to include strict type narrowing (`isinstance(cached_data, WeatherData)`) for polymorphic cache retrieval, ensuring 100% strict Mypy type-check compliance.
- [ ] T007 [P] Define presentation schemas in `src/presentation/schemas.py`:
  - `DailyForecastResponse`: `date: str`, `temp_min: float`, `temp_max: float`, `condition: str`, `icon_code: str`.
  - `ForecastResponse`: `city: str`, `country: str`, `coordinates: dict[str, float]`, `units: UnitSystem`, `daily_forecasts: list[DailyForecastResponse]`, `timestamp: datetime`.
- [ ] T008 [P] Ensure exception handling in `src/presentation/exception_handlers.py` and `src/main.py` maps domain exceptions to structured JSON error envelopes (`{"error": {"code": str, "message": str, "retry_after": int | null}}`): `InvalidCityNameError` -> 400 (`"INVALID_CITY_NAME"`), `CityNotFoundError` -> 404 (`"CITY_NOT_FOUND"`), `RateLimitExceededError` -> 429 (`"RATE_LIMIT_EXCEEDED"`), and `WeatherProviderError` -> 502 (`"PROVIDER_ERROR"` with 30s retry-after).

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Retrieve 5-Day Daily Forecast by City Name (Priority: P1) 🎯 MVP

**Goal**: Enable consumers to request `GET /api/v1/weather/{city}/forecast` and receive a structured 5-day daily forecast containing city metadata and exactly 5 consecutive local calendar days of high/low temperatures, condition summary, and icon code.

**Independent Test**: Send `GET /api/v1/weather/London/forecast` and verify HTTP 200 with metadata and an array of exactly 5 consecutive daily forecasts (`daily_forecasts`).

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T009 [P] [US1] Create unit tests for `ForecastRequest`, `DailyForecast`, and `ForecastData` entity validation in `tests/unit/test_entities.py` (validate empty/whitespace city raising `InvalidCityNameError`, city >100 chars, `len(daily_forecasts) != 5` invariant check).
- [ ] T010 [P] [US1] Create unit tests for `GetForecastUseCase` in `tests/unit/test_forecast_use_case.py` verifying:
  - Local calendar date grouping using UTC timezone offset (`timezone_offset`).
  - Chronological sorting and selection of the first 5 local calendar days (`sorted_dates[:5]`).
  - Daily extreme temperature calculation (`temp_min = min(temps)`, `temp_max = max(temps)`).
  - Midday condition selection minimizing second-precision distance from 12:00:00 local time (`abs((local_dt.hour * 3600 + local_dt.minute * 60 + local_dt.second) - 43200)`).
  - Deterministic earlier-interval tie-breaking when two intervals are equidistant from midday (including fractional UTC offsets like UTC+5:30).
  - `WeatherProviderError` raised when the provider returns fewer than 5 local calendar days.
- [ ] T011 [P] [US1] Create integration tests for `GET /api/v1/weather/{city}/forecast` in `tests/integration/test_forecast_api.py` (200 success with 5 days, 404 city not found, 400 invalid city name, 502 provider error).

### Implementation for User Story 1

- [ ] T012 [US1] Implement `OpenWeatherMapClient.get_forecast_raw(city: str, units: UnitSystem) -> RawForecastData` in `src/infrastructure/weather_provider.py` to query OpenWeatherMap `/data/2.5/forecast`, mapping HTTP errors to domain exceptions (`CityNotFoundError`, `RateLimitExceededError`, `WeatherProviderError`) and parsing intervals without business aggregation.
- [ ] T013 [US1] Implement `GetForecastUseCase` in `src/application/use_cases/get_forecast.py` (and re-export in `src/application/use_cases/__init__.py`) executing timezone conversion, grouping by local date, validation of `>= 5` days (raising `WeatherProviderError` if `< 5`), slicing `[:5]`, calculating daily `temp_min`/`temp_max`, and selecting midday condition/icon using second-precision distance with deterministic earlier-interval tie-breaking.
- [ ] T014 [US1] Create `get_forecast_use_case` dependency provider in `src/presentation/dependencies.py`.
- [ ] T015 [US1] Implement route `GET /api/v1/weather/{city}/forecast` in `src/presentation/routers/weather.py` using `city: str = Path(..., min_length=1, max_length=100)`, calling `GetForecastUseCase.execute(ForecastRequest(city=city, units=UnitSystem.METRIC))`, and mapping `ForecastData` to `ForecastResponse`.

**Checkpoint**: At this point, User Story 1 is fully functional and testable independently as an MVP.

---

## Phase 4: User Story 2 - Forecast Temperature Units and Query Parameter Handling (Priority: P2)

**Goal**: Allow clients to specify temperature units (`metric` for Celsius, `imperial` for Fahrenheit) via the `units` query parameter on `GET /api/v1/weather/{city}/forecast`, defaulting to `metric`.

**Independent Test**: Request `GET /api/v1/weather/London/forecast?units=imperial` and verify temperatures are in Fahrenheit and `units` is `"imperial"`.

### Tests for User Story 2 ⚠️

- [ ] T016 [P] [US2] Create unit tests in `tests/unit/test_forecast_use_case.py` verifying `GetForecastUseCase` correctly passes `UnitSystem.METRIC` and `UnitSystem.IMPERIAL` through `ForecastRequest` to the provider and domain entity.
- [ ] T017 [P] [US2] Create integration tests in `tests/integration/test_forecast_api.py` for query parameter handling:
  - `?units=metric` returns Celsius values and `units: "metric"`.
  - `?units=imperial` returns Fahrenheit values and `units: "imperial"`.
  - Omitting `units` defaults to `units: "metric"`.
  - Unsupported `?units=kelvin` returns HTTP 422 Unprocessable Entity.

### Implementation for User Story 2

- [ ] T018 [US2] Update `GET /api/v1/weather/{city}/forecast` route in `src/presentation/routers/weather.py` to accept `units: UnitSystem = Query(default=UnitSystem.METRIC)` and pass it into `ForecastRequest(city=city, units=units)` for use case execution.

**Checkpoint**: At this point, User Stories 1 AND 2 work seamlessly together.

---

## Phase 5: User Story 3 - In-Memory Caching and Performance Optimization (Priority: P3)

**Goal**: Implement in-memory TTL caching (15-minute / 900s) for forecast responses using key `forecast:{city_lower}:{units}` to provide low-latency responses and protect external provider rate limits.

**Independent Test**: Issue two identical forecast requests sequentially; the second request must return cached data without an external provider call.

### Tests for User Story 3 ⚠️

- [ ] T019 [P] [US3] Create unit tests in `tests/unit/test_forecast_use_case.py` verifying cache hit returns cached `ForecastData` immediately with debug logging, and cache miss fetches from provider, caches result with 900s TTL, and logs info.
- [ ] T020 [P] [US3] Create integration tests in `tests/integration/test_forecast_api.py` verifying sequential identical requests hit cache, and provider 429 rate limit returns HTTP 429 with `RATE_LIMIT_EXCEEDED` and `Retry-After` header.

### Implementation for User Story 3

- [ ] T021 [US3] Update `GetForecastUseCase` in `src/application/use_cases/get_forecast.py` to accept `cache: CachePort`, `logger: LoggerPort`, and `cache_ttl_seconds: int = 900` in `__init__`, checking `cache.get(request.cache_key)` on invocation, storing `cache.set(request.cache_key, forecast_data, self._cache_ttl)` on miss, and emitting structured logs.
- [ ] T022 [US3] Update `get_forecast_use_case` dependency provider in `src/presentation/dependencies.py` to inject `cache=get_cache()`, `logger=get_logger()`, and `cache_ttl_seconds=settings.cache_ttl_seconds`.

**Checkpoint**: All user stories (US1, US2, US3) are independently functional, cached, and fully tested.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: API documentation synchronization, static analysis, linting, and test coverage verification

- [ ] T023 [P] Update OpenAPI route metadata and descriptions in `src/presentation/routers/weather.py` and `src/main.py` matching `/specs/006-add-a-5-day-forecast/contracts/openapi.yaml`.
- [ ] T024 [P] Validate `specs/006-add-a-5-day-forecast/quickstart.md` commands and sample responses against the running application.
- [ ] T025 Run full Pytest test suite with coverage enforcement (`pytest --cov=src --cov-fail-under=80 tests/`) to ensure >= 80% coverage on business logic.
- [ ] T026 [P] Run Ruff linter and formatter check (`ruff check src tests` and `ruff format --check src tests`) to ensure compliance with 100-character line length limit.
- [ ] T027 [P] Run Mypy strict type checking (`mypy src tests`) to ensure zero type errors under `strict = true`.

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1: Setup ──────────────────────┐
                                     │
Phase 2: Foundational ◀──────────────┘
         │
         ├──▶ Phase 3: US1 (P1) ─┐
         │                       │
         ├──▶ Phase 4: US2 (P2) ─┼──▶ Phase 6: Polish
         │                       │
         └──▶ Phase 5: US3 (P3) ─┘
```

- **Setup (Phase 1)**: No dependencies - can start immediately.
- **Foundational (Phase 2)**: Depends on Phase 1 - BLOCKS all user stories.
- **User Story 1 (Phase 3)**: Depends on Foundational completion. Delivers core MVP.
- **User Story 2 (Phase 4)**: Depends on Foundational and builds on US1 route.
- **User Story 3 (Phase 5)**: Depends on Foundational and integrates caching into US1 use case & dependencies.
- **Polish (Phase 6)**: Depends on all user stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Independent of US2/US3.
- **User Story 2 (P2)**: Extends US1 route with `units` query parameter.
- **User Story 3 (P3)**: Adds caching and logging to US1 use case and updates dependency injection.

### Within Each User Story

- Tests (TDD) MUST be written and fail before implementation.
- Domain models and ports before services/use cases.
- Use cases before presentation routers.
- Dependency injection providers updated in lockstep with use case constructors.

### Parallel Opportunities

- **Phase 1**: T001 and T002 can run in parallel.
- **Phase 2**: T004, T005, T006, T007, T008 can run in parallel once T003 is established.
- **Phase 3 Tests**: T009, T010, T011 can run in parallel.
- **Phase 4 Tests**: T016 and T017 can run in parallel.
- **Phase 5 Tests**: T019 and T020 can run in parallel.
- **Phase 6**: T023, T024, T026, T027 can run in parallel.

---

## Parallel Example: User Story 1

```bash
# Launch all US1 tests in parallel:
pytest tests/unit/test_entities.py -k "forecast" &
pytest tests/unit/test_forecast_use_case.py &
pytest tests/integration/test_forecast_api.py &
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T002).
2. Complete Phase 2: Foundational (T003-T008) - critical prerequisite.
3. Complete Phase 3: User Story 1 (T009-T015).
4. **STOP and VALIDATE**: Verify `GET /api/v1/weather/London/forecast` returns 5 consecutive daily forecasts.
5. Deploy/demo MVP.

### Incremental Delivery

1. Foundation ready (Phase 1 & 2).
2. Add User Story 1 (Phase 3) -> Basic 5-day forecast lookup (MVP).
3. Add User Story 2 (Phase 4) -> Unit system parameterization (`metric`/`imperial`).
4. Add User Story 3 (Phase 5) -> In-memory TTL caching (15 min) and rate limit handling.
5. Polish (Phase 6) -> OpenAPI docs, linting, strict typing, and test coverage verification.

---

## Notes

- All tasks include exact file paths for automated agent execution.
- [P] tasks indicate different files and no dependencies.
- [Story] labels (US1, US2, US3) map tasks directly to user stories for traceability.
- Strict Clean Architecture dependency flow is preserved: Domain -> Application -> Infrastructure / Presentation.
- Strict typing and linting standards verified at every phase.
