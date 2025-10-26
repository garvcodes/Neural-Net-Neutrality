````markdown
# Neural Net Neutrality 🧭

**Track how LLM political leanings evolve — clearly and fairly.**

Neural Net Neutrality is an open, reproducible system for monitoring and visualizing how large language models' political leanings shift over time. It evaluates multiple LLM providers (OpenAI, Anthropic, Google) across a consistent set of political positioning questions, aggregates results into compass coordinates, and makes data available for research and auditing.

---

## 🎯 Research Goals

This project exists to answer critical questions about AI alignment and model behavior:

1. **Political Bias in LLMs**: Do language models exhibit consistent political biases? If so, how strong are they and do they vary by provider?

2. **Temporal Drift**: How do model positions shift over time? Do newer versions move toward or away from political extremes?

3. **Provider Differences**: Do different LLM providers (OpenAI vs Anthropic vs Google) show significantly different political leanings?

4. **Transparency & Accountability**: How can we create reproducible, auditable methods for measuring AI political alignment that are accessible to researchers and the public?

5. **Bias Detection Methodology**: What is the best approach to measuring political bias in language models using structured, scalable surveys?

This work contributes to:
- **AI Safety**: Understanding model behavior across the political spectrum
- **Responsible AI**: Auditing and monitoring model drift
- **Research Transparency**: Making methodology and data open and reproducible
- **Policy & Governance**: Informing discussions about AI regulation and oversight

