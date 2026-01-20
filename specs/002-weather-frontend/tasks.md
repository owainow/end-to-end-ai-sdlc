# Tasks: Weather Frontend

> **Spec:** 002-weather-frontend  
> **Created:** 2026-01-20  
> **Total Tasks:** 24  
> **Estimated Effort:** 4-6 hours

---

## Phase 1: Infrastructure Setup

### T001: Create static directory structure ✅
- **Priority:** Must
- **Estimate:** 5 min
- **Dependencies:** None
- **Acceptance Criteria:**
  - [x] `static/` directory exists at project root
  - [x] Directory is empty and ready for frontend files

### T002: Update FastAPI to serve static files ✅
- **Priority:** Must
- **Estimate:** 10 min
- **Dependencies:** T001
- **File:** `src/main.py`
- **Acceptance Criteria:**
  - [x] Import `StaticFiles` from `fastapi.staticfiles`
  - [x] Mount static files at root path `/`
  - [x] Static mount is added AFTER all API routes
  - [x] `html=True` enables serving `index.html` for `/`
  - [x] Server starts without errors

---

## Phase 2: HTML Structure & CDN Setup

### T003: Create base HTML file with CDN links ✅
- **Priority:** Must
- **Estimate:** 15 min
- **Dependencies:** T001
- **File:** `static/index.html`
- **Acceptance Criteria:**
  - [x] Valid HTML5 document structure
  - [x] Tailwind CSS CDN script included
  - [x] Weather Icons CSS CDN included
  - [x] Viewport meta tag for responsive design
  - [x] Page title set to "Weather App"
  - [x] Favicon link (optional)

### T004: Create page layout structure ✅
- **Priority:** Must
- **Estimate:** 15 min
- **Dependencies:** T003
- **File:** `static/index.html`
- **Acceptance Criteria:**
  - [x] Centered container with max-width
  - [x] Header section with app title
  - [x] Search section placeholder
  - [x] Content area for weather/error/loading
  - [x] Responsive padding (mobile vs desktop)
  - [x] Light gray background applied

---

## Phase 3: Search Functionality

### T005: Create search input and button ✅
- **Priority:** Must
- **Estimate:** 15 min
- **Dependencies:** T004
- **File:** `static/index.html`
- **FR:** FR-F01
- **Acceptance Criteria:**
  - [x] Text input with placeholder "Enter city name..."
  - [x] Search button with icon or text
  - [x] Form wrapper for submit handling
  - [x] Input has accessible label (sr-only)
  - [x] Focus states visible
  - [x] Tailwind styling applied

### T006: Implement search form submission handler ✅
- **Priority:** Must
- **Estimate:** 15 min
- **Dependencies:** T005
- **File:** `static/index.html` (script section)
- **Acceptance Criteria:**
  - [x] Form submit event listener attached
  - [x] Default form submission prevented
  - [x] City value extracted and trimmed
  - [x] Empty input shows validation message
  - [x] Valid input triggers weather fetch

### T007: Implement input validation ✅
- **Priority:** Must
- **Estimate:** 10 min
- **Dependencies:** T006
- **File:** `static/index.html` (script section)
- **Acceptance Criteria:**
  - [x] Empty input shows "Please enter a city name"
  - [x] Input < 2 chars shows "City name too short"
  - [x] Validation message displays inline
  - [x] Validation clears on new input

---

## Phase 4: API Integration

### T008: Implement fetchWeather function ✅
- **Priority:** Must
- **Estimate:** 20 min
- **Dependencies:** T006
- **File:** `static/index.html` (script section)
- **FR:** FR-F02
- **Acceptance Criteria:**
  - [x] Function accepts city and units parameters
  - [x] Constructs URL with query parameters
  - [x] City name is URL-encoded
  - [x] Uses fetch API with async/await
  - [x] Returns parsed JSON on success
  - [x] Throws Error with message on failure

### T009: Implement error response handling ✅
- **Priority:** Must
- **Estimate:** 15 min
- **Dependencies:** T008
- **File:** `static/index.html` (script section)
- **FR:** FR-F13, FR-F14
- **Acceptance Criteria:**
  - [x] 404 error shows "City not found" message
  - [x] 429 error shows rate limit message
  - [x] 502 error shows provider unavailable message
  - [x] 500 error shows generic error message
  - [x] Network errors caught and handled
  - [x] Error detail extracted from response body

