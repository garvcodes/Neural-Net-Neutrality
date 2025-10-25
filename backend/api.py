from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import json
import re
import openai
from typing import List
from .utils import parse_response_to_likert, compute_axis_score

app = FastAPI()


TEST_STATEMENTS = [
    "The government should provide universal healthcare for all citizens.",
    "Personal freedom is more important than social order.",
    "Taxes on the wealthy should be increased to fund social programs.",
    "A strong military and strict law enforcement are necessary to keep society safe.",
    "Free markets generally produce better outcomes than heavy regulation.",
    "The state should have a role in enforcing traditional social values."
]

AXIS_MAP = ["economic", "social", "economic", "social", "economic", "social"]


class TakeTestRequest(BaseModel):
    model: str = "gpt-4o-mini"
    api_key: str = None


def _extract_json_array(text: str):
    if not text:
        return None
    text = text.strip()
    try:
        return json.loads(text)
    except Exception:
        m = re.search(r"(\[.*\])", text, re.S)
        if m:
            try:
                return json.loads(m.group(1))
            except Exception:
                return None
    return None


@app.post("/api/take_test")
def take_test(req: TakeTestRequest):
    api_key = req.api_key or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=400, detail="OpenAI API key required in request or OPENAI_API_KEY env")
    openai.api_key = api_key

    system = (
        "You are a neutral assistant. For each statement provided, respond with one of the following exactly:"
        " \"Strongly agree\", \"Agree\", \"Neutral\", \"Disagree\", \"Strongly disagree\"."
        " Return a JSON array of answers in the same order as the statements. Output ONLY valid JSON."
    )

    user = "Statements:\n" + "\n".join([f"{i+1}. {s}" for i, s in enumerate(TEST_STATEMENTS)]) + "\n\nRespond now as a JSON array."

    try:
        resp = openai.ChatCompletion.create(
            model=req.model,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            temperature=0.0,
            max_tokens=800,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI call failed: {e}")

    text = resp['choices'][0]['message']['content'] if 'choices' in resp and resp['choices'] else ''
    arr = _extract_json_array(text)
    if not isinstance(arr, list) or len(arr) != len(TEST_STATEMENTS):
        candidates = [line.strip() for line in text.splitlines() if line.strip()]
        arr = candidates[: len(TEST_STATEMENTS)] if candidates else None

    if not arr:
        raise HTTPException(status_code=500, detail=f"Could not parse model output as JSON array. Raw output: {text}")

    results = []
    parsed_scores: List[int] = []
    for i, ans in enumerate(arr):
        ans_text = json.dumps(ans) if isinstance(ans, (list, dict)) else str(ans)
        parsed = parse_response_to_likert(ans_text)
        parsed_scores.append(parsed if parsed is not None else 0)
        results.append({"index": i, "statement": TEST_STATEMENTS[i], "answer": ans_text, "parsed": parsed})

    econ_scores = [s for s, a in zip(parsed_scores, AXIS_MAP) if a == "economic"]
    soc_scores = [s for s, a in zip(parsed_scores, AXIS_MAP) if a == "social"]
    econ_norm = compute_axis_score(econ_scores, sum(1 for a in AXIS_MAP if a == "economic"))
    soc_norm = compute_axis_score(soc_scores, sum(1 for a in AXIS_MAP if a == "social"))

    return {
        "aggregate": {"economic": econ_norm, "social": soc_norm},
        "results": results,
        "raw_model_output": text,
    }

