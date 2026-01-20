# Tasks: Real-Time City Weather API

**Input**: Design documents from `/specs/001-realtime-city-weather/`  
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: Included per constitution requirement (80% coverage, integration tests for all endpoints)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Project Initialization)

**Purpose**: Create project structure and configure development environment

- [ ] T001 Create project directory structure per plan.md in src/domain/, src/application/, src/infrastructure/, src/presentation/
- [ ] T002 Initialize Python project with pyproject.toml (Python 3.11+, FastAPI, httpx, pydantic, python-dotenv)
- [ ] T003 [P] Create requirements.txt with pinned dependencies
- [ ] T004 [P] Configure Ruff linting in pyproject.toml
- [ ] T005 [P] Configure mypy strict mode in pyproject.toml
- [ ] T006 [P] Create .env.example with required environment variables (OPENWEATHERMAP_API_KEY, CACHE_TTL_SECONDS, LOG_LEVEL, ENVIRONMENT)
- [ ] T007 [P] Create .gitignore for Python project (venv, __pycache__, .env, .pytest_cache)
- [ ] T008 Create tests/ directory structure with tests/unit/, tests/integration/, tests/conftest.py

**Checkpoint**: Project skeleton ready for development

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story implementation

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T009 Create domain exceptions in src/domain/exceptions.py (CityNotFoundError, WeatherProviderUnavailableError, RateLimitExceededError, StaleDataError, ValidationError)
- [ ] T010 [P] Create UnitSystem enum in src/domain/entities.py (metric, imperial)
- [ ] T011 [P] Create Coordinates dataclass in src/domain/entities.py (latitude, longitude with validation)
- [ ] T012 Create WeatherData entity in src/domain/entities.py (all fields per data-model.md)
- [ ] T013 Create WeatherRequest entity in src/domain/entities.py (city, units with validation)
- [ ] T014 Create port interfaces in src/application/interfaces.py (WeatherProviderPort, CachePort)
- [ ] T015 [P] Create environment configuration in src/infrastructure/config.py (Settings class with pydantic-settings)
- [ ] T016 [P] Create structured logging setup in src/infrastructure/logging.py (structlog JSON configuration)
- [ ] T017 Create TTL cache implementation in src/infrastructure/cache.py (implements CachePort, 15-min TTL)
- [ ] T018 Create error response schemas in src/presentation/schemas.py (ErrorResponse, ErrorDetail per OpenAPI spec)
- [ ] T019 Create FastAPI app initialization in src/main.py (app factory, health endpoint)
- [ ] T020 [P] Create logging middleware in src/presentation/middleware.py (request_id, duration, path logging)
- [ ] T021 [P] Create exception handlers in src/presentation/api.py (map domain exceptions to HTTP responses)
- [ ] T022 Create shared test fixtures in tests/conftest.py (mock weather provider, test client, sample data)

**Checkpoint**: Foundation ready - user story implementation can begin

---

## Phase 3: User Story 1 - View Current Weather by City Name (Priority: P1) 🎯 MVP

**Goal**: Users can search for a city by name and view current weather conditions (temperature, humidity, wind speed, description)

**Independent Test**: Request weather for "London" and verify all required fields returned with correct data types

### Tests for User Story 1

- [ ] T023 [P] [US1] Create unit tests for WeatherData entity validation in tests/unit/test_entities.py
- [ ] T024 [P] [US1] Create unit tests for GetWeatherUseCase in tests/unit/test_use_cases.py
- [ ] T025 [P] [US1] Create unit tests for TTL cache in tests/unit/test_cache.py
- [ ] T026 [P] [US1] Create integration test for GET /api/v1/weather endpoint (valid city) in tests/integration/test_api.py
- [ ] T027 [P] [US1] Create integration test for GET /api/v1/weather endpoint (city not found) in tests/integration/test_api.py
- [ ] T028 [P] [US1] Create integration test for GET /api/v1/weather endpoint (provider unavailable) in tests/integration/test_api.py

### Implementation for User Story 1

- [ ] T029 [US1] Create OpenWeatherMap adapter in src/infrastructure/weather_provider.py (implements WeatherProviderPort)
- [ ] T030 [US1] Implement GetWeatherUseCase in src/application/use_cases.py (cache check, provider call, cache store)
- [ ] T031 [US1] Create WeatherResponse schema in src/presentation/schemas.py (Pydantic model per OpenAPI spec)
- [ ] T032 [US1] Create WeatherRequestParams schema in src/presentation/schemas.py (city required, units optional)
- [ ] T033 [US1] Implement GET /api/v1/weather endpoint in src/presentation/api.py (basic city lookup, metric units default)
- [ ] T034 [US1] Wire up dependency injection in src/main.py (use case, provider, cache instances)
- [ ] T035 [US1] Add request logging for weather endpoint in src/presentation/api.py (city, cache_hit fields)

**Checkpoint**: User Story 1 complete - can retrieve weather by city name with caching

---

## Phase 4: User Story 2 - View Weather with Temperature Units (Priority: P2)

**Goal**: Users can choose between Celsius and Fahrenheit units when viewing weather data

**Independent Test**: Request weather for "London" with units=imperial and verify temperature is in Fahrenheit

### Tests for User Story 2

- [ ] T036 [P] [US2] Create unit test for unit conversion logic in tests/unit/test_entities.py
- [ ] T037 [P] [US2] Create integration test for GET /api/v1/weather with units=metric in tests/integration/test_api.py
- [ ] T038 [P] [US2] Create integration test for GET /api/v1/weather with units=imperial in tests/integration/test_api.py
- [ ] T039 [P] [US2] Create integration test for default units behavior in tests/integration/test_api.py

### Implementation for User Story 2

