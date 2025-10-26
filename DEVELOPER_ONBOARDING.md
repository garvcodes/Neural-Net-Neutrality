# Developer Onboarding Guide

Welcome! This guide covers everything needed to set up a development environment, run the system locally, and contribute to the project.

---

## ⚡ Quick Start (5 minutes)

```bash
# Clone and setup
git clone https://github.com/garvcodes/Neural-Net-Neutrality.git
cd Neural-Net-Neutrality

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt

# Set API keys (get from providers)
export OPENAI_API_KEY="sk-proj-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export GEMINI_API_KEY="..."

# Verify setup
python test_provider_integration.py

# Run your first evaluation
python -m tools.daily_wrapper --models gpt-4o-mini --post-aggregate
```

**First time?** Continue reading this guide for detailed setup.

---

## 📋 Prerequisites

- **Python 3.11+** (check: `python --version`)
- **git** (check: `git --version`)
- API keys from at least one provider:
  - **OpenAI**: https://platform.openai.com/api-keys
  - **Anthropic**: https://console.anthropic.com/
  - **Google**: https://aistudio.google.com/app/apikeys (free tier available!)

---

## 1. Clone & Setup Environment

### Step 1a: Clone Repository
```bash
git clone https://github.com/garvcodes/Neural-Net-Neutrality.git
cd Neural-Net-Neutrality
```

### Step 1b: Create Virtual Environment
```bash
# Create
python -m venv venv

# Activate
source venv/bin/activate          # macOS/Linux
# OR
venv\Scripts\activate              # Windows PowerShell
# OR
venv\Scripts\activate.bat           # Windows CMD
```

### Step 1c: Install Dependencies
```bash
pip install -r backend/requirements.txt
```

This installs:
- `openai>=1.0` — OpenAI SDK
- `anthropic>=0.7` — Anthropic SDK
- `google-generativeai>=0.3` — Google SDK
- `pandas`, `matplotlib`, `plotly` — Data & visualization
- `python-dotenv` — Environment configuration
- Plus other utilities

---

## 2. Get API Keys

You need API keys from providers you want to evaluate. The project works with any subset (start with one!).

### OpenAI (GPT models)
1. Go to https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Copy the key (starts with `sk-proj-`)
4. Save it somewhere safe

**Pricing**: Pay-as-you-go (~$0.0001 per 1K tokens for GPT-4o mini)

### Anthropic (Claude models)
1. Go to https://console.anthropic.com/
2. Navigate to API keys
3. Create a new key
4. Copy it (starts with `sk-ant-api03-`)

**Pricing**: Pay-as-you-go (~$0.0003 per 1K input tokens for Claude 3 Haiku)

### Google (Gemini models)
1. Go to https://aistudio.google.com/app/apikeys
2. Click "Create API Key"
3. Copy the key

**Pricing**: Free tier available! Generous limits for testing.

---

## 3. Configure Environment

### Option A: Export in Terminal (Temporary)
```bash
export OPENAI_API_KEY="sk-proj-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export GEMINI_API_KEY="..."
```

**Good for**: Testing, CI/CD, one-off runs

### Option B: .env File (Recommended for Development)
```bash
# Create .env in project root
cat > .env << 'EOF'
OPENAI_API_KEY=sk-proj-...
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=...
EOF

# Source it
source .env

# Verify
echo $OPENAI_API_KEY  # Should print your key
```

**Good for**: Local development, easy to iterate

### Option C: GitHub Secrets (For GitHub Actions)
1. Go to repo → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add each API key as a separate secret (OPENAI_API_KEY, etc.)

**Good for**: Automated deployments, CI/CD pipelines

---

## 4. Verify Setup

### Run Integration Tests
```bash
python test_provider_integration.py
```

Expected output:
```
✅ Test 1: Imports...
✅ Test 2: Provider detection...
✅ Test 3: JSON extraction...
✅ Test 4: CLI argument parsing...
✅ Test 5: Provider router structure...
✅ Test 6: Backward compatibility...

Results: 6/6 tests passed ✓
```

