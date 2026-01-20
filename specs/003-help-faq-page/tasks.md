# Tasks: Help & FAQ Page

> **Spec:** 003-help-faq-page  
> **Created:** 2026-01-20  
> **Total Tasks:** 19  
> **Estimated Effort:** 3-4 hours

---

## Summary

| Phase | Description | Tasks | Status |
|-------|-------------|-------|--------|
| Phase 1 | HTML Structure | T001-T006 | ⬜ Not Started |
| Phase 2 | CSS Styling | T007-T009 | ⬜ Not Started |
| Phase 3 | JavaScript Integration | T010-T014 | ⬜ Not Started |
| Phase 4 | FAQ Data & Rendering | T015-T016 | ⬜ Not Started |
| Phase 5 | Testing & Polish | T017-T019 | ⬜ Not Started |

---

## Phase 1: HTML Structure

### T001: Add help button to header
- **Status:** ⬜ Not Started
- **Priority:** Must
- **Estimate:** 10 min
- **Dependencies:** None
- **File:** `static/index.html`

**Description:**
Add a help button to the header, positioned next to the unit toggle buttons.

**Acceptance Criteria:**
- [ ] Help button displays with question mark icon
- [ ] Button uses consistent styling with existing header elements
- [ ] Button has minimum 44x44px touch target
- [ ] Button has `id="help-btn"` for JavaScript targeting

**Implementation Notes:**
```html
<button id="help-btn" class="flex items-center gap-1 px-3 py-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors" title="Help & FAQ">
    <span class="text-lg">❓</span>
    <span class="hidden sm:inline text-sm font-medium">Help</span>
</button>
```

---

### T002: Wrap main content in weather-view div
- **Status:** ⬜ Not Started
- **Priority:** Must
- **Estimate:** 10 min
- **Dependencies:** None
- **File:** `static/index.html`

**Description:**
Wrap the existing main content (search, welcome message, loading, error, weather card) in a `#weather-view` container div to enable view switching.

**Acceptance Criteria:**
- [ ] New `<div id="weather-view">` wraps search and content areas
- [ ] No visual changes to existing layout
- [ ] All existing functionality continues to work

**Implementation Notes:**
Add opening `<div id="weather-view">` after `<main>` opening tag, close before footer.

---

### T003: Create help-view container structure
- **Status:** ⬜ Not Started
- **Priority:** Must
- **Estimate:** 15 min
- **Dependencies:** T002
- **File:** `static/index.html`

**Description:**
Create the help view container with the basic structure for back button, quick tips section, and FAQ section.

**Acceptance Criteria:**
- [ ] `<div id="help-view" class="hidden">` created after weather-view
- [ ] Contains header with back button
- [ ] Contains placeholder sections for quick tips and FAQ
- [ ] Uses consistent max-width and padding with weather view

**Implementation Notes:**
```html
<div id="help-view" class="hidden max-w-2xl mx-auto px-4 py-6">
    <!-- Back navigation -->
    <!-- Quick tips section -->
    <!-- FAQ section -->
</div>
```

---

### T004: Add back navigation button
- **Status:** ⬜ Not Started
- **Priority:** Must
- **Estimate:** 5 min
- **Dependencies:** T003
- **File:** `static/index.html`

**Description:**
Add a "Back to Weather" button at the top of the help view for navigation.

**Acceptance Criteria:**
- [ ] Button displays "← Back to Weather" text
- [ ] Button has `id="back-to-weather-btn"` for JavaScript targeting
- [ ] Positioned at top of help view
- [ ] Has appropriate hover state

---

### T005: Create quick tips HTML section
- **Status:** ⬜ Not Started
- **Priority:** Should
- **Estimate:** 10 min
- **Dependencies:** T003
- **File:** `static/index.html`

**Description:**
Create a quick tips section with 3 tip cards showing key app features.

**Acceptance Criteria:**
- [ ] Section has heading "Quick Tips"
- [ ] Contains 3 tip cards in a responsive grid
- [ ] Each card has icon, title, and brief description
- [ ] Cards cover: Search, Unit Toggle, City Specificity

**Implementation Notes:**
Tips content:
1. **Search Any City** - Enter a city name to get current weather
2. **Toggle Units** - Switch between °C and °F anytime
3. **Be Specific** - Add country code for better accuracy

---

### T006: Create FAQ accordion HTML
- **Status:** ⬜ Not Started
- **Priority:** Must
- **Estimate:** 15 min
- **Dependencies:** T003
- **File:** `static/index.html`

**Description:**
Create the FAQ section with accordion items using native `<details>/<summary>` elements, organized by category.

