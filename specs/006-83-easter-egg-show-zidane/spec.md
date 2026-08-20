# Feature Specification: Easter Egg - Zidane GIF for France Weather Queries

**Feature Branch**: `006-83-easter-egg-show-zidane`

**Created**: 2026-08-20

**Status**: Draft

**Input**: User description: "[#83] Easter egg: show Zidane GIF for weather queries in France"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Weather API Easter Egg Flag for French Queries (Priority: P1)

As an API consumer or client application querying the weather service, when I request weather data for any location that resolves to France (country code `FR`), I receive an `easter_egg` attribute set to `"zidane"` in the response payload. For queries resolving to any other country or when the country code is absent, the `easter_egg` attribute is `null`.

**Why this priority**: The backend detection and Clean Architecture propagation of the easter egg decision is the foundational data contract that unlocks both API consumers and the frontend celebration UI.

**Independent Test**: Can be tested independently via API integration tests and application unit tests by querying cities in France (e.g., Paris, Lyon, Marseille, Nice) and verifying `easter_egg == "zidane"`, while querying non-French cities (e.g., London, Tokyo, New York) verifies `easter_egg == null`.

**Acceptance Scenarios**:

1. **Given** a weather query resolving to a location with country code `"FR"` (case-insensitive, e.g., `"FR"`, `"fr"`), **When** the weather data is processed through the use case, **Then** the API response contains `"easter_egg": "zidane"`.
2. **Given** a weather query resolving to a location with a non-FR country code (e.g., `"GB"`, `"US"`, `"DE"`, `"JP"`), **When** the weather data is processed through the use case, **Then** the API response contains `"easter_egg": null`.
3. **Given** a weather query where the provider returns an empty or missing country code (e.g., `""`), **When** the weather data is processed through the use case, **Then** the API response contains `"easter_egg": null`.
4. **Given** a weather query by geographic coordinates that resolve to France (country code `"FR"`), **When** the use case executes, **Then** the API response contains `"easter_egg": "zidane"`.

---

### User Story 2 - UI Celebration with Zidane GIF (Priority: P2)

As a user searching for weather in France on the web application, I want to see a celebratory Zidane GIF displayed above the weather details card so that my search experience is delightfully animated.

**Why this priority**: Delivers the visual user-facing celebration directly tied to the easter egg requirement.

**Independent Test**: Can be tested independently in the browser or via automated DOM tests by rendering a weather result with `"easter_egg": "zidane"` and asserting that the image element is visible, positioned above the weather metrics, points to `https://media.tenor.com/B8gpHhxJOksAAAAM/zidane-shocked.gif`, and has alt text `"Zizou approves"`.

**Acceptance Scenarios**:

1. **Given** a search result with `"easter_egg": "zidane"`, **When** the weather card is rendered in the UI, **Then** the easter egg container is displayed above the weather details, containing an `<img>` tag with `src="https://media.tenor.com/B8gpHhxJOksAAAAM/zidane-shocked.gif"` and `alt="Zizou approves"`.
2. **Given** an active weather display showing the Zidane GIF for a French city, **When** the user performs a new search for a non-French location (where `easter_egg` is `null`), **Then** the easter egg container (including any GIF or fallback text) is completely hidden.
3. **Given** an active weather display showing the Zidane GIF, **When** the user switches temperature units (metric/imperial), **Then** the weather card re-renders while preserving the easter egg GIF display without visual glitches.

---

### User Story 3 - Resilient Frontend Fallback and State Re-arming (Priority: P3)

As a user searching for French weather in an environment where external GIF media is blocked or fails to load (e.g., network timeout, content blocker, offline cache degradation), I want to see the fallback text "🇫🇷 Zizou approves" instead of a broken image icon, and I want subsequent searches to re-arm and retry loading the media.

**Why this priority**: Ensures graceful degradation, accessibility, and robust state lifecycle across successive searches without broken image glyphs.

**Independent Test**: Can be tested independently by simulating an `error` event on the easter egg `<img>` element and verifying that the image is hidden, the text `"🇫🇷 Zizou approves"` is displayed immediately, and executing a subsequent search for a French location re-arms the image loader state.

**Acceptance Scenarios**:

1. **Given** a weather response with `"easter_egg": "zidane"`, **When** the GIF resource triggers an `error` event (failed fetch or blocked host), **Then** the image element is hidden and the text element with `"🇫🇷 Zizou approves"` is displayed in its place.
2. **Given** a previous search where the image failed and displayed fallback text, **When** the user executes a new search that resolves to a French location, **Then** the UI resets the image error state and re-arms the image source to attempt loading the GIF again.
3. **Given** a search error state (e.g., 404 City Not Found or 500 Provider Error), **When** the error banner is displayed, **Then** the easter egg container (both GIF and fallback text) is hidden.

---

### Edge Cases

