# Implementation Plan: City Name Validation and Friendly Error Responses

**Branch**: `006-79-validate-city-names-and` | **Date**: 2026-08-20 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/006-79-validate-city-names-and/spec.md`

## Summary

Prevent 500 Internal Server Errors when requests contain empty, whitespace-only, numeric, symbolic, or over-long city names by implementing boundary validation in the presentation layer before backend processing. Return structured HTTP 422 responses containing friendly, actionable error messages and an `x-correlation-id` tracing identifier that strictly match organizational API standards (`{"error": {"code": "UNPROCESSABLE_ENTITY", "message": "...", "target": "city", "details": [], "correlationId": "..."}}`). Update active OpenAPI contracts, global exception handlers, middleware, and existing test suites to enforce compliance across all endpoints.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: FastAPI (>=0.109.0), Pydantic (>=2.5.0), structlog (>=24.1.0), httpx (>=0.26.0)  
**Storage**: In-memory TTL cache for weather data (no database changes required)  
**Testing**: pytest, pytest-asyncio, pytest-cov  
**Target Platform**: Linux server / Azure Container Apps / Azure App Service  
**Project Type**: Web Service (FastAPI REST API)  
**Performance Goals**: Boundary validation overhead < 1ms, API endpoint p95 < 200ms  
**Constraints**: Strict adherence to Organization API Design Standards (camelCase JSON fields, standard error payload shape, `x-correlation-id` header matching `error.correlationId`, HTTP status code 422) and backward compatibility for coordinate-based weather queries  
**Scale/Scope**: Presentation layer (`routers/weather.py`, `middleware.py`, `exception_handlers.py`, `schemas.py`), domain validation, active OpenAPI contract (`specs/001-realtime-city-weather/contracts/openapi.yaml`), unit tests, and integration tests (`tests/integration/test_api.py`)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence & Resolution Strategy |
|-----------|--------|--------------------------------|
| **I. API-First Design** | ✅ PASS | Active contract at `specs/001-realtime-city-weather/contracts/openapi.yaml` will be updated to document 422 responses, `UNPROCESSABLE_ENTITY` code, and `ErrorDetail` schema fields (`target`, `details`, `correlationId`). |
| **II. Clean Architecture** | ✅ PASS | Validation executed at presentation boundary (FastAPI dependency/router) before domain use case execution (`GetWeatherUseCase`). Domain entities remain decoupled from HTTP constructs. |
| **III. Org Standards Compliance** | ✅ PASS | All validation errors return standard error shape with `code: "UNPROCESSABLE_ENTITY"`, `target`, `details`, and `correlationId` synced with `x-correlation-id` HTTP header. |
| **IV. Technology Stack** | ✅ PASS | Built with Python 3.11+, FastAPI, Pydantic, pytest - matches repository tech stack. |
| **V. Testing Requirements** | ✅ PASS | 100% test coverage target for city validation rules and correlation propagation; existing integration tests updated to assert standard error format. |

**Gate Status**: ✅ All gates pass - proceed to Phase 0 and detailed design.

## Project Structure

### Documentation (this feature)

```text
specs/006-79-validate-city-names-and/
├── plan.md              # This file (implementation plan)
├── research.md          # Research on validation rules & FastAPI error handling
├── data-model.md        # Data models & error schema specifications
├── quickstart.md        # Manual verification & test execution guide
├── contracts/           # Contract diff notes and standard schemas
└── tasks.md             # Tasks definition for execution (/speckit.tasks)
```

### Source Code (repository root)

```text
src/
├── domain/
│   ├── entities.py              # WeatherRequest entity & domain validations
│   ├── exceptions.py            # InvalidCityNameError & domain exceptions
│   └── value_objects.py         # Coordinates, UnitSystem
├── application/
│   ├── use_cases/
│   │   └── get_weather.py       # GetWeatherUseCase
│   └── interfaces.py
├── presentation/
│   ├── dependencies.py          # City name boundary validator dependency
│   ├── exception_handlers.py    # RequestValidationError, HTTPException & custom exception handlers
│   ├── middleware.py            # RequestLoggingMiddleware with correlation ID extraction/generation
│   ├── routers/
│   │   └── weather.py           # GET /api/v1/weather endpoint & parameter handling
│   └── schemas.py               # ErrorDetail, ErrorResponse, WeatherResponse schemas
└── main.py                      # FastAPI application setup & exception handler registration

specs/
└── 001-realtime-city-weather/
    └── contracts/
        └── openapi.yaml         # Active system OpenAPI spec (updated with 422 & extended ErrorDetail)

tests/
├── unit/
│   ├── test_city_validation.py  # Unit tests for city name validation rules
│   ├── test_entities.py         # Unit tests for WeatherRequest
│   └── test_exceptions.py       # Unit tests for exception handlers & schemas
└── integration/
    └── test_api.py              # Integration tests updated for 422 responses and new error shape
