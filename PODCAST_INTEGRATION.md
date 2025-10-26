# Podcast Integration Guide

## Overview

The podcast feature has been successfully integrated into the Neural-Net-Neutrality application. The system generates neutral news briefs using AI and can convert them to audio format.

## Architecture

### Components

```
Frontend (podcast-v2.html)
    ↓
JavaScript Logic (js/podcast-v2.js)
    ↓
API Configuration (js/config.js)
    ↓
Backend FastAPI (backend/api.py)
    ├── /api/podcasts → List episodes
    ├── /api/podcasts/latest → Get today's episode
    └── /api/generate-podcast → Generate new episode
    ↓
Podcast Service (backend/podcast_service.py) [OPTIONAL]
    ↓
External Services:
    ├── OpenAI GPT (script generation) ✅ Integrated
    ├── ElevenLabs (text-to-speech) ⏳ Ready to integrate
    └── Cloud Storage (audio files) ⏳ Ready to integrate
```

## Current Status

### ✅ Completed

1. **Backend Endpoints** (backend/api.py)
   - `POST /api/generate-podcast` - Generates podcast script from articles
   - `GET /api/podcasts` - Returns list of podcast episodes
   - `GET /api/podcasts/latest` - Returns today's episode
   - All endpoints return mock data for testing

2. **Frontend UI** (podcast-v2.html + js/podcast-v2.js)
   - Complete Spotify-style podcast player interface
   - Episode grid/library display
   - Sticky bottom player bar with all controls
   - Play/pause, skip ±15s, volume, speed (0.5x-2x), progress seeking
   - Responsive design for mobile/tablet/desktop
   - Keyboard shortcuts support

3. **Navigation Integration**
   - Podcast link added to index.html main menu
   - Podcast link added to podcast-v2.html navigation
   - All pages now include podcast in navigation

4. **Configuration**
   - API configuration in js/config.js
   - Backend URL configured for Render deployment
   - CORS enabled for cross-origin requests

5. **Sample Data**
   - 5 sample articles in `get_sample_articles()` function
   - 5+ sample episodes in mock episode list
   - Ready for testing without external APIs

### 🔄 Ready to Implement

1. **Real Article Sources**
   - Replace `get_sample_articles()` with real API calls
   - Options: NewsAPI, Guardian API, NY Times API
   - Fetch AI/politics related articles

2. **Text-to-Speech Audio Generation**
   - ElevenLabs API integration (requires API key)
   - Generate professional news anchor voice
   - Store audio files in cloud storage
   - Update audio_url in response

3. **Audio File Storage**
   - AWS S3, Google Cloud Storage, or similar
   - Store generated MP3 files
   - Return signed URLs for playback
   - Implement cleanup/archiving strategy

4. **Episode Persistence**
   - Create `podcast_episodes` table in Supabase
   - Store episode metadata and audio URL
   - Track play counts and engagement
   - Avoid regenerating same episode

5. **Scheduled Generation**
   - Implement daily cron job or scheduled task
   - Generate episode daily at specified time
   - Fetch latest articles and create podcast
   - Store in database

## API Endpoints

### POST /api/generate-podcast

Generate a podcast episode from articles.

**Request:**
```json
{
  "articles": [
    {
      "id": 1,
      "title": "Article Title",
      "content": "Article content...",
      "summary": "Brief summary",
      "source": "Source Name",
      "url": "https://example.com",
      "published_at": "2025-01-01T00:00:00"
    }
  ],
  "title": "Daily Brief - January 1, 2025",
  "model": "gpt-4o-mini",
  "voice": "news_anchor"
}
```

**Response:**
```json
{
  "success": true,
  "episode_id": "episode_20250101_120000",
  "script": "Welcome to Neutral Network News...",
  "duration_seconds": 180,
  "title": "Daily Brief - January 1, 2025",
  "articles": [...],
  "metadata": {
    "generated_at": "2025-01-01T12:00:00",
    "model": "gpt-4o-mini",
    "voice": "news_anchor",
    "articles_count": 5,
    "word_count": 850
  }
}
```

### GET /api/podcasts

Get list of podcast episodes.

**Query Parameters:**
- `limit` (optional, default 10): Number of episodes to return

**Response:**
```json
{
  "episodes": [
    {
      "id": "episode_1",
      "title": "Daily Brief - January 1, 2025",
      "description": "Your daily AI-generated neutral news podcast",
      "publication_date": "2025-01-01",
      "audio_url": "https://storage.example.com/podcast_1.mp3",
      "duration_seconds": 180,
      "cover_image_url": "https://example.com/cover.jpg",
      "play_count": 5
    }
  ],
  "count": 1,
  "total_available": 10
}
```

### GET /api/podcasts/latest

