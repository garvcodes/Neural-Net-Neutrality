# ✅ Render Production Voting - Quick Checklist

## Phase 1: Prepare Code (Done ✓)

- [x] Remove hardcoded DATABASE_URL from `supabase_db.py`
- [x] Add `os.getenv("DATABASE_URL")` with error handling
- [x] Remove duplicate endpoints from `supabase_db.py`
- [x] Create `.env.example` template
- [x] All changes pushed to GitHub

```bash
git add backend/supabase_db.py .env.example
git commit -m "Fix: Use environment variables for database"
git push origin debate
```

---

## Phase 2: Set Up Database (5 min)

- [ ] Create Supabase account at https://supabase.com (GitHub signup)
- [ ] Create new project (name: `neural-net-neutrality-db`)
- [ ] Set strong password (e.g., `K9@mPq2$xL9vN4wR2z`)
- [ ] Wait 2-3 min for initialization
- [ ] Go to Settings → Database → Connection info
- [ ] Copy PostgreSQL connection string (Psycopg2 tab)
- [ ] **Save it!** You need it soon

**Your connection string looks like:**
```
postgresql://postgres:K9@mPq2$xL9vN4wR2z@aws-1-us-east-1.pooler.supabase.com:5432/postgres
```

---

## Phase 3: Deploy to Render (10 min)

- [ ] Create Render account at https://render.com (GitHub signup)
- [ ] Create new **Web Service**
- [ ] Select repo: `garvcodes/Neural-Net-Neutrality`
- [ ] Select branch: `debate`
- [ ] Set configuration:
  - Runtime: Python 3.11
  - Build: `pip install -r backend/requirements.txt`
  - Start: `uvicorn backend.api:app --host 0.0.0.0 --port 10000`
- [ ] Click **Create Web Service**
- [ ] Wait for deployment (2-5 min)
- [ ] Check logs for: `✅ Database initialized with 7 models`
- [ ] **Copy your Render URL** (top of dashboard)

**Your Render URL looks like:**
```
https://neural-net-neutrality-api.onrender.com
```

---

## Phase 4: Connect Database to Render (2 min)

In Render dashboard:

- [ ] Click **Environment** (left sidebar)
- [ ] Click **Add Environment Variable**
- [ ] Add `DATABASE_URL`:
  - Key: `DATABASE_URL`
  - Value: (Paste your Supabase connection string)
- [ ] Click **Add**
- [ ] Optionally add other API keys:
  - `OPENAI_API_KEY=sk-...`
  - `ANTHROPIC_API_KEY=sk-ant-...`
  - `GOOGLE_API_KEY=AIzaSy...`
- [ ] Click **Manual Deploy** to restart with env vars
- [ ] Wait for deployment
- [ ] Check logs for success message

---

## Phase 5: Update Frontend (2 min)

Edit `js/config.js`:

```javascript
const API_CONFIG = {
  BACKEND_URL: 'https://YOUR_RENDER_URL.onrender.com'
};
```

Replace with your actual Render URL from Phase 3.

Push changes:
```bash
git add js/config.js
git commit -m "Update: Use Render production backend"
git push origin debate
```

---

## Phase 6: Test Everything (5 min)

### Test 1: Backend Health
```
Visit: https://YOUR_RENDER_URL/health
Expected: {"status": "healthy"}
```

### Test 2: Ratings Endpoint
```
Visit: https://YOUR_RENDER_URL/api/ratings
Expected: All models with 1500 rating
```

### Test 3: Full Debate
1. Open your frontend (GitHub Pages or local)
2. Go to `/debate.html`
3. Select 2 models
4. Enter topic: "AI should be regulated"
5. Click **Start Debate**
6. Wait for arguments
7. Click **Vote: Pro Wins**
8. See: **✓ Vote recorded!**

### Test 4: Verify Vote Recorded
1. Refresh `/api/ratings` endpoint
2. One model ~1516, other ~1484
3. ✅ **Vote worked!**

---

## Phase 7: Team Rollout

- [ ] Share Render URL with team
- [ ] Each person updates their `js/config.js`
- [ ] Everyone tests voting works
- [ ] Celebrate! 🎉

---

## Troubleshooting Quick Fixes

| Error | Fix |
|-------|-----|
| `DATABASE_URL not set` | Add to Render Environment, redeploy |
| `could not translate host` | Check Supabase connection string format |
| `psycopg2 not found` | Ensure in requirements.txt, redeploy |
| Vote fails silently | Check browser console (F12), check Render logs |
| Ratings don't update | Check `/api/ratings` endpoint, check database connection |

---

## Key Files Modified

```
backend/supabase_db.py     - Now reads from environment
.env.example               - Template for team
js/config.js               - Points to Render URL
```

---

## Production Architecture

```
┌─ Browser ──────────────┐
│ GitHub Pages           │ ← Frontend (static)
└────────┬───────────────┘
         │
         ↓ /api/* requests
┌─ Render Web Service ────────┐
│ neural-net-neutrality-api   │ ← Backend
│ FastAPI + uvicorn           │
└────────┬────────────────────┘
         │
         ↓ psycopg2 connection
┌─ Supabase PostgreSQL ──────┐
│ elo_ratings table          │ ← Database
│ Managed by Supabase        │
└────────────────────────────┘
```

---

## Success Criteria

✅ All of these should be true:

- [ ] Code has no hardcoded passwords
- [ ] Supabase project created and running
- [ ] Render service deployed successfully
- [ ] DATABASE_URL in Render environment
- [ ] `/health` returns 200
- [ ] `/api/ratings` shows models
- [ ] Frontend uses correct Render URL
- [ ] Debate generates arguments
- [ ] Vote button works
- [ ] Vote recorded confirmation appears
- [ ] Ratings update after vote
- [ ] Multiple votes change scores properly

---

## Time Estimate

| Phase | Time | Status |
|-------|------|--------|
| 1. Code prep | 2 min | ✅ Done |
| 2. Supabase | 5 min | ⏳ Your turn |
| 3. Render deploy | 10 min | ⏳ Your turn |
| 4. Connect DB | 2 min | ⏳ Your turn |
| 5. Update frontend | 2 min | ⏳ Your turn |
| 6. Test | 5 min | ⏳ Your turn |
| **Total** | **~25 min** | ⏳ In progress |

---

## You're Ready! 🚀

Everything is set up. Just follow the phases above.

**Questions?**
- Detailed guide: See `RENDER_PRODUCTION_SETUP.md`
- Step-by-step: See `RENDER_DEPLOY_STEPS.md`
- Architecture: See `RENDER_PRODUCTION_SETUP.md`

---

**Let's ship it!** 🚀✨