```

**Structure Decision**: Single Python FastAPI project following 4-layer Clean Architecture. Feature documentation resides under `specs/006-79-validate-city-names-and/`. The active system contract at `specs/001-realtime-city-weather/contracts/openapi.yaml` is maintained as the single source of truth for the OpenAPI spec.

## Detailed Architecture & Solution Strategy

### 1. Parameter Validation Rules & Precedence Order
City boundary validation executes in the presentation layer according to the following strict pipeline:

1. **Incomplete Coordinate Check**: If `lat` or `lon` is provided without the other, immediately return HTTP 422 with message `"Both lat and lon must be provided together, or neither"` and `target: "coordinates"`.
2. **Missing Input Check**: If neither `city` nor complete `(lat, lon)` coordinates are provided, return HTTP 422 with message `"Either city or coordinates (lat and lon) must be provided"` and `target: "city"`.
3. **Boundary City Validation**: If `city` query parameter is present (non-`None`):
   - **Whitespace Trimming**: Strip leading and trailing whitespace from `city`.
   - **Empty Check**: If trimmed `city` is empty (`""`), return HTTP 422 with message `"City name cannot be empty"` and `target: "city"`.
   - **Max Length Check**: If trimmed `city` length > 100 characters, return HTTP 422 with message `"City name must not exceed 100 characters"` and `target: "city"`.
   - **Alphabetic Letter Presence Check**: If trimmed `city` contains no alphabetic characters (e.g., `"12345"`, `"123-456"`, `"!!!"`), return HTTP 422 with message `"City name must contain letters and cannot consist only of numbers or special characters"` and `target: "city"`.
4. **Execution Precedence**:
   - If `city` parameter is present and fails validation, reject immediately with HTTP 422 regardless of whether `lat`/`lon` coordinates were also supplied.
   - If `city` is valid AND valid `(lat, lon)` coordinates are provided, coordinates take precedence for weather data retrieval in `GetWeatherUseCase` (maintaining backward compatibility).
   - If `city` parameter is absent (`None`), but valid coordinates are provided, city validation is skipped and coordinates are used directly.

### 2. Request Correlation ID Propagation
To ensure the `error.correlationId` in response payloads matches the HTTP `x-correlation-id` header:
1. `RequestLoggingMiddleware` (`src/presentation/middleware.py`) checks incoming request headers for `x-correlation-id`. If missing or empty, it generates a new ID in `req-<uuid4>` format.
2. The middleware stores this identifier in `request.state.correlation_id` and attaches `x-correlation-id: <correlation-id>` to the HTTP response headers.
3. Global exception handlers (`src/presentation/exception_handlers.py`) retrieve `request.state.correlation_id` (with a fallback to header inspection/generation if `request.state` is not set) and populate `"correlationId"` in the returned JSON payload.

### 3. Global Standardized Error Handling
To eliminate FastAPI's default `{"detail": [...]}` error format:
1. `RequestValidationError` Handler: Intercepts Pydantic/FastAPI request validation errors, extracts the primary parameter target (e.g. `"city"`), maps the first error message into a human-friendly string, and outputs the standardized `ErrorResponse` payload:
   ```json
   {
     "error": {
       "code": "UNPROCESSABLE_ENTITY",
       "message": "City name cannot be empty",
       "target": "city",
       "details": [],
       "correlationId": "req-abc-123"
     }
   }
   ```
2. `HTTPException` Handler: Formats raised HTTP exceptions (e.g., status 422 or 404) into the standard `ErrorResponse` schema with appropriate `code` (`UNPROCESSABLE_ENTITY` for 422) and `correlationId`.
3. `InvalidCityNameError` Domain Exception Handler: Mapped to HTTP 422 with `UNPROCESSABLE_ENTITY` code and `target: "city"`.

### 4. Schema & OpenAPI Contract Synchronization
1. `src/presentation/schemas.py`: Update `ErrorDetail` and `ErrorResponse` models:
   - `code`: `str` (includes `"UNPROCESSABLE_ENTITY"`).
   - `message`: `str`.
   - `target`: `str | None` (e.g. `"city"`).
   - `details`: `list[dict[str, Any]]` (default `[]`).
   - `correlationId`: `str`.
2. `specs/001-realtime-city-weather/contracts/openapi.yaml`:
   - Add explicit `422` response specification to `/api/v1/weather`.
   - Update `ErrorDetail` schema definition to include `target`, `details`, `correlationId`, and `UNPROCESSABLE_ENTITY` enum value.

### 5. Integration Test Updates
1. Existing assertions in `tests/integration/test_api.py` checking legacy `data["detail"]` (e.g., lines 250, 258, 316) will be updated to assert `data["error"]["message"]` and `data["error"]["code"] == "UNPROCESSABLE_ENTITY"`.
2. New test cases will be added to verify empty city (`?city=`), numeric city (`?city=12345`), over-long city, correlation ID header propagation, and coordinate precedence with valid city names.

## Complexity Tracking

> No constitution violations requiring justification. All changes align with Clean Architecture and Organization API Design Standards.
