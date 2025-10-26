"""
backend/providers.py

Multi-provider adapter layer for calling LLMs (OpenAI, Anthropic Claude, Google Gemini).
Each provider returns Likert answers in the same format so downstream parsing/aggregation
is provider-agnostic.

Requires environment variables for API keys:
  - OPENAI_API_KEY (for GPT models)
  - ANTHROPIC_API_KEY (for Claude models)
  - GEMINI_API_KEY (for Gemini models)

Usage:
  from backend.providers import call_model
  answers = call_model("gpt-4o-mini", system_msg, user_msg, api_key="sk-...")
  answers = call_model("claude-3-sonnet-20240229", system_msg, user_msg, api_key="sk-ant-...")
  answers = call_model("gemini-2.0-flash", system_msg, user_msg, api_key="...")
"""

import json
import os
import re
from typing import Dict, Any, List, Optional

# Load .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"), override=False)
except ImportError:
    pass  # dotenv not installed, rely on env vars


def infer_provider(model: str) -> str:
    """Guess provider from model name."""
    if model.startswith("gpt-") or model.startswith("o1"):
        return "openai"
    elif model.startswith("claude-"):
        return "anthropic"
    elif model.startswith("gemini-"):
        return "gemini"
    else:
        # Default to OpenAI for ambiguous names
        return "openai"


def call_model(
    model: str,
    system_msg: str,
    user_msg: str,
    api_key: Optional[str] = None,
    params: Optional[Dict[str, Any]] = None,
    provider: Optional[str] = None,
) -> str:
    """
    Call a model via the appropriate provider and return the assistant content as a string.
    
    Args:
        model: model identifier (e.g. "gpt-4o-mini", "claude-3-sonnet-20240229", "gemini-2.0-flash")
        system_msg: system prompt
        user_msg: user message
        api_key: API key for the provider (if None, reads from env)
        params: optional dict with temperature, max_tokens, etc.
        provider: provider name ("openai", "anthropic", "gemini"). If None, inferred from model name.
    
    Returns:
        assistant content string
    
    Raises:
        RuntimeError if API key is missing or provider is unsupported
    """
    params = params or {}
    provider = provider or infer_provider(model)
    
    if provider == "openai":
        return _call_openai(model, system_msg, user_msg, api_key, params)
    elif provider == "anthropic":
        return _call_anthropic(model, system_msg, user_msg, api_key, params)
    elif provider == "gemini":
        return _call_gemini(model, system_msg, user_msg, api_key, params)
    else:
        raise RuntimeError(f"Unknown provider: {provider}")


# ========== OpenAI ==========

def _call_openai(
    model: str,
    system_msg: str,
    user_msg: str,
    api_key: Optional[str] = None,
    params: Optional[Dict[str, Any]] = None,
) -> str:
    """Call OpenAI chat.completions with JSON mode."""
    try:
        from openai import OpenAI
    except ImportError:
        raise RuntimeError("openai package not installed. Run: pip install openai")
    
    params = params or {}
    api_key = api_key or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not found in env and no api_key provided")
    
    client = OpenAI(api_key=api_key)
    
    # Build request kwargs
    request_kwargs = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ],
        "temperature": float(params.get("temperature", 0.0)),
        "max_tokens": int(params.get("max_tokens", 1200)),
    }
    
    # Only use JSON mode if "json" appears in system or user message
    if "json" in system_msg.lower() or "json" in user_msg.lower():
        request_kwargs["response_format"] = {"type": "json_object"}
    
    resp = client.chat.completions.create(**request_kwargs)
    return (resp.choices[0].message.content or "").strip()


# ========== Anthropic Claude ==========

