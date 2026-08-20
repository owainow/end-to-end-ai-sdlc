# Tasks: Easter Egg - Zidane GIF for France Weather Queries

**Input**: Design documents from `/specs/006-83-easter-egg-show-zidane/`

**Prerequisites**: [plan.md](plan.md) (required), [spec.md](spec.md) (required for user stories)

**Tests**: Included per specification requirements (unit tests for easter egg logic and API integration tests).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Exact file paths are specified in descriptions

## Path Conventions

- Single project structure: `src/`, `tests/`, `static/`, and `specs/` at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and validation of clean repository state

- [ ] T001 Verify clean environment, dependencies, and testing baselines across `src/` and `tests/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core architectural models, DTOs, provider safety, and baseline use-case / router contracts that MUST be complete and type-checked before individual story implementation

**⚠️ CRITICAL**: Foundational tasks must establish a fully typed and passing baseline before story work begins

- [ ] T002 [P] Create `WeatherResult` application DTO in `src/application/dto.py` with `weather_data: WeatherData` and `easter_egg: str | None = None`
- [ ] T003 [P] Update `_parse_response` in `src/infrastructure/weather_provider.py` to safely extract country code using `(data.get("sys") or {}).get("country") or ""` to avoid `NoneType` `AttributeError` and guarantee a valid `str`
- [ ] T004 [P] Update `WeatherResponse` schema in `src/presentation/schemas.py` to declare `easter_egg: str | None = Field(default=None, ...)` and update JSON schema examples
- [ ] T005 [P] Update OpenAPI specification contract in `specs/001-realtime-city-weather/contracts/openapi.yaml` declaring `easter_egg` property on `WeatherResponse`
- [ ] T006 Update `GetWeatherUseCase.execute` signature and return type in `src/application/use_cases/get_weather.py` to return `WeatherResult` (wrapping `weather_data` with baseline `easter_egg=None`)
- [ ] T007 Update presentation router `get_weather` in `src/presentation/routers/weather.py` to unpack `WeatherResult` (`result.weather_data` and `result.easter_egg`) into `WeatherResponse`
- [ ] T008 [P] Add `sample_weather_result` fixture in `tests/conftest.py` returning `WeatherResult(weather_data=sample_weather_data, easter_egg=None)`
- [ ] T009 Refactor existing unit tests in `tests/unit/test_use_cases.py` and integration test mocks in `tests/integration/test_api.py` to consume `WeatherResult`, ensuring full test suite and strict type checking pass

**Checkpoint**: Foundation ready - `mypy src` passes under strict mode and all existing tests in `pytest tests/` pass.

---

## Phase 3: User Story 1 - Weather API Easter Egg Flag for French Queries (Priority: P1) 🎯 MVP

**Goal**: When a weather query resolves to France (country code `FR`), the application layer use case flags `easter_egg="zidane"`, and presentation returns `"easter_egg": "zidane"` in the JSON payload (or `null` for non-FR / missing country).

**Independent Test**: Can be tested independently via application unit tests and API integration tests by querying French locations (e.g., Paris, Lyon) to assert `"easter_egg": "zidane"` and non-French locations (e.g., London, Tokyo, empty country) to assert `"easter_egg": null`.

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T010 [P] [US1] Add unit tests in `tests/unit/test_use_cases.py` for `GetWeatherUseCase` easter egg evaluation covering uppercase `"FR"`, lowercase `"fr"`, whitespace `" FR "`, non-French codes (`"GB"`, `"US"`, `"DE"`), and empty country `""`
- [ ] T011 [P] [US1] Add API integration tests in `tests/integration/test_api.py` for `/api/v1/weather` verifying `"easter_egg": "zidane"` for French queries and `"easter_egg": null` for non-French / missing country queries

### Implementation for User Story 1

- [ ] T012 [US1] Implement country code normalization and easter egg evaluation in `GetWeatherUseCase.execute` within `src/application/use_cases/get_weather.py` (`country_code = (weather_data.country or "").strip().upper()`, setting `easter_egg="zidane"` if `country_code == "FR"` else `None`)

**Checkpoint**: At this point, User Story 1 is fully functional and all unit and integration tests pass independently (`pytest tests/unit/test_use_cases.py tests/integration/test_api.py`).

---

## Phase 4: User Story 2 - UI Celebration with Zidane GIF (Priority: P2)

**Goal**: Display celebratory Zidane GIF (`https://media.tenor.com/B8gpHhxJOksAAAAM/zidane-shocked.gif`, alt: "Zizou approves") above the weather details card when `weather.easter_egg === 'zidane'`, and ensure it is hidden for non-French locations and unit switches.

**Independent Test**: Can be verified in browser or DOM inspections: querying a French location displays the GIF container above the city name; subsequent queries to non-French locations hide the container completely.

### Implementation for User Story 2

