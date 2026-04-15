# Research: Recent Search History

**Feature**: 011-recent-search-history  
**Date**: 2026-04-15

## R1: sessionStorage for Search History Persistence

**Decision**: Use `sessionStorage` for storing the search history list.

**Rationale**: sessionStorage is scoped to a single browser tab, automatically cleared when the tab closes, and does not persist across page refreshes. This exactly matches the spec requirement (FR-009) for session-only history. It requires no server-side changes and has synchronous read/write which is simpler than IndexedDB.

**Alternatives considered**:
- `localStorage`: Persists across sessions and tabs — does not meet the privacy/session-scoped requirement.
- In-memory JavaScript array only: Would work but loses state on any navigation within the SPA (not applicable here since it's a single page, but sessionStorage is still preferred for robustness).
- IndexedDB: Overkill for storing 5 small JSON objects; async API adds unnecessary complexity.

## R2: Data Serialization Format

**Decision**: Store history as a JSON-serialized array of objects in a single sessionStorage key (`searchHistory`).

**Rationale**: A single key with a JSON array is simpler than multiple indexed keys. The data volume is tiny (5 entries, ~500 bytes max). `JSON.parse`/`JSON.stringify` is fast and universally supported.

**Alternatives considered**:
- Multiple sessionStorage keys (one per entry): More complex to manage ordering, deletion, and the 5-entry cap.
- Custom serialization: No benefit over JSON for this data size and shape.

## R3: History Entry Data Shape

**Decision**: Each entry stores `{ city, temperature, iconCode, units, timestamp }`.

**Rationale**: `city` is used for display and deduplication (case-insensitive comparison). `temperature` and `iconCode` are displayed in the history entry per clarification. `units` is stored alongside temperature so the display is correct even if the user toggles units between searches. `timestamp` is stored for ordering verification but not displayed.

**Alternatives considered**:
- Storing the full weather API response: Too much data for sessionStorage and unnecessary — only display fields are needed.
- Storing only city name: Insufficient per clarification decision to show temperature + icon.

## R4: Collapsible Section Pattern

**Decision**: Use `<details>/<summary>` HTML pattern, consistent with the FAQ section and the 5-day forecast section.

**Rationale**: Already used in the codebase (FAQ items use `<details>/<summary>`, forecast section planned to use the same). Native HTML element provides built-in accessibility (keyboard operable with Enter/Space, screen reader compatible) and requires no JavaScript for basic expand/collapse. CSS animations for smooth transitions already exist in the codebase.

**Alternatives considered**:
- Custom JavaScript show/hide with button: More code, requires manual ARIA attributes, no benefit over native element.
- Third-party accordion library: Unnecessary dependency for a single collapsible section.

## R5: Deduplication Strategy

**Decision**: Deduplicate by case-insensitive city name comparison. When a duplicate is found, remove the existing entry and insert the new one at the top with updated weather data.

**Rationale**: The API returns normalized city names (e.g., "London"), so exact match after lowering both sides is sufficient. Updating temperature/icon on re-search was explicitly decided during clarification.

**Alternatives considered**:
- Fuzzy matching (Levenshtein distance): Overcomplicated for this use case; the API normalizes city names already.
- No deduplication (allow duplicates): Explicitly rejected in spec FR-007.
