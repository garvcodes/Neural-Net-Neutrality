#!/usr/bin/env python3
"""
example_multi_provider_run.py

Quick example: run a subset of models from different providers and plot them together.

Usage:
  export OPENAI_API_KEY="sk-..."
  export ANTHROPIC_API_KEY="sk-ant-..."
  export GEMINI_API_KEY="..."
  python example_multi_provider_run.py

This will:
1. Run gpt-4o-mini, claude-3-haiku, and gemini-2.0-flash on the question bank
2. Parse all responses
3. Aggregate scores
4. Plot all three on the same compass
5. Print the run ID
"""

import os
import sys
import shutil

def main():
    # Add repo root to path so imports work
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    from tools import run_models, aggregate, plot_runs
    from backend.providers import infer_provider
    
    # Models to run: one from each provider
    models = [
        'gpt-4o-mini',               # OpenAI (cheap/fast)
        'claude-3-haiku-20240307',   # Anthropic (cheap/fast)
        'gemini-2.0-flash',          # Google (cheap/fast)
    ]
    
    print("=" * 60)
    print("Multi-Provider Political Compass Example")
    print("=" * 60)
    print()
    print(f"Models: {models}")
    print(f"Providers: {', '.join(set(infer_provider(m) for m in models))}")
    print()
    
    # Check that required API keys are present
    providers_needed = set(infer_provider(m) for m in models)
    for provider in providers_needed:
        key_name = {
            'openai': 'OPENAI_API_KEY',
            'anthropic': 'ANTHROPIC_API_KEY',
            'gemini': 'GEMINI_API_KEY',
        }[provider]
        if not os.environ.get(key_name):
            print(f"ERROR: {key_name} not found in environment")
            print(f"Set it with: export {key_name}='...'")
            sys.exit(1)
    
    print("✓ All required API keys found")
    print()
    
    # Step 1: Run models
    print("Step 1: Running models...")
    print("-" * 60)
    try:
        run_id = run_models.run_models(
            models,
            api_keys=None,  # Will read from env
            outdir='data/runs',
            params={'temperature': 0.0, 'max_tokens': 1200},
            questions_path='data/questions.json'
        )
        print(f"✓ Run complete: {run_id}")
    except Exception as e:
        print(f"✗ Run failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print()
    
    # Step 2: Aggregate
    print("Step 2: Aggregating results...")
    print("-" * 60)
    try:
        aggregate.aggregate_runs('data/runs', 'data/summary/aggregates.csv')
        print("✓ Aggregation complete")
    except Exception as e:
        print(f"✗ Aggregation failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print()
    
    # Step 3: Plot
    print("Step 3: Generating plots...")
    print("-" * 60)
    try:
        plot_runs.main('data/summary/aggregates.csv', 'data/plots')
        print("✓ Plotting complete")
    except Exception as e:
        print(f"✗ Plotting failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print()
    
    # Step 4: Copy compass to public assets
    print("Step 4: Updating public assets...")
    print("-" * 60)
    try:
        src = os.path.join('data/plots', 'compass_latest.png')
        dst_dir = os.path.join('public', 'assets')
        os.makedirs(dst_dir, exist_ok=True)
        dst = os.path.join(dst_dir, 'compass_latest.png')
        if os.path.exists(src):
            shutil.copyfile(src, dst)
            print(f"✓ Updated: {dst}")
        else:
            print(f"⚠ Plot not found at {src}")
    except Exception as e:
        print(f"⚠ Could not copy compass image: {e}")
    
    print()
    print("=" * 60)
    print("SUCCESS!")
    print("=" * 60)
    print()
    print("Results:")
    print(f"  - Run ID: {run_id}")
    print(f"  - Per-run data: data/runs/{run_id}__*")
    print(f"  - Aggregates: data/summary/aggregates.csv")
    print(f"  - Latest compass: assets/compass_latest.png")
    print()
    print("Next steps:")
    print("  - View the compass in assets/compass_latest.png")
    print("  - Inspect aggregates.csv to see model scores")
    print("  - Run the dashboard: streamlit run web/dashboard.py")
    print()


if __name__ == '__main__':
    main()
