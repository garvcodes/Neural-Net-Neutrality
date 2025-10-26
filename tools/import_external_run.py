#!/usr/bin/env python3
"""
tools/import_external_run.py

Helper to import an external model's answers (JSON array or newline-separated file)
and write the CSV + meta files in the same format produced by `tools/run_models.py`.

Usage examples:
  # JSON array file with 40 answers
  python -m tools.import_external_run --model gemini-pro --answers-file /path/to/answers.json

  # newline-separated answers
  python -m tools.import_external_run --model gemini-pro --answers-file /path/to/answers.txt

Arguments:
  --model        Model name to record (e.g., gemini-pro)
  --answers-file Path to file containing answers (JSON array or newline-separated)
  --outdir       Output directory (default: data/runs)
  --questions    Path to question bank JSON (default: data/questions.json)
  --run-id       Optional run id to use (if omitted, one is generated)
  --timestamp    Optional ISO timestamp to use for rows (default: now UTC)

The script writes:
  data/runs/<run_id>__<model>.csv
  data/runs/<run_id>__<model>_meta.json
  data/runs/<run_id>__meta_common.json

These files match the format used by the main runner so aggregator/plotter pick them up.
"""

import argparse
import csv
import json
import os
import uuid
from datetime import datetime, timezone
from typing import List

from backend.utils import parse_response_to_likert


def load_answers(path: str) -> List[str]:
    with open(path, 'r', encoding='utf-8') as fh:
        txt = fh.read().strip()
    # Try JSON first
    try:
        arr = json.loads(txt)
        if isinstance(arr, list):
            return [str(x) for x in arr]
    except Exception:
        pass
    # Fallback: split lines
    lines = [ln.strip() for ln in txt.splitlines() if ln.strip()]
    if lines:
        return lines
    # Final fallback: split on commas
    parts = [p.strip() for p in txt.split(',') if p.strip()]
    return parts


def load_questions(path: str = 'data/questions.json'):
    with open(path, 'r', encoding='utf-8') as fh:
        qb = json.load(fh)
    return qb.get('questions', [])


def ensure_outdir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def make_run_id(provided: str | None = None):
    if provided:
        return provided
    return f"run_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}_{uuid.uuid4().hex[:6]}"


def write_csv_and_meta(run_id: str, model: str, questions: List[dict], answers: List[str], outdir: str, ts: str):
    ensure_outdir(outdir)
    rows = []
    parsed_count = 0
    for q, ans in zip(questions, answers):
        parsed = parse_response_to_likert(ans)
        if parsed is not None:
            parsed_count += 1
        rows.append({
            'run_id': run_id,
            'model': model,
            'question_id': q.get('id'),
            'question_text': q.get('text'),
            'raw_answer': ans,
            'parsed_score': parsed if parsed is not None else '',
            'timestamp': ts,
        })

    parsed_fraction = parsed_count / max(1, len(questions))

    csv_path = os.path.join(outdir, f"{run_id}__{model}.csv")
    with open(csv_path, 'w', newline='', encoding='utf-8') as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    # meta per-model
    per_model_meta = {
        'run_id': run_id,
        'created_at': datetime.now(timezone.utc).isoformat(),
        'models': [model],
        'model': model,
        'run_timestamp': ts,
        'parsed_fraction': parsed_fraction,
        'raw_response_preview': json.dumps(answers[:10])[:500],
    }
    meta_path = os.path.join(outdir, f"{run_id}__{model}_meta.json")
    with open(meta_path, 'w', encoding='utf-8') as fh:
        json.dump(per_model_meta, fh, indent=2)

    # top-level common meta (so aggregator can find run-level info)
    common_meta = {
        'run_id': run_id,
        'created_at': datetime.now(timezone.utc).isoformat(),
        'models': [model],
        'n_questions': len(questions),
    }
    common_path = os.path.join(outdir, f"{run_id}__meta_common.json")
    with open(common_path, 'w', encoding='utf-8') as fh:
        json.dump(common_meta, fh, indent=2)

    print('Wrote', csv_path)
    print('Wrote', meta_path)
    print('Wrote', common_path)


def main():
    p = argparse.ArgumentParser(description='Import external model answers into repo run format')
    p.add_argument('--model', required=True, help='Model name to record (e.g., gemini-pro)')
    p.add_argument('--answers-file', required=True, help='Path to JSON array or newline-separated answers file')
    p.add_argument('--outdir', default='data/runs', help='Output directory')
    p.add_argument('--questions', default='data/questions.json', help='Question bank JSON path')
    p.add_argument('--run-id', default=None, help='Optional run id to use (default generated)')
    p.add_argument('--timestamp', default=None, help='Optional ISO timestamp for rows (default now UTC)')
    args = p.parse_args()

    answers = load_answers(args.answers_file)
    questions = load_questions(args.questions)

    if not questions:
        print('No questions loaded from', args.questions)
        return

    n_q = len(questions)
    if len(answers) < n_q:
        # pad with empty strings
        answers = answers + [''] * (n_q - len(answers))
    elif len(answers) > n_q:
        answers = answers[:n_q]

    run_id = make_run_id(args.run_id)
    ts = args.timestamp or datetime.now(timezone.utc).isoformat()

    write_csv_and_meta(run_id, args.model, questions, answers, args.outdir, ts)


if __name__ == '__main__':
    main()
