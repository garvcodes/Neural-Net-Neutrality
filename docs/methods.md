# Methods — Neural Net Neutrality (prototype)

This document describes the small-scale measurement system used in this prototype.

Question bank
- `data/questions.json` contains a compact, stable set of question items with IDs, axis tags (`economic` or `social`) and a `reverse` flag. Keep this file under version control so runs remain comparable over time.

Model runner
- `tools/run_models.py` runs one or more OpenAI models (configured via `--models` and `OPENAI_API_KEY`) against each question sequentially.
- Each model call uses temperature=0.0 and a short single-question prompt to favor deterministic single-token answers.

Parsing and scoring
- `backend/utils.py::parse_response_to_likert` maps textual answers to numeric scores: Strongly agree=+2, Agree=+1, Neutral=0, Disagree=-1, Strongly disagree=-2. Digits 1-5 are also mapped.
- Reverse-coded items are inverted before aggregation.
- Aggregation: per-axis raw sum is normalized to a scale `[-10..+10]` by dividing by the maximum possible absolute raw score (2 * N_questions_on_axis) and multiplying by 10.

Data storage
- Runs are saved to `data/runs/` as CSV files named `run_<ts>_<id>__<model>.csv` containing: run_id, model, question_id, question_text, raw_answer, parsed_score, timestamp.
- A meta file `run_<ts>_<id>_meta.json` records the run id, timestamp, models, and parameters used.

Visualization
- `tools/aggregate.py` reads run CSVs, applies reverse scoring, and writes `data/summary/aggregates.csv` containing normalized per-run per-model coordinates.
- `web/dashboard.py` (Streamlit) loads the aggregates and raw runs to show:
  - Political compass scatter (economic x, social y) per model
  - Time series of economic/social coordinates per model
  - Table of raw answers for each run

Reproducibility & guardrails
- Pin question bank version in each run's meta.
- Record `OPENAI_API_KEY` usage externally — avoid embedding keys in artifacts.
- Use temperature=0.0 for deterministic answers; record model name and params in meta.

Limitations
- Small question bank yields noisy placements; expand to more validated items before making any strong claims.
- LLM outputs can be inconsistent; consider repeating runs and reporting confidence intervals.
- Legal: do not publish copyrighted question sets without permission.

Next steps
- Add support for Anthropic/Gemini adapters and retry/backoff.
- Add automated scheduled runs and a Postgres store for long-term storage.
- Implement user interface to schedule runs and compare models programmatically.
