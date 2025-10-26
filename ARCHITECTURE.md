# Political Compass Multi-Provider Architecture

## Visual Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      User Interface                              │
│  CLI: tools/daily_wrapper.py or tools/run_models.py             │
│  Example: --models gpt-4o-mini,claude-3-sonnet,gemini-2.0      │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│              Provider Router & Dispatcher                        │
│                backend/providers.py                             │
│                                                                  │
│  ┌─ infer_provider(model_name) ──┐                              │
│  │  • gpt-* → "openai"           │                              │
│  │  • claude-* → "anthropic"      │                              │
│  │  • gemini-* → "gemini"         │                              │
│  └────────────────────────────────┘                              │
│                                                                  │
│  ┌─ call_model(model, ..., provider) ──────────┐                │
│  │                                              │                │
│  │  Dispatch based on provider:                 │                │
│  │                                              │                │
│  ├─→ _call_openai()                            │                │
│  │    • from openai import OpenAI               │                │
│  │    • client.chat.completions.create()        │                │
│  │                                              │                │
│  ├─→ _call_anthropic()                         │                │
│  │    • import anthropic                        │                │
│  │    • client.messages.create()                │                │
│  │                                              │                │
│  └─→ _call_gemini()                            │                │
│       • import google.generativeai              │                │
│       • genai.GenerativeModel()                 │                │
│                                                                  │
│  extract_json_answers(response_text)                             │
│  • Robust parsing of JSON, fallback strategies                   │
└──────────────────┬───────────────────────────────────────────────┘
                   │
         ┌─────────┼─────────┐
         │         │         │
         ▼         ▼         ▼
    ┌────────┐ ┌────────┐ ┌────────┐
    │  GPT   │ │ Claude │ │ Gemini │
    │ Model  │ │ Model  │ │ Model  │
    │ Call   │ │ Call   │ │ Call   │
    └────────┘ └────────┘ └────────┘
         │         │         │
         └─────────┼─────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────────┐
