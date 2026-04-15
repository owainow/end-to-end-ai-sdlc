# Feature Specification: Recent Search History

**Feature Branch**: `011-recent-search-history`  
**Created**: 2026-04-15  
**Status**: Draft  
**Input**: User description: "I want this feature to add a recent history part to the website. I want to be able to see the last 5 searches from my session under a recent history tab."

## Clarifications

### Session 2026-04-15

- Q: Should each history entry display only the city name, or also show a brief weather summary (e.g., temperature and icon) from the time of the search? → A: City name + temperature + weather icon from time of search
- Q: How should the "Recent History" tab be positioned in the UI relative to the existing Help button? → A: A collapsible section below the weather card (always visible on the main page, same `<details>/<summary>` pattern as forecast)
- Q: Should the Recent History section default to expanded or collapsed when the page first loads (after at least one search)? → A: Collapsed by default (user clicks to expand)
- Q: When the user re-searches from history (clicks an entry), should the temperature and icon stored in that history entry update to the fresh data, or remain as the original snapshot? → A: Update the entry's temperature and icon to the fresh values from the new API response

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View Recent Search History (Priority: P1)

As a user, after searching for one or more cities, I want to see a "Recent History" tab/section on the page that lists my last 5 searches from the current browser session so I can quickly review what I've already looked up.

**Why this priority**: This is the core functionality — displaying search history is the entire point of the feature. Without this, no other stories are meaningful.

**Independent Test**: Can be fully tested by searching for 3 different cities (e.g., "London", "Paris", "Tokyo"), then viewing the Recent History section and confirming all 3 searches appear in reverse chronological order (most recent first) with the city name visible.

**Acceptance Scenarios**:

1. **Given** a user has searched for at least one city, **When** the user views the Recent History section, **Then** the searched city appears in the history list
2. **Given** a user has not searched for any city in the current session, **When** the user views the Recent History section, **Then** an empty state message is shown (e.g., "No recent searches")
3. **Given** a user has searched for 5 or more cities, **When** the user views the Recent History section, **Then** only the 5 most recent searches are displayed, ordered from most recent to oldest
4. **Given** a user has searched for 6 cities, **When** the user views the Recent History section, **Then** the oldest (first) search is no longer visible, replaced by the 6th search at the top

---

### User Story 2 - Click a History Entry to Re-search (Priority: P2)

As a user, I want to click on a city in my recent search history to immediately re-fetch and display the weather for that city so I can quickly revisit previous searches without retyping.

**Why this priority**: Re-searching from history is the primary interactive value of the feature but depends on the history list (P1) being in place first.

**Independent Test**: Can be tested by searching for "London", then searching for "Paris", then clicking "London" in the history list and verifying the weather card updates to show London's current weather.

**Acceptance Scenarios**:

1. **Given** the Recent History section shows a list of previously searched cities, **When** the user clicks on a city name in the list, **Then** the app fetches and displays the current weather for that city
2. **Given** the user clicks a history entry, **When** the weather loads successfully, **Then** the clicked city moves to the top of the history list as the most recent search
3. **Given** the user clicks a history entry, **When** the weather is loading, **Then** the same loading indicator used for normal searches is shown

---

### User Story 3 - History Persists Within Session Only (Priority: P2)

As a user, I want my search history to persist only for the current browser session (tab) so that my history is automatically cleared when I close the tab, maintaining my privacy.

**Why this priority**: Session-scoped persistence is a key requirement that defines the data lifecycle. It's critical for the privacy model.

**Independent Test**: Can be tested by searching for cities, verifying they appear in history, then closing and reopening the browser tab and confirming the history is empty.

**Acceptance Scenarios**:

1. **Given** a user has searched for cities and the history list is populated, **When** the user refreshes the page, **Then** the history is cleared (session storage, not local storage)
2. **Given** a user opens a new browser tab to the same app, **When** they view the Recent History section, **Then** it shows an empty state — history is not shared across tabs

---

### User Story 4 - History Displayed as Collapsible Section (Priority: P3)

As a user, I want the Recent History to appear as a collapsible section below the weather card so I can expand or collapse it without leaving the main weather view.

**Why this priority**: UI placement is important for usability but the feature still works if history is always expanded — the collapsible toggle just keeps the UI cleaner.

