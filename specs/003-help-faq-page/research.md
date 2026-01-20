# Research: Help & FAQ Page

> **Spec:** 003-help-faq-page  
> **Date:** 2026-01-20

---

## 1. Existing Codebase Analysis

### Current Architecture
The Weather App frontend is a **single-page application (SPA)** contained in `static/index.html`:

- **Framework**: Vanilla JavaScript with Tailwind CSS (CDN)
- **Icons**: Weather Icons library (CDN)
- **State**: Simple state object with properties for city, weather, units, loading, error
- **Storage**: localStorage for unit preference persistence
- **Styling**: Tailwind utility classes with custom animations

### Key Patterns to Follow

```javascript
// State management pattern
const state = {
    city: '',
    weather: null,
    units: 'metric',
    loading: false,
    error: null
};

// DOM element caching
const elements = {
    searchForm: document.getElementById('search-form'),
    // ... cached references
};

// Content state functions
function hideAllContent() { /* ... */ }
function showWelcome() { /* ... */ }
function showLoading() { /* ... */ }
```

### Header Structure
The current header contains:
1. App title with weather icon
2. Unit toggle buttons (°C/°F)

**Insertion point for Help button**: After the unit toggle, maintaining visual balance.

---

## 2. Accordion Component Patterns

### Native HTML: `<details>` / `<summary>`
**Pros:**
- Zero JavaScript required
- Built-in accessibility
- Keyboard navigation works automatically
- Graceful degradation

**Cons:**
- Limited animation support (can be worked around with CSS)
- Styling can be tricky across browsers

**Example:**
```html
<details class="group">
    <summary class="cursor-pointer p-4 flex justify-between items-center">
        <span>Question text</span>
        <svg class="transform group-open:rotate-180 transition-transform">...</svg>
    </summary>
    <div class="p-4 pt-0">
        <p>Answer text</p>
    </div>
</details>
```

### JavaScript Accordion
**Pros:**
- Full control over animations
- Single-open behavior easier to implement
- More styling flexibility

**Cons:**
- Requires JavaScript
- Must implement accessibility manually

### Recommendation: **Native `<details>` with CSS enhancements**
Aligns with NFR-H04 (graceful degradation without JS) and reduces complexity.

---

## 3. Hash-Based Routing

### Implementation Pattern
```javascript
// Check hash on load and changes
function handleHashChange() {
    const hash = window.location.hash;
    if (hash === '#help') {
        showHelpView();
    } else {
        showWeatherView();
    }
}

window.addEventListener('hashchange', handleHashChange);
document.addEventListener('DOMContentLoaded', handleHashChange);
```

### Benefits:
- Bookmarkable URLs (`/index.html#help`)
- Browser back/forward navigation works
- No server-side changes required
- Maintains SPA experience

---

## 4. Accessibility Requirements

### ARIA for Accordions (with `<details>`)
The `<details>` element is inherently accessible, but enhancements:

```html
<details>
    <summary role="button" aria-expanded="false">
        Question
    </summary>
    <div role="region" aria-labelledby="summary-id">
        Answer
    </div>
</details>
```

### Keyboard Navigation
- `<details>` supports Enter/Space to toggle
- Tab navigation moves between items
- No additional JS needed

### Screen Reader Considerations
- Use descriptive summary text
- Answers should be in logical reading order
- Category headings use proper heading levels

---

## 5. Tailwind CSS Patterns for FAQ

### Accordion Card Styling
```html
<details class="bg-white rounded-lg shadow-sm border border-gray-200 mb-2 group">
    <summary class="p-4 cursor-pointer list-none flex justify-between items-center
                    hover:bg-gray-50 transition-colors focus:outline-none 
                    focus:ring-2 focus:ring-blue-500 focus:ring-inset rounded-lg">
        <span class="font-medium text-gray-800">Question?</span>
        <svg class="w-5 h-5 text-gray-500 transform transition-transform duration-200 
                    group-open:rotate-180">
            <!-- Chevron icon -->
        </svg>
    </summary>
    <div class="px-4 pb-4 text-gray-600">
        Answer content here.
    </div>
</details>
```

### Removing Default Summary Marker
```css
/* Hide the default disclosure triangle */
details summary::-webkit-details-marker {
    display: none;
}
details summary {
    list-style: none;
}
```

---

## 6. Quick Tips Component

### Card-Based Layout
```html
<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
    <div class="bg-blue-50 rounded-xl p-4 text-center">
        <i class="wi wi-day-sunny text-3xl text-blue-500 mb-2"></i>
        <h3 class="font-medium text-gray-800">Search Any City</h3>
        <p class="text-sm text-gray-600">Enter a city name to get weather</p>
    </div>
    <!-- More tips... -->
</div>
```

---

## 7. View Switching Strategy

### HTML Structure
```html
<body>
    <div id="weather-view">
        <!-- Existing weather app content -->
    </div>
    
    <div id="help-view" class="hidden">
        <!-- Help page content -->
    </div>
</body>
```

### JavaScript Toggle
```javascript
function showWeatherView() {
    document.getElementById('weather-view').classList.remove('hidden');
    document.getElementById('help-view').classList.add('hidden');
}

function showHelpView() {
    document.getElementById('weather-view').classList.add('hidden');
    document.getElementById('help-view').classList.remove('hidden');
}
```

---

## 8. Browser Compatibility

### `<details>` Element Support
- ✅ Chrome 12+
- ✅ Firefox 49+
- ✅ Safari 6+
- ✅ Edge 79+
- ⚠️ IE11: Not supported (graceful degradation shows content expanded)

### Tailwind `group-open` Variant
- Uses the CSS `:open` pseudo-class
- Supported in same browsers as `<details>`

---

## 9. Performance Considerations

### No Additional Dependencies
- Use existing Tailwind CSS (already loaded)
- Use existing Weather Icons (already loaded)
- No new libraries needed

### Minimal DOM Impact
- Help view content is static HTML
- No API calls required
- Instant view switching

### Lazy Rendering (Optional)
If help content is large, could defer rendering until first view, but likely unnecessary for FAQ size.

---

## 10. Decisions Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| View architecture | Hash routing in SPA | Maintains existing architecture, bookmarkable |
| Accordion component | Native `<details>` | Accessible, no JS required, graceful degradation |
| Styling | Tailwind utilities | Consistent with existing codebase |
| Animation | CSS transitions | Simple, performant |
| Help button location | Header, after unit toggle | Visible but not intrusive |
