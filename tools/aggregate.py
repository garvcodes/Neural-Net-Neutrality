#!/usr/bin/env python3
"""
tools/aggregate.py

Compute per-run aggregates (economic and social) from CSV run outputs and save a summary CSV for plotting.

Usage:
  python tools/aggregate.py --indir data/runs --out summary/aggregates.csv
"""

import os
import csv
import argparse
import json
from collections import defaultdict
from backend.utils import compute_axis_score


def aggregate_runs(indir, outpath):
    os.makedirs(os.path.dirname(outpath), exist_ok=True)
    # find CSV files
    files = [f for f in os.listdir(indir) if f.endswith('.csv')]
    summaries = []
    for fn in files:
        path = os.path.join(indir, fn)
        # model is part of filename after __
        parts = fn.split('__')
        run_id = parts[0]
        model = parts[1].rsplit('.csv', 1)[0] if len(parts) > 1 else 'unknown'
        rows = []
        with open(path, 'r', encoding='utf-8') as fh:
            reader = csv.DictReader(fh)
            for r in reader:
                rows.append(r)
        # group scores by axis using question bank mapping
        # load question bank
        import json
        qbank = json.load(open('data/questions.json'))
        qmap = {q['id']: q for q in qbank['questions']}
        econ_scores = []
        soc_scores = []
        for r in rows:
            qid = r['question_id']
            score = r['parsed_score']
            try:
                s = float(score)
            except Exception:
                continue
            q = qmap.get(qid)
            if not q:
                continue
            # apply reverse
            if q.get('reverse'):
                s = -s
            if q['axis'] == 'economic':
                econ_scores.append(s)
            else:
                soc_scores.append(s)

        econ_norm = compute_axis_score(econ_scores, max(1, sum(1 for q in qbank['questions'] if q['axis']=='economic')))
        soc_norm = compute_axis_score(soc_scores, max(1, sum(1 for q in qbank['questions'] if q['axis']=='social')))

        # try to find run-level meta (written by run_models)
        meta_path = os.path.join(indir, f"{run_id}__{model}_meta.json")
        parsed_fraction = None
        run_timestamp = None
        if os.path.exists(meta_path):
            try:
                meta = json.load(open(meta_path))
                parsed_fraction = meta.get('parsed_fraction')
                run_timestamp = meta.get('run_timestamp') or meta.get('created_at')
            except Exception:
                parsed_fraction = None

        # fallback: compute parsed_fraction from CSV rows if meta missing
        if parsed_fraction is None:
            total = 0
            parsed = 0
            for r in rows:
                total += 1
                if r.get('parsed_score') not in (None, '', 'None'):
                    parsed += 1
            parsed_fraction = parsed / max(1, total)

        # fallback timestamp from first row
        if not run_timestamp and rows:
            run_timestamp = rows[0].get('timestamp')

        summaries.append({'run_id': run_id, 'model': model, 'economic': econ_norm, 'social': soc_norm, 'parsed_fraction': parsed_fraction, 'run_timestamp': run_timestamp})

    # write out
    with open(outpath, 'w', newline='', encoding='utf-8') as fh:
        fieldnames = ['run_id', 'model', 'economic', 'social', 'parsed_fraction', 'run_timestamp']
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for s in summaries:
            writer.writerow(s)
    print('Wrote summary to', outpath)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--indir', default='data/runs')
    parser.add_argument('--out', default='data/summary/aggregates.csv')
    args = parser.parse_args()
    aggregate_runs(args.indir, args.out)
