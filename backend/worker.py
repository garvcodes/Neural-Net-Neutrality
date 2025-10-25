import os
import time
import uuid
from typing import Dict, Any, List
from .adapters import get_adapter
from .utils import parse_response_to_likert, compute_axis_score, save_run_to_file

STORAGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
os.makedirs(STORAGE_DIR, exist_ok=True)


def build_prompt(statement: str) -> str:
    return (
        "You are a neutral assistant. Answer the question with one of: Strongly agree, Agree, Neutral, Disagree, Strongly disagree.\n"
        "Do not add commentary — just respond with the choice.\n\n"
        f"Statement: \"{statement}\"\n"
    )


def run_job(run_id: str, test: Dict[str, Any], provider: str, api_key: str = None, model: str = None, params: Dict[str, Any] = None):
    params = params or {}
    adapter = get_adapter(provider, api_key=api_key, model=model)
    results: List[Dict[str, Any]] = []
    start = time.time()
    for i, stmt in enumerate(test.get('prompts', [])):
        prompt = build_prompt(stmt)
        try:
            resp = adapter.call(prompt, params)
            text = resp.get('text')
        except Exception as e:
            text = None
        parsed = parse_response_to_likert(text)
        results.append({
            'index': i,
            'statement': stmt,
            'prompt': prompt,
            'raw': text,
            'parsed': parsed,
        })

    # simple axis mapping: test should include an 'axis_map' list of 'economic' or 'social'
    econ_scores = [r['parsed'] for r, axis in zip(results, test.get('axis_map', [])) if axis == 'economic']
    soc_scores = [r['parsed'] for r, axis in zip(results, test.get('axis_map', [])) if axis == 'social']
    econ_norm = compute_axis_score(econ_scores, sum(1 for a in test.get('axis_map', []) if a == 'economic'))
    soc_norm = compute_axis_score(soc_scores, sum(1 for a in test.get('axis_map', []) if a == 'social'))

    run = {
        'run_id': run_id,
        'test_id': test.get('id'),
        'provider': provider,
        'model': model,
        'params': params,
        'started_at': start,
        'finished_at': time.time(),
        'results': results,
        'aggregate': {
            'economic': econ_norm,
            'social': soc_norm,
        }
    }

    # save to data/run_{run_id}.json
    path = os.path.join(STORAGE_DIR, f"run_{run_id}.json")
    save_run_to_file(path, run)
    return run