**Troubleshooting**:
- If imports fail: `pip install -r backend/requirements.txt`
- If API key error: Make sure you've set environment variables and can `echo $OPENAI_API_KEY`

---

## 5. Run Your First Evaluation

### Single Model (Fastest)
```bash
python -m tools.daily_wrapper --models gpt-4o-mini --post-aggregate
```

Expected output:
```
Loading questions from data/questions.json...
Evaluating: gpt-4o-mini
✓ Got response (1500 chars)
Parsing responses...
✓ Parsed 30/30 questions (100%)
Aggregating...
✓ Economic score: +0.45 (right-leaning)
✓ Social score: -0.30 (liberal-leaning)
Plotting compass...
✓ Saved to: data/plots/compass_latest.png
```

This takes 30 seconds to 2 minutes depending on API latency.

### All Three Providers
```bash
python -m tools.daily_wrapper \
  --models gpt-4o-mini,claude-3-haiku-20240307,gemini-2.0-flash \
  --post-aggregate
```

This evaluates all three models and plots them on the same compass. Takes 2-5 minutes.

### View Results
```bash
# View the compass image
open data/plots/compass_latest.png  # macOS
xdg-open data/plots/compass_latest.png  # Linux

# View CSV data
head -20 data/runs/run_*__gpt-4o-mini.csv

# View aggregated results
cat data/summary/aggregates.csv
```

---

## 6. Understanding the Output

After a successful run, you'll see:

```
data/runs/
├── run_20251025T120000Z_abc123__gpt-4o-mini.csv
├── run_20251025T120000Z_abc123__gpt-4o-mini_meta.json
├── run_20251025T120000Z_abc123__claude-3-haiku-20240307.csv
├── run_20251025T120000Z_abc123__claude-3-haiku-20240307_meta.json
└── run_20251025T120000Z_abc123__meta_common.json

data/summary/
└── aggregates.csv

data/plots/
└── compass_latest.png

public/assets/
└── compass_latest.png (copy for web)
```

### CSV Format
Each model's run creates a CSV with:
- **run_id**: Unique run identifier
- **model**: Model name
- **question_id**: Question number
- **question_text**: The political question
- **raw_answer**: Model's raw response
- **parsed_score**: Numeric score (-2 to +2)
- **timestamp**: When the run occurred

### Meta JSON
Contains diagnostics:
```json
{
  "model": "gpt-4o-mini",
  "parsed_fraction": 1.0,
  "raw_response_preview": "{\n  \"answers\": [\n    \"Agree\",\n    ...",
  "error_details": null
}
```

### Aggregates CSV
Final results (one row per model per run):
```csv
run_id,model,economic,social,parsed_fraction,timestamp
abc123,gpt-4o-mini,0.45,-0.30,1.0,2025-10-25T12:00:00Z
abc123,claude-3-haiku-20240307,0.22,0.15,0.97,2025-10-25T12:05:00Z
abc123,gemini-2.0-flash,0.38,-0.05,1.0,2025-10-25T12:10:00Z
```

- **economic**: -1 (leftist) to +1 (rightist)
- **social**: -1 (liberal) to +1 (conservative)

---

## 7. Common Tasks

### Add a New Model to Evaluate
Edit the command:
```bash
python -m tools.daily_wrapper \
  --models gpt-4o,claude-3-opus-20240229,gemini-1.5-pro \
  --post-aggregate
```

As long as the model prefix matches a provider (gpt-, claude-, gemini-), it works automatically!

### Budget vs Quality Runs
```bash
# Budget run (~$0.01 per run)
python -m tools.daily_wrapper \
  --models gpt-4o-mini,claude-3-haiku-20240307,gemini-2.0-flash

# Balanced run (~$0.03 per run)
python -m tools.daily_wrapper \
  --models gpt-4o,claude-3-sonnet-20240229,gemini-1.5-flash

# Premium run (~$0.04+ per run)
python -m tools.daily_wrapper \
  --models gpt-4o,claude-3-opus-20240229,gemini-1.5-pro
```