**Acceptance Criteria:**
- [ ] Section has heading "Frequently Asked Questions"
- [ ] 4 category sections: Getting Started, Weather Data, Troubleshooting, Privacy & Data
- [ ] Each category has 2-3 FAQ items
- [ ] Each FAQ item uses `<details>/<summary>` pattern
- [ ] Total of 12 FAQ items

---

## Phase 2: CSS Styling

### T007: Style help button with hover state
- **Status:** ⬜ Not Started
- **Priority:** Must
- **Estimate:** 5 min
- **Dependencies:** T001
- **File:** `static/index.html`

**Description:**
Ensure help button styling matches the existing app design and has proper hover/focus states.

**Acceptance Criteria:**
- [ ] Button uses app color palette (blue tones)
- [ ] Hover state has visual feedback
- [ ] Focus state has visible outline for accessibility
- [ ] Transitions are smooth (150-200ms)

---

### T008: Style quick tips cards
- **Status:** ⬜ Not Started
- **Priority:** Should
- **Estimate:** 10 min
- **Dependencies:** T005
- **File:** `static/index.html`

**Description:**
Style the quick tips cards with consistent design using Tailwind CSS.

**Acceptance Criteria:**
- [ ] Cards use light blue background (`bg-blue-50`)
- [ ] Icons are large and colorful
- [ ] Text is centered and readable
- [ ] Cards are responsive (3 columns → 1 column on mobile)
- [ ] Cards have rounded corners and padding

---

### T009: Style FAQ accordion items
- **Status:** ⬜ Not Started
- **Priority:** Must
- **Estimate:** 15 min
- **Dependencies:** T006
- **File:** `static/index.html`

**Description:**
Style the FAQ accordion with proper expand/collapse visual indicators and smooth transitions.

**Acceptance Criteria:**
- [ ] Questions have white background with subtle border
- [ ] Chevron indicator rotates on expand (180°)
- [ ] Smooth height transition on expand/collapse
- [ ] Answer text has appropriate padding
- [ ] Category headings are styled with icons
- [ ] Proper spacing between items

---

## Phase 3: JavaScript Integration

### T010: Add element references to JavaScript
- **Status:** ⬜ Not Started
- **Priority:** Must
- **Estimate:** 10 min
- **Dependencies:** T003, T004
- **File:** `static/index.html`

**Description:**
Add references to new DOM elements in the `elements` object.

**Acceptance Criteria:**
- [ ] `elements.weatherView` references `#weather-view`
- [ ] `elements.helpView` references `#help-view`
- [ ] `elements.helpBtn` references `#help-btn`
- [ ] `elements.backToWeatherBtn` references `#back-to-weather-btn`

**Implementation Notes:**
```javascript
// Add to elements object
weatherView: document.getElementById('weather-view'),
helpView: document.getElementById('help-view'),
helpBtn: document.getElementById('help-btn'),
backToWeatherBtn: document.getElementById('back-to-weather-btn'),
```

---

### T011: Create showHelpView function
- **Status:** ⬜ Not Started
- **Priority:** Must
- **Estimate:** 15 min
- **Dependencies:** T010
- **File:** `static/index.html`

**Description:**
Create function to show the help view and hide the weather view.

**Acceptance Criteria:**
- [ ] Function hides weather view
- [ ] Function shows help view
- [ ] Function updates `state.currentView` to 'help'
- [ ] Function updates URL hash to `#help`

**Implementation Notes:**
```javascript
function showHelpView() {
    elements.weatherView.classList.add('hidden');
    elements.helpView.classList.remove('hidden');
    state.currentView = 'help';
    window.location.hash = 'help';
}
```

---

### T012: Create showWeatherView function
- **Status:** ⬜ Not Started
- **Priority:** Must
- **Estimate:** 15 min
- **Dependencies:** T010
- **File:** `static/index.html`

**Description:**
Create function to show the weather view and hide the help view.

**Acceptance Criteria:**
- [ ] Function hides help view
- [ ] Function shows weather view
- [ ] Function updates `state.currentView` to 'weather'
- [ ] Function clears URL hash
- [ ] Restores previous weather state (if any)

**Implementation Notes:**
```javascript
function showWeatherView() {
    elements.helpView.classList.add('hidden');
    elements.weatherView.classList.remove('hidden');
    state.currentView = 'weather';
    history.pushState('', document.title, window.location.pathname);
}
```

---

### T013: Add hash routing handlers
- **Status:** ⬜ Not Started
- **Priority:** Must
- **Estimate:** 15 min
- **Dependencies:** T011, T012
- **File:** `static/index.html`

**Description:**
Add event listeners for hash change and initial page load to handle routing.

**Acceptance Criteria:**
- [ ] `hashchange` event listener calls appropriate view function
- [ ] On page load, check hash and show correct view
- [ ] Direct navigation to `#help` works
- [ ] Browser back/forward navigation works