│              Uniform Response Processing                        │
│                                                                  │
│  parse_answers_from_content(content, n_expected)               │
│  • Extract JSON (array or object)                               │
│  • Sanitize answers (unquote, remove numbering)                │
│  • Return list of answer strings                                │
└──────────────────┬───────────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────────┐
│              CSV Output (Provider-Agnostic)                     │
│                                                                  │
│  data/runs/run_<timestamp>__<model>.csv                         │
│  ├─ run_id, model, question_id, question_text                  │
│  ├─ raw_answer, parsed_score, timestamp                         │
│  └─ (one row per question)                                      │
│                                                                  │
│  data/runs/run_<timestamp>__<model>_meta.json                   │
│  ├─ model, parsed_fraction, raw_response_preview               │
│  └─ (metadata for this model's run)                             │
└──────────────────┬───────────────────────────────────────────────┘
                   │
         ┌─────────┼─────────┐
         │         │         │
         ▼         ▼         ▼
    ┌────────┐ ┌────────┐ ┌────────┐
    │   GPT  │ │ Claude │ │ Gemini │
    │  CSV   │ │  CSV   │ │  CSV   │
    │        │ │        │ │        │
    └────────┘ └────────┘ └────────┘
         │         │         │
         └─────────┼─────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────────┐
│              Aggregation (Provider-Agnostic)                   │
│                tools/aggregate.py                               │
│                                                                  │
│  For each model:                                                │
│  1. Load per-question parsed_scores                             │
│  2. Group by axis (economic, social)                            │
│  3. Apply polarity (✓ agree left, ✗ agree right)               │
│  4. Normalize by max possible score                             │
│  5. Output: (econ_norm, soc_norm) ∈ [-1, +1]²                 │
│                                                                  │
│  Output: data/summary/aggregates.csv                            │
│  ├─ run_id, model, x (economic), y (social)                   │
│  ├─ parsed_fraction, timestamp                                  │
│  └─ (one row per model per run)                                │
└──────────────────┬───────────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────────┐
│              Plotting (Provider-Agnostic)                       │
│                tools/plot_runs.py                                │
│                                                                  │
│  For each model in aggregates.csv:                              │
│  • Plot (x, y) on 2D compass                                    │
│  • Label with model name                                        │
│  • Include time-series for trend tracking                       │
│                                                                  │
│  Output: data/plots/compass_latest.png                          │
│         assets/compass_latest.png (copy)                │
│                                                                  │
│  ┌──────────────────────────┐                                   │
│  │   POLITICAL COMPASS      │                                   │
│  │                          │                                   │
│  │    (Left)  ← econ →      │                                   │
│  │      ●                   │  ● gpt-4o-mini                   │
│  │  ●●●                     │  ● claude-3-sonnet               │
│  │   ●  ●                   │  ● gemini-2.0-flash              │
│  │                          │                                   │
│  │      ↑ social ↓          │                                   │
│  └──────────────────────────┘                                   │
└──────────────────────┬───────────────────────────────────────────┘
                       │
                       ▼
         ┌─────────────────────────┐
         │  Landing Page           │
         │  index.html      │
         │  (display compass)      │
         └─────────────────────────┘
```

## Data Flow Example

**Input**: `--models gpt-4o-mini,claude-3-sonnet-20240229,gemini-2.0-flash`

**Step 1**: Provider detection
```
gpt-4o-mini              → openai
claude-3-sonnet-20240229 → anthropic
gemini-2.0-flash         → gemini
```

**Step 2**: Model calls (in parallel-friendly manner)
```
gpt-4o-mini:
  call_openai("gpt-4o-mini", system, user, api_key=OPENAI_API_KEY)
  → {"answers": ["Agree", "Disagree", "Neutral", ...]}

claude-3-sonnet-20240229:
  call_anthropic("claude-3-sonnet-20240229", system, user, api_key=ANTHROPIC_API_KEY)
  → "["Disagree", "Neutral", "Agree", ...]"

gemini-2.0-flash:
  call_gemini("gemini-2.0-flash", system, user, api_key=GEMINI_API_KEY)
  → ["Strongly agree", "Agree", "Neutral", ...]
```

**Step 3**: Parsing (identical for all)
```
parse_answers_from_content(response, n_expected=30)
→ ["Agree", "Disagree", "Neutral", ...]

parse_response_to_likert("Agree")
→ +1
```

**Step 4**: Per-run CSV output (identical format)
```
data/runs/run_20251025T120000Z_abc123__gpt-4o-mini.csv
data/runs/run_20251025T120000Z_abc123__claude-3-sonnet-20240229.csv
data/runs/run_20251025T120000Z_abc123__gemini-2.0-flash.csv

All have same schema:
run_id, model, question_id, question_text, raw_answer, parsed_score, timestamp
```

**Step 5**: Aggregation
```
Read all 3 CSVs
Normalize scores per axis
Write to: data/summary/aggregates.csv

run_id, model, x, y, parsed_fraction, timestamp
..., gpt-4o-mini, +0.45, -0.30, 1.0, ...
..., claude-3-sonnet-20240229, +0.22, +0.15, 0.97, ...
..., gemini-2.0-flash, +0.38, -0.05, 1.0, ...
```

**Step 6**: Plotting
```
Plot three points on compass:
  • gpt-4o-mini @ (+0.45, -0.30)
  • claude-3-sonnet @ (+0.22, +0.15)
  • gemini-2.0-flash @ (+0.38, -0.05)

Output: assets/compass_latest.png
```

## Key Invariants

1. **Provider detection is automatic** — no manual routing needed
2. **Response parsing is universal** — all responses go through the same pipeline
3. **CSV format is provider-agnostic** — aggregator doesn't care where data came from
4. **Plotting treats all models equally** — compass displays all points the same way
5. **New providers require minimal code** — just add a `_call_newprovider()` function and update `infer_provider()` and `call_model()`

## Example Commands

### Run all three providers (cheapest models)
```bash
python -m tools.daily_wrapper --models gpt-4o-mini,claude-3-haiku-20240307,gemini-2.0-flash
```

### Run all three providers (highest quality)
```bash
python -m tools.daily_wrapper --models gpt-4o,claude-3-opus-20240229,gemini-1.5-pro
```

### OpenAI only (backward compatible)
```bash
python -m tools.run_models --models gpt-4o-mini,gpt-4o,gpt-3.5-turbo --post-aggregate
```

### Mixed with explicit API keys
```bash
python -m tools.run_models \
  --models gpt-4o-mini,claude-3-sonnet-20240229 \
  --api-key-openai "$OPENAI_API_KEY" \
  --api-key-anthropic "$ANTHROPIC_API_KEY" \
  --post-aggregate
```

### Just run Gemini to test
```bash
python -m tools.run_models \
  --models gemini-2.0-flash \
  --api-key-gemini "$GEMINI_API_KEY" \
  --post-aggregate
```

## Failure Modes & Recovery

| Issue | Cause | Recovery |
|-------|-------|----------|
| `API key not found` | Missing env var | Set `export OPENAI_API_KEY=...` |
| `Provider not recognized` | Typo in model name | Check model name prefix (gpt-, claude-, gemini-) |
| `JSON parse error` | Response wasn't JSON | Check `raw_response_preview` in meta; report to provider |
| `Low parsed_fraction` | Likert parsing failed | Verify model is returning Likert phrases; check backend/utils.py |
| `Compass is centrist` | Parsed fraction < 1.0 or polarity inverted | Check data/summary/aggregates.csv; verify questions.json polarity values |

## Adding a New Provider (Template)

To add support for a new LLM provider (e.g., Hugging Face, Together AI):

1. **Add provider client to requirements.txt**:
   ```
   new-provider-lib>=1.0
   ```

2. **Add to `backend/providers.py`**:
   ```python
   def _call_newprovider(model, system_msg, user_msg, api_key=None, params=None):
       import new_provider_lib
       api_key = api_key or os.environ.get("NEWPROVIDER_API_KEY")
       if not api_key:
           raise RuntimeError("NEWPROVIDER_API_KEY not found")
       # ... call the API, return response text
       return response_text
   ```

3. **Update `infer_provider()` in `backend/providers.py`**:
   ```python
   def infer_provider(model: str) -> str:
       if model.startswith("newprovider-"):
           return "newprovider"
       # ... other cases
   ```

4. **Update `call_model()` in `backend/providers.py`**:
   ```python
   elif provider == "newprovider":
       return _call_newprovider(model, system_msg, user_msg, api_key, params)
   ```

5. **Update CLI in `tools/run_models.py` and `tools/daily_wrapper.py`**:
   ```python
   parser.add_argument("--api-key-newprovider", default=None, help="...")
   ```

6. **Done** — the rest of the pipeline handles it automatically!

---

**That's it!** The multi-provider architecture is designed to be extensible with minimal effort.
