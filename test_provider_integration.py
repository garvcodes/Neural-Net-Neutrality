#!/usr/bin/env python3
"""
test_provider_integration.py

Quick integration test: verify that the provider adapter layer works correctly.

Run from repo root:
  python test_provider_integration.py

Does NOT require API keys (only tests the import and routing logic).
"""

import sys
import os

def test_imports():
    """Test that all required modules can be imported."""
    print("Test 1: Imports...")
    try:
        from backend.providers import (
            call_model,
            infer_provider,
            extract_json_answers,
        )
        print("  ✓ backend.providers imports OK")
        
        from tools.run_models import run_models, call_model_batch
        print("  ✓ tools.run_models imports OK")
        
        from tools.daily_wrapper import main
        print("  ✓ tools.daily_wrapper imports OK")
        
        return True
    except ImportError as e:
        print(f"  ✗ Import failed: {e}")
        return False


def test_provider_detection():
    """Test that model names are correctly mapped to providers."""
    print("\nTest 2: Provider detection...")
    from backend.providers import infer_provider
    
    test_cases = [
        ("gpt-4o-mini", "openai"),
        ("gpt-4", "openai"),
        ("o1-preview", "openai"),
        ("claude-3-sonnet-20240229", "anthropic"),
        ("claude-3-opus-20240229", "anthropic"),
        ("gemini-2.0-flash", "gemini"),
        ("gemini-1.5-pro", "gemini"),
    ]
    
    all_pass = True
    for model_name, expected_provider in test_cases:
        detected = infer_provider(model_name)
        status = "✓" if detected == expected_provider else "✗"
        print(f"  {status} {model_name} → {detected} (expected: {expected_provider})")
        if detected != expected_provider:
            all_pass = False
    
    return all_pass


def test_json_extraction():
    """Test that JSON extraction handles various formats."""
    print("\nTest 3: JSON extraction...")
    from backend.providers import extract_json_answers
    
    test_cases = [
        # Standard JSON array
        (
            '["Agree", "Disagree", "Neutral"]',
            ["Agree", "Disagree", "Neutral"],
            "standard JSON array"
        ),
        # JSON object with "answers" key
        (
            '{"answers": ["Strongly agree", "Agree", "Neutral", "Disagree", "Strongly disagree"]}',
            ["Strongly agree", "Agree", "Neutral", "Disagree", "Strongly disagree"],
            "JSON object with answers key"
        ),
        # With extra text around JSON
        (
            'Here are my responses:\n["Agree", "Neutral", "Disagree"]\n\nHope this helps!',
            ["Agree", "Neutral", "Disagree"],
            "JSON in text"
        ),
        # Line-separated (fallback)
        (
            'Agree\nNeutral\nDisagree',
            ["Agree", "Neutral", "Disagree"],
            "line-separated"
        ),
    ]
    
    all_pass = True
    for content, expected, description in test_cases:
        result = extract_json_answers(content, len(expected))
        # Just check length and first element to keep it simple
        if len(result) == len(expected) and result[0] == expected[0]:
            print(f"  ✓ {description}")
        else:
            print(f"  ✗ {description}")
            print(f"    Expected: {expected}")
            print(f"    Got:      {result}")
            all_pass = False
    
    return all_pass


def test_cli_argument_parsing():
    """Test that CLI arguments are parsed correctly."""
    print("\nTest 4: CLI argument parsing...")
    import argparse
    from tools.run_models import (
        run_models,
    )
    
    # Just verify the function signature accepts api_keys
    import inspect
    sig = inspect.signature(run_models)
    params = list(sig.parameters.keys())
    
    if 'api_keys' in params:
        print(f"  ✓ run_models() accepts api_keys parameter")
        return True
    else:
        print(f"  ✗ run_models() missing api_keys parameter")
        print(f"    Found parameters: {params}")
        return False


def test_provider_router_structure():
    """Test that call_model function has the right structure."""
    print("\nTest 5: Provider router structure...")
    from backend.providers import call_model
    import inspect
    
    sig = inspect.signature(call_model)
    params = list(sig.parameters.keys())
    
    expected_params = ['model', 'system_msg', 'user_msg', 'api_key', 'params', 'provider']
    if all(p in params for p in expected_params):
        print(f"  ✓ call_model() has all expected parameters")
        return True
    else:
        print(f"  ✗ call_model() missing parameters")
        print(f"    Expected: {expected_params}")
        print(f"    Found:    {params}")
        return False


def test_backward_compatibility():
    """Verify old OpenAI-only code patterns still work."""
    print("\nTest 6: Backward compatibility...")
    
    # Old pattern: run_models with a single api_key
    # New pattern: run_models with api_keys dict
    # Should still work if we pass None or an empty dict
    
    from tools.run_models import run_models
    import inspect
    
    # Check that the function can be called with api_keys=None
    sig = inspect.signature(run_models)
    api_keys_param = sig.parameters.get('api_keys')
    
    if api_keys_param and api_keys_param.default is None:
        print(f"  ✓ run_models() has api_keys with default=None")
        return True
    else:
        print(f"  ✗ api_keys parameter doesn't have default")
        return False


def main():
    print("=" * 60)
    print("Multi-Provider Integration Tests")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_provider_detection,
        test_json_extraction,
        test_cli_argument_parsing,
        test_provider_router_structure,
        test_backward_compatibility,
    ]
    
    results = [test() for test in tests]
    
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 60)
    
    if all(results):
        print("\n✓ All tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
