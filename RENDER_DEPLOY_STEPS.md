# 🚀 Step-by-Step Render Deployment Guide

## What You'll Do

1. ✅ Fix the code (remove hardcoded password) - **DONE** ✓
2. ✅ Create Supabase database
3. ✅ Get DATABASE_URL from Supabase
4. ✅ Create Render web service
5. ✅ Add DATABASE_URL to Render environment
6. ✅ Update frontend to use Render URL
7. ✅ Test voting works in production

---

## Prerequisites

- GitHub account (already have)
- Supabase account (free, 2 min signup)
- Render account (free, 2 min signup)
- Your code pushed to GitHub branch `debate`

---

## Step 1: Create Supabase Database (5 min)

### A. Create Supabase Account

1. Go to https://supabase.com
2. Click **Sign Up**
3. Choose **GitHub** (fastest)
4. Authorize Supabase to access your GitHub

### B. Create Project

1. Click **New Project**
2. Fill in:
   - **Name**: `neural-net-neutrality-db`
   - **Database Password**: Create something strong like `K9@mPq2$xL9vN4wR2z`
   - **Region**: Pick closest to your users (e.g., `us-east-1` for East Coast)
3. Click **Create new project**
4. Wait 2-3 minutes for database to initialize

### C. Get Connection String

Once your project is ready:

1. Click **Settings** (bottom left)
2. Click **Database**
3. Look for "Connection info" section
4. Click the **Psycopg2** tab (important!)
5. Copy the full connection string:
   ```
   postgresql://postgres:YOUR_PASSWORD@aws-1-us-east-1.pooler.supabase.com:5432/postgres
   ```

**SAVE THIS!** You need it in Step 3.

---

## Step 2: Ensure Code is Fixed (Already Done ✓)

The code has been fixed to:
- ✅ Read DATABASE_URL from environment (not hardcoded)
- ✅ Remove duplicate endpoints from `supabase_db.py`
- ✅ Load `.env` for local development

Just make sure these changes are pushed to GitHub:

```bash
git add backend/supabase_db.py .env.example
git commit -m "Fix: Use environment variables for database connection"
git push origin debate
```

---

## Step 3: Create Render Web Service (5 min)

### A. Create Render Account

1. Go to https://render.com
2. Click **Sign Up**
3. Choose **GitHub** (fastest)
4. Authorize Render to access your GitHub repos

### B. Create New Web Service

1. In Render dashboard, click **New +** → **Web Service**
2. Select your repo: **garvcodes/Neural-Net-Neutrality**
3. Pick branch: **debate** (or **main** if you merged)
4. Fill in:
   - **Name**: `neural-net-neutrality-api`
   - **Region**: Pick same as Supabase (e.g., `Oregon` for `us-west`)
   - **Runtime**: Python 3.11
   - **Build Command**:
     ```bash
     pip install -r backend/requirements.txt
     ```
   - **Start Command**:
     ```bash
     uvicorn backend.api:app --host 0.0.0.0 --port 10000
     ```

5. Scroll to **Advanced** settings
6. Leave defaults (instance type, auto-deploy, etc.)
7. Click **Create Web Service**

### C. Wait for Deployment

Render will:
1. Clone your repo
2. Install dependencies
3. Start the server

This takes 2-5 minutes. You'll see logs in real-time.

**Success = You see:**
```
✅ Database initialized with 7 models
INFO:     Application startup complete
```

---

## Step 4: Add Environment Variables (2 min)

### A. Get Your Render URL

Once deployment succeeds:
1. Look at the top of the Render dashboard
2. Find your service's URL (looks like):
   ```
   https://neural-net-neutrality-api.onrender.com
   ```
3. **Copy this!** You need it in the next steps

### B. Add DATABASE_URL to Environment

In your Render service dashboard:

1. Click **Environment** (left sidebar)
2. Click **Add Environment Variable**
3. Enter:
   - **Key**: `DATABASE_URL`
   - **Value**: (Paste your Supabase connection string from Step 1C)
4. Click **Add**

### C. Add Other API Keys (Optional)

Add these if you want to test specific LLM providers:

- **Key**: `OPENAI_API_KEY` → **Value**: `sk-...`
- **Key**: `ANTHROPIC_API_KEY` → **Value**: `sk-ant-...`
- **Key**: `GOOGLE_API_KEY` → **Value**: `AIzaSy...`

### D. Redeploy

After adding environment variables:

1. Click **Manual Deploy** (or wait for auto-redeploy)
2. Wait for deployment to complete
3. Check logs for **"✅ Database initialized with 7 models"**

---

## Step 5: Update Frontend Config (2 min)

Your frontend needs to know the Render backend URL.

### Edit `js/config.js`

Open `js/config.js` and update:

```javascript
const API_CONFIG = {
  // For production, use your Render URL
  BACKEND_URL: 'https://neural-net-neutrality-api.onrender.com'
  
  // For local testing, uncomment this:
  // BACKEND_URL: 'http://localhost:8000'
};
```