def _call_anthropic(
    model: str,
    system_msg: str,
    user_msg: str,
    api_key: Optional[str] = None,
    params: Optional[Dict[str, Any]] = None,
) -> str:
    """Call Anthropic Claude API."""
    try:
        import anthropic
    except ImportError:
        raise RuntimeError("anthropic package not installed. Run: pip install anthropic")
    
    params = params or {}
    api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY not found in env and no api_key provided")
    
    client = anthropic.Anthropic(api_key=api_key)
    msg = client.messages.create(
        model=model,
        max_tokens=int(params.get("max_tokens", 1200)),
        system=system_msg,
        messages=[{"role": "user", "content": user_msg}],
    )
    # Claude returns a list of content blocks; extract text from the first
    if msg.content and len(msg.content) > 0:
        content_block = msg.content[0]
        if hasattr(content_block, 'text'):
            return content_block.text.strip()
    return ""


# ========== Google Gemini ==========

def _call_gemini(
    model: str,
    system_msg: str,
    user_msg: str,
    api_key: Optional[str] = None,
    params: Optional[Dict[str, Any]] = None,
) -> str:
    """Call Google Gemini API (generative AI)."""
    try:
        import google.generativeai as genai
    except ImportError:
        raise RuntimeError("google-generativeai package not installed. Run: pip install google-generativeai")
    
    params = params or {}
    api_key = api_key or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not found in env and no api_key provided")
    
    genai.configure(api_key=api_key)
    gen_model = genai.GenerativeModel(model_name=model, system_instruction=system_msg)
    
    response = gen_model.generate_content(
        user_msg,
        generation_config=genai.types.GenerationConfig(
            temperature=float(params.get("temperature", 0.0)),
            max_output_tokens=int(params.get("max_tokens", 1200)),
        ),
    )
    return (response.text or "").strip()


# ========== Helper: extract JSON answers ==========

def extract_json_answers(content: str, n_expected: int) -> List[str]:
    """
    Parse JSON answers from model response.
    Tries several fallback strategies to handle different response formats.
    Returns a list of answer strings (possibly with some empty if unparseable).
    """
    answers = None
    
    # Primary: try {"answers": [...]} or just [...]
    try:
        obj = json.loads(content)
        if isinstance(obj, dict):
            maybe = obj.get("answers")
            if isinstance(maybe, list):
                answers = maybe
        elif isinstance(obj, list):
            answers = obj
    except Exception:
        pass
    
    # Fallback: grab first [...] block
    if not isinstance(answers, list):
        m = re.search(r"\[(?:.|\n)*\]", content)
        if m:
            try:
                answers = json.loads(m.group(0))
                if not isinstance(answers, list):
                    answers = None
            except Exception:
                answers = None
    
    # Fallback: split by lines or commas
    if not isinstance(answers, list) or len(answers) != n_expected:
        lines = [ln.strip() for ln in content.splitlines() if ln.strip()]
        if len(lines) >= n_expected:
            answers = lines[:n_expected]
        else:
            # Try comma-split (respecting quoted strings)
            parts = re.split(r',\s*(?=(?:[^"]*"[^"]*")*[^"]*$)', content)
            parts = [p.strip() for p in parts if p.strip()]
            if len(parts) >= n_expected:
                answers = parts[:n_expected]
            else:
                answers = parts
    
    # Sanitize each answer
    cleaned = []
    for a in answers or []:
        try:
            if isinstance(a, (list, dict)):
                s = json.dumps(a)
            else:
                s = str(a).strip()
            # Remove trailing commas
            s = s.rstrip(",")
            # Unquote JSON strings
            if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
                try:
                    s = json.loads(s)
                except Exception:
                    s = s[1:-1]
            # Remove leading numbering
            s = re.sub(r'^\s*\d+\s*[\.\)]\s*', '', s)
            s = s.strip()
        except Exception:
            s = str(a)
        cleaned.append(s)
    
    # Pad or truncate to expected length
    if len(cleaned) < n_expected:
        cleaned += [""] * (n_expected - len(cleaned))
    elif len(cleaned) > n_expected:
        cleaned = cleaned[:n_expected]
    
    return [str(x) for x in cleaned]
