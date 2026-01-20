# Data Model: Help & FAQ Page

> **Spec:** 003-help-faq-page  
> **Date:** 2026-01-20

---

## 1. Overview

The Help & FAQ page is a **static content feature** that doesn't require backend APIs or persistent data storage. All data structures are client-side JavaScript objects used to render the FAQ content.

---

## 2. FAQ Data Structure

### FAQ Item
```javascript
/**
 * @typedef {Object} FAQItem
 * @property {string} id - Unique identifier for the FAQ item
 * @property {string} question - The question text
 * @property {string} answer - The answer text (can include HTML)
 */

// Example:
{
    id: 'search-weather',
    question: 'How do I search for weather?',
    answer: 'Enter a city name in the search box and press Enter or click the search button.'
}
```

### FAQ Category
```javascript
/**
 * @typedef {Object} FAQCategory
 * @property {string} id - Unique identifier for the category
 * @property {string} title - Display title for the category
 * @property {string} icon - Emoji or icon class for visual representation
 * @property {FAQItem[]} items - Array of FAQ items in this category
 */

// Example:
{
    id: 'getting-started',
    title: 'Getting Started',
    icon: '🚀',
    items: [
        { id: 'search-weather', question: '...', answer: '...' },
        { id: 'change-units', question: '...', answer: '...' }
    ]
}
```

---

## 3. Quick Tips Data Structure

### Tip Item
```javascript
/**
 * @typedef {Object} TipItem
 * @property {string} id - Unique identifier
 * @property {string} title - Short title for the tip
 * @property {string} description - Brief description
 * @property {string} icon - Weather icon class or emoji
 * @property {string} iconColor - Tailwind color class for icon
 */

// Example:
{
    id: 'tip-search',
    title: 'Search Any City',
    description: 'Enter a city name to get current weather conditions',
    icon: 'wi wi-day-cloudy',
    iconColor: 'text-blue-500'
}
```

---

## 4. Complete FAQ Data Object

```javascript
const FAQ_DATA = {
    categories: [
        {
            id: 'getting-started',
            title: 'Getting Started',
            icon: '🚀',
            items: [
                {
                    id: 'gs-search',
                    question: 'How do I search for weather?',
                    answer: 'Enter a city name in the search box and press Enter or click the search button. The app will display current weather conditions for that location.'
                },
                {
                    id: 'gs-units',
                    question: 'How do I change temperature units?',
                    answer: 'Use the °C/°F toggle buttons at the top of the app. Your preference is saved automatically.'
                },
                {
                    id: 'gs-cities',
                    question: 'What cities can I search for?',
                    answer: 'You can search for any city worldwide. Try entering the city name, or for more accuracy, include the country (e.g., "London, UK" or "Paris, France").'
                }
            ]
        },
        {
            id: 'weather-data',
            title: 'Weather Data',
            icon: '☁️',
            items: [
                {
                    id: 'wd-source',
                    question: 'Where does the weather data come from?',
                    answer: 'Our weather data is provided by OpenWeatherMap, a trusted weather data provider used by millions of applications worldwide.'
                },
                {
                    id: 'wd-update',
                    question: 'How often is the weather data updated?',
                    answer: 'Weather data is fetched in real-time when you search. The data from our provider is typically updated every 10-15 minutes.'
                },
                {
                    id: 'wd-feelslike',
                    question: 'What does "Feels like" temperature mean?',
                    answer: '"Feels like" is the apparent temperature that accounts for wind chill and humidity, representing how the temperature actually feels to a person.'
                }
            ]
        },
        {
            id: 'troubleshooting',
            title: 'Troubleshooting',
            icon: '🔧',
            items: [
                {
                    id: 'ts-notfound',
                    question: "Why can't I find my city?",
                    answer: 'Try checking the spelling or adding the country name. Some smaller towns may not be in the database. Try a nearby larger city instead.'
                },
                {
                    id: 'ts-error',
                    question: 'Why am I seeing an error message?',
                    answer: 'This usually means the weather service is temporarily unavailable. Please try again in a few moments. If the problem persists, check your internet connection.'
                },
                {
                    id: 'ts-wrong',
                    question: 'The temperature seems wrong. What should I do?',
                    answer: 'Ensure you have the correct unit selected (°C or °F). Weather stations may occasionally report unusual readings; try refreshing after a few minutes.'
                }
            ]
        },
        {
            id: 'privacy',
            title: 'Privacy & Data',
            icon: '🔒',
            items: [
                {
                    id: 'pv-location',
                    question: 'Does the app track my location?',
                    answer: 'No, the app does not access your device location. You manually enter the city you want to check.'
                },
                {
                    id: 'pv-storage',
                    question: 'What data is stored on my device?',
                    answer: 'Only your temperature unit preference (Celsius or Fahrenheit) is stored locally in your browser. No personal data is collected or stored.'
                }
            ]
        }
    ]
};
```