**Implementation Notes:**
```javascript
function handleRouteChange() {
    if (window.location.hash === '#help') {
        showHelpView();
    } else {
        showWeatherView();
    }
}

window.addEventListener('hashchange', handleRouteChange);
window.addEventListener('DOMContentLoaded', handleRouteChange);
```

---

### T014: Wire up button event listeners
- **Status:** ⬜ Not Started
- **Priority:** Must
- **Estimate:** 5 min
- **Dependencies:** T010
- **File:** `static/index.html`

**Description:**
Add click event listeners to the help button and back button.

**Acceptance Criteria:**
- [ ] Help button click calls `showHelpView()`
- [ ] Back button click calls `showWeatherView()`

**Implementation Notes:**
```javascript
elements.helpBtn.addEventListener('click', showHelpView);
elements.backToWeatherBtn.addEventListener('click', showWeatherView);
```

---

## Phase 4: FAQ Data & Rendering

### T015: Define FAQ_DATA and QUICK_TIPS constants
- **Status:** ⬜ Not Started
- **Priority:** Should
- **Estimate:** 10 min
- **Dependencies:** None
- **File:** `static/index.html`

**Description:**
Define the FAQ data structure and quick tips content as JavaScript constants.

**Acceptance Criteria:**
- [ ] `FAQ_DATA` object contains 4 categories
- [ ] Each category has id, title, icon, and items array
- [ ] Each item has id, question, and answer
- [ ] `QUICK_TIPS` array contains 3 tip objects
- [ ] Data matches content from spec.md

---

### T016: Create FAQ and Tips render functions
- **Status:** ⬜ Not Started
- **Priority:** Should
- **Estimate:** 15 min
- **Dependencies:** T015
- **File:** `static/index.html`

**Description:**
Create functions to dynamically render FAQ and tips from data.

**Acceptance Criteria:**
- [ ] `renderFAQItem(item)` returns HTML for single FAQ item
- [ ] `renderFAQCategory(category)` returns HTML for category with items
- [ ] `renderQuickTips()` populates tips section
- [ ] `renderFAQ()` populates FAQ section
- [ ] Functions called on page load

**Note:** This task is optional if FAQ content is hard-coded in HTML. Recommended for maintainability.

---

## Phase 5: Testing & Polish

### T017: Test navigation flows
- **Status:** ⬜ Not Started
- **Priority:** Must
- **Estimate:** 10 min
- **Dependencies:** T013, T014
- **File:** N/A (Manual Testing)

**Description:**
Test all navigation paths between weather and help views.

**Test Cases:**
- [ ] Click help button → help view displays
- [ ] Click back button → weather view displays
- [ ] Navigate to `#help` URL directly → help view displays
- [ ] Browser back button from help → weather view displays
- [ ] Refresh on `#help` → stays on help view
- [ ] Search weather → help → back → weather data still visible

---

### T018: Test accessibility
- **Status:** ⬜ Not Started
- **Priority:** Must
- **Estimate:** 10 min
- **Dependencies:** All HTML/CSS tasks
- **File:** N/A (Manual Testing)

**Description:**
Verify accessibility requirements are met.

**Test Cases:**
- [ ] Tab through all interactive elements
- [ ] Enter/Space activates buttons
- [ ] Enter/Space expands FAQ items
- [ ] Focus visible on all elements
- [ ] Screen reader announces questions and answers
- [ ] Chevron rotation doesn't break screen reader

---

### T019: Test responsive design
- **Status:** ⬜ Not Started
- **Priority:** Must
- **Estimate:** 10 min
- **Dependencies:** All HTML/CSS tasks
- **File:** N/A (Manual Testing)

**Description:**
Verify responsive layout across device sizes.

**Test Cases:**
- [ ] Desktop (1280px+): Full layout, 3 tip columns
- [ ] Tablet (768px): Adjusted layout, 2-3 tip columns
- [ ] Mobile (375px): Single column, stacked layout
- [ ] Text readable without horizontal scroll
- [ ] Touch targets minimum 44x44px
- [ ] FAQ accordion easy to tap on mobile

---

## Task Dependencies

```
T001 ──────────────────────────────► T007
                                      │
T002 ──► T003 ──┬──► T004 ──────────► T010 ──┬──► T011 ──┬──► T013 ──► T017
                │                            │           │
                ├──► T005 ──► T008           │           └──► T012 ──┘
                │                            │
                └──► T006 ──► T009           └──► T014

T015 ──────────────────────────────────────────────► T016

T007, T008, T009 ─────────────────────────────────► T018, T019
```

---

## Notes

- All tasks modify `static/index.html` - this is a single-file frontend
- No backend changes required
- No new dependencies - uses existing Tailwind CSS and Weather Icons
- Consider committing after each phase for clean git history
