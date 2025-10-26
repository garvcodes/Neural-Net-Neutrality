# 🚀 Voting in Production with Render Backend

## What You Have

Your team provided solid database voting code. Now we need to:

1. ✅ Remove hardcoded Supabase password from code
2. ✅ Add DATABASE_URL as environment variable
3. ✅ Fix duplicate endpoints
4. ✅ Deploy to Render with proper configuration
5. ✅ Test voting works end-to-end

---

## Step 1: Fix the Code (Remove Hardcoded Password)

### Issue
Line 21 in `backend/supabase_db.py` has hardcoded password:
```python
DATABASE_URL = "postgresql://postgres.xzsbfdeduchwgtzbwhfp:[password]@aws-1-us-east-2.pooler.supabase.com:5432/postgres"
```

**This is a SECURITY RISK** - never commit passwords to git!

### Solution
Replace lines 14-21 with environment variable loading:

```python
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get connection from environment (required for production)
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL not set. Add to Render environment variables.")
```

---

## Step 2: Fix Duplicate Endpoints

The file has TWO voting endpoints which will cause conflicts:

1. **Line ~290:** `@app.get("/ratings")` - Should be `@app.get("/api/ratings")`
2. **Line ~300:** `@app.post("/api/vote")` - This is correct but conflicts with one in `api.py`

### Solution
**Delete lines 289-320** (the `app = FastAPI()`, middleware, and duplicate endpoints from `supabase_db.py`).

These should only exist in `backend/api.py`, not in `supabase_db.py`.

`supabase_db.py` should be a **utility module** only - no Flask/FastAPI app.

---

## Step 3: Set Up Supabase Database

### Create Supabase Project (Free)

1. Go to https://supabase.com
2. Sign up with GitHub (or email)
3. Click **New Project**
4. Fill in:
   - Name: `neural-net-neutrality`
   - Database Password: Create strong password (e.g., `K9@mPq2$xL9vN4`)
   - Region: Pick closest to your users
5. Click **Create new project** (takes ~2 min)

### Get Your Connection String

Once created:

1. Go to **Settings → Database** (left sidebar)
2. Find "Connection info"
3. Switch to **Psycopg2** tab
4. Copy the full PostgreSQL string:
   ```
   postgresql://postgres:PASSWORD@HOST:5432/postgres
   ```

**Keep this safe!** You'll use it in Render environment variables.

---

## Step 4: Deploy to Render

### Create Render Account

1. Go to https://render.com
2. Sign up with GitHub
3. Create new **Web Service**
4. Select your GitHub repo `garvcodes/Neural-Net-Neutrality`
5. Configure:
   - **Name**: `neural-net-neutrality-api`
   - **Region**: Pick closest to users
   - **Branch**: `debate` (or `main`)
   - **Runtime**: Python 3.11
   - **Build Command**: 
     ```
     pip install -r backend/requirements.txt
     ```
   - **Start Command**:
     ```
     uvicorn backend.api:app --host 0.0.0.0 --port 10000
     ```

### Add Environment Variables in Render

1. In Render dashboard, go to your service
2. Click **Environment** (left sidebar)
3. Add these variables:

```
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@YOUR_HOST:5432/postgres
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=AIzaSy...
```

**Get DATABASE_URL from Supabase** (see Step 3 above)

4. Click **Save changes** and redeploy

---

## Step 5: Update Frontend to Use Production Backend

Your frontend needs to know the Render backend URL.

### Update `js/config.js`

```javascript
const API_CONFIG = {
  BACKEND_URL: 'https://neural-net-neutrality-api.onrender.com'
  // Or: process.env.NODE_ENV === 'production' 
  //     ? 'https://neural-net-neutrality-api.onrender.com'
  //     : 'http://localhost:8000'
};
```

**Replace with your actual Render URL** (from Render dashboard)

### Test in Production

Once deployed:

1. Open your frontend (e.g., `https://garvcodes.github.io/debate.html`)
2. Start a debate
3. Vote
4. See "✓ Vote recorded!"

---

## How It Works (End-to-End)

