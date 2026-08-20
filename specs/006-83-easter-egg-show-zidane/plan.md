# Implementation Plan: Easter Egg - Zidane GIF for France Weather Queries

**Branch**: `006-83-easter-egg-show-zidane` | **Date**: 2026-08-20 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/006-83-easter-egg-show-zidane/spec.md`

## Summary

Implement an easter egg celebration that triggers when weather queries resolve to France (ISO country code `FR`). The backend use case (`GetWeatherUseCase`) evaluates the provider-resolved country code and exposes the easter egg decision within an application result DTO (`WeatherResult`), which the presentation router maps to `WeatherResponse.easter_egg` (`"zidane"` or `null`). The single-page frontend (`static/index.html`) displays the celebratory Zidane GIF (`https://media.tenor.com/B8gpHhxJOksAAAAM/zidane-shocked.gif`, alt: "Zizou approves") above the weather card with robust image re-arming and fallback text (`"🇫🇷 Zizou approves"`) when media loading fails.

## Technical Context

**Language/Version**: Python 3.11+ (CPython)  
**Primary Dependencies**: FastAPI (>=0.109.0), Uvicorn (>=0.27.0), HTTPX (>=0.26.0), Pydantic v2 (>=2.5.0), pydantic-settings (>=2.1.0), Structlog (>=24.1.0), Tailwind CSS (client-side CDN), Weather Icons (client-side CDN)  
**Storage**: In-memory TTL cache (`InMemoryCache` with 900s expiration); no persistent database  
**Testing**: pytest (>=7.4.0), pytest-asyncio, pytest-cov, HTTPX ASGITransport test client  
**Target Platform**: Linux container (Python 3.11-slim) on Azure Container Apps  
**Project Type**: Single project (FastAPI backend + static single-page frontend client)  
**Performance Goals**: <200ms p95 latency for cached weather responses; sub-millisecond use-case easter egg evaluation overhead  
**Constraints**: Strict Clean Architecture inward-only dependency flow; Ruff linting with 100-char line limit; Mypy strict mode (`strict = true`); minimum 80% test coverage; zero new external dependencies  
**Scale/Scope**: Weather API endpoint `/api/v1/weather`, OpenAPI specification, and single-page HTML/JS client  

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle / Standard | Status | Evidence & Compliance Strategy |
|----------------------|--------|---------------------------------|
| **Strict Clean Architecture Layer Separation** | ✅ PASS | `WeatherData` domain entity retains provider-resolved ISO country code. Application layer (`GetWeatherUseCase`) evaluates country code normalization and returns application DTO `WeatherResult(weather_data, easter_egg)`. Presentation router maps `WeatherResult` into `WeatherResponse`. Inward dependency flow is preserved with no domain leaks. |
| **API-First & Contract Synchronization** | ✅ PASS | Presentation schema `WeatherResponse` in `src/presentation/schemas.py` and OpenAPI contract `specs/001-realtime-city-weather/contracts/openapi.yaml` add `easter_egg: Optional[str]` field. |
| **Code Quality & Typing Standards** | ✅ PASS | Python 3.11 explicit type annotations across all layers passing `mypy --strict`; clean formatting and imports passing `ruff check` (100 char limit). |
| **Testing Bar & Fixture Integrity** | ✅ PASS | Full unit test coverage for use-case easter egg evaluation (`"FR"`, `"fr"`, `" FR "`, non-FR, missing/empty country). Existing unit tests in `test_use_cases.py` and integration tests in `test_api.py` refactored to consume `WeatherResult`, avoiding `AttributeError` crashes. >=80% coverage maintained. |
| **Security & Dependency Policy** | ✅ PASS | No new dependencies added. No secrets or external credentials leaked. Sanitized and normalized string handling. |
| **Frontend DOM Resiliency & Re-arming** | ✅ PASS | Client handles image error events synchronously with fallback text `"🇫🇷 Zizou approves"`. Dynamic re-arming on successive searches guarantees proper image load retry without getting stuck in stale error states. |

**Gate Status**: ✅ All gates pass.

## Project Structure

### Documentation (this feature)

```text
specs/006-83-easter-egg-show-zidane/
├── plan.md              # This file
├── spec.md              # Feature specification
└── tasks.md             # Implementation tasks breakdown (/speckit.tasks)
```

### Source Code (repository root)

