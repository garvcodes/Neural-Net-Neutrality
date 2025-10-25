import os
import time
from typing import Dict, Any

try:
    import openai
except Exception:
    openai = None

try:
    import anthropic
except Exception:
    anthropic = None

# Gemini: placeholder - many users call via Google's APIs or HTTP wrappers. We'll use requests as a fallback.
import requests


class BaseAdapter:
    def __init__(self, api_key: str = None):
        self.api_key = api_key

    def call(self, prompt: str, params: Dict[str, Any]):
        raise NotImplementedError()


class OpenAIAdapter(BaseAdapter):
    def __init__(self, api_key: str = None, model: str = "gpt-4o-mini"):
        super().__init__(api_key)
        self.model = model
        if openai and api_key:
            openai.api_key = api_key

    def call(self, prompt: str, params: Dict[str, Any] = None):
        params = params or {}
        timeout = params.get("timeout", 30)
        # basic sync call for prototype
        if openai is None:
            return {"text": "(openai sdk not installed)", "tokens": 0}
        resp = openai.ChatCompletion.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=params.get("temperature", 0.0),
            max_tokens=params.get("max_tokens", 60),
        )
        text = resp.choices[0].message.content.strip()
        return {"text": text, "meta": resp}


class AnthropicAdapter(BaseAdapter):
    def __init__(self, api_key: str = None, model: str = "claude-2.1"):
        super().__init__(api_key)
        self.model = model
        if anthropic and api_key:
            self.client = anthropic.Client(api_key)
        else:
            self.client = None

    def call(self, prompt: str, params: Dict[str, Any] = None):
        params = params or {}
        if self.client is None:
            return {"text": "(anthropic sdk not installed)", "tokens": 0}
        # Wrap prompt in Claude style
        system = params.get("system", "You are a helpful assistant.")
        resp = self.client.completions.create(
            model=self.model,
            prompt=prompt,
            max_tokens_to_sample=params.get("max_tokens", 60),
            temperature=params.get("temperature", 0.0),
        )
        text = resp.completion.strip()
        return {"text": text, "meta": resp}


class GeminiAdapter(BaseAdapter):
    def __init__(self, api_key: str = None, model: str = "gemini-1.5"):
        super().__init__(api_key)
        self.model = model
        self.api_key = api_key

    def call(self, prompt: str, params: Dict[str, Any] = None):
        # Placeholder: call Google Gemini via an HTTP API or their client library.
        # For the prototype we'll return a canned response if no network integration is configured.
        return {"text": "(gemini placeholder) Agree", "meta": {}}


def get_adapter(provider: str, api_key: str = None, model: str = None):
    provider = provider.lower()
    if provider == "openai":
        return OpenAIAdapter(api_key=api_key, model=model or "gpt-4o-mini")
    if provider == "anthropic":
        return AnthropicAdapter(api_key=api_key, model=model or "claude-2.1")
    if provider == "gemini":
        return GeminiAdapter(api_key=api_key, model=model or "gemini-1.5")
    raise ValueError("Unknown provider: %s" % provider)