### T010: Implement loading state management ✅
- **Priority:** Must
- **Estimate:** 10 min
- **Dependencies:** T008
- **File:** `static/index.html` (script section)
- **FR:** FR-F03
- **Acceptance Criteria:**
  - [x] Loading state set true before fetch
  - [x] Loading state set false after fetch (success or error)
  - [x] Search button disabled during loading
  - [x] Input disabled during loading (optional)

---

## Phase 5: Weather Card Display

### T011: Create weather card HTML structure ✅
- **Priority:** Must
- **Estimate:** 20 min
- **Dependencies:** T004
- **File:** `static/index.html`
- **FR:** FR-F04
- **Acceptance Criteria:**
  - [x] Card container with rounded corners and shadow
  - [x] City name and country header
  - [x] Temperature display area (large text)
  - [x] Weather icon placeholder
  - [x] Feels like temperature
  - [x] Stats grid for humidity and wind
  - [x] Description text at bottom
  - [x] Card initially hidden

### T012: Implement weather icon mapping ✅
- **Priority:** Should
- **Estimate:** 15 min
- **Dependencies:** T003
- **File:** `static/index.html` (script section)
- **FR:** FR-F08, FR-F16
- **Acceptance Criteria:**
  - [x] WEATHER_ICON_MAP object with all icon codes
  - [x] Maps 01d-50n to Weather Icons classes
  - [x] getWeatherIconClass() function
  - [x] Returns 'wi-na' for unknown codes
  - [x] Day/night variants handled

### T013: Implement renderWeatherCard function ✅
- **Priority:** Must
- **Estimate:** 20 min
- **Dependencies:** T011, T012
- **File:** `static/index.html` (script section)
- **FR:** FR-F04, FR-F05, FR-F06, FR-F07, FR-F08, FR-F11, FR-F12
- **Acceptance Criteria:**
  - [x] Updates city name element
  - [x] Updates temperature with unit symbol
  - [x] Updates feels like temperature
  - [x] Updates humidity percentage
  - [x] Updates wind speed with unit
  - [x] Updates weather icon class
  - [x] Updates description text
  - [x] Shows weather card, hides other content

### T014: Implement temperature formatting ✅
- **Priority:** Must
- **Estimate:** 10 min
- **Dependencies:** T013
- **File:** `static/index.html` (script section)
- **FR:** FR-F05
- **Acceptance Criteria:**
  - [x] formatTemperature(temp, units) function
  - [x] Rounds to nearest integer
  - [x] Appends °C for metric
  - [x] Appends °F for imperial

### T015: Implement wind speed formatting ✅
- **Priority:** Must
- **Estimate:** 10 min
- **Dependencies:** T013
- **File:** `static/index.html` (script section)
- **FR:** FR-F07
- **Acceptance Criteria:**
  - [x] formatWindSpeed(speed, units) function
  - [x] Shows m/s for metric
  - [x] Shows mph for imperial
  - [x] Preserves decimal precision

---

## Phase 6: Unit Toggle

### T016: Create unit toggle UI ✅
- **Priority:** Must
- **Estimate:** 15 min
- **Dependencies:** T004
- **File:** `static/index.html`
- **FR:** FR-F09
- **Acceptance Criteria:**
  - [x] Toggle button group in header
  - [x] °C button and °F button
  - [x] Active state styling (filled background)
  - [x] Inactive state styling (outline)
  - [x] Keyboard accessible

### T017: Implement localStorage persistence ✅
- **Priority:** Must
- **Estimate:** 10 min
- **Dependencies:** T016
- **File:** `static/index.html` (script section)
- **FR:** FR-F10
- **Acceptance Criteria:**
  - [x] getStoredUnits() reads from localStorage
  - [x] saveUnits() writes to localStorage
  - [x] Default to 'metric' if not stored
  - [x] Key is 'weatherUnits'

### T018: Implement unit toggle handler ✅
- **Priority:** Must
- **Estimate:** 15 min
- **Dependencies:** T016, T017
- **File:** `static/index.html` (script section)
- **FR:** FR-F09, FR-F10
- **Acceptance Criteria:**
  - [x] Click handlers on toggle buttons
  - [x] Updates active button styling
  - [x] Saves preference to localStorage
  - [x] Re-fetches weather if data exists
  - [x] Updates display with new units

### T019: Initialize units on page load ✅
- **Priority:** Must
- **Estimate:** 10 min
- **Dependencies:** T017, T018
- **File:** `static/index.html` (script section)
- **Acceptance Criteria:**
  - [x] Load preference from localStorage on init
  - [x] Set correct button as active
  - [x] State variable initialized correctly

---

## Phase 7: Loading & Error States