- **Case Sensitivity in Country Code**: If the provider returns lowercase `"fr"` or mixed case `"Fr"`, the system must normalize the string and trigger the easter egg.
- **Whitespace in Country Code**: If the provider returns `" FR "` with leading/trailing spaces, the system must trim whitespace before evaluation.
- **Provider Payload Missing `sys.country`**: If OpenWeatherMap returns no `sys` object or an empty `country` field, the system must treat the country as empty and return `easter_egg: null` without raising an unhandled exception.
- **Rapid Consecutive Searches**: Rapid switching between French (e.g., Paris), non-French (e.g., Berlin), and French (e.g., Marseille) searches must cleanly toggle and re-arm the easter egg UI without race conditions or lingering DOM artifacts.
- **Ad-blockers and Content Security / CORS**: If third-party image hosts are blocked by browser extensions, the synchronous `onerror` DOM handler must activate the fallback text immediately without throwing unhandled JavaScript exceptions.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The domain entity `WeatherData` MUST retain the country code as resolved from the weather provider.
- **FR-002**: Country detection MUST originate solely from the provider's resolved ISO country code (`sys.country`), NOT from a static or hardcoded list of city names.
- **FR-003**: The application layer use case (`GetWeatherUseCase`) MUST encapsulate and expose the easter egg decision logic (evaluating whether the normalized country code is `"FR"`) rather than leaking domain evaluation rules into presentation routers.
- **FR-004**: The presentation layer response schema (`WeatherResponse`) and OpenAPI specification contract (`contracts/openapi.yaml`) MUST define an optional `easter_egg: Optional[str]` field (nullable string), which is `"zidane"` when triggered and `null` otherwise.
- **FR-005**: The presentation router MUST map the use case result (including the easter egg decision) to `WeatherResponse` without directly implementing domain rule comparisons in the HTTP route handler.
- **FR-006**: When `easter_egg` is `"zidane"`, the frontend client MUST display the GIF located at `https://media.tenor.com/B8gpHhxJOksAAAAM/zidane-shocked.gif` above the weather information card with the `alt` attribute set to `"Zizou approves"`.
- **FR-007**: When `easter_egg` is `null` or absent, the frontend client MUST ensure the easter egg display container is hidden.
- **FR-008**: The frontend client MUST bind an error event handler (`onerror`) to the easter egg image element that synchronously hides the broken image and reveals the fallback text `"🇫🇷 Zizou approves"`.
- **FR-009**: The frontend client MUST implement a state reset / re-arming mechanism when rendering weather cards, ensuring that previous image error states do not prevent subsequent French weather queries from attempting to load the GIF.
- **FR-010**: All API contracts, Pydantic schemas, and OpenAPI documentation in `specs/001-realtime-city-weather/contracts/openapi.yaml` MUST be synchronized with the new `easter_egg` field.

### Key Entities

- **`WeatherData` (Domain Entity)**: Represents the core weather metrics for a requested location. Contains `city_name: str`, `country: str` (ISO 3166 code), `coordinates: Coordinates`, temperature, pressure, humidity, wind, description, and timestamp.
- **`WeatherResponse` (Presentation Schema / Contract)**: Serialized API payload returned by `GET /api/v1/weather`. Contains all formatted weather metrics plus `easter_egg: str | None` (`"zidane"` or `null`).
- **`EasterEggState` (Frontend Client View Model)**: Represents the client-side state of the easter egg UI, managing visibility (`visible`/`hidden`), media loading status (`loading`/`loaded`/`error`), active image source URL, and fallback text state.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of weather API requests resolving to country code `"FR"` (case-insensitive) return `"easter_egg": "zidane"` in the JSON payload.
- **SC-002**: 100% of weather API requests resolving to any country other than `"FR"`, or with empty country code, return `"easter_egg": null`.
- **SC-003**: 100% test coverage for the easter egg rule evaluation across domain and application use case test suites (including `"FR"`, `"fr"`, non-FR codes like `"GB"`, empty string, and whitespace).
- **SC-004**: If the external GIF URL triggers an `error` event, the frontend immediately and synchronously transitions from the image display to the fallback text `"🇫🇷 Zizou approves"` without throwing unhandled exceptions or interrupting weather metrics display.
- **SC-005**: All automated lint checks (`ruff check`), type checks (`mypy --strict`), and unit/integration test suites maintain a minimum of 80% business logic coverage and pass without regression.
- **SC-006**: The OpenAPI contract file (`specs/001-realtime-city-weather/contracts/openapi.yaml`) and FastAPI interactive documentation (`/docs`) accurately declare the `easter_egg` property on `WeatherResponse`.

## Assumptions

- The external GIF host `media.tenor.com` remains publicly accessible for client-side image requests over HTTPS.
- The country code returned by OpenWeatherMap for locations within the French Republic conforms to the two-letter ISO 3166-1 alpha-2 standard `"FR"`.
- The easter egg identifier `"zidane"` is extensible in the future should other country-specific easter eggs be introduced.
- Existing frontend styling adheres to Tailwind CSS and existing layout conventions without requiring external UI framework dependencies.
