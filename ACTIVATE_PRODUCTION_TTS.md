# How to Activate Real TTS in Production

## Current Status ⚠️

Production is running the podcast code, but:
- ✅ Script generation works perfectly
- ❌ Audio is still using archive.org sample
- ❌ `ELEVENLABS_API_KEY` not set in Render environment

**Reason:** The environment variable is missing from Render deployment.

---

## Solution: Add ElevenLabs API Key to Render

### Step 1: Get ElevenLabs API Key

1. Go to https://elevenlabs.io/
2. Sign up or log in
3. Go to Account → API Key
4. Copy your API key (looks like `sk_...`)

### Step 2: Add to Render Environment

**Option A: Via Render Dashboard (GUI)**

1. Go to https://dashboard.render.com/
2. Click on your backend service (neural-net-neutrality)
3. Go to **Environment** tab on the left
4. Click **Add Environment Variable**
5. Name: `ELEVENLABS_API_KEY`
6. Value: Paste your API key (e.g., `sk_...`)
7. Click **Save**
8. Wait 1-2 minutes for auto-redeploy

**Option B: Via CLI (if you have Render CLI)**

```bash
# Set environment variable
render env set ELEVENLABS_API_KEY sk_your_key_here

# Or edit render.yaml if you have it
```

### Step 3: Verify Deployment

After saving:
1. Check Render dashboard - should show "Deploying..." then "Live"
2. Takes 2-5 minutes to redeploy
3. Test endpoint:

```bash
curl https://neural-net-neutrality.onrender.com/api/generate-podcast
```

Look for:
```json
"tts_provider": "ElevenLabs"  // Should change from "Sample (Archive.org)"
```

### Step 4: Test Real Audio

```bash
# Generate a new podcast
curl -X POST https://neural-net-neutrality.onrender.com/api/generate-podcast \
  -H "Content-Type: application/json" \
  -d '{}' | jq '.audio_url' | head -c 50

# Should now return a real audio file instead of archive.org sample
```

---

## What Happens After Adding Key

### Before (Current)
```
POST /api/generate-podcast
  ↓
  Script generation ✅ OpenAI GPT
  ↓
  Audio generation ❌ Falls back to sample
  ↓
  Response: "audio_url": "https://archive.org/download/..."
             "tts_provider": "Sample (Archive.org)"
```

### After (With ElevenLabs Key)
```
POST /api/generate-podcast
  ↓
  Script generation ✅ OpenAI GPT
  ↓
  Audio generation ✅ ElevenLabs TTS (Real!)
  ↓
  Response: "audio_url": "data:audio/mp3;base64,..." (or S3 URL)
             "tts_provider": "ElevenLabs"
             Audio is REAL professional voice! 🎙️
```

---

## Current API Response (From Production)

```json
{
  "success": true,
  "episode_id": "episode_20251026_163249",
  "script": "Hello and welcome to Neutral Network News...",
  "audio_url": "https://archive.org/download/testmp3testfile/mpthreetest.mp3",
  "duration_seconds": 144,
  "title": "Daily Brief - October 26, 2025",
  "articles": [...],
  "metadata": {
    "generated_at": "2025-10-26T16:32:49.142306",
    "model": "gpt-4o-mini",
    "voice": "news_anchor",
    "articles_count": 5,
    "word_count": 362,
    "tts_provider": "Sample (Archive.org)"  // ← THIS WILL CHANGE
  }
}
```

After adding key:
```json
{
  ...same as above but...
  "audio_url": "data:audio/mp3;base64,...[real audio bytes]...",
  "metadata": {
    ...
    "tts_provider": "ElevenLabs"  // ✅ NOW REAL!
  }
}
```

---

## Why It's Still Using Sample

The backend code checks:
```python
elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")

if elevenlabs_key:
    # Use real ElevenLabs TTS
    audio = elevenlabs_client.text_to_speech.convert(...)
else:
    # Fall back to sample for demo/testing
    audio_url = "https://archive.org/download/testmp3testfile/mpthreetest.mp3"
```

