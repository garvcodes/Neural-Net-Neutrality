#!/usr/bin/env python3
"""
tools/daily_wrapper.py

Run one or more models on the canonical question bank, aggregate results, and produce plots.
Supports multi-provider models: OpenAI GPT, Anthropic Claude, Google Gemini.

This script is suitable for local scheduling (cron) or CI (GitHub Actions). It requires the
appropriate API keys to be available in the environment (OPENAI_API_KEY, ANTHROPIC_API_KEY, GEMINI_API_KEY).

Usage:
  python -m tools.daily_wrapper --models gpt-4o-mini,claude-3-sonnet-20240229,gemini-2.0-flash
  python -m tools.daily_wrapper  # uses env $MODELS or default list
"""

import os
import sys
import argparse
import shutil
from backend.providers import infer_provider


def main(models, api_keys=None, runs_dir='data/runs', summary_out='data/summary/aggregates.csv', plots_out='data/plots'):
    """
    Args:
        models: list of model names (e.g., ['gpt-4o-mini', 'claude-3-sonnet-20240229', 'gemini-2.0-flash'])
        api_keys: dict of provider -> api_key or None (will read from env)
        runs_dir, summary_out, plots_out: paths for outputs
    """
    # lazy imports so module can be inspected without heavy deps
    from tools import run_models
    from tools import aggregate
    from tools import plot_runs

    api_keys = api_keys or {}
    
    # Verify that each required provider has an API key
    providers_needed = set(infer_provider(m) for m in models)
    for provider in providers_needed:
        if provider == "openai":
            if not (api_keys.get("openai") or os.environ.get("OPENAI_API_KEY")):
                print("ERROR: OpenAI model requested but OPENAI_API_KEY not found (env or --api-keys)")
                sys.exit(1)
        elif provider == "anthropic":
            if not (api_keys.get("anthropic") or os.environ.get("ANTHROPIC_API_KEY")):
                print("ERROR: Anthropic model requested but ANTHROPIC_API_KEY not found (env or --api-keys)")
                sys.exit(1)
        elif provider == "gemini":
            if not (api_keys.get("gemini") or os.environ.get("GEMINI_API_KEY")):
                print("ERROR: Gemini model requested but GEMINI_API_KEY not found (env or --api-keys)")
                sys.exit(1)

    print('Starting run for models:', models)
    print('Providers:', ', '.join(providers_needed))
    
    # Pass the api_keys dict or None; run_models will read from env as needed
    run_id = run_models.run_models(models, api_keys=api_keys, outdir=runs_dir)
    
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
    parser = argparse.ArgumentParser(description='Run political compass models across multiple providers.')
    parser.add_argument(
        '--models',
        required=False,
        help='Comma-separated model names (e.g., gpt-4o-mini,claude-3-sonnet-20240229,gemini-2.0-flash). '
             'If omitted, uses $MODELS env or a default list.'
    )
    parser.add_argument(
        '--api-key-openai',
        default=None,
        help='OpenAI API key (or set OPENAI_API_KEY env var)'
    )
    parser.add_argument(
        '--api-key-anthropic',
        default=None,
        help='Anthropic API key (or set ANTHROPIC_API_KEY env var)'
    )
    parser.add_argument(
        '--api-key-gemini',
        default=None,
        help='Google Gemini API key (or set GEMINI_API_KEY env var)'
    )
    parser.add_argument('--runs-dir', default='data/runs')
    parser.add_argument('--summary-out', default='data/summary/aggregates.csv')
    parser.add_argument('--plots-out', default='data/plots')
    args = parser.parse_args()
    
    # Determine models list: CLI > env MODELS > sensible default
    if args.models:
        models = [m.strip() for m in args.models.split(',') if m.strip()]
    else:
        env_models = os.environ.get('MODELS')
        if env_models:
            models = [m.strip() for m in env_models.split(',') if m.strip()]
        else:
            # sensible default set including OpenAI, Anthropic, and Google models
            models = [
                'gpt-4o-mini',
                'gpt-4o',
                'gpt-4o-realtime-preview',
                'gpt-4',
                'gpt-3.5-turbo',
                # Uncomment below to include non-OpenAI providers (requires API keys)
                # 'claude-3-sonnet-20240229',
                # 'gemini-2.0-flash',
            ]
            print('No --models or $MODELS provided. Using default models:', models)
    
    # Build api_keys dict from args or leave empty for env fallback
    api_keys = {}
    if args.api_key_openai:
        api_keys['openai'] = args.api_key_openai
    if args.api_key_anthropic:
        api_keys['anthropic'] = args.api_key_anthropic
    if args.api_key_gemini:
        api_keys['gemini'] = args.api_key_gemini
    
    main(models, api_keys=api_keys or None, runs_dir=args.runs_dir, summary_out=args.summary_out, plots_out=args.plots_out)