Get today's podcast episode.

**Response:**
```json
{
  "episode": {
    "id": "episode_latest",
    "title": "Daily Brief - January 1, 2025",
    "description": "Your daily AI-generated neutral news podcast",
    "publication_date": "2025-01-01",
    "audio_url": "https://storage.example.com/podcast_latest.mp3",
    "duration_seconds": 180,
    "cover_image_url": "https://example.com/cover.jpg",
    "play_count": 42
  },
  "found": true
}
```

## Frontend Features

### Podcast Player Controls

- **Play/Pause** - Start/stop playback
- **Skip Back/Forward** - Jump ±15 seconds
- **Progress Bar** - Seek to any position
- **Speed Control** - Adjust playback speed (0.5x to 2x)
- **Volume Control** - Adjust volume with mute option
- **Time Display** - Current time and total duration
- **Sort Controls** - Sort episodes by date (newest/oldest)

### Keyboard Shortcuts

- **Space** - Play/pause
- **Left Arrow** - Skip back 15s
- **Right Arrow** - Skip forward 15s
- **Up Arrow** - Increase volume
- **Down Arrow** - Decrease volume
- **M** - Mute/unmute
- **S** - Toggle speed
- **1-6** - Set speed (1x = 1x, 2 = 1.5x, etc.)

## Implementation Guide

### Phase 1: Testing Current Implementation

```bash
# 1. Start the backend server
cd backend
python -m uvicorn api:app --reload

# 2. In another terminal, start a simple HTTP server for frontend
cd ..
python -m http.server 8000

# 3. Open browser
# http://localhost:8000/podcast-v2.html

# 4. Test features
# - Page should load and display sample episodes
# - Click play on an episode
# - Test player controls (pause, skip, volume, speed)
# - Generate new podcast via API
```

### Phase 2: Add Real Articles

```python
# backend/api.py - replace get_sample_articles()

# Option 1: NewsAPI (Free tier available)
# https://newsapi.org/

def get_real_articles() -> List[Dict]:
    import requests
    
    api_key = os.getenv("NEWSAPI_KEY")
    if not api_key:
        return get_sample_articles()  # Fallback
    
    response = requests.get(
        "https://newsapi.org/v2/everything",
        params={
            "q": "artificial intelligence",
            "sortBy": "publishedAt",
            "language": "en",
            "apiKey": api_key
        }
    )
    
    if response.status_code != 200:
        return get_sample_articles()
    
    articles = []
    for item in response.json()["articles"][:5]:
        articles.append({
            "id": item["url"],
            "title": item["title"],
            "content": item["content"] or item["description"],
            "summary": item["description"],
            "source": item["source"]["name"],
            "url": item["url"],
            "published_at": item["publishedAt"]
        })
    
    return articles
```

### Phase 3: Add Text-to-Speech

```python
# backend/api.py - add TTS to /api/generate-podcast

async def generate_podcast_with_audio(req: GeneratePodcastRequest):
    # ... [existing script generation code] ...
    
    # Add TTS generation
    script = response.choices[0].message.content
    
    # Generate audio using ElevenLabs
    audio_url = await generate_audio_from_script(script, voice=req.voice)
    
    response_data = {
        "script": script,
        "audio_url": audio_url,  # Real URL instead of mock
        # ... rest of response
    }
    
    return response_data

async def generate_audio_from_script(script: str, voice: str = "news_anchor") -> str:
    """Convert script to audio using ElevenLabs"""
    import httpx
    
    api_key = os.getenv("ELEVENLABS_API_KEY")
    voice_id = "news_anchor_voice_id"  # Map voice name to ID
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
            headers={"xi-api-key": api_key},
            json={
                "text": script,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75
                }
            }
        )
        
        if response.status_code != 200:
            raise Exception(f"ElevenLabs error: {response.text}")
        
        # Save audio file
        audio_file_path = await save_audio_file(response.content)
        
        # Upload to cloud storage and get URL
        audio_url = await upload_to_storage(audio_file_path)
        
        return audio_url
```

### Phase 4: Add Database Persistence

```python
# backend/supabase_db.py - add new functions

async def store_podcast_episode(episode: Dict) -> str:
    """Store generated episode in database"""
    result = supabase.table("podcast_episodes").insert({
        "episode_id": episode["episode_id"],
        "title": episode["title"],
        "description": episode["description"],
        "script": episode["script"],
        "audio_url": episode["audio_url"],
        "duration_seconds": episode["duration_seconds"],
        "publication_date": episode["publication_date"],
        "articles_count": len(episode["articles"]),
        "articles": json.dumps(episode["articles"]),
        "created_at": datetime.now().isoformat()
    }).execute()
    
    return result.data[0]["id"]

async def get_podcast_episodes(limit: int = 10) -> List[Dict]:
    """Retrieve episodes from database"""
    result = supabase.table("podcast_episodes")\
        .select("*")\
        .order("publication_date", desc=True)\
        .limit(limit)\
        .execute()
    
    return result.data

async def increment_play_count(episode_id: str) -> None:
    """Track episode plays"""
    supabase.table("podcast_episodes")\
        .update({"play_count": f"play_count + 1"})\
        .eq("episode_id", episode_id)\
        .execute()
```