Since `ELEVENLABS_API_KEY` is not set in Render environment, it falls back to sample.

---

## Step-by-Step Render Dashboard Instructions

1. **Open Render Dashboard**
   - https://dashboard.render.com/

2. **Select Your Service**
   - Look for "neural-net-neutrality" in services
   - Click on it

3. **Go to Environment Tab**
   - Left sidebar → Environment (or click on service name → Environment)

4. **Add New Variable**
   - Button: "+ Add Environment Variable"
   - Key: `ELEVENLABS_API_KEY`
   - Value: `sk_...` (your API key from elevenlabs.io)
   - Click "Save"

5. **Wait for Redeploy**
   - You'll see "Redeploying..." status
   - Wait 2-5 minutes
   - Status changes to "Live"

6. **Test It**
   ```bash
   curl https://neural-net-neutrality.onrender.com/api/podcasts
   # Should now use real audio!
   ```

---

## Troubleshooting

### Still showing Sample (Archive.org)?

1. **Check Render status** - Make sure deployment completed (should say "Live")
2. **Force refresh** - Hard refresh browser (Cmd+Shift+R on Mac)
3. **Check Render logs** - Environment section shows if variable is loaded
4. **Verify API key** - Make sure you copied it correctly from elevenlabs.io

### Getting 500 error?

- Check Render logs for error message
- Verify API key has credits (sign in to elevenlabs.io)
- Make sure `OPENAI_API_KEY` is also set (should already be)

### Audio won't play?

- If using data:audio/mp3;base64, that's normal (embedded audio)
- Browser might need refresh to load player properly
- Check browser console for CORS errors

---

## Free Credits on ElevenLabs

- Sign up → Get $5 free credits monthly
- Roughly 200-300 podcast generations per month free
- After that: $0.30 per 1M characters
- Professional news anchor voice is same price as others

---

## After Production is Live with Real TTS

You can then:

1. **Show in demo** - "Here's real audio being generated with ElevenLabs"
2. **Demonstrate quality** - Professional news anchor voice
3. **Explain architecture** - Articles → GPT → ElevenLabs → Public audio
4. **Talk about scale** - Can handle 1000s of requests per day
5. **Discuss future** - Real articles, scheduled generation, cloud storage

---

## What Your Demo Partner Will See

After you add the key and redeploy:

1. **Generate Podcast** endpoint returns REAL audio
2. **Podcast Episode List** plays with professional voice
3. **Audio Quality** sounds like professional news broadcast
4. **Response metadata** shows `"tts_provider": "ElevenLabs"`

**This is the difference between POC and production!**

---

## Summary

| Component | Status | Fix |
|-----------|--------|-----|
| Script Generation | ✅ Works | Already deployed |
| OpenAI API Key | ✅ Set | Already in Render |
| ElevenLabs TTS | ❌ Not active | Add API key to Render |
| Frontend | ✅ Works | Already deployed |
| Audio Playback | ✅ Works | Works with any audio URL |

**Only thing needed: Add `ELEVENLABS_API_KEY` to Render environment variables**

---

## ElevenLabs API Key Format

Your key will look like:
```
sk_1a2b3c4d5e6f7g8h9i0j...
```

It's NOT your email or password, it's a unique API token you get from your ElevenLabs account.

---

## Time Estimate

- **Get ElevenLabs key:** 5 minutes (if not already done)
- **Add to Render:** 2 minutes
- **Redeploy:** 2-5 minutes (automatic)
- **Verify working:** 2 minutes
- **Total:** ~10-15 minutes

**Then your production demo will have REAL TTS audio!** 🎙️

---

## Questions?

- **Where to get key?** https://elevenlabs.io/ → Account → API Key
- **How to access Render?** https://dashboard.render.com/
- **How to verify it worked?** Call `/api/generate-podcast` and check `tts_provider` in response
- **What if I don't have Render access?** Contact the person who set it up or ask for dashboard credentials