```text
src/
├── domain/
│   ├── entities.py              # WeatherData (contains country: str), WeatherRequest
│   ├── exceptions.py            # Domain exceptions
│   └── value_objects.py         # Coordinates, UnitSystem
├── application/
│   ├── dto.py                   # WeatherResult application DTO (weather_data, easter_egg)
│   ├── interfaces.py            # WeatherProviderPort, CachePort, LoggerPort
│   └── use_cases/
│       └── get_weather.py       # GetWeatherUseCase (evaluates FR country code -> 'zidane')
├── infrastructure/
│   ├── cache.py                 # InMemoryCache
│   ├── config.py                # Settings
│   └── weather_provider.py      # OpenWeatherMapProvider (maps sys.country to WeatherData.country)
├── presentation/
│   ├── dependencies.py          # FastAPI dependency providers
│   ├── routers/
│   │   └── weather.py           # Maps WeatherResult to WeatherResponse schema
│   └── schemas.py               # WeatherResponse (adds easter_egg: Optional[str] = None)
└── main.py                      # FastAPI application entry point

static/
└── index.html                   # Single-page client with easter egg container, GIF, and fallback text

specs/
└── 001-realtime-city-weather/
    └── contracts/
        └── openapi.yaml         # Updated OpenAPI contract declaring easter_egg

tests/
├── unit/
│   ├── test_entities.py         # Domain entity tests
│   └── test_use_cases.py        # Use case tests (refactored for WeatherResult + easter egg cases)
├── integration/
│   └── test_api.py              # API endpoint tests (refactored mock fixtures + easter egg cases)
└── conftest.py                  # Shared test fixtures (sample_weather_data, sample_weather_result)
```

**Structure Decision**: Single project adhering to strict Clean Architecture. Backend business logic cleanly partitions country-based easter egg rules in the application layer (`src/application/dto.py` and `src/application/use_cases/get_weather.py`), while presentation schemas and OpenAPI contracts expose the optional string field. The single-page frontend (`static/index.html`) manages the DOM lifecycle for rendering, error fallback, and state re-arming.

---

## Detailed Technical Strategy & Implementation Design

### 1. Application Layer: Use Case Result DTO & Easter Egg Decision

- **Application DTO (`src/application/dto.py` or `src/application/use_cases/get_weather.py`)**:
  Define a frozen dataclass representing the use case output:
  ```python
  @dataclass(frozen=True)
  class WeatherResult:
      """Application use case result wrapping domain weather data and easter egg."""
      weather_data: WeatherData
      easter_egg: str | None = None
  ```
- **Evaluation Logic in `GetWeatherUseCase.execute`**:
  ```python
  country_code = (weather_data.country or "").strip().upper()
  easter_egg = "zidane" if country_code == "FR" else None
  return WeatherResult(weather_data=weather_data, easter_egg=easter_egg)
  ```
- **Caching Considerations**:
  The underlying `WeatherData` entity is stored in the cache. When retrieved from cache on subsequent requests, `GetWeatherUseCase` computes the `WeatherResult` consistently from `weather_data.country`.

### 2. Presentation Layer: Schemas, Routers, and OpenAPI Contract

- **Response Schema (`src/presentation/schemas.py`)**:
  Extend `WeatherResponse`:
  ```python
  easter_egg: str | None = Field(
      default=None,
      description="Easter egg identifier when triggered (e.g., 'zidane' for France), null otherwise",
  )
  ```
  Update `model_config.json_schema_extra.example` to document `easter_egg: "zidane"` or `None`.
- **Router Mapping (`src/presentation/routers/weather.py`)**:
  Unpack `WeatherResult`:
  ```python
  result = await use_case.execute(request)
  weather_data = result.weather_data
  return WeatherResponse(
      city=weather_data.city_name,
      country=weather_data.country,
      coordinates={
          "latitude": weather_data.coordinates.latitude,
          "longitude": weather_data.coordinates.longitude,
      },
      temperature=weather_data.temperature,
      feels_like=weather_data.feels_like,
      humidity=weather_data.humidity,
      wind_speed=weather_data.wind_speed,
      pressure=weather_data.pressure,
      visibility=weather_data.visibility,
      description=weather_data.description,
      icon_code=weather_data.icon_code,
      units=weather_data.units,
      timestamp=weather_data.timestamp,
      easter_egg=result.easter_egg,
  )
  ```
- **OpenAPI Contract (`specs/001-realtime-city-weather/contracts/openapi.yaml`)**:
  Add `easter_egg` property to the `WeatherResponse` component schema:
  ```yaml
  easter_egg:
    type: string
    nullable: true
    description: "Easter egg identifier when triggered (e.g. 'zidane' for France), null otherwise"
    example: "zidane"
  ```