---

## 5. Quick Tips Data Object

```javascript
const QUICK_TIPS = [
    {
        id: 'tip-search',
        title: 'Search Any City',
        description: 'Enter a city name to get current weather',
        icon: 'wi wi-day-cloudy',
        iconColor: 'text-blue-500'
    },
    {
        id: 'tip-units',
        title: 'Toggle Units',
        description: 'Switch between °C and °F anytime',
        icon: 'wi wi-thermometer',
        iconColor: 'text-red-400'
    },
    {
        id: 'tip-accuracy',
        title: 'Be Specific',
        description: 'Add country for better accuracy',
        icon: 'wi wi-stars',
        iconColor: 'text-yellow-500'
    }
];
```

---

## 6. Application State Extension

### Current State Object
```javascript
const state = {
    city: '',
    weather: null,
    units: 'metric',
    loading: false,
    error: null
};
```

### Extended State for Help View
```javascript
const state = {
    // Existing properties
    city: '',
    weather: null,
    units: 'metric',
    loading: false,
    error: null,
    
    // New property for view management
    currentView: 'weather'  // 'weather' | 'help'
};
```

---

## 7. DOM Element References (New)

```javascript
// Add to elements object
const elements = {
    // ... existing elements
    
    // Views
    weatherView: document.getElementById('weather-view'),
    helpView: document.getElementById('help-view'),
    
    // Help navigation
    helpButton: document.getElementById('help-btn'),
    backToWeatherBtn: document.getElementById('back-to-weather-btn')
};
```

---

## 8. No Backend Changes Required

This feature is entirely client-side:
- ❌ No new API endpoints
- ❌ No database tables
- ❌ No server-side rendering
- ✅ Static HTML/CSS/JS only

---

## 9. Entity Relationship (Conceptual)

```
┌─────────────────┐
│   FAQ_DATA      │
├─────────────────┤
│ categories[]    │
└────────┬────────┘
         │ contains
         ▼
┌─────────────────┐
│  FAQCategory    │
├─────────────────┤
│ id              │
│ title           │
│ icon            │
│ items[]         │
└────────┬────────┘
         │ contains
         ▼
┌─────────────────┐
│   FAQItem       │
├─────────────────┤
│ id              │
│ question        │
│ answer          │
└─────────────────┘

┌─────────────────┐
│  QUICK_TIPS[]   │
├─────────────────┤
│ TipItem         │
│ TipItem         │
│ TipItem         │
└─────────────────┘
```

---

## 10. Data Rendering Functions

```javascript
/**
 * Render a single FAQ item as a details/summary element
 * @param {FAQItem} item
 * @returns {string} HTML string
 */
function renderFAQItem(item) {
    return `
        <details class="bg-white rounded-lg border border-gray-200 mb-2 group">
            <summary class="p-4 cursor-pointer list-none flex justify-between items-center">
                <span class="font-medium text-gray-800">${item.question}</span>
                <!-- Chevron icon -->
            </summary>
            <div class="px-4 pb-4 text-gray-600">
                ${item.answer}
            </div>
        </details>
    `;
}

/**
 * Render a FAQ category with all its items
 * @param {FAQCategory} category
 * @returns {string} HTML string
 */
function renderFAQCategory(category) {
    const itemsHtml = category.items.map(renderFAQItem).join('');
    return `
        <div class="mb-6">
            <h3 class="text-lg font-semibold text-gray-800 mb-3">
                ${category.icon} ${category.title}
            </h3>
            ${itemsHtml}
        </div>
    `;
}

/**
 * Render a quick tip card
 * @param {TipItem} tip
 * @returns {string} HTML string
 */
function renderTip(tip) {
    return `
        <div class="bg-blue-50 rounded-xl p-4 text-center">
            <i class="${tip.icon} ${tip.iconColor} text-3xl mb-2"></i>
            <h3 class="font-medium text-gray-800">${tip.title}</h3>
            <p class="text-sm text-gray-600">${tip.description}</p>
        </div>
    `;
}
```
