# ⚡ Quick Start - 5 Minutes

## The Fastest Way to Test Everything Locally

### Terminal 1: Backend Setup (2 min)
```bash
cd /Users/gg027/Desktop/Neural-Net-Neutrality

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Create minimal .env file (use fake keys for testing)
cat > .env << 'EOF'
OPENAI_API_KEY=sk-proj-test
ANTHROPIC_API_KEY=sk-ant-test
GEMINI_API_KEY=test
EOF

# Start backend server
uvicorn backend.api:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

**Keep this terminal open!**

---

### Terminal 2: Frontend Setup (1 min)
```bash
# Open NEW terminal tab (Cmd+T)
cd /Users/gg027/Desktop/Neural-Net-Neutrality

# Start simple HTTP server
python3 -m http.server 3000
```

You should see:
```
Serving HTTP on 0.0.0.0 port 3000
```

**Keep this terminal open too!**

---

### Browser: Test It (2 min)
```
1. Open browser: http://localhost:3000/debate.html
2. Select models and enter topic
3. Click "Start Debate"
4. Watch arguments appear
5. Vote on winner
6. Check ratings at http://localhost:3000/ratings.html
```

---

## What You'll See

✅ Debate page loads  
✅ Model dropdowns work  
✅ Can enter a debate topic  
✅ Loading spinner appears  
✅ Arguments display  
✅ Can vote  
✅ Vote feedback appears  

---

## Quick Troubleshooting

| Issue | Fix |
|-------|-----|
| "Cannot find module" | Make sure venv is activated: `source venv/bin/activate` |
| "Connection refused" | Check both servers are running in separate terminals |
| "CORS error" | Normal - backend is running and has CORS middleware |
| "API key error" | Use fake keys in .env for now - they won't be called |

---

## To Test with Real API Calls

1. Get real API keys:
   - OpenAI: https://platform.openai.com/api-keys
   - Anthropic: https://console.anthropic.com/
   - Google: https://aistudio.google.com/app/apikey

2. Update `.env` file with real keys

3. Run debate and watch it work!

---

## What to Check

### Frontend Works?
- [ ] debate.html loads at http://localhost:3000/debate.html
- [ ] No errors in browser console (F12)
- [ ] Buttons and inputs work

### Backend Works?
- [ ] http://localhost:8000/health returns: `{"status":"healthy"}`
- [ ] No errors in terminal 1

### Full Integration Works?
- [ ] Start debate → spinner appears
- [ ] Arguments load (with or without real API)
- [ ] Can vote
- [ ] Vote confirmation appears

---

## Next Steps

- Read `LOCAL_SETUP.md` for detailed setup
- Read `DEBATE_QUICK_START.md` for feature guide
- Read `DEBATE_CODE_REFERENCE.md` to customize

---

## Useful Ports to Know

- **Frontend:** http://localhost:3000/
- **Backend:** http://localhost:8000/
- **Backend Docs:** http://localhost:8000/docs (auto-generated)

---

## Done! 🎉

You now have the full Neural Net Neutrality project running locally with the new Debate Arena feature!

Want to make changes? Just edit files and:
- Frontend: Refresh browser (Cmd+R)
- Backend: Auto-reloads (that's what --reload does)
