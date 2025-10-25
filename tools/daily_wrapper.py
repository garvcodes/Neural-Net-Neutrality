#!/usr/bin/env python3
"""
tools/daily_wrapper.py

Run one or more models on the canonical question bank, aggregate results, and produce plots.

This script is suitable for local scheduling (cron) or CI (GitHub Actions). It expects OPENAI_API_KEY
to be available in the environment or passed via --api-key.
"""

import os
import sys
import argparse
import shutil


def main(models, api_key=None, runs_dir='data/runs', summary_out='data/summary/aggregates.csv', plots_out='data/plots'):
    # lazy imports so module can be inspected without heavy deps
    from tools import run_models
    from tools import aggregate
    from tools import plot_runs

    api_key = api_key or os.environ.get('OPENAI_API_KEY')
    if not api_key:
        print('OPENAI_API_KEY is required (set env or pass --api-key)')
        sys.exit(1)

    print('Starting run for models:', models)
    run_id = run_models.run_models(models, api_key=api_key, outdir=runs_dir)
    print('Aggregation...')
    aggregate.aggregate_runs(runs_dir, summary_out)
    print('Plotting...')
    plot_runs.main(summary_out, plots_out)
    # copy latest compass image into public assets for the landing page
    try:
        src = os.path.join(plots_out, 'compass_latest.png')
        dst_dir = os.path.join('public', 'assets')
        os.makedirs(dst_dir, exist_ok=True)
        dst = os.path.join(dst_dir, 'compass_latest.png')
        if os.path.exists(src):
            shutil.copyfile(src, dst)
            print('Updated public asset:', dst)
    except Exception as e:
        print('Could not copy compass image to public assets:', e)
    print('Done. Run id:', run_id)
    return run_id


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--models', required=True, help='Comma-separated model names (OpenAI)')
    parser.add_argument('--api-key', default=None, help='OpenAI API key (optional)')
    parser.add_argument('--runs-dir', default='data/runs')
    parser.add_argument('--summary-out', default='data/summary/aggregates.csv')
    parser.add_argument('--plots-out', default='data/plots')
    args = parser.parse_args()
    models = [m.strip() for m in args.models.split(',') if m.strip()]
    main(models, api_key=args.api_key, runs_dir=args.runs_dir, summary_out=args.summary_out, plots_out=args.plots_out)
