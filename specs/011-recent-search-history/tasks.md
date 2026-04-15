# Tasks: Recent Search History

**Input**: Design documents from `/specs/011-recent-search-history/`
**Prerequisites**: plan.md, spec.md, research.md, quickstart.md

## Phase 1: Setup (Shared Infrastructure)

### T001: Add searchHistory array to state object

- **Priority:** Must
- **Dependencies:** None
- **File:** `static/index.html`
- **FR:** FR-002

- [ ] Add `searchHistory: []` to the existing `state` object in the State Management section

### T002: Add sessionStorage constants

- **Priority:** Must
- **Dependencies:** None
- **File:** `static/index.html`
- **FR:** FR-009

- [ ] Add `SEARCH_HISTORY: 'searchHistory'` to the existing `STORAGE_KEYS` constant
- [ ] Add `MAX_HISTORY_ENTRIES: 5` to a new `HISTORY_CONFIG` constant object

## Phase 2: Foundational (Blocking Prerequisites)

### T003: Implement sessionStorage read/write helper functions

- **Priority:** Must
- **Dependencies:** T002
- **File:** `static/index.html`
- **FR:** FR-002, FR-009

- [ ] Add `getStoredHistory()` function that reads and JSON-parses the `searchHistory` key from sessionStorage, returning an empty array on missing/invalid data
- [ ] Add `saveHistory(entries)` function that JSON-stringifies and writes the entries array to sessionStorage

### T004: Implement addSearchHistoryEntry function

- **Priority:** Must
- **Dependencies:** T001, T003
- **File:** `static/index.html`
- **FR:** FR-002, FR-003, FR-004, FR-007, FR-008

- [ ] Add `addSearchHistoryEntry(city, temperature, iconCode, units)` function
- [ ] Deduplicate by case-insensitive city name comparison — remove existing entry if found
- [ ] Prepend new entry object `{ city, temperature, iconCode, units, timestamp }` to front of array
- [ ] Enforce max 5 entries by slicing array
- [ ] Update `state.searchHistory` and call `saveHistory()`

### T005: Implement getSearchHistory function

- **Priority:** Must
- **Dependencies:** T003
- **File:** `static/index.html`
- **FR:** FR-004

- [ ] Add `getSearchHistory()` function that returns `state.searchHistory` (already ordered most recent first)

## Phase 3: User Story 1 — View Recent Search History (P1) 🎯 MVP

### T006: Add Recent History HTML structure

- **Priority:** Must
- **Dependencies:** None
- **File:** `static/index.html`
- **FR:** FR-001, FR-012

- [ ] Add a `<details>` element (without `open` attribute, so collapsed by default) with `id="history-section"` after the `#weather-card` div inside `#content-area`
- [ ] Add `<summary>` element with text "Recent History" styled consistently with existing collapsible sections
- [ ] Add `<div id="history-container">` inside the details element for dynamic content
- [ ] Add empty state message div with `id="history-empty"` containing "No recent searches yet"
- [ ] Section hidden by default via `class="hidden"`, shown after first successful search

### T007: Add Recent History CSS styles

- **Priority:** Must
- **Dependencies:** None
- **File:** `static/index.html`
- **FR:** FR-001

- [ ] Add styles for history entry rows (horizontal layout: icon, city name, temperature)
- [ ] Reuse existing `details`/`summary` animation styles (slideDown keyframe already exists)
- [ ] Add hover state for clickable history entries

### T008: Add DOM element references for history

- **Priority:** Must
- **Dependencies:** T006
- **File:** `static/index.html`
- **FR:** FR-001

- [ ] Add `historySection`, `historyContainer`, and `historyEmpty` to the `elements` object referencing the new DOM elements

### T009: Implement renderSearchHistory function

- **Priority:** Must
- **Dependencies:** T005, T008
- **File:** `static/index.html`
- **FR:** FR-001, FR-004, FR-005, FR-011

- [ ] Add `renderSearchHistory()` function that reads from `state.searchHistory`
- [ ] If history is empty, show the empty state message and keep section hidden
- [ ] If history has entries, show the section and render each entry as a horizontal row with weather icon (using `getWeatherIconClass` and `getIconColorClass`), city name, and temperature (formatted with unit symbol)
- [ ] Each entry rendered as a clickable element with `data-city` attribute

### T010: Integrate history recording into handleSearch

- **Priority:** Must
- **Dependencies:** T004, T009
- **File:** `static/index.html`
- **FR:** FR-002, FR-010

- [ ] After successful weather fetch in `handleSearch()`, call `addSearchHistoryEntry()` with city name from API response (`weather.city`), temperature (`weather.temperature`), icon code (`weather.icon_code`), and current units (`weather.units`)
- [ ] Call `renderSearchHistory()` after adding entry
- [ ] Do NOT add entry on fetch failure (FR-010)

### T011: Integrate history recording into handleGeolocation

- **Priority:** Must
- **Dependencies:** T004, T009
- **File:** `static/index.html`
- **FR:** FR-002, FR-011

