# Quickstart: Recent Search History

**Feature**: 011-recent-search-history  
**Branch**: `011-recent-search-history`

## Overview

This feature adds a "Recent History" collapsible section to the weather app that displays the last 5 successful searches from the current browser session. It is entirely frontend-only — no backend changes are needed.

## Prerequisites

- Existing weather app running (`python -m uvicorn src.main:app --reload`)
- Browser with sessionStorage support (all modern browsers)

## What Changes

### Modified Files

| File | Change |
|------|--------|
| `static/index.html` | Add Recent History HTML section + JavaScript logic |

### No Backend Changes

This feature does not modify any Python files, API endpoints, or backend tests. The existing `/api/v1/weather` endpoint is reused as-is when the user clicks a history entry to re-search.

## Key Implementation Details

### HTML Structure
- A `<details>/<summary>` element placed after the `#weather-card` div inside `#content-area`
- Contains a list (`<div>`) of history entries, each showing city name, temperature, and weather icon
- Defaults to collapsed (no `open` attribute on `<details>`)
- Hidden when no searches have been performed

### JavaScript Components
1. **State**: Add `searchHistory: []` to the existing `state` object
2. **SearchHistory manager**: Functions to add/remove/get/persist entries using sessionStorage
3. **Render function**: `renderSearchHistory()` to update the DOM from state
4. **Integration hooks**: Calls to record history after successful searches in `handleSearch()` and `handleGeolocation()`
5. **Click handler**: Re-search when a history entry is clicked

### Storage
- Single sessionStorage key: `searchHistory`
- Value: JSON array of `{ city, temperature, iconCode, units, timestamp }`
- Max 5 entries, most recent first
- Cleared automatically on tab close (sessionStorage behavior)

## How to Test

1. Start the app and search for a city (e.g., "London")
2. Verify a "Recent History" section appears below the weather card (collapsed by default)
3. Expand the section — "London" with temperature and icon should appear
4. Search for more cities — verify history updates (max 5, most recent first)
5. Click a history entry — verify weather re-loads for that city
6. Search for the same city again — verify no duplicate, entry moves to top with updated data
7. Close the browser tab and reopen — verify history is empty
