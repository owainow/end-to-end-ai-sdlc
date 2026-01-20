# Quickstart: Weather Frontend

> **Spec:** 002-weather-frontend  
> **Created:** 2026-01-20

---

## Prerequisites

- Weather API running (from spec 001)
- Modern web browser (Chrome, Firefox, Safari, Edge)
- No additional tools required (no Node.js, no build step)

---

## Quick Setup

### 1. Verify API is Running

```bash
# Start the API (if not already running)
cd weatherapp
python -m uvicorn src.main:get_app --factory --reload
```

Test the API:
```bash
curl "http://localhost:8000/api/v1/weather?city=London&units=metric"
```

### 2. Create Static Directory

```bash
mkdir -p static
```

### 3. Create Frontend File

Create `static/index.html` with the frontend code (see implementation tasks).

### 4. Update FastAPI to Serve Static Files

Add to `src/main.py`:
```python
from fastapi.staticfiles import StaticFiles

# After creating app, mount static files
app.mount("/", StaticFiles(directory="static", html=True), name="static")
```

### 5. Access the Frontend

Open browser to: `http://localhost:8000/`

---

## Development Workflow

### Making Changes

1. Edit `static/index.html`
2. Refresh browser (no build step needed)
3. Check browser DevTools console for errors

### Testing API Integration

1. Open browser DevTools → Network tab
2. Search for a city
3. Verify API request goes to `/api/v1/weather`
4. Check response data

### Testing Responsive Design

1. Open browser DevTools
2. Toggle device toolbar (Ctrl+Shift+M / Cmd+Shift+M)
3. Test at various breakpoints:
   - 320px (mobile)
   - 768px (tablet)
   - 1024px (laptop)
   - 1440px (desktop)

---

## CDN Dependencies

The frontend loads these from CDN (no local installation):

| Library | CDN URL |
|---------|---------|
| Tailwind CSS | `https://cdn.tailwindcss.com` |
| Weather Icons | `https://cdnjs.cloudflare.com/ajax/libs/weather-icons/2.0.12/css/weather-icons.min.css` |

---

## File Structure

```
weatherapp/
├── src/                    # Backend (existing)
├── static/                 # Frontend (new)
│   └── index.html         # Single-file frontend
├── tests/                  # Backend tests
└── specs/
    ├── 001-realtime-city-weather/
    └── 002-weather-frontend/
```

---

## Troubleshooting

### Frontend not loading
- Ensure FastAPI has `StaticFiles` mount
- Check that `static/index.html` exists
- Verify server is running on port 8000

### API requests failing
- Check browser console for CORS errors (shouldn't happen with same-origin)
- Verify API is running: `curl http://localhost:8000/health`
- Check Network tab for actual error response

### Styles not applying
- Ensure Tailwind CDN script is loading
- Check browser console for script errors
- Verify internet connection (CDN requires network)

### Weather icons not showing
- Verify Weather Icons CSS is loading
- Check icon class names match Weather Icons documentation
- Inspect element to see if icon font is applied

---

## Next Steps After Setup

1. **Manual Testing:** Run through test checklist in spec.md
2. **Browser Testing:** Test in Chrome, Firefox, Safari, Edge
3. **Mobile Testing:** Use device emulation or real devices
4. **Accessibility Testing:** Use browser accessibility tools
