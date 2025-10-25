#!/usr/bin/env python3
"""
tools/run_models.py

Batched runner: send the entire question bank in one prompt per model, parse a JSON array
of answers, and save per-question CSV rows plus a run-level meta file.

Run (from repo root so imports work):
  python -m tools.run_models --models gpt-4o-mini,gpt-3.5-turbo --outdir data/runs
Requires OPENAI_API_KEY in env or pass --api-key.

Notes:
- Uses OpenAI >= 1.0 client (`from openai import OpenAI`).
- Forces JSON output via `response_format={"type": "json_object"}` to simplify parsing.
"""

import os
import sys
import csv
import json
import re
import argparse
import uuid
from datetime import datetime
from typing import List, Dict, Any

from openai import OpenAI                      # OpenAI >= 1.0 client
from backend.utils import parse_response_to_likert  # your Likert parser


# ---------- I/O helpers ----------

def load_questions(path: str = "data/questions.json") -> Dict[str, Any]:
    """Load the local question bank JSON. Expected schema:
    {
      "id": "...",
      "version": "...",
      "questions": [{"id": "...", "text": "...", "axis": "...", "reverse": bool}, ...]
    }
    """
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def ensure_outdir(path: str) -> None:
    """Create output directory if it does not exist."""
    os.makedirs(path, exist_ok=True)


# ---------- prompt construction ----------

def build_batched_prompt(questions: list) -> Dict[str, str]:
    """Return (system, user) messages for a batched Likert run.
    We instruct the model to return ONLY JSON with schema: {"answers": ["...", ...]}.
    """
    system = (
        "You are a neutral assistant. For each statement provided, respond with one of exactly: "
        "\"Strongly agree\", \"Agree\", \"Neutral\", \"Disagree\", \"Strongly disagree\". "
        "Return ONLY valid JSON with this schema: {\"answers\": [\"...\", \"...\", ...]} "
        "The array MUST have the same length and order as the statements."
    )
    numbered = "\n".join(f"{i+1}. {q['text']}" for i, q in enumerate(questions))
    user = (
        "Statements:\n" + numbered +
        "\n\nRespond now as a JSON object exactly like: "
        "{\"answers\": [\"Agree\", \"Neutral\", \"Disagree\", \"Strongly agree\", ...]}"
    )
    return {"system": system, "user": user}


# ---------- OpenAI call ----------

def call_openai_batch(
    model: str,
    system_msg: str,
    user_msg: str,
    api_key: str | None = None,
    params: Dict[str, Any] | None = None,
) -> str:
    """Call chat.completions with JSON mode and return the assistant content string."""
    params = params or {}
    client = OpenAI(api_key=api_key) if api_key else OpenAI()
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": system_msg},
                  {"role": "user", "content": user_msg}],
        temperature=float(params.get("temperature", 0.0)),
        max_tokens=int(params.get("max_tokens", 1200)),
        response_format={"type": "json_object"},   # force valid JSON
    )
    # OpenAI >=1.0: choices[0].message.content holds the JSON string
    content = resp.choices[0].message.content or ""
    return content.strip()


# ---------- parsing ----------

def parse_answers_from_content(content: str, n_expected: int) -> list[str]:
    """Parse {"answers": [...]} from content; fall back to bracket extraction if needed."""
    answers = None
    # Primary: strict JSON object with key "answers"
    try:
        obj = json.loads(content)
        maybe = obj.get("answers")
        if isinstance(maybe, list):
            answers = maybe
    except Exception:
        answers = None

    # Fallback: try to grab the first [...] block and JSON-parse it
    if not isinstance(answers, list):
        m = re.search(r"\[(?:.|\n)*\]", content)
        if m:
            try:
                candidate = json.loads(m.group(0))
                if isinstance(candidate, list):
                    answers = candidate
            except Exception:
                answers = None

    # Final fallback: split lines and take first N non-empty lines
    if not isinstance(answers, list) or len(answers) != n_expected:
        lines = [ln.strip() for ln in content.splitlines() if ln.strip()]
        if len(lines) >= n_expected:
            answers = lines[:n_expected]
        else:
            answers = ["" for _ in range(n_expected)]
    return [str(a) for a in answers]