### T020: Create loading spinner component ✅
- **Priority:** Must
- **Estimate:** 10 min
- **Dependencies:** T004
- **File:** `static/index.html`
- **FR:** FR-F03
- **Acceptance Criteria:**
  - [x] Spinner element with animation
  - [x] Centered in content area
  - [x] Uses Tailwind animate-spin
  - [x] Initially hidden
  - [x] Accessible loading text (sr-only)

### T021: Create error display component ✅
- **Priority:** Must
- **Estimate:** 15 min
- **Dependencies:** T004
- **File:** `static/index.html`
- **FR:** FR-F13, FR-F14
- **Acceptance Criteria:**
  - [x] Error container with red styling
  - [x] Error icon
  - [x] Error message text element
  - [x] Initially hidden
  - [x] Friendly, non-technical language

### T022: Implement content state management ✅
- **Priority:** Must
- **Estimate:** 15 min
- **Dependencies:** T011, T020, T021
- **File:** `static/index.html` (script section)
- **Acceptance Criteria:**
  - [x] hideAllContent() hides card, spinner, error
  - [x] showLoading() shows only spinner
  - [x] showWeather() shows only card
  - [x] showError(message) shows only error with message
  - [x] Smooth transitions (optional)

---

## Phase 8: Responsive Design & Polish

### T023: Implement responsive layout ✅
- **Priority:** Must
- **Estimate:** 20 min
- **Dependencies:** T004, T011
- **File:** `static/index.html`
- **FR:** FR-F15
- **Acceptance Criteria:**
  - [x] Mobile-first base styles
  - [x] Container adapts to screen width
  - [x] Temperature text scales with breakpoints
  - [x] Touch targets minimum 44x44px
  - [x] No horizontal scroll on mobile
  - [x] Tested at 320px, 768px, 1024px, 1440px

### T024: Add accessibility attributes ✅
- **Priority:** Should
- **Estimate:** 15 min
- **Dependencies:** T005, T011, T016
- **File:** `static/index.html`
- **NFR:** NFR-F04
- **Acceptance Criteria:**
  - [x] Form has accessible name
  - [x] Input has label (visible or sr-only)
  - [x] Buttons have accessible names
  - [x] Icons have aria-labels
  - [x] Focus order is logical
  - [x] Color contrast meets WCAG AA

---

## Task Summary

| Phase | Tasks | Priority Mix | Status |
|-------|-------|--------------|--------|
| 1. Infrastructure | T001-T002 | 2 Must | ✅ Complete |
| 2. HTML Structure | T003-T004 | 2 Must | ✅ Complete |
| 3. Search | T005-T007 | 3 Must | ✅ Complete |
| 4. API Integration | T008-T010 | 3 Must | ✅ Complete |
| 5. Weather Card | T011-T015 | 4 Must, 1 Should | ✅ Complete |
| 6. Unit Toggle | T016-T019 | 4 Must | ✅ Complete |
| 7. Loading/Error | T020-T022 | 3 Must | ✅ Complete |
| 8. Polish | T023-T024 | 1 Must, 1 Should | ✅ Complete |

**Total: 24/24 Tasks Complete ✅**

---

## Dependency Graph

```
T001 ─┬─→ T002 ─→ [API serving static files]
      │
      └─→ T003 ─→ T004 ─┬─→ T005 ─→ T006 ─→ T007
                        │         └─→ T008 ─→ T009
                        │                   └─→ T010
                        │
                        ├─→ T011 ─┬─→ T013 ─→ T014
                        │         │        └─→ T015
                        │         └─→ T012
                        │
                        ├─→ T016 ─→ T017 ─→ T018 ─→ T019
                        │
                        ├─→ T020 ─┐
                        │         ├─→ T022
                        └─→ T021 ─┘
                        │
                        └─→ T023 ─→ T024
```

---

## FR/NFR Coverage

| Requirement | Task(s) |
|-------------|---------|
| FR-F01 | T005 |
| FR-F02 | T008 |
| FR-F03 | T010, T020 |
| FR-F04 | T011, T013 |
| FR-F05 | T013, T014 |
| FR-F06 | T013 |
| FR-F07 | T013, T015 |
| FR-F08 | T012, T013 |
| FR-F09 | T016, T018 |
| FR-F10 | T017, T018 |
| FR-F11 | T013 |
| FR-F12 | T013 |
| FR-F13 | T009, T021 |
| FR-F14 | T009, T021 |
| FR-F15 | T023 |
| FR-F16 | T012 |
| NFR-F04 | T024 |

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-20 | Initial task breakdown |
| 1.1 | 2026-01-20 | All tasks implemented |