**Independent Test**: Can be tested by searching for a city, then verifying a "Recent History" collapsible section appears below the weather card, clicking the header collapses/expands the history list.

**Acceptance Scenarios**:

1. **Given** the user has performed at least one successful search, **When** they view the main weather page, **Then** a "Recent History" collapsible section is visible below the weather card
2. **Given** the Recent History section is expanded, **When** the user clicks the section header, **Then** the history list collapses with a smooth animation
3. **Given** the Recent History section is collapsed, **When** the user clicks the section header, **Then** the history list expands to show all entries

---

### Edge Cases

- What happens when the user searches for the same city twice consecutively? The duplicate should not create a second entry — instead, the existing entry should move to the top of the list.
- What happens when the user searches via the geolocation button? The geolocation search should also be recorded in history using the resolved city name.
- What happens when a search fails (city not found)? Failed searches should NOT be added to the history — only successful weather lookups are recorded.
- What happens when the history list is empty and the user navigates to the Recent History tab? An empty state message (e.g., "No recent searches yet. Search for a city to see your history here.") should be displayed.
- How does the history interact with the unit toggle? History entries store the city name only; re-searching from history uses the currently selected unit preference.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST display a "Recent History" collapsible section below the weather card, using the `<details>/<summary>` HTML pattern, visible on the main weather view whenever at least one search has been performed. The section MUST default to collapsed.
- **FR-002**: System MUST record each successful weather search (city name, temperature, weather icon) in a session-scoped history list
- **FR-003**: System MUST store a maximum of 5 entries in the history list, discarding the oldest entry when a 6th is added (FIFO with cap)
- **FR-004**: History entries MUST be ordered from most recent to oldest (reverse chronological)
- **FR-005**: Each history entry MUST display the city name, the temperature at the time of the search, and the weather icon from the time of the search
- **FR-006**: Users MUST be able to click a history entry to re-search and display the weather for that city
- **FR-007**: When a user searches for a city already in the history list, the system MUST move the existing entry to the top rather than creating a duplicate
- **FR-008**: When a history entry is re-searched (either by clicking or by manual re-search of the same city), the system MUST update the entry's stored temperature and weather icon to the fresh values from the new API response
- **FR-009**: Search history MUST persist only for the current browser session (sessionStorage) and MUST NOT survive page refresh or tab close
- **FR-010**: Failed searches (city not found, API errors) MUST NOT be added to the history
- **FR-011**: Geolocation-based searches MUST also be recorded in history using the resolved city name
- **FR-012**: The Recent History section MUST show an empty state message when no searches have been performed
- **FR-013**: The Recent History section MUST be keyboard-accessible (focusable, operable with Enter/Space)
- **FR-014**: This feature is frontend-only — no new backend API endpoints are required. History is managed entirely in the browser using JavaScript and sessionStorage.

### Key Entities

- **SearchHistoryEntry**: Represents a single search in the history. Key attributes: city name, temperature at time of search, weather icon code at time of search, timestamp of search
- **SearchHistoryList**: Manages the ordered collection of up to 5 SearchHistoryEntry items. Responsible for deduplication, ordering, and cap enforcement.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can view their last 5 searches within 1 click/tap from the main weather view
- **SC-002**: Clicking a history entry loads the weather for that city within the same time as a normal search
- **SC-003**: 100% of successful searches are recorded in the history list (including geolocation-based searches)
- **SC-004**: Duplicate city searches never produce duplicate history entries
- **SC-005**: History is fully cleared when the browser tab is closed or the page is refreshed (verified via sessionStorage)
- **SC-006**: The Recent History section is fully operable via keyboard-only navigation

## Assumptions

- Search history is a frontend-only feature — no API endpoint or backend persistence is needed.
- The history is stored in the browser's `sessionStorage`, meaning it is scoped to a single tab and cleared on tab close / page refresh.
- History entries store the city name (as returned by the API in the weather response), not the raw user input, to ensure consistent display.
- The "Recent History" section uses the same `<details>/<summary>` collapsible pattern as the forecast section, displayed below the weather card on the main view.
- Re-searching from history uses the currently selected temperature unit (metric/imperial), not the unit that was active at the time of the original search.
