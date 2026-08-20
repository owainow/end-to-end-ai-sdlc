# Feature Specification: City Name Validation and Friendly Error Responses

**Feature Branch**: `006-79-validate-city-names-and`

**Created**: 2026-08-20

**Status**: Draft

**Input**: User description: "[#79] Validate city names and return friendly errors. Requests with empty, numeric, or over-long city names currently bubble up as 500s. Validate input at the API boundary and return a structured 422 with a helpful message, matching our error-shape conventions. Include unit tests for the validation rules."

## User Scenarios & Testing

### User Story 1 - Boundary City Name Validation & Friendly Errors (Priority: P1)

As an API client or application developer, I want city name query parameters validated at the API boundary before backend processing, so that invalid inputs (empty strings, numeric/symbolic strings, or over-long names) return helpful HTTP 422 error messages rather than HTTP 500 internal server errors.

**Why this priority**: Preventing 500 internal server errors for invalid client input is essential for API robustness, security, and developer experience. Boundary validation ensures fast feedback and consistent error messaging.

**Independent Test**: Can be fully tested by sending invalid city queries (`GET /api/v1/weather?city=12345`, `GET /api/v1/weather?city=`, `GET /api/v1/weather?city=a...[>100 chars]`) and verifying that HTTP 422 responses are returned with clear, descriptive error messages.

**Acceptance Scenarios**:

1. **Given** an API request with a valid city name (e.g., "London", "São Paulo", "Saint-Étienne"), **When** the endpoint `GET /api/v1/weather` is called, **Then** the system accepts the request and returns weather data with HTTP 200 OK.
2. **Given** an API request with an empty city name or whitespace-only city name (`?city=` or `?city=%20%20`), **When** the request is received, **Then** the system returns HTTP 422 Unprocessable Entity with error message "City name cannot be empty".
3. **Given** an API request with a purely numeric string, numeric-punctuation, or non-alphabetic symbol string (`?city=12345`, `?city=123-456`, `?city=!!!`), **When** the request is received, **Then** the system returns HTTP 422 Unprocessable Entity with error message "City name must contain letters and cannot consist only of numbers or special characters".
4. **Given** an API request with a city name exceeding 100 characters after whitespace trimming, **When** the request is received, **Then** the system returns HTTP 422 Unprocessable Entity with error message "City name must not exceed 100 characters".
5. **Given** an API request with valid city name surrounded by leading or trailing whitespace (`?city=%20London%20`), **When** the request is processed, **Then** the system trims the whitespace prior to validation and processes "London" successfully.

---

### User Story 2 - Standardized Error Payload & Request Correlation (Priority: P2)

As an API client developer or system administrator, I want validation error responses to conform strictly to organizational API standards and include a correlation ID, so that client error handling is predictable and issues can be correlated in server logs.

**Why this priority**: API standards compliance ensures consistent client error handling across all organization microservices, and correlation IDs enable end-to-end request tracing.

**Independent Test**: Can be fully tested by sending any invalid request with or without an `x-correlation-id` HTTP header, and inspecting the JSON response body structure and headers.

**Acceptance Scenarios**:

1. **Given** an invalid city request containing an `x-correlation-id: req-abc-123` HTTP header, **When** validation fails, **Then** the response body contains `"correlationId": "req-abc-123"` inside the structured `error` object.
2. **Given** an invalid city request missing the `x-correlation-id` HTTP header, **When** validation fails, **Then** the system automatically generates a unique correlation ID (e.g. `req-<uuid>`), sets `x-correlation-id` header in the response, and populates `"correlationId"` in the error JSON payload.
3. **Given** any HTTP 422 validation failure, **When** the error payload is returned, **Then** it matches the standard error structure: `{"error": {"code": "UNPROCESSABLE_ENTITY", "message": "<descriptive message>", "target": "city", "details": [], "correlationId": "<correlation-id>"}}`.

---

### User Story 3 - Coordinate Query Compatibility & Parameter Precedence (Priority: P3)

As an API client querying weather by geographical coordinates (`lat`/`lon`), I want to request weather data without supplying a `city` parameter, while ensuring that if a `city` parameter is explicitly provided alongside coordinates, it is still validated at the boundary.

**Why this priority**: Coordinate-based lookups are a core API capability that must not be broken by city validation requirements. Clear parameter precedence rules prevent ambiguous API behaviors.

**Independent Test**: Can be fully tested by submitting valid coordinate queries (`GET /api/v1/weather?lat=51.5074&lon=-0.1278`), queries missing both city and coordinates, and queries supplying valid coordinates with an invalid city name.

**Acceptance Scenarios**:

1. **Given** an API request containing valid latitude and longitude coordinates and no city parameter (`GET /api/v1/weather?lat=51.5074&lon=-0.1278`), **When** the request is processed, **Then** boundary validation passes without requiring `city` and weather data for the coordinates is returned with HTTP 200.
2. **Given** an API request missing both `city` and coordinate parameters (`GET /api/v1/weather`), **When** the request is received, **Then** boundary validation returns HTTP 422 with message "Either city or coordinates (lat and lon) must be provided".
3. **Given** an API request providing valid `lat` and `lon` coordinates alongside an invalid `city` parameter (`GET /api/v1/weather?lat=51.5&lon=-0.12&city=12345`), **When** the request is received, **Then** boundary validation executes on `city` first and returns HTTP 422 Unprocessable Entity rejecting the invalid city name.

---

### Edge Cases

