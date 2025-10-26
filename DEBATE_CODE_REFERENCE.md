# Debate Feature - Code Reference & Examples

## Quick Reference

### Key Files

```javascript
// Frontend
debate.html              // UI markup
js/debate.js            // Debate logic
css/debate.css          // Styling

// Backend  
backend/api.py          // /api/debate endpoint
backend/providers.py    // Model calls (unchanged)
```

### Key Functions

```javascript
// debate.js
submitVote()            // Send vote to backend
typeWriter()            // Animated argument reveal
updateModelLabel()      // Update displayed model name
```

---

## API Reference

### Request Body

```json
{
  "topic": "string (required)",
  "model_pro": "string (default: 'gpt-4o-mini')",
  "model_con": "string (default: 'gemini-2.0-flash')",
  "api_key_pro": "string (optional)",
  "api_key_con": "string (optional)"
}
```

### Response Body

```json
{
  "topic": "string",
  "pro_argument": "string (2-3 paragraphs)",
  "con_argument": "string (2-3 paragraphs)",
  "model_pro": "string",
  "model_con": "string",
  "arguments": {
    "pro_argument": {
      "model": "string",
      "argument": "string or null",
      "error": "string or null"
    },
    "con_argument": {
      "model": "string", 
      "argument": "string or null",
      "error": "string or null"
    }
  }
}
```

---

## Code Examples

### JavaScript - Making API Call

```javascript
// From js/debate.js
const response = await fetch(`${API_CONFIG.BACKEND_URL}/api/debate`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    topic: currentTopic,
    model_pro: currentModelPro,
    model_con: currentModelCon,
  }),
});

const data = await response.json();
// data.pro_argument and data.con_argument contain the responses
```

### Python - Backend Endpoint

```python
@app.post("/api/debate")
def debate(req: DebateRequest):
    """Debate endpoint: get pro and con arguments from two models."""
    
    if not req.topic or not req.topic.strip():
        raise HTTPException(status_code=400, detail="Topic is required")
    
    pro_system = (
        "You are an expert debater arguing in favor of a position. "
        "Make a clear, well-reasoned argument with 2-3 key points..."
    )
    
    con_system = (
        "You are an expert debater arguing against a position. "
        "Make a clear, well-reasoned counterargument with 2-3 key points..."
    )
    
    user_msg = f"Debate topic: {req.topic}"
    
    # Call both models
    pro_arg = call_model(req.model_pro, pro_system, user_msg, req.api_key_pro)
    con_arg = call_model(req.model_con, con_system, user_msg, req.api_key_con)
    
    return {
        "topic": req.topic,
        "pro_argument": pro_arg,
        "con_argument": con_arg,
        "model_pro": req.model_pro,
        "model_con": req.model_con,
    }
```

### JavaScript - Typewriter Effect

```javascript
async function typeWriter(element, text, speed = 12) {
  element.textContent = "";
  element.classList.add("typing");
  
  for (let i = 0; i < text.length; i++) {
    element.textContent += text[i];
    await new Promise((r) => setTimeout(r, speed));
    element.scrollTop = element.scrollHeight; // auto-scroll
  }
  
  element.classList.remove("typing");
}

// Usage:
await typeWriter(proArgument, data.pro_argument || "No argument provided.", 8);
await typeWriter(conArgument, data.con_argument || "No argument provided.", 8);
```

### JavaScript - Vote Submission

```javascript
async function submitVote(winnerModel, loserModel, button) {
  button.disabled = true;
  const originalText = button.textContent;
  button.textContent = "Voting...";

  try {
    const response = await fetch(`${API_CONFIG.BACKEND_URL}/api/vote`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        winner_model: winnerModel,
        loser_model: loserModel,
        prompt: currentTopic,
      }),
    });

    const data = await response.json();
    if (data.success) {
      button.textContent = `✓ Vote recorded!`;
      setTimeout(() => {
        button.textContent = originalText;
        button.disabled = false;
      }, 2000);
    }
  } catch (err) {
    console.error("Vote error:", err);
    button.textContent = "Error voting";
    button.disabled = false;
  }
}
```

---

## CSS Examples

### Pro/Con Column Styling

```css
.pro-column {
  border-left: 4px solid #10b981;  /* Green for Pro */
  padding-left: 1.5rem;
}

.con-column {
  border-right: 4px solid #ef4444;  /* Red for Con */
  padding-right: 1.5rem;
}

.position-badge.pro {
  background: #d1fae5;
  color: #065f46;
}

.position-badge.con {
  background: #fee2e2;
  color: #991b1b;
}
```

### Responsive Grid

```css
.debate-container {
  display: grid;
  grid-template-columns: 1fr auto 1fr;  /* Desktop */
  gap: 1.5rem;
}

@media (max-width: 1024px) {
  .debate-container {
    grid-template-columns: 1fr;  /* Mobile */
  }
}
```

### Loading Spinner