- [ ] T040 [US2] Update OpenWeatherMap adapter to pass units parameter in src/infrastructure/weather_provider.py
- [ ] T041 [US2] Update cache key generation to include units in src/infrastructure/cache.py
- [ ] T042 [US2] Update GetWeatherUseCase to handle units parameter in src/application/use_cases.py
- [ ] T043 [US2] Update weather endpoint to accept units query parameter in src/presentation/api.py

**Checkpoint**: User Story 2 complete - can request weather in metric or imperial units

---

## Phase 5: User Story 3 - View Extended Weather Details (Priority: P3)

**Goal**: Users can see additional weather details (feels-like temperature, pressure, visibility)

**Independent Test**: Request weather for "London" and verify feels_like, pressure, visibility fields are present

### Tests for User Story 3

- [ ] T044 [P] [US3] Create unit test for extended fields in WeatherData in tests/unit/test_entities.py
- [ ] T045 [P] [US3] Create integration test verifying all extended fields in response in tests/integration/test_api.py

### Implementation for User Story 3

- [ ] T046 [US3] Verify OpenWeatherMap adapter maps all extended fields in src/infrastructure/weather_provider.py
- [ ] T047 [US3] Verify WeatherResponse schema includes all extended fields in src/presentation/schemas.py
- [ ] T048 [US3] Add unit-appropriate formatting for pressure and visibility in src/presentation/schemas.py

**Checkpoint**: User Story 3 complete - full weather data including extended details

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Error handling refinement, observability, documentation

- [ ] T049 [P] Implement rate limit error handling with Retry-After header in src/presentation/api.py
- [ ] T050 [P] Implement stale data error handling (15-min threshold) in src/application/use_cases.py
- [ ] T051 [P] Add metrics collection middleware in src/presentation/middleware.py (request count, latency histogram)
- [ ] T052 [P] Create /health endpoint implementation in src/presentation/api.py
- [ ] T053 [P] Add OpenAPI metadata and tags in src/main.py (title, description, version per contracts/openapi.yaml)
- [ ] T054 [P] Create README.md with setup and usage instructions at repository root
- [ ] T055 [P] Validate quickstart.md instructions work end-to-end
- [ ] T056 Run full test suite and verify 80% coverage threshold
- [ ] T057 Run Ruff linting and fix any issues
- [ ] T058 Run mypy type checking and fix any issues

**Checkpoint**: Feature complete, tested, and documented

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1: Setup ──────────────────────┐
                                     │
Phase 2: Foundational ◀──────────────┘
         │
         ├──▶ Phase 3: US1 (P1) ─┐
         │                       ├──▶ Phase 6: Polish
         ├──▶ Phase 4: US2 (P2) ─┤
         │                       │
         └──▶ Phase 5: US3 (P3) ─┘
```

### User Story Dependencies

| Story | Depends On | Can Parallel With |
|-------|------------|-------------------|
| US1 (P1) | Phase 2 only | US2, US3 (after Phase 2) |
| US2 (P2) | Phase 2 only | US1, US3 (after Phase 2) |
| US3 (P3) | Phase 2 only | US1, US2 (after Phase 2) |

### Within Each User Story

1. Tests MUST be written and FAIL before implementation
2. Adapter/infrastructure before use cases
3. Use cases before presentation
4. Core implementation before integration

### Parallel Opportunities

**Phase 1** (all [P] tasks):
- T003, T004, T005, T006, T007 can run in parallel

**Phase 2** (all [P] tasks):
- T010, T011, T015, T016, T020, T021 can run in parallel

**Phase 3 Tests** (all [P] tasks):
- T023, T024, T025, T026, T027, T028 can run in parallel

**Phase 4 Tests** (all [P] tasks):
- T036, T037, T038, T039 can run in parallel

**Phase 5 Tests** (all [P] tasks):
- T044, T045 can run in parallel

**Phase 6** (all [P] tasks):
- T049, T050, T051, T052, T053, T054, T055 can run in parallel

---

## Parallel Execution Examples

### User Story 1 - Tests (can run together)

```bash
# Launch all US1 tests in parallel:
pytest tests/unit/test_entities.py -k "weather_data" &
pytest tests/unit/test_use_cases.py &
pytest tests/unit/test_cache.py &
pytest tests/integration/test_api.py -k "valid_city or not_found or unavailable" &
```

### User Story 1 - Models (can run together)

```bash
# These files have no dependencies on each other:
# - src/domain/entities.py (WeatherData, Coordinates, UnitSystem)
# - src/domain/exceptions.py (all exception classes)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only) 🎯

1. ✅ Complete Phase 1: Setup (T001-T008)
2. ✅ Complete Phase 2: Foundational (T009-T022)
3. ✅ Complete Phase 3: User Story 1 (T023-T035)
4. **STOP and VALIDATE**: Test weather lookup works for any city
5. **Deploy MVP**: Basic weather API with caching

### Incremental Delivery

| Increment | Includes | Value Delivered |
|-----------|----------|-----------------|
| MVP | US1 | Basic city weather lookup |
| v1.1 | +US2 | Temperature unit preferences |
| v1.2 | +US3 | Extended weather details |
| v1.3 | +Polish | Full observability, docs |

### Recommended Order

```
Setup → Foundational → US1 → [Deploy MVP] → US2 → US3 → Polish → [Final Release]
```

---

## Notes

- All tasks include exact file paths for LLM execution
- [P] tasks can be parallelized (different files, no dependencies)
- [USn] labels map tasks to user stories for traceability
- Constitution requires 80% coverage - tests included
- Constitution requires integration tests for all endpoints - included
- Verify tests fail before implementing (TDD)
- Commit after each task or logical group
