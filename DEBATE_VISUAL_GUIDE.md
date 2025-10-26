# Debate Feature - Visual Guide & Examples

## 🎭 User Experience Flow

### Step 1: Landing on Debate Page
```
┌────────────────────────────────────────────────┐
│  Neural Net Neutrality                         │
│  Home  Battle!  [Debate!]  Ratings            │
├────────────────────────────────────────────────┤
│                                                │
│         LLM Debate Arena                      │
│                                                │
│  Choose a topic, select two models, and       │
│  watch them debate. Then vote for the winner. │
│                                                │
├────────────────────────────────────────────────┤
│  Pro Model:  [GPT-4o Mini ▼]                  │
│                         VS                     │
│  Con Model:  [Gemini 2.0 Flash ▼]             │
│                                                │
│  Debate Topic:                                 │
│  [Enter topic here...]                        │
│  [Start Debate Button]                        │
│                                                │
└────────────────────────────────────────────────┘
```

### Step 2: Loading State
```
┌────────────────────────────────────────────────┐
│                                                │
│              ⟳ Loading Spinner                 │
│                                                │
│    Debaters are preparing their arguments...  │
│                                                │
└────────────────────────────────────────────────┘
```

### Step 3: Arguments Revealed
```
┌──
──────────────────────────────────────────────┐
│  Topic: Universal Basic Income                │
├─────────────────────┬─────────────────────────┤
│  PRO                │  CON                    │
│  ═════════════════  │  ═════════════════     │
│ [Green Badge]       │ [Red Badge]            │
│ GPT-4o Mini         │ Gemini 2.0 Flash       │
│                     │                        │
│ Argument For:       │ Argument Against:      │
│                     │                        │
│ UBI would           │ UBI is economically    │
│ stimulate growth    │ unfeasible because...  │
│ by providing stable │                        │
│ income that enables │ The costs would be     │
│ consumption and     │ unsustainable and      │
│ entrepreneurship... │ discourage work...     │
│                     │                        │
│ [Vote: Pro Wins]    │ [Vote: Con Wins]       │
└─────────────────────┴─────────────────────────┘
```

### Step 4: Vote Recorded
```
┌────────────────────────────────────────────────┐
│  [✓ Vote recorded!]                           │
│  ...then after 2 seconds...                   │
│  [Vote: Pro Wins]  [Vote: Con Wins]           │
│                                                │
│  [Start New Debate Button]                    │
└────────────────────────────────────────────────┘
```

---

## 📱 Responsive Design Examples

### Desktop (1200px+)
```
┌──────────────────────────────────────────────────┐
│  Model Selection (horizontal)                   │
├──────────────────────────────────────────────────┤
│  Topic Input                                    │
├──────────────────────────────────────────────────┤
│  ┌────────────┬──────┬────────────┐             │
│  │ PRO        │ vs   │ CON        │             │
│  │ ───────────┼──────┼────────────│             │
│  │ Argument   │      │ Argument   │             │
│  │ (left col) │      │ (right col)│             │
│  │ [Vote Pro] │      │ [Vote Con] │             │
│  └────────────┴──────┴────────────┘             │
└──────────────────────────────────────────────────┘
```

### Tablet (768px - 1023px)
```
┌────────────────────────────────────┐
│  Model Selection (vertical stack)  │
├────────────────────────────────────┤
│  Topic Input                       │
├────────────────────────────────────┤
│  ┌────────────────────────────────┐│
│  │ PRO                            ││
│  │ ────────────────────────────── ││
│  │ Argument (stacked)             ││
│  │ [Vote Pro]                     ││
│  └────────────────────────────────┘│
│  ┌────────────────────────────────┐│
│  │ CON                            ││
│  │ ────────────────────────────── ││
│  │ Argument (stacked)             ││
│  │ [Vote Con]                     ││
│  └────────────────────────────────┘│
└────────────────────────────────────┘
```

### Mobile (< 768px)
```
┌──────────────────────┐
│ Model Select (stack) │
├──────────────────────┤
│ Topic Input          │
├──────────────────────┤
│ ┌──────────────────┐ │
│ │ PRO              │ │
│ │ ──────────────── │ │
│ │ Argument (full)  │ │
│ │ [Vote Pro]       │ │
│ └──────────────────┘ │
│ ┌──────────────────┐ │
│ │ CON              │ │
│ │ ──────────────── │ │
│ │ Argument (full)  │ │
│ │ [Vote Con]       │ │
│ └──────────────────┘ │
└──────────────────────┘
```

