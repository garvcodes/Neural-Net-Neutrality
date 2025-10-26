#!/bin/bash
# Quick commands to run the political compass pipeline

# Setup (run once)
cd /Users/gg027/Desktop/NNN
pip install -r backend/requirements.txt

# Run single OpenAI model (fastest way to test)
python -m tools.run_models --models gpt-4o-mini --post-aggregate

# Run all three providers together
python -m tools.daily_wrapper --models gpt-4o-mini,claude-3-haiku-20240307,gemini-2.0-flash

# Run OpenAI models only
python -m tools.run_models --models gpt-4o-mini,gpt-4o,gpt-3.5-turbo --post-aggregate

# Run Anthropic models only
python -m tools.run_models --models claude-3-haiku-20240307,claude-3-sonnet-20240229 --post-aggregate

# Run Google Gemini only
python -m tools.run_models --models gemini-2.0-flash,gemini-1.5-pro --post-aggregate

# View results
open assets/compass_latest.png
cat data/summary/aggregates.csv

# Test setup
python test_provider_integration.py
python example_multi_provider_run.py
