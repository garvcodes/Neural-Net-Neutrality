# 🚀 Local Development Setup Guide

## Quick Start (5 minutes)

This guide walks you through spinning up the Neural Net Neutrality project locally to test the new Debate feature.

---

## Prerequisites

Make sure you have installed:
- ✅ **Python 3.11+** → Check: `python3 --version`
- ✅ **Git** → Check: `git --version`
- ✅ **A text editor** (VS Code, etc.)

---

## Step 1: Clone & Navigate (2 min)

```bash
# If you haven't already, navigate to the project
cd /Users/gg027/Desktop/Neural-Net-Neutrality

# Verify you're in the right place
pwd
# Should show: /Users/gg027/Desktop/Neural-Net-Neutrality

ls -la
# Should show: debate.html, backend/, js/, css/, etc.
```

---

## Step 2: Create Virtual Environment (1 min)

```bash
# Create Python virtual environment
python3 -m venv venv

# Activate it (macOS/Linux)
source venv/bin/activate

# You should see (venv) in your terminal prompt
# Verify: which python
# Should show: /Users/gg027/Desktop/Neural-Net-Neutrality/venv/bin/python
```

---

## Step 3: Install Dependencies (2 min)

```bash
# Make sure you're in the project root and venv is activated
cd /Users/gg027/Desktop/Neural-Net-Neutrality

# Install all requirements
pip install -r backend/requirements.txt

# Verify key packages installed
pip list | grep -E "fastapi|uvicorn|openai|anthropic|google"
```

---

## Step 4: Set Up API Keys (2 min)

You'll need at least one API key to test. Create a `.env` file:

```bash
# Create .env file in project root
cat > .env << 'EOF'
# OpenAI
OPENAI_API_KEY=sk-proj-your-key-here

# Anthropic (Claude)
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Google Gemini
GEMINI_API_KEY=your-key-here

# Optional: Database URL (for Supabase)
# SUPABASE_URL=https://your-project.supabase.co
# SUPABASE_KEY=your-anon-key
EOF
```

Replace with your actual API keys from:
- OpenAI: https://platform.openai.com/api-keys
- Anthropic: https://console.anthropic.com/
- Google: https://aistudio.google.com/app/apikey

**For testing without real API calls**, you can use placeholder values - we'll set up a mock mode below.

---

## Step 5: Start Backend Server (1 min)

```bash
# Make sure venv is activated
# (you should see (venv) in your prompt)

# Start the FastAPI server
uvicorn backend.api:app --reload --host 0.0.0.0 --port 8000

# You should see:
# INFO:     Uvicorn running on http://0.0.0.0:8000
# INFO:     Application startup complete
```

**Keep this terminal open!** The server needs to keep running.

---

## Step 6: Open Frontend in Browser (New Terminal Tab)

```bash
# Open a NEW terminal tab (Cmd+T in Terminal)

# Navigate to project
cd /Users/gg027/Desktop/Neural-Net-Neutrality

# Start simple HTTP server (Python 3)
python3 -m http.server 3000

# You should see:
# Serving HTTP on 0.0.0.0 port 3000
```

**Keep this terminal open too!**

---

## Step 7: Test the Debate Feature 🎉

### Option A: Direct File Access (Easiest - No Server Needed)
```
1. Open Finder
2. Navigate to /Users/gg027/Desktop/Neural-Net-Neutrality
3. Double-click debate.html
4. Should open in your default browser
```

### Option B: Browser - Via HTTP Server (Recommended)
```
1. Open browser
2. Go to: http://localhost:3000/debate.html
3. Should load the debate page
```

### Option C: Backend API Check
```bash
# In a third terminal (with venv activated):
curl http://localhost:8000/health

# Should return: {"status":"healthy"}
```

---

## Step 8: Test the Debate Feature

### Manual Testing Steps:

1. **Open debate.html** → http://localhost:3000/debate.html

2. **Fill in the form:**
   - Pro Model: Select "GPT-4o Mini"
   - Con Model: Select "Gemini 2.0 Flash"
   - Topic: Enter "Universal Basic Income"

3. **Click "Start Debate"**

4. **Watch the magic:**
   - You should see loading spinner
   - Arguments should appear with typewriter effect
   - Two arguments (Pro and Con) should display

5. **Vote:**
   - Click "Vote: Pro Wins" or "Vote: Con Wins"
   - Should show "✓ Vote recorded!"