---

## 🎨 Color Scheme

### Pro (Left Side - Green)
```
Background:  #d1fae5  (very light green)
Text:        #065f46  (dark green)
Border:      #10b981  (medium green)
Badge:       Green theme

Example Pro Argument Box:
┌─────────────────────────────┐
│  PRO (Green Badge)          │
├─────────────────────────────┤
│  Argument For:              │
│  [Green-tinted text area]   │
│  UBI would help by...       │
└─────────────────────────────┘
```

### Con (Right Side - Red)
```
Background:  #fee2e2  (very light red)
Text:        #991b1b  (dark red)
Border:      #ef4444  (medium red)
Badge:       Red theme

Example Con Argument Box:
┌─────────────────────────────┐
│  CON (Red Badge)            │
├─────────────────────────────┤
│  Argument Against:          │
│  [Red-tinted text area]     │
│  UBI would fail because...  │
└─────────────────────────────┘
```

### Primary Actions
```
Button: #4f46e5 (indigo)
Hover:  Darker indigo + shadow
Active: Pressed down effect
```

---

## 🔄 Data Flow Diagram

```
┌─────────────────────────┐
│   User Enters Topic     │
│  (e.g., "Climate Act")  │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│  User Selects Models    │
│  (Pro vs Con)           │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│  JavaScript Validates   │
│  Input & Sends API Call │
└────────────┬────────────┘
             ↓
      ┌──────────────┐
      │ Backend API  │
      │ /api/debate  │
      └──────┬───────┘
             ↓
      ┌──────────────────────────┐
      │  call_model(Pro)         │  ← OpenAI/Anthropic/Google
      │  call_model(Con)         │  ← Different LLM
      └──────┬───────────────────┘
             ↓
      ┌──────────────────────────┐
      │  Return JSON with both   │
      │  arguments to frontend   │
      └──────┬───────────────────┘
             ↓
┌──────────────────────────────┐
│  JavaScript Displays with    │
│  Typewriter Effect           │
└──────┬───────────────────────┘
       ↓
┌──────────────────────────────┐
│  User Reads Arguments        │
│  and Votes for Winner        │
└──────┬───────────────────────┘
       ↓
┌──────────────────────────────┐
│  JavaScript Sends Vote to    │
│  /api/vote endpoint          │
└──────┬───────────────────────┘
       ↓
┌──────────────────────────────┐
│  Backend Updates Elo Ratings │
│  in Database                 │
└──────┬───────────────────────┘
       ↓
┌──────────────────────────────┐
│  Frontend Shows Vote Result  │
│  User can Start New Debate   │
└──────────────────────────────┘
```

---

## 📊 State Diagram

```
                    ┌─────────────────┐
                    │  Initial State  │
                    │  (Show Form)    │
                    └────────┬────────┘
                             ↓
                    ┌─────────────────┐
      ┌─────────────│ User Enters     │
      │             │ Topic & Models  │
      │             └────────┬────────┘
      │                      ↓
      │             ┌──────────────────┐
      │             │  Validating      │
      │             │  Input           │
      │             └────────┬─────────┘
      │          Error ↙    ↓   ↘ Valid
      │                    ┌──────────────┐
      │                    │ Loading      │
      │                    │ State        │
      │                    └────────┬─────┘
      │                             ↓
      │                    ┌──────────────────┐
      │             ┌──────│ API Call to      │
      │             │      │ /api/debate      │
      │             │      └────────┬─────────┘
      │             │     Error ↙   ↓   ↘ Success
      │             │              ┌─────────────┐
      │             ↓              │ Show Results│
      │      ┌──────────────────┐  │ (Arguments) │
      │      │ Show Error State │  └──────┬──────┘
      │      │ Offer Retry      │         ↓
      │      └──────────────────┘  ┌─────────────┐
      │              ↑              │ User Votes  │
      │              └──────────────│             │
      │                             └──────┬──────┘
      │                                    ↓
      │                           ┌──────────────┐
      │                           │ Voting...    │
      │                           │ (Show        │
      │                           │  spinner)    │
      │                           └──────┬───────┘
      │                        Error ↙   ↓   ↘ Success
      └───────────────────────────────┐  ├─────────────┐
                                      ↓  ↓             ↓
                              ┌──────────────────┐  ┌──────────────┐
                              │ Error Displayed  │  │ Vote Success │
                              │                  │  │              │
                              └──────┬───────────┘  └──────┬───────┘
                                     ↑                     ↓
                                     └─────────┬──────────┘
                                              ↓
                                    ┌──────────────────┐
                                    │ Return to Form   │
                                    │ New Debate Ready │
                                    └──────────────────┘
```

