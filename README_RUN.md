# Running the measurement prototype

Quick steps to run a measurement against the small question bank and preview results.

1. Install dependencies

```bash
cd /Users/gg027/Desktop/NNN/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install
```

2. Start the API (optional — not required to run `tools/run_models.py` which calls OpenAI directly)

```bash
uvicorn backend.api:app --reload
```

3. Run the models (example)

```bash
python tools/run_models.py --models gpt-4o-mini,gpt-3.5-turbo --api-key "$OPENAI_API_KEY"
```

4. Aggregate results

```bash
python tools/aggregate.py --indir data/runs --out data/summary/aggregates.csv
```

5. Start the dashboard

```bash
streamlit run web/dashboard.py
```

Files produced
- `data/runs/` — per-run CSV files and meta JSON
- `data/summary/aggregates.csv` — per-run per-model normalized coordinates
