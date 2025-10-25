"""
Deprecated: multi-provider adapters

This module used to provide adapters for OpenAI/Anthropic/Gemini. The current
prototype uses direct OpenAI calls in `tools/run_models.py` and the adapter
layer was removed to simplify the pipeline. The file remains as a deprecated
stub to avoid accidental imports; do not use.
"""

raise RuntimeError("backend.adapters has been deprecated and removed. Use tools/run_models.py or backend/api.py instead.")