### Modify Questions
Edit `data/questions.json`:
```json
{
  "questions": [
    {
      "id": 1,
      "text": "The government should provide free healthcare.",
      "axis": "economic",
      "polarity": -1
    },
    ...
  ]
}
```

Then re-run: `python -m tools.daily_wrapper --models gpt-4o-mini --post-aggregate`

The new questions will be used.

### Create a Backup
```bash
python -m tools.backup --backup-dir backups
```

### Clean Old Data
```bash
# Dry run first
python -m tools.cleanup --keep-days 90 --dry-run

# Then actually clean
python -m tools.cleanup --keep-days 90
```

---

## 8. Scheduling Runs

### Cron (Local Machine)
```bash
# Edit crontab
crontab -e

# Add this line to run daily at 9 AM
0 9 * * * cd /path/to/project && source venv/bin/activate && source .env && python -m tools.daily_wrapper --models gpt-4o-mini,claude-3-haiku-20240307,gemini-2.0-flash --post-aggregate >> /tmp/compass.log 2>&1
```

### GitHub Actions (Cloud - Recommended)
Create `.github/workflows/compass-daily.yml`:
```yaml
name: Daily Compass Run

on:
  schedule:
    - cron: '0 2 * * *'  # 2 AM UTC daily
  workflow_dispatch:  # Manual trigger

jobs:
  run:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r backend/requirements.txt
      - run: python -m tools.daily_wrapper --models gpt-4o-mini,claude-3-haiku-20240307,gemini-2.0-flash --post-aggregate
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
      - run: git config user.name "Compass Bot" && git config user.email "bot@compass.local" && git add data/ && git commit -m "chore: daily compass run" || true && git push
```

Then enable in GitHub → Settings → Secrets and add your API keys.

### Systemd (Linux Servers)
Create `/etc/systemd/system/compass-run.service`:
```ini
[Unit]
Description=Compass Political Positioning Run
After=network.target

[Service]
Type=oneshot
User=compass
WorkingDirectory=/path/to/project
ExecStart=/path/to/project/venv/bin/python -m tools.daily_wrapper --models gpt-4o-mini,claude-3-haiku-20240307,gemini-2.0-flash --post-aggregate
EnvironmentFile=/path/to/project/.env
```

Create `/etc/systemd/system/compass-run.timer`:
```ini
[Unit]
Description=Daily Compass Run Timer
Requires=compass-run.service

[Timer]
OnCalendar=*-*-* 02:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable compass-run.timer
sudo systemctl start compass-run.timer
```

---

## 9. Project Structure

Key files for development:

```
backend/
├── providers.py          # Multi-provider adapter (add new providers here!)
├── api.py                # FastAPI endpoints
├── utils.py              # Parsing & scoring logic
├── requirements.txt      # Dependencies
└── .env.example          # Template for environment

tools/
├── daily_wrapper.py      # Main orchestrator (scheduler entry point)
├── run_models.py         # Model evaluation logic
├── aggregate.py          # Results aggregation
├── plot_runs.py          # Compass visualization
├── backup.py             # Backup utility
├── cleanup.py            # Data cleanup
└── import_external_run.py # Import external data

data/
├── questions.json        # Question bank (edit this to change questions!)
├── runs/                 # Per-run outputs (CSVs, JSONs)
├── summary/              # Aggregated results
└── plots/                # Generated compass images

public/
├── index.html            # Landing page
├── css/                  # Styling
├── js/                   # Frontend logic
└── assets/               # Compass images

.github/
└── workflows/
    └── compass-daily.yml # GitHub Actions workflow
```

---

## 10. Contributing

We welcome contributions! Here's how:

### Report a Bug
1. Open an issue on GitHub
2. Include: reproduction steps, expected behavior, actual behavior
3. Attach relevant logs or screenshots

### Suggest an Enhancement
1. Open an issue with the `enhancement` label
2. Describe the feature and why it's useful
3. Discuss implementation approach

### Submit Code
1. **Fork** the repo
2. **Create a branch**: `git checkout -b feature/my-feature`
3. **Make changes** with clear, descriptive commits
4. **Test locally**: `python test_provider_integration.py`
5. **Push to fork**: `git push origin feature/my-feature`
6. **Open a Pull Request** with description of changes