### Phase 5: Schedule Daily Generation

```python
# tools/daily_podcast_generator.py

from apscheduler.schedulers.background import BackgroundScheduler
import asyncio

def generate_daily_podcast():
    """Generate podcast at specified time each day"""
    
    # Get latest articles
    articles = get_real_articles()
    
    if not articles:
        print("No articles available for podcast")
        return
    
    # Generate script
    script = generate_script(articles)
    
    # Generate audio
    audio_url = generate_audio_from_script(script)
    
    # Store in database
    episode = {
        "episode_id": f"episode_{datetime.now().strftime('%Y%m%d')}",
        "title": f"Daily Brief - {datetime.now().strftime('%B %d, %Y')}",
        "description": "Daily AI-generated neutral news podcast",
        "script": script,
        "audio_url": audio_url,
        "duration_seconds": estimate_duration(script),
        "publication_date": datetime.now().strftime("%Y-%m-%d"),
        "articles": articles
    }
    
    store_podcast_episode(episode)
    print(f"Generated podcast: {episode['episode_id']}")

def start_scheduler():
    """Start background scheduler"""
    scheduler = BackgroundScheduler()
    
    # Run daily at 6 AM UTC
    scheduler.add_job(
        generate_daily_podcast,
        'cron',
        hour=6,
        minute=0,
        timezone='UTC'
    )
    
    scheduler.start()
    print("Podcast scheduler started")
```

## Environment Variables

```bash
# Required for script generation
OPENAI_API_KEY=sk-...

# Optional - for real articles
NEWSAPI_KEY=...
GUARDIAN_API_KEY=...

# Optional - for audio generation
ELEVENLABS_API_KEY=...

# Optional - for audio storage
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_STORAGE_BUCKET=...
```

## Testing Checklist

- [ ] Backend server starts without errors
- [ ] `/api/podcasts` returns sample episodes
- [ ] `/api/podcasts/latest` returns today's episode
- [ ] `/api/generate-podcast` generates script successfully
- [ ] Frontend loads podcast page without errors
- [ ] Episode list displays correctly
- [ ] Play button works (HTML5 audio element)
- [ ] Pause button works
- [ ] Skip forward/back works
- [ ] Volume control works
- [ ] Speed control cycles through speeds
- [ ] Progress bar displays and updates
- [ ] Seek works (clicking on progress bar)
- [ ] Navigation links work on all pages

## Deployment

1. **Commit and push to GitHub**
   ```bash
   git add .
   git commit -m "Integrate podcast functionality"
   git push origin main
   ```

2. **Deploy backend to Render**
   - Render automatically redeploys from GitHub
   - Verify new endpoints in deployment logs

3. **Verify frontend URLs**
   - Update API_CONFIG.BACKEND_URL if needed
   - Verify API calls work in production

4. **Test in production**
   - Load podcast page from GitHub Pages
   - Test all player controls
   - Verify episode list loads

## Troubleshooting

### Episodes not loading
- Check browser console for fetch errors
- Verify backend URL in js/config.js
- Verify CORS is enabled in FastAPI
- Check backend server is running

### Audio not playing
- Verify audio_url is valid
- Check browser DevTools → Network for audio file
- Verify audio format is supported (MP3)
- Check volume is not muted

### Script generation failing
- Verify OPENAI_API_KEY is set
- Check OpenAI API quota/billing
- Check request format matches API spec

### API returning 500 errors
- Check backend logs for exceptions
- Verify all required imports are installed
- Verify environment variables are set

## Next Steps

1. **Immediate**: Test current implementation with sample data
2. **Short-term**: Add real article source (NewsAPI)
3. **Medium-term**: Implement TTS audio generation
4. **Long-term**: Add episode persistence and scheduling

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [ElevenLabs API](https://elevenlabs.io/docs)
- [NewsAPI Documentation](https://newsapi.org/)
- [OpenAI API Reference](https://platform.openai.com/docs)
- [HTML5 Audio Element](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/audio)

## Support

For issues or questions about the podcast integration, refer to:
- `ARCHITECTURE.md` - System design overview
- `DEVELOPER_ONBOARDING.md` - Development setup guide
- Code comments in `backend/api.py` and `js/podcast-v2.js`