6. **Check Leaderboard:**
   - Go to http://localhost:3000/ratings.html
   - Models should appear in ratings table

---

## 🔧 Troubleshooting

### Issue: "Cannot find module 'fastapi'"
```bash
# Make sure venv is activated
source venv/bin/activate

# Reinstall requirements
pip install -r backend/requirements.txt
```

### Issue: "Connection refused" on localhost:8000
```bash
# Make sure backend server is running
# Check first terminal - should show Uvicorn running

# If not running, start it:
cd /Users/gg027/Desktop/Neural-Net-Neutrality
source venv/bin/activate
uvicorn backend.api:app --reload
```

### Issue: "CORS error" in browser console
```bash
# Make sure backend is running (it has CORS middleware)
# Frontend URL and Backend URL might be mismatched

# Check js/config.js - for local dev, change to:
const API_CONFIG = {
  BACKEND_URL: 'http://localhost:8000',
  ...
};
```

### Issue: "API key not found" error
```bash
# Make sure .env file exists in project root
cat .env | grep OPENAI_API_KEY

# Or set as environment variables:
export OPENAI_API_KEY="sk-proj-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export GEMINI_API_KEY="..."
```

### Issue: Models not responding
```bash
# Check your API key is valid
# Try testing with OpenAI first (most stable)

# Or use mock mode (see next section)
```

---

## 🎭 Mock Mode (No API Keys Needed)

For testing UI without spending API credits, you can mock the responses:

### Step 1: Modify config.js (Temporary)
```javascript
// In js/config.js, add at top:
const MOCK_MODE = true;  // Set to false for real API

// In js/debate.js, replace the API fetch with:
if (MOCK_MODE) {
  // Fake delay
  await new Promise(r => setTimeout(r, 2000));
  
  const data = {
    pro_argument: "This is a mock pro argument. UBI would stimulate economic growth...",
    con_argument: "This is a mock con argument. UBI would be unsustainable...",
    topic: currentTopic,
    model_pro: currentModelPro,
    model_con: currentModelCon,
  };
  
  // Continue with UI update
  debateResults.classList.remove("hidden");
  await Promise.all([
    typeWriter(proArgument, data.pro_argument, 8),
    typeWriter(conArgument, data.con_argument, 8),
  ]);
} else {
  // Real API call (original code)
  // ...
}
```

---

## 📁 File Structure for Reference

```
/Users/gg027/Desktop/Neural-Net-Neutrality/
├── debate.html              ← Open this in browser
├── index.html
├── ratings.html
├── battle.html
│
├── js/
│   ├── debate.js            ← Frontend logic
│   ├── config.js            ← Backend URL config
│   ├── battle.js
│   └── ratings.js
│
├── css/
│   ├── debate.css           ← Debate styles
│   ├── battle.css
│   └── styles.css
│
├── backend/
│   ├── api.py               ← FastAPI server
│   ├── providers.py         ← LLM provider calls
│   ├── requirements.txt     ← Python dependencies
│   └── ...
│
└── .env                     ← Your API keys (CREATE THIS)
```

---

## 🚀 Full Local Setup Command Reference

### All-in-One Setup Script

Create a file named `setup_local.sh`:

```bash
#!/bin/bash

# Setup local development environment
cd /Users/gg027/Desktop/Neural-Net-Neutrality

echo "1. Creating virtual environment..."
python3 -m venv venv

echo "2. Activating virtual environment..."
source venv/bin/activate

echo "3. Installing dependencies..."
pip install -r backend/requirements.txt

echo "4. Creating .env file..."
cat > .env << 'EOF'
OPENAI_API_KEY=sk-proj-test
ANTHROPIC_API_KEY=sk-ant-test
GEMINI_API_KEY=test
EOF

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Terminal 1: source venv/bin/activate && uvicorn backend.api:app --reload"
echo "2. Terminal 2: python3 -m http.server 3000"
echo "3. Browser: http://localhost:3000/debate.html"
```

Usage:
```bash
chmod +x setup_local.sh
./setup_local.sh
```

---

## 📊 Testing Checklist

Use this checklist to verify everything works:

### Frontend
- [ ] debate.html loads without errors (F12 Console)
- [ ] Model dropdowns populate correctly
- [ ] Topic input accepts text
- [ ] "Start Debate" button clickable
- [ ] Loading spinner appears
- [ ] Arguments display with typewriter effect
- [ ] Vote buttons appear after arguments
- [ ] Navigation links work (Home, Battle!, Debate!, Ratings)

### Backend
- [ ] `http://localhost:8000/health` returns 200
- [ ] `http://localhost:8000/api/debate` accepts POST requests
- [ ] API returns expected JSON structure
- [ ] Error handling works (test with empty topic)

### Integration
- [ ] Vote submission works
- [ ] Ratings update after voting
- [ ] Ratings page displays models
- [ ] Different model combinations work

### Responsive Design
- [ ] Desktop view (1200px+): 3 columns (Pro | vs | Con)
- [ ] Tablet view (768px): Stacked layout
- [ ] Mobile view (<768px): Full-width single column

---

## 🎬 Common Development Tasks

### View Backend Logs
```bash
# Terminal running uvicorn will show:
# - Request logs
# - Error messages
# - API call details

# For more verbose logging, modify api.py:
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Test API Directly
```bash
# Test /api/debate endpoint
curl -X POST http://localhost:8000/api/debate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Test Topic",
    "model_pro": "gpt-4o-mini",
    "model_con": "gemini-2.0-flash"
  }'

# Test /api/vote endpoint
curl -X POST http://localhost:8000/api/vote \
  -H "Content-Type: application/json" \
  -d '{
    "winner_model": "gpt-4o-mini",
    "loser_model": "gemini-2.0-flash",
    "prompt": "Test Topic"
  }'
```

### Debug JavaScript
```bash
# Open browser DevTools (F12)
# Go to Console tab
# Type commands to test:
console.log(currentTopic);
console.log(API_CONFIG);
```

### Check Network Requests
```bash
# In browser DevTools
# Go to Network tab
# Start a debate
# Watch the POST request to /api/debate
# Click on request to see Request/Response headers and body
```

### View Network Traffic
```bash
# Can also use in terminal
watch -n 1 'netstat -an | grep 8000'
```

---

## 🔄 Development Workflow

### For Frontend Changes:
1. Edit `debate.html`, `js/debate.js`, or `css/debate.css`
2. Refresh browser (Cmd+R)
3. Changes should appear immediately

### For Backend Changes:
1. Edit `backend/api.py`
2. Backend auto-reloads (uvicorn --reload)
3. Refresh browser or re-test API
4. Changes should be live

### For Adding Features:
1. Frontend: Add HTML in debate.html
2. Frontend: Add logic in js/debate.js
3. Backend: Add endpoint in backend/api.py
4. Test both sides
5. Check responsive design

---

## 🌐 Port Reference

| Service | Port | URL |
|---------|------|-----|
| HTTP Server (Frontend) | 3000 | http://localhost:3000 |
| FastAPI (Backend) | 8000 | http://localhost:8000 |
| Uvicorn Docs | 8000 | http://localhost:8000/docs |
| Uvicorn ReDoc | 8000 | http://localhost:8000/redoc |

---

## 📚 Useful Commands

```bash
# Activate virtual environment
source venv/bin/activate

# Deactivate virtual environment
deactivate

# Install new package
pip install package-name

# Check installed packages
pip list

# View requirements
cat backend/requirements.txt

# Start backend server
uvicorn backend.api:app --reload

# Start frontend server
python3 -m http.server 3000

# View running processes
ps aux | grep python
ps aux | grep http

# Kill process on port
lsof -ti:8000 | xargs kill -9
lsof -ti:3000 | xargs kill -9

# Test API
curl -X GET http://localhost:8000/health
curl -X POST http://localhost:8000/api/debate ...
```

---

## ✨ Hot Tips

1. **Use VS Code:** Great for editing, debugging, and built-in terminal
2. **Open in DevTools:** Press F12 in browser for Network, Console debugging
3. **Auto-reload:** Backend auto-reloads with `--reload` flag
4. **Mock Mode:** Perfect for UI testing without API costs
5. **Separate Terminals:** Keep backend and frontend in different tabs
6. **Test Early:** Test API before testing full UI flow

---

## 🎉 You're Ready!

You should now be able to:
✅ Run backend server locally
✅ Serve frontend files locally
✅ Test debate feature in browser
✅ Debug issues with DevTools
✅ Make code changes and see them live

**Happy coding!** 🚀
