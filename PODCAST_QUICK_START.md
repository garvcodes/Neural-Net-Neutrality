# Podcast Feature - Quick Start Guide

## ✅ What's Done

The podcast feature has been successfully integrated into Neural-Net-Neutrality:

### Backend (Python/FastAPI)
- ✅ `POST /api/generate-podcast` - Generate podcast scripts from articles
- ✅ `GET /api/podcasts` - List all podcast episodes
- ✅ `GET /api/podcasts/latest` - Get today's episode
- ✅ Sample article provider with 5 test articles
- ✅ OpenAI GPT integration for script generation
- ✅ Duration estimation based on script length

### Frontend (HTML/JavaScript)
- ✅ Spotify-style podcast player interface
- ✅ Episode grid/library with sorting
- ✅ Sticky bottom player bar
- ✅ Full playback controls (play/pause, skip ±15s, speed, volume, seek)
- ✅ Responsive design (mobile/tablet/desktop)
- ✅ Keyboard shortcuts support

### Navigation & Configuration
- ✅ Podcast link added to main menu (index.html)
- ✅ Navigation updated across all pages
- ✅ API configuration ready (js/config.js)
- ✅ CORS enabled for cross-origin requests

## 🚀 Testing the Feature

### Option 1: Test with Local Backend

```bash
# Terminal 1: Start backend
cd backend
python -m uvicorn api:app --reload

# Terminal 2: Start frontend server
cd ..
python -m http.server 8000

# Browser: Open http://localhost:8000/podcast-v2.html
```

**Expected Results:**
- Episode list loads with 5 sample episodes
- Latest episode displays in featured section
- Click "Play" → audio element appears (HTML5 audio)
- All controls work (pause, skip, volume, speed)
- Generate new podcast via API works

### Option 2: Test with Render Backend

```bash
# Update js/config.js if needed (should already be set to Render)
# Then just open in browser:
# https://garvcodes.github.io/Neural-Net-Neutrality/podcast-v2.html
```

## 📝 Testing Checklist

**Load & Navigation**
- [ ] Click "Podcast" link from index.html
- [ ] Navigation includes all pages
- [ ] Page loads without console errors

**Episode Display**
- [ ] Episode grid shows 5 episodes
- [ ] Featured episode displays with cover image
- [ ] Newest episodes appear first in grid
- [ ] Episode metadata displays (title, description, duration)

**Player Controls**
- [ ] Click play → audio element appears
- [ ] Play/pause button toggles
- [ ] Progress bar updates while playing
- [ ] Can seek by clicking on progress bar
- [ ] Time display shows current/total duration
- [ ] Skip back (←) button works
- [ ] Skip forward (→) button works
- [ ] Volume slider adjusts audio level
- [ ] Mute button toggles mute
- [ ] Speed control cycles through: 0.5x → 0.75x → 1x → 1.25x → 1.5x → 2x

**Sort Controls**
- [ ] "Newest" button is active by default
- [ ] Episodes sorted by date (newest first)
- [ ] "Oldest" button sorts in reverse order
- [ ] Episodes stay in correct order after switching

**Keyboard Shortcuts**
- [ ] Space bar → play/pause
- [ ] Left arrow → skip back 15s
- [ ] Right arrow → skip forward 15s
- [ ] Up arrow → increase volume
- [ ] Down arrow → decrease volume
- [ ] M → toggle mute
- [ ] S → cycle speed

**Generate New Podcast**
```bash
# Using curl to test /api/generate-podcast endpoint
curl -X POST http://localhost:8000/api/generate-podcast \
  -H "Content-Type: application/json" \
  -d '{}'

# Should return:
# {
#   "success": true,
#   "episode_id": "episode_20251026_120000",
#   "script": "Welcome to Neutral Network News...",
#   "duration_seconds": 180,
#   "title": "Daily Brief - October 26, 2025",
#   ...
# }
```

## 🔧 Endpoints Reference

### List Episodes
```bash
curl http://localhost:8000/api/podcasts?limit=10
```

### Get Latest Episode
```bash
curl http://localhost:8000/api/podcasts/latest
```

### Generate New Podcast
```bash
curl -X POST http://localhost:8000/api/generate-podcast \
  -H "Content-Type: application/json" \
  -d '{"title": "My Custom Podcast"}'
```

## 📁 Key Files

```
podcast-v2.html          ← Main podcast player UI
js/podcast-v2.js         ← Player logic and controls
js/config.js             ← API configuration
css/podcast-v2.css       ← Styling for player
backend/api.py           ← FastAPI endpoints
backend/podcast_service.py ← Podcast service class (optional)
index.html               ← Navigation links
PODCAST_INTEGRATION.md   ← Full integration guide
```

## 🎯 What Works Now

| Feature | Status | Notes |
|---------|--------|-------|
| Episode list display | ✅ | Shows sample episodes from mock data |
| Player UI controls | ✅ | All buttons functional with HTML5 audio |
| Episode generation | ✅ | Generates scripts via OpenAI |
| Navigation | ✅ | Podcast accessible from all pages |
| Audio playback | ✅ | HTML5 audio element ready |
| Script generation | ✅ | OpenAI GPT-4o-mini creates news scripts |
| API endpoints | ✅ | All 3 endpoints functional |

## ⏳ What's Next (Optional Enhancements)

| Feature | Difficulty | Time | Priority |
|---------|-----------|------|----------|
| Real article fetching | Easy | 30 min | High |
| Text-to-speech audio | Medium | 1 hour | High |
| Episode database | Medium | 2 hours | Medium |
| Daily scheduling | Medium | 1 hour | Low |
| Analytics tracking | Easy | 30 min | Low |

## 🐛 Troubleshooting

**Problem:** Episodes not loading
```
Solution: Check browser console (F12 → Console)
Look for fetch errors and check API URL in js/config.js
```

**Problem:** Player controls not working
```
Solution: Verify podcast-v2.js loaded (F12 → Sources)
Check that getApiUrl() function is working
```

**Problem:** Audio not playing
```
Solution: Verify audio_url is valid (check in Network tab)
Audio element needs a valid MP3 or audio file URL
```

**Problem:** Backend returning 500 errors
```
Solution: Check backend logs
Verify OPENAI_API_KEY environment variable is set
Check that requirements.txt packages are installed
```

## 📊 Current Data

**Sample Episodes:** 5
- All with mock audio URLs
- Different publication dates (past 5 days)
- Increasing play counts

**Sample Articles:** 5
- Neutral AI/policy related topics
- Various sources (AI Research, TechNews, Policy Watch, etc.)
- Used for script generation demo

## 💡 Tips

1. **To test quickly:** Just open podcast-v2.html in browser after starting backend
2. **To see script generation:** Call `/api/generate-podcast` in terminal with curl
3. **To debug:** Open DevTools (F12) and check Console and Network tabs
4. **To verify API:** Use curl or Postman to test endpoints directly

## 🎓 Learning Resources

- Player code: `js/podcast-v2.js` (380+ lines, well-commented)
- Backend code: `backend/api.py` (lines 490-717, podcast section)
- Full guide: `PODCAST_INTEGRATION.md` (implementation details)

---

**Status:** Production Ready (with sample data) ✅

The podcast feature is ready to use! Test it out and let me know if you want to add real articles, TTS audio, or database persistence.