```
┌─ Browser ─────────────────────────┐
│ User votes on debate.html          │
└───────────────────┬────────────────┘
                    │
                    ↓ POST /api/vote
        ┌─ Render Backend ──────────────┐
        │ (neural-net-neutrality-api)   │
        │ api.py: @app.post("/api/vote")│
        │   ↓                            │
        │ supabase_db.py:                │
        │   update_ratings()             │
        └────────────────┬───────────────┘
                         │
                         ↓ psycopg2 connection
              ┌─ Supabase Database ──────────┐
              │ PostgreSQL (managed)         │
              │ Table: elo_ratings           │
              │ Updates winner & loser score │
              └─────────────────────────────┘
```

---

## Checklist Before Deploying

- [ ] Removed hardcoded DATABASE_URL from code
- [ ] Replaced with `os.getenv("DATABASE_URL")`
- [ ] Removed `app = FastAPI()` from `supabase_db.py`
- [ ] Removed duplicate endpoints from `supabase_db.py`
- [ ] `backend/api.py` has the endpoints (not `supabase_db.py`)
- [ ] Created Supabase project
- [ ] Got PostgreSQL connection string from Supabase
- [ ] Render web service configured
- [ ] DATABASE_URL added to Render environment variables
- [ ] Other API keys added to Render environment variables
- [ ] Frontend `js/config.js` has correct Render URL
- [ ] Backend starts successfully with `✅ Database initialized` message

---

## Troubleshooting

### Error: "DATABASE_URL not set"

**Fix:**
1. Go to Render dashboard
2. Click your service
3. Go to **Environment**
4. Add `DATABASE_URL` with your Supabase connection string
5. Click **Save and Redeploy**

### Error: "could not translate host name"

**Means:** Supabase connection string is wrong

**Fix:**
1. Go to Supabase dashboard
2. Settings → Database → Connection info
3. Copy PostgreSQL string again carefully
4. Update in Render environment variables
5. Redeploy

### Error: "psycopg2 could not be resolved"

**Fix:**
1. Make sure `psycopg2-binary` is in `backend/requirements.txt`
2. Commit and push changes
3. Render will auto-redeploy with new requirements

### Voting works locally but not in production

**Check:**
1. Is Render backend running? (Check logs in Render dashboard)
2. Did environment variables get saved? (Check Render → Environment)
3. Is frontend using correct backend URL? (Check `js/config.js`)
4. Open browser console (F12) and check for CORS errors

### "Cannot find module dotenv"

**Fix:**
1. Ensure `.env` works locally first
2. For Render, you DON'T need `.env` - use Render's environment variables
3. Code should handle both (`.env` for local, environment variables for production)

---

## File Changes Summary

### `backend/supabase_db.py`

**KEEP:**
- `calc_prob()` function
- `update_elo()` function
- `init_database()` function
- `ensure_table_exists()` function
- `get_rating()` function
- `update_ratings()` function
- `get_all_ratings()` function
- `reset_ratings()` function

**REMOVE/CHANGE:**
- Line 21: Hardcoded `DATABASE_URL` → Use `os.getenv("DATABASE_URL")`
- Lines 289-320: Don't include `app = FastAPI()` and endpoints here
- Should import `load_dotenv` and `os`

### `backend/api.py`

**Keep as-is:**
- All imports
- `@app.post("/api/vote")` endpoint
- `@app.get("/api/ratings")` endpoint
- All other endpoints

**Already correct!**

---

## Production Checklist (After Deployment)

- [ ] Visit production URL in browser
- [ ] Navigate to `/debate.html`
- [ ] Create debate with two models
- [ ] Click vote
- [ ] See "✓ Vote recorded!"
- [ ] Check `/api/ratings` endpoint
- [ ] See updated model scores
- [ ] Create second debate and vote opposite
- [ ] Verify scores changed again
- [ ] Have multiple team members test

---

## Next Steps

1. **Fix code** (remove hardcoded password, duplicate endpoints)
2. **Create Supabase project** (takes 2 min)
3. **Get DATABASE_URL** from Supabase
4. **Deploy to Render** (auto-deploys on push)
5. **Add DATABASE_URL** to Render environment variables
6. **Test voting** works in production

Once done, your **voting system is live!** 🎉

---

## Quick Reference

| Item | Value |
|------|-------|
| Supabase | https://supabase.com |
| Render | https://render.com |
| Your Repo | https://github.com/garvcodes/Neural-Net-Neutrality |
| Render URL | `https://neural-net-neutrality-api.onrender.com` (example) |
| Database Type | PostgreSQL (managed by Supabase) |
| API Framework | FastAPI (Python) |

---

**Ready to ship voting to production!** 🚀
