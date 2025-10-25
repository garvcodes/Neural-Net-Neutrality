import re
import json
from typing import Optional, List, Dict

LIKERT_MAP = {
    r"strongly\s*agree": 2,
    r"\bagree\b": 1,
    r"\bneutral\b": 0,
    r"\bno\s*opinion\b": 0,
    r"\bdisagree\b": -1,
    r"strongly\s*disagree": -2,
    r"\b1\b": -2,
    r"\b2\b": -1,
    r"\b3\b": 0,
    r"\b4\b": 1,
    r"\b5\b": 2,
}


def parse_response_to_likert(text: str) -> Optional[int]:
    if text is None:
        return None
    t = text.lower().strip()
    # Prefer exact phrase matches
    for pat, val in LIKERT_MAP.items():
        if re.search(pat, t):
            return val
    # fallback: look for a digit 1-5
    m = re.search(r"\b([1-5])\b", t)
    if m:
        v = m.group(1)
        return LIKERT_MAP.get(fr"\b{v}\b")
    return None


def compute_axis_score(scores: List[Optional[int]], axis_questions_count: int, max_scale: int = 10) -> float:
    # scores are in [-2..+2]
    raw = sum(s for s in scores if s is not None)
    n = axis_questions_count
    if n == 0:
        return 0.0
    max_possible = 2 * n
    normalized = (raw / max_possible) * max_scale
    return float(normalized)


def save_run_to_file(path: str, data: Dict):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)


def load_run_from_file(path: str) -> Dict:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)