- **Missing `city` parameter with valid coordinates**: When `lat` and `lon` are present and valid, omitting `city` is valid and does not trigger city missing validation.
- **Missing both `city` and coordinates**: Triggers HTTP 422 with message "Either city or coordinates (lat and lon) must be provided".
- **Incomplete coordinates without `city`**: Supplying `lat` without `lon` or `lon` without `lat` triggers HTTP 422 with message "Both lat and lon must be provided together, or neither".
- **City name length exceeding limit including whitespace**: A query parameter like `?city=%20%20...[100 chars]...%20%20` is trimmed first. If trimmed length <= 100, it is valid; if trimmed length > 100, it returns HTTP 422.
- **Non-ASCII / Accented city names**: Names containing non-ASCII alphabetic characters (e.g., "München", "Tokyo", "Malmö", "København") are valid city names and pass validation.
- **Numbers mixed with alphabetic characters**: Names containing numbers along with letters (e.g. "7th District", "Sector 7") pass validation if they contain at least one alphabetic letter. Strings containing only digits, hyphens, spaces, and punctuation (e.g., "123-456", "123 456", "!!!") fail validation.
- **Missing request correlation ID**: System generates a unique `req-<uuid>` correlation ID and propagates it to both response headers and the error payload.

## Requirements

### Functional Requirements

- **FR-001**: System MUST validate the `city` query parameter at the API boundary before invoking application use cases or downstream external weather services.
- **FR-002**: System MUST allow the `city` parameter to be omitted when valid `lat` and `lon` coordinate parameters are provided. If neither a valid `city` nor complete `lat`/`lon` coordinates are provided, system MUST return HTTP 422 Unprocessable Entity with message "Either city or coordinates (lat and lon) must be provided".
- **FR-003**: System MUST trim leading and trailing whitespace from the `city` parameter value before executing length or character format validation rules.
- **FR-004**: System MUST reject `city` parameter values that are empty or consist solely of whitespace characters after trimming with HTTP 422 Unprocessable Entity and error message "City name cannot be empty".
- **FR-005**: System MUST reject `city` parameter values whose length exceeds 100 characters after trimming with HTTP 422 Unprocessable Entity and error message "City name must not exceed 100 characters".
- **FR-006**: System MUST reject `city` parameter values that do not contain at least one alphabetic letter (including purely numeric strings like "12345", digit-punctuation strings like "123-456", or symbol-only strings like "!!!") with HTTP 422 Unprocessable Entity and error message "City name must contain letters and cannot consist only of numbers or special characters".
- **FR-007**: System MUST accept valid city names containing letters (including Unicode/accented characters), spaces, hyphens, apostrophes, and periods, provided the string contains at least one letter.
- **FR-008**: System MUST execute city parameter boundary validation whenever `city` is present in the request query string, even if valid `lat` and `lon` coordinate parameters are also provided in the same request.
- **FR-009**: System MUST extract the request correlation ID from the `x-correlation-id` HTTP header if present on the request, or generate a unique correlation ID in format `req-<uuid>` if the header is missing, and attach it to the request context.
- **FR-010**: System MUST return all boundary validation error responses using HTTP status code 422 Unprocessable Entity and structured JSON payload matching organizational standards:
  ```json
  {
    "error": {
      "code": "UNPROCESSABLE_ENTITY",
      "message": "<descriptive message>",
      "target": "city",
      "details": [],
      "correlationId": "<correlation-id>"
    }
  }
  ```
- **FR-011**: System MUST update Pydantic response models (`ErrorResponse`, `ErrorDetail`) and OpenAPI specifications (`/docs/openapi.yaml` and contract specs) to support HTTP 422 validation responses, including `target`, `details` array, `correlationId`, and `UNPROCESSABLE_ENTITY` error code.
- **FR-012**: System MUST include comprehensive unit tests covering all city validation rules, whitespace trimming, coordinate interaction rules, correlation ID handling, and error response payload formatting.

### Key Entities

- **`ValidationErrorResponse`**: Standardized HTTP 422 response entity containing top-level `error` object.
- **`ErrorDetail`**: Detailed error payload entity containing:
  - `code` (string): Error classification code (`UNPROCESSABLE_ENTITY`).
  - `message` (string): Human-readable error message explaining the specific validation failure.
  - `target` (string, optional): Query parameter or field that failed validation (e.g. `"city"`).
  - `details` (list): Detailed sub-error list (default `[]`).
  - `correlationId` (string): Unique request tracing identifier (`req-<uuid>` or from request header).
- **`CityValidationRule`**: Set of boundary validation logic rules applied sequentially: whitespace trimming -> non-empty check -> max length check -> alphabetic letter presence check.

## Success Criteria

### Measurable Outcomes

- **SC-001**: 100% of invalid city requests (empty strings, whitespace-only, purely numeric, symbol-only, or >100 characters) return HTTP 422 Unprocessable Entity with a structured error payload instead of HTTP 500.
- **SC-002**: 100% of coordinate-only weather queries (`lat`/`lon` without `city`) complete successfully with HTTP 200 without requiring `city`.
- **SC-003**: 100% of error responses returned by the weather API include a non-null `correlationId` and strictly match the updated OpenAPI schema definition.
- **SC-004**: City validation rules and request context correlation ID logic achieve 100% unit test line coverage.

## Assumptions

- Boundary validation executes in the presentation layer (FastAPI router / custom exception handler / dependency) before passing requests to application use cases.
- Request correlation ID extraction and fallback generation (`req-<uuid>`) can be handled via presentation middleware or request dependency to ensure correlation ID availability across all handlers and error responses.
- Whitespace trimming occurs at the boundary before length or character checks, preventing framework default parameter length validation from returning unformatted error payloads.
- OpenAPI contract files (`/docs/openapi.yaml` and `specs/001-realtime-city-weather/contracts/openapi.yaml`) will be updated to reflect HTTP 422 responses and the extended `ErrorDetail` fields (`target`, `details`, `correlationId`, `UNPROCESSABLE_ENTITY`).
