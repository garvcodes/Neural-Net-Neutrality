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
from datetime import datetime, timezone
from typing import List, Dict, Any

from backend.utils import parse_response_to_likert  # your Likert parser
from backend.providers import call_model, extract_json_answers  # multi-provider support


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


# ---------- Multi-provider call ----------

def call_model_batch(
    model: str,
    system_msg: str,
    user_msg: str,
    api_key: str | None = None,
    params: Dict[str, Any] | None = None,
) -> str:
    """Call any LLM (OpenAI GPT, Anthropic Claude, Google Gemini) and return assistant content.
    
    Provider is auto-detected from model name:
      - gpt-*, o1-* -> OpenAI
      - claude-* -> Anthropic
      - gemini-* -> Google
    
    Requires appropriate API key in env or passed as api_key param.
    """
    return call_model(model, system_msg, user_msg, api_key=api_key, params=params)

# ---------- parsing ----------

def parse_answers_from_content(content: str, n_expected: int) -> list[str]:
    """Parse {"answers": [...]} from content; fall back to bracket extraction if needed.
    Robustly sanitize returned items so they match the Likert parser in backend/utils.py.
    """
    answers = None
    # Primary: strict JSON object with key "answers"
    try:
        obj = json.loads(content)
        maybe = obj.get("answers") if isinstance(obj, dict) else None
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
            # attempt to parse comma/quoted CSV-like lists inside the content
            parts = re.split(r',\s*(?=(?:[^"]*"[^"]*")*[^"]*$)', content)
            parts = [p.strip() for p in parts if p.strip()]
            if len(parts) >= n_expected:
                answers = parts[:n_expected]
            else:
                # as a last resort, pad with empty strings
                answers = parts[:n_expected] + [""] * max(0, n_expected - len(parts))

    # Sanitize each answer: unquote JSON strings, remove trailing commas/quotes, strip numbering
    cleaned = []
    for a in answers:
        try:
            if isinstance(a, (list, dict)):
                s = json.dumps(a)
            else:
                s = str(a).strip()
            # remove trailing commas leftover from partial lists
            s = s.rstrip(",")
            # strip common surrounding quotes
            if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
                try:
                    s = json.loads(s)
                except Exception:
                    s = s[1:-1]
            # remove leading numbering like "1. Agree" or "1) Agree"
            s = re.sub(r'^\s*\d+\s*[\.\)]\s*', '', s)
            s = s.strip()
        except Exception:
            s = str(a)
        cleaned.append(s)

    # Ensure length
    if len(cleaned) < n_expected:
        cleaned += [""] * (n_expected - len(cleaned))
    elif len(cleaned) > n_expected:
        cleaned = cleaned[:n_expected]

    return [str(x) for x in cleaned]


# ---------- main runner ----------

def run_models(
    models: List[str],
    api_keys: Dict[str, str] | None = None,
    outdir: str = "data/runs",
    params: Dict[str, Any] | None = None,
    questions_path: str = "data/questions.json",
) -> str:
    """Execute all models over the bank, write CSV + per-model meta, return run_id.
    
    Args:
        models: list of model names (auto-detects provider from name)
        api_keys: dict mapping provider name ("openai", "anthropic", "gemini") to API key.
                  If None or missing a key, will read from environment.
        outdir: output directory for run artifacts
        params: optional parameters (temperature, max_tokens) for all models
        questions_path: path to questions.json
    """
    ensure_outdir(outdir)
    qbank = load_questions(questions_path)
    questions = qbank["questions"]

    # Run identifier to group outputs
    run_id = f"run_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}_{uuid.uuid4().hex[:6]}"
    meta_common = {
        "run_id": run_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
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

    api_keys = api_keys or {}

    # Per-model loop
    for model in models:
        ts = datetime.now(timezone.utc).isoformat()
        try:
            # Pass None for api_key so the provider adapter reads from env
            # Or pass a provider-specific key if provided in api_keys dict
            from backend.providers import infer_provider
            provider = infer_provider(model)
            provider_api_key = api_keys.get(provider) if api_keys else None
            content = call_model_batch(model, system_msg, user_msg, api_key=provider_api_key, params=params)
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
    parser = argparse.ArgumentParser(description="Run multiple models on the question bank (batched). Supports OpenAI, Anthropic Claude, and Google Gemini.")
    parser.add_argument("--models", required=True, help="Comma-separated model names (e.g., gpt-4o-mini,claude-3-sonnet-20240229,gemini-2.0-flash)")
    parser.add_argument("--api-key-openai", default=None, help="OpenAI API key (or use OPENAI_API_KEY env)")
    parser.add_argument("--api-key-anthropic", default=None, help="Anthropic API key (or use ANTHROPIC_API_KEY env)")
    parser.add_argument("--api-key-gemini", default=None, help="Google Gemini API key (or use GEMINI_API_KEY env)")
    parser.add_argument("--outdir", default="data/runs", help="Output directory for run CSVs and meta")
    parser.add_argument("--questions", default="data/questions.json", help="Path to question bank JSON")
    parser.add_argument("--temperature", default="0.0", help="Sampling temperature (default 0.0)")
    parser.add_argument("--max-tokens", dest="max_tokens", default="1200", help="Max tokens for response (default 1200)")
    parser.add_argument("--post-aggregate", dest="post_aggregate", action="store_true", help="Run aggregation and plotting after models complete (default: on)")
    parser.add_argument("--no-post-aggregate", dest="post_aggregate", action="store_false", help="Do not run aggregation and plotting after models complete")
    parser.set_defaults(post_aggregate=True)
    parser.add_argument("--summary-out", default="data/summary/aggregates.csv", help="Path to write aggregates CSV when --post-aggregate is set")
    parser.add_argument("--plots-out", default="data/plots", help="Output directory for plots when --post-aggregate is set")
    args = parser.parse_args()

    # Model list
    models = [m.strip() for m in args.models.split(",") if m.strip()]

    # Params for model calls
    params = {
        "temperature": float(args.temperature),
        "max_tokens": int(args.max_tokens),
    }

    # Build api_keys dict from CLI args; env vars are consulted by the provider adapters if not found
    api_keys = {}
    if args.api_key_openai:
        api_keys['openai'] = args.api_key_openai
    if args.api_key_anthropic:
        api_keys['anthropic'] = args.api_key_anthropic
    if args.api_key_gemini:
        api_keys['gemini'] = args.api_key_gemini

    # Execute
    run_models(models, api_keys=api_keys or None, outdir=args.outdir, params=params, questions_path=args.questions)
    # Optionally run aggregation + plotting immediately after
    if args.post_aggregate:
        try:
            from tools import aggregate, plot_runs
            print('Post-run: aggregating...')
            aggregate.aggregate_runs(args.outdir, args.summary_out)
            print('Post-run: plotting...')
            plot_runs.main(args.summary_out, args.plots_out)
            # copy latest compass image into public assets for the landing page (same as daily_wrapper)
            try:
                import shutil
                src = os.path.join(args.plots_out, 'compass_latest.png')
                dst_dir = os.path.join('public', 'assets')
                os.makedirs(dst_dir, exist_ok=True)
                dst = os.path.join(dst_dir, 'compass_latest.png')
                if os.path.exists(src):
                    shutil.copyfile(src, dst)
                    print('Updated public asset:', dst)
            except Exception as e:
                print('Could not copy compass image to public assets:', e)
        except Exception as e:
            print('Post-aggregate failed:', e)