- [ ] After successful weather fetch in geolocation success callback, call `addSearchHistoryEntry()` with the resolved city name, temperature, icon code, and units from the API response
- [ ] Call `renderSearchHistory()` after adding entry

**Checkpoint**: At this point, User Story 1 should be fully functional — searching for cities populates the collapsed Recent History section, entries show city name + temperature + icon, max 5 entries, most recent first, no duplicates.

---

## Phase 4: User Story 2 — Click History Entry to Re-search (P2)

### T012: Add click handler for history entries

- **Priority:** Must
- **Dependencies:** T009
- **File:** `static/index.html`
- **FR:** FR-006, FR-008

- [ ] Add event delegation on `historyContainer` for click events on history entry elements
- [ ] Extract city name from `data-city` attribute of clicked element
- [ ] Call `fetchWeather(city, state.units)` to re-search
- [ ] Show loading state using existing `showLoading()` function
- [ ] On success, call `renderWeatherCard(weather)` and `addSearchHistoryEntry()` with fresh data (updates temperature/icon per FR-008)
- [ ] Call `renderSearchHistory()` to reflect the reordered/updated list
- [ ] On failure, call `showError()` — do NOT update history entry

**Checkpoint**: At this point, clicking a history entry re-fetches weather, updates the card, and refreshes the history entry with fresh data.

---

## Phase 5: User Story 3 — Session-Only Persistence (P2)

### T013: Initialize history from sessionStorage on page load

- **Priority:** Must
- **Dependencies:** T003, T009
- **File:** `static/index.html`
- **FR:** FR-009

- [ ] In the `init()` function, call `getStoredHistory()` and assign result to `state.searchHistory`
- [ ] Call `renderSearchHistory()` to restore any existing history on load
- [ ] Verify that sessionStorage is used (not localStorage) — history clears on tab close

**Checkpoint**: History persists within the tab session via sessionStorage and is cleared on tab close/refresh as expected.

---

## Phase 6: User Story 4 — Collapsible Section Behavior (P3)

### T014: Ensure section visibility toggles with search state

- **Priority:** Should
- **Dependencies:** T006, T009
- **File:** `static/index.html`
- **FR:** FR-001, FR-012

- [ ] When first search succeeds, remove `hidden` class from `historySection` to make the collapsed `<details>` element visible
- [ ] When `hideAllContent()` is called (during loading/error states), do NOT hide the history section — it persists below the content area
- [ ] Ensure keyboard accessibility: tab to summary, Enter/Space to toggle

**Checkpoint**: The collapsible section appears after first search, stays visible, and can be expanded/collapsed by click or keyboard.

---

## Phase 7: Polish & Cross-Cutting Concerns

### T015: Handle content area state transitions

- **Priority:** Should
- **Dependencies:** T014
- **File:** `static/index.html`
- **FR:** FR-001

- [ ] Ensure history section visibility is preserved when switching between weather view and help view
- [ ] When returning from help view to weather view, history section remains in its previous expand/collapse state

### T016: Verify keyboard accessibility

- **Priority:** Should
- **Dependencies:** T006, T012
- **File:** `static/index.html`
- **FR:** FR-013

- [ ] Verify Tab navigation reaches the history summary element and individual history entries
- [ ] Verify Enter/Space toggles the collapsible section
- [ ] Verify Enter/Space on a history entry triggers re-search
- [ ] Add `role="button"` and `tabindex="0"` to history entry elements for keyboard operability

### T017: Run quickstart end-to-end validation

- **Priority:** Must
- **Dependencies:** T016

- [ ] Start server and search for 3 cities — verify history populates with city, temp, icon
- [ ] Verify max 5 cap and deduplication
- [ ] Verify click-to-re-search updates weather card and history entry
- [ ] Verify collapsed-by-default behavior
- [ ] Verify history clears on page refresh (sessionStorage)
- [ ] Verify keyboard navigation through history section

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational — core MVP
- **User Story 2 (Phase 4)**: Depends on US1 (T009 render function needed for click targets)
- **User Story 3 (Phase 5)**: Depends on Foundational (T003) — can run in parallel with US1/US2
- **User Story 4 (Phase 6)**: Depends on US1 (T006, T009)
- **Polish (Phase 7)**: Depends on all user stories

### Parallel Opportunities

- T001 and T002 (Setup) can run in parallel
- T006 and T007 (HTML structure and CSS) can run in parallel
- US3 (Phase 5) can run in parallel with US1/US2 since it only depends on Foundational
- T010 and T011 (search and geolocation integration) can run in parallel

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001–T002)
2. Complete Phase 2: Foundational (T003–T005)
3. Complete Phase 3: User Story 1 (T006–T011)
4. **STOP and VALIDATE**: Search for cities, verify history displays correctly
5. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational → Core history infrastructure ready
2. Add User Story 1 → History displays after searches (MVP!)
3. Add User Story 2 → Click to re-search from history
4. Add User Story 3 → SessionStorage persistence on load
5. Add User Story 4 → Collapsible section polish
6. Polish → Keyboard accessibility, state transitions, validation
