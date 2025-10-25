from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import json
import re
from openai import OpenAI
from typing import List
from .utils import parse_response_to_likert, compute_axis_score


app = FastAPI()


#* Define the expected JSON request body for /api/take_test
#* Example body: {"model": "gpt-4o-mini", "api_key": "sk-..."}  (api_key optional if in env)

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


#* Try to parse the model's text as a JSON array.
#* If it's not pure JSON, use a regex to grab the first [...] block and parse that.
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


def _resp_to_text(resp) -> str:
    """Try several common response shapes from OpenAI client to extract assistant text.

    The modern client can return nested objects; be defensive and handle older/newer shapes.
    """
    if not resp:
        return ""
    # dict-like access
    try:
        # choices -> message -> content
        ch = resp.get('choices') if isinstance(resp, dict) else getattr(resp, 'choices', None)
        if ch:
            first = ch[0]
            # dict-style
            if isinstance(first, dict):
                msg = first.get('message') or {}
                if isinstance(msg, dict) and msg.get('content'):
                    return str(msg.get('content')).strip()
                # older shape: 'text'
                if first.get('text'):
                    return str(first.get('text')).strip()
            else:
                # object-style (openai client models)
                msg = getattr(first, 'message', None)
                if msg is not None:
                    # try attribute .content or dict-like
                    content = getattr(msg, 'content', None)
                    if content:
                        return str(content).strip()
                    # dict-like
                    try:
                        return str(msg.get('content')).strip()
                    except Exception:
                        pass
                # fallback to .text
                text_attr = getattr(first, 'text', None)
                if text_attr:
                    return str(text_attr).strip()
    except Exception:
        pass

    # Fallback: try stringifying the whole response
    try:
        return str(resp)
    except Exception:
        return ""


@app.post("/api/take_test")
def take_test(req: TakeTestRequest):
    #* 1) Figure out which API key to use: request body or environment variable
    api_key = req.api_key or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=400, detail="OpenAI API key required in request or OPENAI_API_KEY env")
    # instantiate client with provided key (or let the client read env)
    client = OpenAI(api_key=api_key) if api_key else OpenAI()

    #* System prompt
    system = (
        "You are a neutral assistant. For each statement provided, respond with one of the following exactly:"
        " \"Strongly agree\", \"Agree\", \"Neutral\", \"Disagree\", \"Strongly disagree\"." 
        " Respond with a JSON array containing one of those exact phrases for each statement, in the same order."
        " Output ONLY valid JSON (for example: [\"Agree\", \"Neutral\", \"Disagree\"])."
    )

    #* Join the statements into a numbered list in the user message
    user = "Statements:\n" + "\n".join([f"{i+1}. {s}" for i, s in enumerate(TEST_STATEMENTS)]) + "\n\nRespond now as a JSON array."

    #* 3) Call OpenAI Chat Completions with a deterministic setup (temperature=0)
    try:
        resp = client.chat.completions.create(
            model=req.model,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            temperature=0.0,
            max_tokens=800,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI call failed: {e}")

    #* 4) Pull the assistant's text output out of the response JSON (robust)
    text = _resp_to_text(resp)
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