```css
.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #e0e7ff;
  border-top: 4px solid #4f46e5;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
```

---

## Customization Examples

### Changing Debate Temperature

```python
# In backend/api.py, around line 315
pro_arg = call_model(
    model=req.model_pro,
    system_msg=pro_system,
    user_msg=user_msg,
    api_key=req.api_key_pro,
    params={"temperature": 0.9, "max_tokens": 1000}  # Change here
)
```

Higher temperature = more creative but potentially less coherent
Lower temperature = more deterministic and focused

### Changing Typewriter Speed

```javascript
// In debate.js, around line 58
await typeWriter(proArgument, data.pro_argument || "...", 4);  // Faster (4ms)
await typeWriter(conArgument, data.con_argument || "...", 4);
```

Lower number = faster reveal, higher number = slower reveal

### Changing Colors

```css
/* In css/debate.css */
.pro-column {
  border-left: 4px solid #3b82f6;  /* Change from green to blue */
}

.position-badge.pro {
  background: #dbeafe;
  color: #1e40af;
}
```

---

## Testing Examples

### cURL Test

```bash
# Test the /api/debate endpoint
curl -X POST http://localhost:8000/api/debate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Universal Basic Income",
    "model_pro": "gpt-4o-mini",
    "model_con": "gemini-2.0-flash"
  }'
```

### Python Test

```python
import requests

response = requests.post(
    "http://localhost:8000/api/debate",
    json={
        "topic": "Should AI be regulated?",
        "model_pro": "claude-3-haiku-20240307",
        "model_con": "gpt-4o-mini"
    }
)

print(response.json())
```

### JavaScript Test (Browser Console)

```javascript
const topic = "Remote work productivity";
const response = await fetch("http://localhost:8000/api/debate", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    topic: topic,
    model_pro: "gpt-4o-mini",
    model_con: "gemini-2.0-flash"
  })
});

const data = await response.json();
console.log("Pro argument:", data.pro_argument);
console.log("Con argument:", data.con_argument);
```

---

## Error Handling

### Frontend Error Handling

```javascript
if (!response.ok) {
  const errorData = await response.json();
  throw new Error(errorData.detail || "Failed to start debate");
}
```

### Backend Error Examples

```python
# Missing topic
raise HTTPException(status_code=400, detail="Topic is required")

# API call failed
except Exception as e:
    arguments["pro_argument"] = {
        "model": req.model_pro,
        "error": str(e),
        "argument": None
    }
```

---

## Debugging Tips

### Enable Browser DevTools
```javascript
// Add to js/debate.js for debugging
console.log("Topic:", currentTopic);
console.log("Model Pro:", currentModelPro);
console.log("Model Con:", currentModelCon);
console.log("API Response:", data);
```

### Check API Keys
```bash
# Make sure API keys are set
echo $OPENAI_API_KEY
echo $ANTHROPIC_API_KEY
echo $GEMINI_API_KEY
```

### Test Backend Directly
```bash
# Start backend in debug mode
python -m backend.api

# Or with uvicorn
uvicorn backend.api:app --reload
```

### Browser Network Tab
1. Open DevTools (F12)
2. Go to Network tab
3. Start a debate
4. Watch POST requests to `/api/debate`
5. Click request to see payload and response

---

## Common Customizations

### Change Default Models

```html
<!-- In debate.html -->
<select id="model-pro-select" class="model-select">
  <option value="claude-3-sonnet-20240229" selected>Claude 3 Sonnet</option>
  <!-- other options -->
</select>
```

### Change Pro/Con System Prompts

```python
# In backend/api.py around line 315
pro_system = (
    "You are a professional debate champion. "
    "Provide the most compelling argument for..."
)

con_system = (
    "You are a critical thinker. "
    "Provide the strongest counterargument against..."
)
```

### Add Debate Topic Examples

```html
<!-- In debate.html, after topic input -->
<div class="topic-examples">
  <p>Popular topics:</p>
  <button onclick="setTopic('Universal Basic Income')">UBI</button>
  <button onclick="setTopic('AI Regulation')">AI Regulation</button>
</div>
```

---

## Performance Metrics

### Expected Times
- Debate generation: 5-15 seconds
- Vote submission: <1 second
- Page load: <2 seconds

### API Costs (Approximate)
- GPT-4o Mini: ~$0.10 per debate
- Claude 3 Haiku: ~$0.15 per debate
- Gemini 2.0 Flash: ~$0.03 per debate

---

## Browser Compatibility

✅ Chrome/Chromium (v90+)
✅ Firefox (v88+)
✅ Safari (v14+)
✅ Edge (v90+)
✅ Mobile browsers (iOS Safari, Chrome Mobile)

---

## Need Help?

Check the documentation files:
- `DEBATE_QUICK_START.md` - User guide
- `DEBATE_FEATURE.md` - Technical overview
- `DEBATE_README.md` - Complete summary
- This file - Code examples & reference
