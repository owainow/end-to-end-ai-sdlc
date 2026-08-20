# Tasks: City Name Validation and Friendly Error Responses

**Input**: Design documents from `specs/006-79-validate-city-names-and/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths shown below assume single project based on `plan.md` structure

---

## Phase 1: Setup & Contract Definitions

**Purpose**: Update active OpenAPI specification contract to support HTTP 422 responses and standard error schema fields before implementation.

- [ ] T001 [P] Update active OpenAPI spec in `specs/001-realtime-city-weather/contracts/openapi.yaml` to include 422 Unprocessable Entity response documentation, `UNPROCESSABLE_ENTITY` error code enum, and updated `ErrorDetail` schema fields (`target`, `details`, `correlationId`, `retry_after`).

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure, schema updates, exception handlers, and legacy test refactoring that MUST be complete before ANY user story can be implemented.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [ ] T002 [P] Update `ErrorDetail` and `ErrorResponse` Pydantic models in `src/presentation/schemas.py` to include `code`, `message`, `target: str | None = None`, `details: list[dict[str, Any]] = Field(default_factory=list)`, `correlationId: str`, while preserving `retry_after: int | None = None` for 429/502 error handlers.
- [ ] T003 [P] Update `RequestLoggingMiddleware` in `src/presentation/middleware.py` to extract `x-correlation-id` from request headers or generate `req-<uuid4>`, store in `request.state.correlation_id`, and ensure `x-correlation-id` HTTP header is attached to all outgoing responses.
- [ ] T004 Create city boundary validation functions and `validate_weather_query_params` dependency in `src/presentation/dependencies.py` accepting `city`, `lat`, and `lon`:
  - Enforce coordinate completeness: if `lat` or `lon` provided without the other, fail with 422, message `"Both lat and lon must be provided together, or neither"`, `target: "coordinates"`.
  - Enforce parameter presence: if both `city` and `(lat, lon)` are missing, fail with 422, message `"Either city or coordinates (lat and lon) must be provided"`, `target: "city"`.
  - Enforce city boundary rules if `city` is present (non-`None`): trim whitespace; if empty -> 422 `"City name cannot be empty"`; if >100 chars -> 422 `"City name must not exceed 100 characters"`; if no alphabetic characters -> 422 `"City name must contain letters and cannot consist only of numbers or special characters"`. If `city` is present, city validation runs FIRST regardless of coordinates.
- [ ] T005 Update `register_exception_handlers` in `src/presentation/exception_handlers.py` to handle `RequestValidationError`, `HTTPException`, `InvalidCityNameError`, `CityNotFoundError`, `RateLimitExceededError`, `WeatherProviderError`, and generic `Exception`:
  - Safely retrieve correlation ID using `getattr(request.state, "correlation_id", None)` with fallback to header inspection or `req-<uuid4>` generation.
  - Set `x-correlation-id` response header on all outgoing `JSONResponse` error objects.
  - Map `RequestValidationError` multi-field errors into scalar `target` (first field name) and `details` array (`[{"target": field, "message": msg}]`).
  - Output `"code": "UNPROCESSABLE_ENTITY"` for all HTTP 422 validation errors (including `InvalidCityNameError`).
- [ ] T006 Refactor legacy error assertions in `tests/integration/test_api.py` (e.g., replacing checks for legacy `data["detail"]` with assertions on `data["error"]["message"]` and `data["error"]["code"]`) so that the integration test suite passes immediately when new exception handlers are registered.

**Checkpoint**: Foundation ready - schemas, exception handlers, middleware, dependencies, and existing integration tests updated.

---

## Phase 3: User Story 1 - Boundary City Name Validation & Friendly Errors (Priority: P1) 🎯 MVP

**Goal**: Validate city query parameters at the API boundary before backend processing, returning HTTP 422 responses with helpful error messages for empty, whitespace-only, numeric, symbolic, or over-long city names.

**Independent Test**: Send requests with invalid city names (`GET /api/v1/weather?city=12345`, `?city=`, `?city=%20%20`, over 100 chars) and verify HTTP 422 response with exact descriptive error message and `target: "city"`.

### Tests for User Story 1 ⚠️

- [ ] T007 [P] [US1] Create unit test suite in `tests/unit/test_city_validation.py` testing boundary validation rules: valid city names ("London"), accented/Unicode names ("München", "São Paulo"), whitespace trimming (" London "), empty strings (""), whitespace-only ("   "), over 100 chars, purely numeric ("12345"), digit-punctuation ("123-456"), symbol-only ("!!!"), and valid mixed letters/numbers ("7th District").

### Implementation for User Story 1

- [ ] T008 [US1] Update `InvalidCityNameError` in `src/domain/exceptions.py` to set default `code="UNPROCESSABLE_ENTITY"` to align domain exceptions with REST design standards.
- [ ] T009 [US1] Update `WeatherRequest` entity validation in `src/domain/entities.py` to match boundary rules (whitespace trimming, non-empty, max 100 chars, alphabetic letter presence requirement).
- [ ] T010 [US1] Inject boundary validator dependency into `GET /api/v1/weather` router endpoint in `src/presentation/routers/weather.py`, enforcing boundary validation on city queries before invoking `GetWeatherUseCase`.

**Checkpoint**: User Story 1 boundary validation is fully functional and unit tested independently.

---

## Phase 4: User Story 2 - Standardized Error Payload & Request Correlation (Priority: P2)

**Goal**: Ensure all validation error responses strictly conform to organizational API standards (`{"error": {"code": "UNPROCESSABLE_ENTITY", "message": "...", "target": "city", "details": [], "correlationId": "req-..."}}`) and propagate `x-correlation-id` HTTP headers bidirectionally.

**Independent Test**: Send invalid city requests with and without `x-correlation-id` header and verify the response payload `"correlationId"` matches the `x-correlation-id` HTTP response header.

### Tests for User Story 2 ⚠️

- [ ] T011 [P] [US2] Create unit test suite in `tests/unit/test_exceptions.py` covering exception handlers, schema serialization (`ErrorDetail`, `ErrorResponse`), multi-field error formatting, and correlation ID extraction/fallback generation.

### Implementation for User Story 2

- [ ] T012 [US2] Verify and refine correlation ID middleware propagation in `src/presentation/middleware.py` and exception handlers in `src/presentation/exception_handlers.py` to guarantee non-null `correlationId` and `x-correlation-id` response header on all error responses.
- [ ] T013 [US2] Add integration tests in `tests/integration/test_api.py` asserting full `ErrorResponse` JSON structure (`code`, `message`, `target`, `details`, `correlationId`) and custom `x-correlation-id` header preservation.

**Checkpoint**: User Stories 1 and 2 work independently and together with standardized error payloads and request tracing.

---

## Phase 5: User Story 3 - Coordinate Query Compatibility & Parameter Precedence (Priority: P3)

**Goal**: Support coordinate-only weather queries (`lat`/`lon` without `city`), missing parameter validation (`422` when neither provided), incomplete coordinate validation (`422` when only `lat` or `lon` provided), and enforce that if `city` is present alongside coordinates, `city` validation runs first before returning coordinates-based weather data.

**Independent Test**: Send valid coordinate queries (`?lat=51.5&lon=-0.12`), missing parameter queries (`/api/v1/weather`), incomplete coordinate queries (`?lat=51.5`), and dual parameter queries with invalid city (`?lat=51.5&lon=-0.12&city=12345`), verifying expected 200 and 422 behaviors.

### Tests for User Story 3 ⚠️

- [ ] T014 [P] [US3] Add unit tests in `tests/unit/test_city_validation.py` covering coordinate parameter interactions: valid coordinates without city, missing both city and coordinates, incomplete coordinates (`lat` only / `lon` only), and invalid city supplied alongside valid coordinates.

### Implementation for User Story 3

- [ ] T015 [US3] Update request processing in `src/presentation/routers/weather.py` to enforce the complete validation pipeline:
  1. Incomplete coordinate check (`lat` without `lon` or `lon` without `lat` -> 422 `"Both lat and lon must be provided together, or neither"`).
  2. Missing parameter check (`city` and `(lat, lon)` both missing -> 422 `"Either city or coordinates (lat and lon) must be provided"`).
  3. Validate `city` if present (if invalid -> 422).
  4. If `city` is valid (or omitted) and `(lat, lon)` present -> execute `GetWeatherUseCase` using coordinates.
- [ ] T016 [US3] Add integration tests in `tests/integration/test_api.py` verifying coordinate-only weather lookups (200 OK), missing parameters (422), incomplete coordinates (422), and dual parameter queries with invalid city (422).

**Checkpoint**: All user stories (US1, US2, US3) are fully implemented, tested, and integrated.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation verification, quickstart updates, and full test suite execution.

- [ ] T017 [P] Update execution and manual verification steps in `specs/006-79-validate-city-names-and/quickstart.md`.
- [ ] T018 Run complete test suite (`pytest --cov=src`) to confirm 100% test pass rate and verify line coverage for city validation rules and exception handling.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup & Contract Definitions (Phase 1)**: No dependencies - can start immediately.
- **Foundational (Phase 2)**: Depends on Phase 1 - BLOCKS all user story work. Refactoring legacy assertions in `tests/integration/test_api.py` (T006) MUST happen in Phase 2 alongside exception handler registration (T005) to ensure tests never fail due to error shape mismatches.
- **User Stories (Phase 3+)**: All depend on Phase 2 completion.
  - User Story 1 (P1) delivers core boundary validation (MVP).
  - User Story 2 (P2) enforces standardized error payload shape and correlation ID tracing.
  - User Story 3 (P3) enforces coordinate interaction rules and parameter precedence.
- **Polish (Phase 6)**: Depends on completion of all user stories.

### Execution Pipeline & Precedence Rules

1. **Dual Parameter Rule**: If `city` is present in the request (`non-None`), `city` boundary validation runs FIRST. If `city` fails validation (empty, >100 chars, numeric/symbolic), the request is rejected with 422 Unprocessable Entity regardless of whether valid coordinates were provided.
2. **Coordinate Precedence Rule**: If `city` is valid (or omitted) AND valid `(lat, lon)` coordinates are provided, coordinates take precedence for weather data retrieval.
3. **Correlation ID Safety Rule**: All exception handlers retrieve correlation ID safely via `getattr(request.state, "correlation_id", None)` and attach `x-correlation-id` to response headers.

### Parallel Opportunities

- **Phase 1**: T001 can run in parallel.
- **Phase 2**: T002, T003 can run in parallel. T004, T005, T006 build on models and middleware.
- **Phase 3 (US1)**: T007 (unit tests) can run in parallel with domain exception/entity updates (T008, T009).
- **Phase 4 (US2)**: T011 (unit tests) can run in parallel with middleware/handler updates (T012).
- **Phase 5 (US3)**: T014 (unit tests) can run in parallel with router updates (T015).
- **Phase 6**: T017 can run in parallel.