[![Status](https://img.shields.io/badge/status-production%20ready-green)]()
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue)](https://www.python.org/)

---

## 🚀 Quick Start

### Option 1: GitHub Actions (Recommended - 15 minutes)

1. **Add API Keys**
   ```
   Settings → Secrets and variables → Actions
   Add: OPENAI_API_KEY, ANTHROPIC_API_KEY, GEMINI_API_KEY, and whatever else
   ```

2. **Run Workflow**
   ```
   Actions → Daily Compass Run → Run workflow
   ```

3. **Verify Output**
   ```bash
   git pull
   ls data/runs/run_*.csv
   cat public/assets/compass_latest.png  # View latest compass
   ```

### Option 2: Local/Self-Hosted

```bash
# Install dependencies
pip install -r backend/requirements.txt

# Run with single provider
python -m tools.daily_wrapper --models gpt-4o-mini --post-aggregate

# Or all providers
python -m tools.daily_wrapper \
  --models gpt-4o-mini,claude-3-haiku-20240307,gemini-2.0-flash \
  --post-aggregate
```

**First time?** → Read [`PRODUCTION_QUICKSTART.md`](./PRODUCTION_QUICKSTART.md) (30 min setup guide)

---

## ✨ Features

### 📊 Multi-Provider Support
- **OpenAI**: GPT-4o, GPT-4o mini, and other models
- **Anthropic**: Claude 3 family (Opus, Sonnet, Haiku)
- **Google**: Gemini models (2.0 Flash, 1.5 Pro, etc.)

All providers evaluated with the same questions, same methodology.

### 🧭 Political Compass
Results plotted on a 2D compass:
- **X-axis (Economic)**: Left ↔ Right
- **Y-axis (Social)**: Liberal ↔ Conservative

Visualize model positions and drift over time.

### 📈 Longitudinal Tracking
- Daily (or scheduled) evaluation runs
- Historical data aggregated and visualized
- Time-series charts showing drift
- Downloadable CSV data for analysis

### 🔍 Transparency & Reproducibility
- Open-source code (MIT license)
- Prompts and questions versioned in git
- Raw response data stored alongside results
- Full audit trail of methodology

### 🔐 Security & Privacy
- API keys stored securely (GitHub Secrets or .env)
- No data sent to external services
- Backups and disaster recovery procedures
- Regular key rotation support

### ⚡ Low Cost & Automation
- ~$0.30/month to run all three providers daily
- Fully automated scheduling (GitHub Actions or cron)
- Minimal infrastructure required
- Scales easily to more models

---

## 📋 What's Inside

```
Neural-Net-Neutrality/
├── README.md                              # This file
├── PRODUCTION_QUICKSTART.md               # ⭐ Get started in 30 min
├── PRODUCTION_SETUP.md                    # Complete deployment guide
├── DEPLOYMENT_CHECKLIST.md                # Pre-launch validation
├── RUNBOOK.md                             # Daily operations
├── PRODUCTION_INDEX.md                    # Master index
│
├── backend/
│   ├── providers.py                       # Multi-provider adapter
│   ├── api.py                             # FastAPI endpoints
│   ├── utils.py                           # Parsing & scoring
│   └── requirements.txt                   # Python dependencies
│
├── tools/
│   ├── daily_wrapper.py                   # Main orchestrator
│   ├── run_models.py                      # Model evaluation
│   ├── aggregate.py                       # Results aggregation
│   ├── plot_runs.py                       # Compass generation
│   ├── backup.py                          # Backup utility
│   ├── cleanup.py                         # Data retention
│   └── ...
│
├── data/
│   ├── questions.json                     # Question bank
│   ├── runs/                              # Per-run results
│   ├── summary/                           # Aggregated data
│   └── plots/                             # Generated charts
│
├── public/
│   ├── index.html                         # Landing page
│   ├── css/styles.css                     # Styling
│   ├── js/main.js                         # Frontend logic
│   └── assets/
│       └── compass_latest.png             # Latest compass
│
└── .github/
    └── workflows/
        └── compass-daily.yml              # GitHub Actions workflow
```

---

## 🏃 Running Evaluations

### Quick Single Model Test
```bash
python -m tools.daily_wrapper --models gpt-4o-mini
```

### Multiple Models (All Providers)
```bash
python -m tools.daily_wrapper \
  --models gpt-4o-mini,claude-3-haiku-20240307,gemini-2.0-flash \
  --post-aggregate
```

### Custom Model Selection
```bash
python -m tools.daily_wrapper \
  --models gpt-4o,claude-3-sonnet-20240229,gemini-1.5-pro \
  --post-aggregate
```

### Output Files
```
data/runs/run_20251025T234436Z_abc123__gpt-4o-mini.csv
data/runs/run_20251025T234436Z_abc123__gpt-4o-mini_meta.json
data/summary/aggregates.csv
data/plots/compass_latest.png
public/assets/compass_latest.png
```

---

## 📊 Understanding Results

### Compass Coordinates
Each model gets plotted on a 2D compass:

```
        Liberal
          ↑
    TL ← + → TR
          |
    -----+-----→ Economic Spectrum
          |
    BL ← + → BR
          ↓
      Conservative
```

- **X (Economic)**: -1 (left/redistributive) to +1 (right/free market)
- **Y (Social)**: -1 (liberal/progressive) to +1 (conservative/traditional)

### CSV Format
```csv
run_id,model,economic,social,parsed_fraction,run_timestamp
abc123,gpt-4o-mini,0.45,-0.15,1.0,2025-10-25T23:44:36Z
abc123,claude-3-haiku-20240307,0.32,0.22,1.0,2025-10-25T23:44:36Z
```

### Diagnostics
- **parsed_fraction**: Percentage of questions successfully parsed (1.0 = 100%)
- **raw_response_preview**: First 200 chars of model's raw response
- **error_details**: Any errors during evaluation

---

## 🔧 Setup & Deployment

### Quick Start (5 minutes)
```bash
# Clone and setup
git clone https://github.com/garvcodes/Neural-Net-Neutrality.git
cd Neural-Net-Neutrality
python -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt

# Set API keys
export OPENAI_API_KEY="sk-proj-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export GEMINI_API_KEY="..."

# Run a test
python -m tools.daily_wrapper --models gpt-4o-mini --post-aggregate
```

See [`DEVELOPER_ONBOARDING.md`](./DEVELOPER_ONBOARDING.md) for detailed setup, troubleshooting, and how to contribute.

### Scheduling (Pick One)

**GitHub Actions** (Easiest - free, no server needed):
```bash
# Add secrets to GitHub repo
# Settings → Secrets and variables → Actions
# Add: OPENAI_API_KEY, ANTHROPIC_API_KEY, GEMINI_API_KEY

# Then go to Actions tab → Daily Compass Run → Run workflow
```

**Local Cron**:
```bash
0 9 * * * cd /path/to/project && source venv/bin/activate && python -m tools.daily_wrapper
```

**Systemd** (Linux servers):
```bash
# See DEVELOPER_ONBOARDING.md for service file templates
```

---

## 💰 Cost Estimates

### Monthly Cost (30 daily runs)
| Provider | Cost | Notes |
|----------|------|-------|
| OpenAI | $0.10-0.15 | gpt-4o-mini (most economical) |
| Anthropic | $0.15-0.20 | claude-3-haiku |
| Google | $0.03-0.05 | gemini-2.0-flash |
| **Total** | **~$0.30-0.40** | Very economical |

### Infrastructure Cost
- **GitHub Actions**: $0 (free tier)
- **Self-Hosted**: $0-100/month (depends on VM)
- **Storage**: Minimal (few MB/month)

---

## 🔐 Security & Privacy

### Data Protection
- ✅ API keys stored securely (GitHub Secrets or .env)
- ✅ No API keys logged or exposed
- ✅ Data stays in your repo/server
- ✅ Backup and restore procedures
- ✅ Disaster recovery plans

### Key Rotation
- Rotate API keys quarterly (or as needed)
- Update in GitHub Secrets or .env
- No restart required

### Access Control
- GitHub: Use branch protection and CODEOWNERS
- Self-Hosted: Use systemd user permissions

See [`PRODUCTION_SETUP.md`](./PRODUCTION_SETUP.md) Section 6 for security details.

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [`ARCHITECTURE.md`](./ARCHITECTURE.md) | System design, data flow, and extensibility |
| [`DEVELOPER_ONBOARDING.md`](./DEVELOPER_ONBOARDING.md) | Setup, running locally, and contributing |
| [`NEXT_STEPS.md`](./NEXT_STEPS.md) | Active development roadmap |

---

## 🛠️ Available Commands

### Evaluation
```bash
# Run models and aggregate
python -m tools.daily_wrapper --models gpt-4o-mini,claude-3-haiku-20240307

# Run without aggregation
python -m tools.run_models --models gpt-4o-mini

# Run and generate plots
python -m tools.daily_wrapper --models gpt-4o-mini --post-aggregate
```

### Data Management
```bash
# Create backup
python -m tools.backup --backup-dir backups

# List backups
python -m tools.backup --backup-dir backups --list

# Clean up old data (90-day retention)
python -m tools.cleanup --keep-days 90 --dry-run
python -m tools.cleanup --keep-days 90 --storage-report
```

### Utilities
```bash
# View aggregated results
tail -10 data/summary/aggregates.csv

# Check latest run metadata
cat data/runs/run_*_meta_common.json | jq

# View compass image
open data/plots/compass_latest.png  # macOS
xdg-open data/plots/compass_latest.png  # Linux
```

---

## 🆘 Troubleshooting

### API Key Issues
```bash
# Verify key is set
echo $OPENAI_API_KEY

# Test API connection
python -c "from openai import OpenAI; print(OpenAI().models.list())"
```

### Model Not Found
Check provider dashboard for latest model names and availability.

### Memory Issues
Run fewer models per batch:
```bash
# Instead of all at once
python -m tools.daily_wrapper \
  --models gpt-4o-mini,claude-3-haiku-20240307 \
  --post-aggregate
```

### More Issues?
See [`RUNBOOK.md`](./RUNBOOK.md) for comprehensive troubleshooting.

---

## 🤝 Contributing

We welcome contributions! Ways to help:

1. **Report Issues**: Found a bug? Open an issue
2. **Suggest Questions**: Have better questions? Propose updates to `data/questions.json`
3. **Add Models**: Want to track a new model? Update the model list
4. **Improve Docs**: Documentation improvements always welcome
5. **Add Features**: New analysis or visualizations? We'd love PRs

---

## 📖 Methodology

The system works in 5 steps:

1. **Question Bank** (`data/questions.json`)
   - 40 political positioning questions
   - Each question maps to economic or social axis
   - Each has polarity (+1 or -1) indicating direction

2. **Batched Prompt**
   - All questions sent to model in one request
   - Strict JSON response format
   - Temperature set to 0.0 (deterministic)

3. **Response Parsing**
   - Extract Likert responses (Strongly agree to Strongly disagree)
   - Map to numeric scores (-2 to +2)
   - Handle parsing errors gracefully

4. **Aggregation**
   - Sum contributions per axis
   - Normalize by max possible score
   - Produce values in [-1, +1] range

5. **Visualization**
   - Plot on 2D compass
   - Generate time-series charts
   - Export data for analysis

See [`docs/methods.md`](./docs/methods.md) for detailed methodology.

---

## 📊 Live Example

Latest compass visualization (updated daily):

![Latest Compass](public/assets/compass_latest.png?raw=true)

View the [interactive dashboard](public/index.html) for real-time results.

---

## ⚙️ Monitoring

### GitHub Actions
- Dashboard: `Actions` tab
- Status: Green ✅ (success) or Red ❌ (failure)
- Notifications: Email from GitHub

### Self-Hosted
- Logs: `sudo journalctl -u compass-run.service`
- Status: `sudo systemctl status compass-run.timer`

### Optional Integrations
- **Sentry**: Error tracking
- **Healthchecks.io**: Ping monitoring

---

## 📄 License

MIT License - See [`LICENSE`](LICENSE) file for details.

---

## 📞 Support

**Getting Started?**
→ Read [`PRODUCTION_QUICKSTART.md`](./PRODUCTION_QUICKSTART.md)

**Questions?**
→ Check [`RUNBOOK.md`](./RUNBOOK.md) troubleshooting section

**Before Production?**
→ Use [`DEPLOYMENT_CHECKLIST.md`](./DEPLOYMENT_CHECKLIST.md)

**Need Details?**
→ See [`PRODUCTION_SETUP.md`](./PRODUCTION_SETUP.md)

---

## 🏆 Status

✅ **Production Ready** - Deploy today  
✅ **Multi-Provider** - OpenAI, Anthropic, Google  
✅ **Well Documented** - 7 comprehensive guides  
✅ **Fully Tested** - Integration tests passing  
✅ **Cost Effective** - ~$0.30/month  

---

**Built for transparency in AI.**  
Last updated: October 25, 2025