### Commit and Push

```bash
git add js/config.js
git commit -m "Update: Use Render production backend URL"
git push origin debate
```

---

## Step 6: Test Voting in Production (5 min)

### A. Test Backend Directly

1. Open browser to your Render URL:
   ```
   https://neural-net-neutrality-api.onrender.com/health
   ```
2. Should see:
   ```json
   {"status": "healthy"}
   ```

### B. Test Ratings Endpoint

1. Open:
   ```
   https://neural-net-neutrality-api.onrender.com/api/ratings
   ```
2. Should see all models with 1500 rating:
   ```json
   {
     "ratings": {
       "OpenAI GPT-4o": {"rating": 1500.0, "wins": 0, "losses": 0},
       ...
     }
   }
   ```

### C. Test Full Debate & Vote

1. Open your frontend (e.g., GitHub Pages deploy)
2. Navigate to `/debate.html`
3. Select two models
4. Enter topic: "AI should be regulated"
5. Click **Start Debate**
6. Wait for arguments to appear
7. Click **Vote: Pro Wins**
8. Should see: **✓ Vote recorded!**

### D. Verify Vote Was Recorded

1. Go back to ratings endpoint:
   ```
   https://neural-net-neutrality-api.onrender.com/api/ratings
   ```
2. Refresh page
3. One model should have ~1516 rating, other ~1484 (not 1500)

✅ **Vote worked!**

---

## Troubleshooting

### Error: "DATABASE_URL not set"

**Problem:** Render started but database URL wasn't configured

**Fix:**
1. Go to Render dashboard
2. Click your service
3. Click **Environment**
4. Check that DATABASE_URL is there
5. Click **Manual Deploy** to restart with env vars

### Error: "could not translate host name"

**Problem:** Supabase connection string is wrong

**Fix:**
1. Go to Supabase dashboard
2. Settings → Database → Connection info
3. Make sure you copied the FULL string (including password)
4. Update in Render environment variables
5. Redeploy

### Error: "psycopg2" not found

**Problem:** Python dependencies didn't install

**Fix:**
1. Check that `psycopg2-binary` is in `backend/requirements.txt`
2. If not, add it: `pip install psycopg2-binary`
3. Update `requirements.txt`: `pip freeze > backend/requirements.txt`
4. Push to GitHub
5. Render will auto-redeploy

### Voting works locally but not in production

**Check:**
1. Is Render backend running?
   - Go to Render dashboard
   - Look for service status (green = running)
   - Check logs for errors
   
2. Is frontend using correct backend URL?
   - Check `js/config.js` has Render URL
   - Open browser console (F12)
   - Look for network errors or CORS issues
   
3. Is DATABASE_URL set?
   - Go to Render → Environment
   - Check DATABASE_URL exists
   - Test endpoint: `https://YOUR_URL/api/ratings`

---

## Monitoring & Logs

### Check Backend Logs

In Render dashboard:
1. Click your service
2. Click **Logs** (left sidebar)
3. See real-time backend output
4. Look for errors or warnings

### Common Log Patterns

**Good:**
```
✅ Database initialized with 7 models
INFO:     Application startup complete
POST /api/vote (200 OK)
```

**Bad:**
```
❌ DATABASE_URL not set
Connection error: could not translate host
```

---

## Successful Deployment Checklist

- [ ] Supabase project created
- [ ] DATABASE_URL copied from Supabase
- [ ] Code pushed to GitHub branch
- [ ] Render service created
- [ ] Deployment succeeded (green checkmark)
- [ ] DATABASE_URL added to Render environment
- [ ] Service redeployed
- [ ] `/health` endpoint returns 200
- [ ] `/api/ratings` shows all models at 1500
- [ ] Frontend updated with Render URL
- [ ] Full debate works
- [ ] Voting works
- [ ] Ratings update after vote

---

## Quick Reference Commands

```bash
# Local testing (before deployment)
source venv/bin/activate
uvicorn backend.api:app --reload

# Check Python version
python3 --version

# List requirements
pip freeze > backend/requirements.txt

# Commit and push
git add .
git commit -m "Deploy voting to production"
git push origin debate
```

---

## Your Render URL

**Once deployed, your backend will be at:**
```
https://neural-net-neutrality-api.onrender.com
```

**Key endpoints:**
- `GET /health` → {"status": "healthy"}
- `GET /api/ratings` → All model ratings
- `POST /api/vote` → Record a vote
- `POST /api/debate` → Generate debate arguments

---

## Next Steps

1. **Complete Steps 1-6 above**
2. **Test voting works end-to-end**
3. **Share Render URL with team**
4. **Celebrate! 🎉 Voting is live!**

---

## Team Deployment

Once you have this working:

1. Share Render URL with team
2. Each team member pushes their feature branches
3. Render auto-deploys on each push
4. Everyone can test the production backend

---

**Your voting system is ready for production!** 🚀

Questions? See `RENDER_PRODUCTION_SETUP.md` for detailed architecture info.
