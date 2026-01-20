# Quickstart Guide: Help & FAQ Page

> **Spec:** 003-help-faq-page  
> **Date:** 2026-01-20

---

## 1. What You're Building

A **Help & FAQ page** for the Weather App frontend that provides:
- Quick tips section for first-time users
- Collapsible FAQ accordion organized by category
- Navigation between the weather view and help view
- Responsive design matching the existing app

---

## 2. Prerequisites

### Required
- ✅ Working Weather App (backend + frontend)
- ✅ Code editor (VS Code recommended)
- ✅ Modern web browser for testing

### Knowledge
- HTML/CSS (Tailwind CSS basics)
- Vanilla JavaScript
- Understanding of the existing `index.html` structure

---

## 3. Project Location

```
WeatherApp/weatherapp/
├── static/
│   └── index.html    ← Primary file to modify
├── main.py           ← No changes needed
└── specs/
    └── 003-help-faq-page/
```

---

## 4. Quick Orientation

### Current Architecture (index.html)

```html
<!-- Header with title, unit toggle -->
<header>...</header>

<!-- Main content -->
<main>
    <!-- Search bar -->
    <div id="search-container">...</div>
    
    <!-- Content states (shown/hidden) -->
    <div id="welcome-message">...</div>
    <div id="loading">...</div>
    <div id="error-container">...</div>
    <div id="weather-card">...</div>
</main>

<!-- Footer -->
<footer>...</footer>
```

### State Management Pattern
```javascript
const state = {
    city: '',
    weather: null,
    units: 'metric',
    loading: false,
    error: null
};

// Content switching
function hideAllContent() { /* hides all states */ }
function showWelcome() { hideAllContent(); elements.welcomeMessage.classList.remove('hidden'); }
function showWeatherCard() { hideAllContent(); elements.weatherCard.classList.remove('hidden'); }
```

---

## 5. Implementation Overview

### Step 1: Add Help Button to Header
```html
<!-- Add to header, near unit toggle -->
<button id="help-btn" class="...">
    <i class="wi wi-info"></i> Help
</button>
```

### Step 2: Create Help View Container
```html
<!-- Add after weather-card -->
<div id="help-view" class="hidden max-w-2xl mx-auto p-4">
    <!-- Back navigation -->
    <button id="back-to-weather-btn">← Back to Weather</button>
    
    <!-- Quick Tips Section -->
    <section id="quick-tips">...</section>
    
    <!-- FAQ Accordion -->
    <section id="faq-section">
        <details>
            <summary>Question here?</summary>
            <p>Answer here.</p>
        </details>
    </section>
</div>
```

### Step 3: Add View Navigation Functions
```javascript
function showHelpView() {
    hideAllContent();
    elements.helpView.classList.remove('hidden');
    elements.searchContainer.classList.add('hidden');
    state.currentView = 'help';
    window.location.hash = 'help';
}

function hideHelpView() {
    elements.helpView.classList.add('hidden');
    elements.searchContainer.classList.remove('hidden');
    state.currentView = 'weather';
    window.location.hash = '';
    showWelcome(); // Or restore previous state
}
```

### Step 4: Wire Up Event Listeners
```javascript
elements.helpButton.addEventListener('click', showHelpView);
elements.backToWeatherBtn.addEventListener('click', hideHelpView);

// Handle hash routing
window.addEventListener('hashchange', () => {
    if (window.location.hash === '#help') {
        showHelpView();
    } else {
        hideHelpView();
    }
});
```

---

## 6. FAQ Accordion Pattern

Using native `<details>` with Tailwind styling:

```html
<details class="bg-white rounded-lg border border-gray-200 mb-2 group">
    <summary class="p-4 cursor-pointer list-none flex justify-between items-center hover:bg-gray-50">
        <span class="font-medium text-gray-800">How do I search for weather?</span>
        <svg class="w-5 h-5 transition-transform group-open:rotate-180">
            <!-- Chevron icon -->
        </svg>
    </summary>
    <div class="px-4 pb-4 text-gray-600">
        Enter a city name in the search box and press Enter or click the search button.
    </div>
</details>
```

---

## 7. Testing Checklist

### Functional Tests
- [ ] Help button opens help view
- [ ] Back button returns to weather view
- [ ] All FAQ items expand/collapse
- [ ] URL hash changes when navigating
- [ ] Direct navigation to `#help` works

### Visual Tests
- [ ] Consistent styling with weather app
- [ ] Responsive on mobile devices
- [ ] Hover states on interactive elements
- [ ] Smooth accordion transitions

### Accessibility Tests
- [ ] Keyboard navigation works
- [ ] ARIA labels present
- [ ] Focus visible on all interactive elements

---

## 8. Common Patterns

### Adding a New FAQ Item
```javascript
// Add to the appropriate category in FAQ_DATA
{
    id: 'new-question-id',
    question: 'Your new question here?',
    answer: 'Your detailed answer here.'
}
```

### Adding a New Category
```javascript
{
    id: 'new-category',
    title: 'New Category',
    icon: '📌',
    items: [
        { id: 'q1', question: '...', answer: '...' }
    ]
}
```

### Styling Quick Tip Cards
```html
<div class="bg-blue-50 rounded-xl p-4 text-center">
    <i class="wi wi-day-sunny text-yellow-500 text-3xl mb-2"></i>
    <h3 class="font-medium text-gray-800">Tip Title</h3>
    <p class="text-sm text-gray-600">Brief description</p>
</div>
```

---

## 9. Files Changed Summary

| File | Action | Description |
|------|--------|-------------|
| `static/index.html` | **Modified** | Add help button, help view section, navigation JS |

---

## 10. Local Development

### Start the Server
```bash
cd weatherapp
python main.py
# or: uvicorn main:app --reload
```

### Open in Browser
```
http://127.0.0.1:8000
http://127.0.0.1:8000/#help  (direct to help page)
```

### Hot Reload
Since the frontend is static HTML, simply refresh the browser after making changes to `index.html`.

---

## 11. Success Criteria

✅ Help button visible in header  
✅ Clicking opens help view with FAQ content  
✅ FAQ items expand/collapse smoothly  
✅ Back button returns to weather search  
✅ Mobile-responsive layout  
✅ URL updates with hash for bookmarking