### 3. Frontend Layer: DOM Structure, Fallback Handling, and State Re-arming

- **DOM Markup in `static/index.html`** (placed immediately above `#city-name` inside `#weather-card`):
  ```html
  <!-- Easter Egg Celebration -->
  <div id="easter-egg-container" class="hidden mb-4 flex flex-col items-center justify-center">
      <img
          id="easter-egg-img"
          src=""
          alt="Zizou approves"
          class="rounded-xl shadow-md max-h-48 object-contain hidden"
      />
      <span id="easter-egg-fallback" class="hidden text-lg font-semibold text-blue-800 bg-blue-100 px-4 py-2 rounded-lg border border-blue-200">
          🇫🇷 Zizou approves
      </span>
  </div>
  ```
- **DOM Element Map**:
  Register `easterEggContainer`, `easterEggImg`, and `easterEggFallback` in the `elements` dictionary.
- **Image Error Binding**:
  In `init()`, bind the `error` event listener:
  ```javascript
  elements.easterEggImg.addEventListener('error', () => {
      elements.easterEggImg.classList.add('hidden');
      elements.easterEggFallback.classList.remove('hidden');
  });
  ```
- **Rendering & State Re-arming Lifecycle in `renderWeatherCard(weather)`**:
  To prevent the browser from caching a broken image error state across successive searches (e.g. Paris fails -> London -> Marseille), re-arm the image source dynamically:
  ```javascript
  const ZIDANE_GIF_URL = 'https://media.tenor.com/B8gpHhxJOksAAAAM/zidane-shocked.gif';

  if (weather.easter_egg === 'zidane') {
      elements.easterEggContainer.classList.remove('hidden');
      elements.easterEggFallback.classList.add('hidden');
      
      // Re-arm image loader: clear then assign src to guarantee load/error re-trigger
      elements.easterEggImg.src = '';
      elements.easterEggImg.classList.remove('hidden');
      elements.easterEggImg.src = ZIDANE_GIF_URL;
  } else {
      elements.easterEggContainer.classList.add('hidden');
      elements.easterEggImg.classList.add('hidden');
      elements.easterEggFallback.classList.add('hidden');
      elements.easterEggImg.src = '';
  }
  ```
- **Visibility in Error and Reset States**:
  Update `hideAllContent()` to ensure `elements.easterEggContainer.classList.add('hidden')`.

### 4. Comprehensive Testing and Fixture Refactoring Strategy

- **Shared Test Fixtures (`tests/conftest.py`)**:
  Provide `sample_weather_result` fixture alongside `sample_weather_data` to support clean mocking.
  ```python
  @pytest.fixture
  def sample_weather_result(sample_weather_data: WeatherData) -> WeatherResult:
      return WeatherResult(weather_data=sample_weather_data, easter_egg=None)
  ```
- **Unit Tests Refactoring (`tests/unit/test_use_cases.py`)**:
  - Update `test_execute_cache_miss`: Assert `result.weather_data.city_name == "London"` and `result.easter_egg is None`.
  - Update `test_execute_cache_hit`: Assert `result.weather_data.city_name == "London"` and `result.easter_egg is None`.
  - Add `test_execute_easter_egg_france_uppercase`: Country `"FR"` returns `easter_egg="zidane"`.
  - Add `test_execute_easter_egg_france_lowercase`: Country `"fr"` returns `easter_egg="zidane"`.
  - Add `test_execute_easter_egg_france_whitespace`: Country `" FR "` returns `easter_egg="zidane"`.
  - Add `test_execute_easter_egg_non_france`: Country `"US"`, `"GB"`, `"DE"` returns `easter_egg=None`.
  - Add `test_execute_easter_egg_empty_country`: Country `""` returns `easter_egg=None`.
- **Integration Tests Refactoring (`tests/integration/test_api.py`)**:
  - Update existing mocks: `mock_use_case.execute = AsyncMock(return_value=WeatherResult(weather_data=sample_weather_data, easter_egg=None))`.
  - Update `test_get_weather_with_units`: `mock_use_case.execute = AsyncMock(return_value=WeatherResult(weather_data=imperial_data, easter_egg=None))`.
  - Add `test_get_weather_easter_egg_france`: Assert `response.json()["easter_egg"] == "zidane"`.
  - Add `test_get_weather_easter_egg_non_france`: Assert `response.json()["easter_egg"] is None`.

---

## Complexity Tracking

> No constitution violations requiring justification.