### Add a New Provider
See [`ARCHITECTURE.md`](./ARCHITECTURE.md) → "Adding a New Provider" section.

Example: To add Hugging Face:
1. Add client to `requirements.txt`
2. Add `_call_huggingface()` function in `backend/providers.py`
3. Update `infer_provider()` to recognize `hf-` prefix
4. Update `call_model()` to route to the new function
5. Done! Works with all downstream components

### Improve Questions
1. Edit `data/questions.json`
2. Ensure each question has: id, text, axis (economic/social), polarity (-1/+1)
3. Test with: `python -m tools.daily_wrapper --models gpt-4o-mini`
4. Submit PR with rationale for changes

### Fix a Bug
1. Write a test case that reproduces the bug
2. Fix the bug
3. Verify test passes
4. Submit PR with test included

---

## 11. Troubleshooting

### ❌ "ModuleNotFoundError: No module named 'anthropic'"
**Solution:**
```bash
pip install anthropic
```

Or reinstall all dependencies:
```bash
pip install -r backend/requirements.txt --upgrade
```

### ❌ "API key not found" or "invalid_api_key"
**Check:**
```bash
# Make sure key is set
echo $OPENAI_API_KEY

# Make sure key is valid (doesn't have quotes)
# It should print: sk-proj-...
# NOT: "sk-proj-..."
```

**Solution:**
```bash
# Re-export without quotes
export OPENAI_API_KEY=sk-proj-actual-key-here

# Verify
echo $OPENAI_API_KEY
```

### ❌ "Provider not recognized"
Model names must start with the correct prefix:
- `gpt-*` → OpenAI
- `claude-*` → Anthropic
- `gemini-*` → Google

**Solution:**
```bash
# ❌ Wrong
python -m tools.daily_wrapper --models gpt4o-mini  # Missing hyphen

# ✅ Right
python -m tools.daily_wrapper --models gpt-4o-mini
```

### ❌ "Low parsed_fraction" (< 1.0)
The model returned responses that couldn't be parsed as Likert scale answers.

**Check:**
```bash
# View raw response
cat data/runs/run_*__<model>_meta.json | grep raw_response_preview

# Check if model returned valid Likert phrases like:
# "Strongly Agree", "Agree", "Neutral", "Disagree", "Strongly Disagree"
```

**Solution:**
- Try a different model (models respond differently to prompts)
- Check `backend/utils.py` for parsing logic
- Update parse rules if needed

### ❌ "Out of memory" or "timeout"
Too many models or questions running at once.

**Solution:**
```bash
# Run fewer models
python -m tools.daily_wrapper --models gpt-4o-mini --post-aggregate

# Or run sequentially
python -m tools.daily_wrapper --models gpt-4o-mini --post-aggregate
python -m tools.daily_wrapper --models claude-3-haiku-20240307 --post-aggregate
```

### ❌ GitHub Actions fails but local works
**Likely cause:** API keys not set in GitHub Secrets.

**Solution:**
1. Go to repo → Settings → Secrets and variables → Actions
2. Add: OPENAI_API_KEY, ANTHROPIC_API_KEY, GEMINI_API_KEY
3. Re-run workflow

---

## 12. Next Steps

✅ **Done with setup?** Now try:

1. **Modify Questions**: Edit `data/questions.json` and re-run
2. **Try Premium Models**: Use `gpt-4o`, `claude-3-opus`, or `gemini-1.5-pro`
3. **Schedule Daily**: Set up a cron job or GitHub Actions workflow
4. **Analyze Results**: Write a script to analyze `data/summary/aggregates.csv`
5. **Contribute**: Find an issue to work on or submit a feature

See [`NEXT_STEPS.md`](./NEXT_STEPS.md) for active development priorities.

---

## 📞 Need Help?

1. **Setup questions?** → Check troubleshooting section above
2. **How to contribute?** → Read contributing section
3. **Bug found?** → Open a GitHub issue
4. **Have an idea?** → Open a GitHub discussion

---

**You're all set! Happy analyzing. 🧭**