- [ ] T013 [P] [US2] Add easter egg HTML markup (`#easter-egg-container`, `#easter-egg-img` with `alt="Zizou approves"`, and `#easter-egg-fallback` with text `"🇫🇷 Zizou approves"`) inside `#weather-card` above `#city-name` in `static/index.html`
- [ ] T014 [US2] Register `easterEggContainer`, `easterEggImg`, and `easterEggFallback` in the `elements` dictionary in `static/index.html`
- [ ] T015 [US2] Update `renderWeatherCard(weather)` in `static/index.html` to toggle `#easter-egg-container` visibility and assign `src="https://media.tenor.com/B8gpHhxJOksAAAAM/zidane-shocked.gif"` when `weather.easter_egg === 'zidane'`, and hide it when `null`
- [ ] T016 [US2] Update `hideAllContent()` and state reset routines in `static/index.html` to ensure `#easter-egg-container` is hidden during loading, error, and welcome states

**Checkpoint**: At this point, User Stories 1 AND 2 both work independently and end-to-end.

---

## Phase 5: User Story 3 - Resilient Frontend Fallback and State Re-arming (Priority: P3)

**Goal**: Gracefully handle media loading failures by displaying the fallback text "🇫🇷 Zizou approves" instead of a broken image icon, and dynamically re-arm the image loading lifecycle on subsequent searches.

**Independent Test**: Can be tested independently by simulating an `error` event on `#easter-egg-img` and verifying that the image is hidden while `"🇫🇷 Zizou approves"` is displayed, followed by a new French search verifying that the image state resets and re-arms.

### Implementation for User Story 3

- [ ] T017 [US3] Bind an `error` event listener on `elements.easterEggImg` in `init()` within `static/index.html` to hide the image element and display `elements.easterEggFallback` with `"🇫🇷 Zizou approves"`
- [ ] T018 [US3] Implement dynamic image loader state re-arming in `renderWeatherCard()` within `static/index.html` by resetting image source (`src = ''` before URL assignment) and toggling element visibility classes on each render

**Checkpoint**: All user stories are independently functional, resilient against network failures, and properly re-armed across rapid searches.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Quality assurance, linting, strict type verification, and test coverage enforcement

- [ ] T019 [P] Run Ruff linter and formatter checks (`ruff check src tests` and `ruff format --check src tests`) to ensure compliance with 100-character line length limits
- [ ] T020 [P] Run Mypy strict type checking (`mypy src tests`) to verify type annotations across all layers
- [ ] T021 Run full test suite with coverage enforcement (`pytest --cov=src --cov-fail-under=80`) to guarantee >=80% business logic coverage and verify zero regressions

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories. Establishes `WeatherResult` DTO, provider country parsing safety, schema/OpenAPI contracts, and updates existing tests to prevent type/attribute breakages.
- **User Story 1 (Phase 3)**: Depends on Foundational completion. Delivers core backend easter egg detection.
- **User Story 2 (Phase 4)**: Depends on Foundational (Phase 2) completion and consumes contract from US1. Delivers frontend GIF display.
- **User Story 3 (Phase 5)**: Depends on User Story 2 DOM structure (Phase 4). Delivers error fallback and state re-arming lifecycle.
- **Polish (Phase 6)**: Depends on all user stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Independent of frontend stories; requires Phase 2 foundational DTO and use-case scaffolding.
- **User Story 2 (P2)**: Requires Phase 2 DOM foundation; renders easter egg data delivered by US1.
- **User Story 3 (P3)**: Enhances the DOM elements and event handlers established in US2.

### Within Each User Story

- Tests (T010, T011) MUST be written and fail before use case implementation in T012.
- HTML markup in T013 before DOM element binding in T014.
- Rendering logic in T015 before fallback re-arming logic in T018.

### Parallel Opportunities

- **Phase 2**: T002, T003, T004, T005, and T008 can all be implemented in parallel across separate files.
- **Phase 3**: Test tasks T010 and T011 can be written in parallel.
- **Phase 4**: Markup preparation T013 can run in parallel with backend test tasks.
- **Phase 6**: Linting (T019) and type checking (T020) can run in parallel.

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Add unit tests in tests/unit/test_use_cases.py for GetWeatherUseCase easter egg evaluation"
Task: "Add API integration tests in tests/integration/test_api.py for /api/v1/weather verifying easter_egg"

# Once tests fail, execute implementation:
Task: "Implement country code normalization and easter egg evaluation in GetWeatherUseCase.execute"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories; ensures `mypy` and `pytest` remain green)
3. Complete Phase 3: User Story 1 (TDD: tests first, then implementation)
4. **STOP and VALIDATE**: Verify API endpoints return `"easter_egg": "zidane"` for French queries and `null` otherwise.

### Incremental Delivery

1. Complete Setup + Foundational → Solid Clean Architecture boundary with `WeatherResult` DTO.
2. Complete User Story 1 → API contract fully functional with unit/integration tests passing.
3. Complete User Story 2 → Visual GIF celebration rendered on frontend.
4. Complete User Story 3 → Fallback text and resilient state re-arming active.
5. Complete Polish → Strict type check, Ruff linting, and 80%+ test coverage validated.

---

## Notes

- `[P]` tasks denote changes in isolated files with no blocking dependencies.
- `[US#]` tags map each task directly to User Story 1, 2, or 3 for traceability.
- Clean Architecture inward-only dependency flow is preserved: Domain (`WeatherData.country`) -> Application (`WeatherResult.easter_egg`) -> Presentation (`WeatherResponse.easter_egg`).
- Country code extraction in `OpenWeatherMapProvider` uses `(data.get("sys") or {}).get("country") or ""` to guarantee a non-null string even on malformed or oceanic provider payloads.