---

## 🎯 API Call Examples

### Request to /api/debate
```json
{
  "topic": "Should AI be heavily regulated?",
  "model_pro": "gpt-4o-mini",
  "model_con": "claude-3-sonnet-20240229"
}
```

### Response from /api/debate
```json
{
  "topic": "Should AI be heavily regulated?",
  "pro_argument": "AI regulation is essential because...[Pro argument]...",
  "con_argument": "Light-touch regulation would be better because...[Con]...",
  "model_pro": "gpt-4o-mini",
  "model_con": "claude-3-sonnet-20240229",
  "arguments": { ... }
}
```

### Vote Request to /api/vote
```json
{
  "winner_model": "gpt-4o-mini",
  "loser_model": "claude-3-sonnet-20240229",
  "prompt": "Should AI be heavily regulated?"
}
```

---

## 📈 Features Comparison

| Feature | Battle! | Debate! |
|---------|---------|---------|
| User Input | Single prompt | Topic + models |
| Model Responses | Same prompt, compare | Different system prompts |
| Temperature | 0.0 (deterministic) | 0.7 (creative) |
| Response Type | Any response | Structured argument |
| Voting | Yes | Yes |
| Elo Ratings | Yes | Yes |
| Duration | Instant | 5-15 seconds |
| Use Case | Quick compare | Deep explore |

---

## 🌈 Example Debates

### Debate 1: Economic Policy
```
Topic: Universal Basic Income
Pro: GPT-4o Mini
Con: Gemini 2.0 Flash

Expected:
- Pro: Economic stimulus, consumer spending, efficiency
- Con: Cost, work disincentives, inflation concerns
```

### Debate 2: Tech Policy
```
Topic: AI Regulation
Pro: Claude 3 Sonnet
Con: GPT-3.5 Turbo

Expected:
- Pro: Safety, alignment, oversight benefits
- Con: Innovation stifling, competitive disadvantage
```

### Debate 3: Environmental
```
Topic: Nuclear Power for Climate
Pro: Gemini 1.5 Pro
Con: Claude 3 Haiku

Expected:
- Pro: Carbon-free, reliable baseload power
- Con: Waste, risk, renewable alternatives
```

---

## ⚙️ Configuration Options

### Temperature
- **Lower (0.0)**: Deterministic, focused
- **Current (0.7)**: Balanced, creative
- **Higher (1.0+)**: Highly creative, diverse

### Max Tokens
- **Current: 800** = 2-3 paragraph arguments
- **Increase to 1200**: Longer, more detailed
- **Decrease to 400**: Short, punchy arguments

### System Prompts
- Can customize to encourage different debate styles
- Examples: "aggressive", "diplomatic", "academic"

---

## 🎬 Animation Timeline

### Typewriter Effect
```
Time: 0ms    ▌ "U"
Time: 8ms    ▌ "Uni"
Time: 16ms   ▌ "Unive"
...
Time: 1500ms ▌ "[Full argument visible]"
```

### Loading Spinner
```
Frame 1:  ◶ (rotated 0°)
Frame 2:  ◷ (rotated 90°)
Frame 3:  ◸ (rotated 180°)
Frame 4:  ◹ (rotated 270°)
[Repeat]
```

---

## 🔐 Security Features

### Input Validation
```
✓ Topic required (non-empty)
✓ Models validated against allowed list
✓ API keys not exposed in frontend
✓ Error messages sanitized
```

### API Security
```
✓ CORS middleware configured
✓ Request validation with Pydantic
✓ Error handling prevents info leaks
✓ All requests validated on backend
```

---

## 📚 Reference

For more details, see:
- `DEBATE_QUICK_START.md` - User guide
- `DEBATE_FEATURE.md` - Technical details
- `DEBATE_CODE_REFERENCE.md` - Code examples
- `IMPLEMENTATION_SUMMARY.md` - Overview