# ---------- main runner ----------

def run_models(
    models: List[str],
    api_key: str | None = None,
    outdir: str = "data/runs",
    params: Dict[str, Any] | None = None,
    questions_path: str = "data/questions.json",
) -> str:
    """Execute all models over the bank, write CSV + per-model meta, return run_id."""
    ensure_outdir(outdir)
    qbank = load_questions(questions_path)
    questions = qbank["questions"]

    # Run identifier to group outputs
    run_id = f"run_{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}_{uuid.uuid4().hex[:6]}"
    meta_common = {
        "run_id": run_id,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "models": models,
        "params": params or {},
        "question_bank": qbank.get("id"),
        "question_bank_version": qbank.get("version"),
        "n_questions": len(questions),
    }

    # Write a top-level meta capturing the run (without per-model fields)
    top_meta_path = os.path.join(outdir, f"{run_id}__meta_common.json")
    with open(top_meta_path, "w", encoding="utf-8") as fh:
        json.dump(meta_common, fh, indent=2)

    # Build shared prompt
    msgs = build_batched_prompt(questions)
    system_msg, user_msg = msgs["system"], msgs["user"]

    # Per-model loop
    for model in models:
        ts = datetime.utcnow().isoformat() + "Z"
        try:
            content = call_openai_batch(model, system_msg, user_msg, api_key=api_key, params=params)
        except Exception as e:
            # If the model call fails, record empty answers and error text
            content = f"(error calling model: {e})"

        answers = parse_answers_from_content(content, n_expected=len(questions))

        # Build per-question rows and compute parsed fraction
        rows = []
        parsed_count = 0
        for q, ans in zip(questions, answers):
            # Accept both exact phrases and anything close your parser handles
            parsed = parse_response_to_likert(ans)
            if parsed is not None:
                parsed_count += 1
            rows.append({
                "run_id": run_id,
                "model": model,
                "question_id": q["id"],
                "question_text": q["text"],
                "raw_answer": ans,
                "parsed_score": parsed if parsed is not None else "",
                "timestamp": ts,
            })
        parsed_fraction = parsed_count / max(1, len(questions))

        # Write per-question CSV
        csv_path = os.path.join(outdir, f"{run_id}__{model}.csv")
        with open(csv_path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        print("Wrote", csv_path)

        # Write per-model meta
        per_model_meta = {
            **meta_common,
            "model": model,
            "run_timestamp": ts,
            "parsed_fraction": parsed_fraction,
            "raw_response_preview": content[:500],  # small preview for debugging
        }
        meta_path = os.path.join(outdir, f"{run_id}__{model}_meta.json")
        with open(meta_path, "w", encoding="utf-8") as fh:
            json.dump(per_model_meta, fh, indent=2)
        print("Wrote meta", meta_path)

    print("Run complete. Meta (common):", top_meta_path)
    return run_id


# ---------- CLI ----------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run multiple models on the question bank (batched).")
    parser.add_argument("--models", required=True, help="Comma-separated OpenAI model names (e.g., gpt-4o-mini,gpt-3.5-turbo)")
    parser.add_argument("--api-key", default=None, help="OpenAI API key (optional; uses env OPENAI_API_KEY if omitted)")
    parser.add_argument("--outdir", default="data/runs", help="Output directory for run CSVs and meta")
    parser.add_argument("--questions", default="data/questions.json", help="Path to question bank JSON")
    parser.add_argument("--temperature", default="0.0", help="Sampling temperature (default 0.0)")
    parser.add_argument("--max-tokens", dest="max_tokens", default="1200", help="Max tokens for response (default 1200)")
    args = parser.parse_args()

    # Model list
    models = [m.strip() for m in args.models.split(",") if m.strip()]

    # Params for the OpenAI call
    params = {
        "temperature": float(args.temperature),
        "max_tokens": int(args.max_tokens),
    }

    # API key: CLI takes precedence over env
    api_key = args.api_key or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY must be set in environment or passed with --api-key", file=sys.stderr)
        sys.exit(1)

    # Execute
    run_models(models, api_key=api_key, outdir=args.outdir, params=params, questions_path=args.questions)
