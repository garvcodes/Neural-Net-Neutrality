from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import json
import re
from openai import OpenAI
from typing import List, Optional, Dict
from .utils import parse_response_to_likert, compute_axis_score
from .providers import call_model
from .supabase_db import update_ratings, get_all_ratings, init_database, store_vote_tags, ensure_tags_table_exists
from .tags import calculate_dimension_scores, validate_tag, get_all_tags


app = FastAPI()

# Initialize database on startup
try:
    init_database()
except Exception as e:
    print(f"Warning: Could not initialize database: {e}")

# Add CORS middleware to allow requests from GitHub Pages
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (or restrict to specific domains)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


class BattleRequest(BaseModel):
    prompt: str
    model_a: str = "gpt-4o-mini"
    model_b: str = "gemini-2.0-flash"
    api_key_a: str = None
    api_key_b: str = None


class VoteRequest(BaseModel):
    winner_model: str
    loser_model: str
    prompt: str = None  # Optional: for logging/analytics


class VoteWithTagsRequest(BaseModel):
    winner_model: str
    loser_model: str
    tags: List[str] = []
    topic: Optional[str] = None
    debate_id: Optional[str] = None


class DebateRequest(BaseModel):
    topic: str
    model_pro: str = "gpt-4o-mini"
    model_con: str = "gemini-2.0-flash"
    api_key_pro: str = None
    api_key_con: str = None


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


@app.post("/api/battle")
def battle(req: BattleRequest):
    """Battle endpoint: get responses from two models for the same prompt."""
    if not req.prompt or not req.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt is required")
    
    system_msg = "You are a helpful assistant. Answer the following prompt concisely and thoughtfully."
    user_msg = req.prompt
    
    responses = {}
    
    # Get response from Model A (default: OpenAI)
    try:
        resp_a = call_model(
            model=req.model_a,
            system_msg=system_msg,
            user_msg=user_msg,
            api_key=req.api_key_a
        )
        responses["model_a"] = {
            "model": req.model_a,
            "response": resp_a
        }
    except Exception as e:
        responses["model_a"] = {
            "model": req.model_a,
            "error": str(e),
            "response": None
        }
    
    # Get response from Model B (default: Gemini)
    try:
        resp_b = call_model(
            model=req.model_b,
            system_msg=system_msg,
            user_msg=user_msg,
            api_key=req.api_key_b
        )
        responses["model_b"] = {
            "model": req.model_b,
            "response": resp_b
        }
    except Exception as e:
        responses["model_b"] = {
            "model": req.model_b,
            "error": str(e),
            "response": None
        }
    
    return {
        "prompt": req.prompt,
        "responses": responses,
        "openai": responses.get("model_a", {}).get("response"),
        "gemini": responses.get("model_b", {}).get("response")
    }


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/api/vote")
def vote(req: VoteRequest):
    """Record a vote and update Elo ratings."""
    if not req.winner_model or not req.loser_model:
        raise HTTPException(status_code=400, detail="winner_model and loser_model are required")
    
    try:
        new_winner_rating, new_loser_rating = update_ratings(req.winner_model, req.loser_model)
        return {
            "success": True,
            "winner_model": req.winner_model,
            "winner_new_rating": new_winner_rating,
            "loser_model": req.loser_model,
            "loser_new_rating": new_loser_rating,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Vote failed: {str(e)}")


@app.post("/api/vote-with-tags")
def vote_with_tags(req: VoteWithTagsRequest):
    """Record vote with tag annotations and calculate dimension scores."""
    if not req.winner_model or not req.loser_model:
        raise HTTPException(status_code=400, detail="winner_model and loser_model are required")
    
    # Validate all tags
    for tag in req.tags:
        if not validate_tag(tag):
            raise HTTPException(status_code=400, detail=f"Invalid tag: {tag}")
    
    try:
        # Initialize tags table if needed
        ensure_tags_table_exists()
        
        # Update Elo ratings
        new_winner_rating, new_loser_rating = update_ratings(req.winner_model, req.loser_model)
        
        # Calculate dimension scores from tags
        dimension_scores = calculate_dimension_scores(req.tags)
        
        # Store tags in database
        from .tags import TAGS_BY_CATEGORY
        tag_categories = {}
        for category, tags_dict in TAGS_BY_CATEGORY.items():
            for tag_name in tags_dict:
                tag_categories[tag_name] = category.value
        
        store_vote_tags(
            winner_model=req.winner_model,
            loser_model=req.loser_model,
            tags=req.tags,
            tag_categories=tag_categories
        )
        
        return {
            "success": True,
            "winner_model": req.winner_model,
            "winner_new_rating": round(new_winner_rating, 2),
            "loser_model": req.loser_model,
            "loser_new_rating": round(new_loser_rating, 2),
            "tags_recorded": len(req.tags),
            "tags": req.tags,
            "dimension_scores": {k: round(v, 3) for k, v in dimension_scores.items()},
        }
    except Exception as e:
        print(f"Vote with tags error: {e}")
        raise HTTPException(status_code=500, detail=f"Vote with tags failed: {str(e)}")


@app.get("/api/tags")
def get_tags():
    """Get all available tags organized by category."""
    try:
        tags = get_all_tags()
        return {
            "success": True,
            "tags": tags,
            "tag_count": sum(len(tag_dict) for tag_dict in tags.values())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch tags: {str(e)}")


@app.get("/api/ratings")
def get_ratings():
    """Get all model Elo ratings."""
    try:
        ratings = get_all_ratings()
        return {
            "ratings": ratings,
            "timestamp": str(__import__('datetime').datetime.now()),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch ratings: {str(e)}")


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


@app.post("/api/debate")
def debate(req: DebateRequest):
    """Debate endpoint: get pro and con arguments from two models for the same topic."""
    if not req.topic or not req.topic.strip():
        raise HTTPException(status_code=400, detail="Topic is required")
    
    # System prompts for each side
    pro_system = (
        "You are an expert debater arguing in favor of a position. "
        "Make a clear, well-reasoned argument with 2-3 key points. "
        "Be persuasive but fair-minded. Keep your response concise but substantive (2-3 paragraphs)."
    )
    
    con_system = (
        "You are an expert debater arguing against a position. "
        "Make a clear, well-reasoned counterargument with 2-3 key points. "
        "Be persuasive but fair-minded. Keep your response concise but substantive (2-3 paragraphs)."
    )
    
    user_msg = f"Debate topic: {req.topic}"
    
    arguments = {}
    
    # Get pro argument from Model Pro
    try:
        pro_arg = call_model(
            model=req.model_pro,
            system_msg=pro_system,
            user_msg=user_msg,
            api_key=req.api_key_pro,
            params={"temperature": 0.7, "max_tokens": 800}
        )
        arguments["pro_argument"] = {
            "model": req.model_pro,
            "argument": pro_arg
        }
    except Exception as e:
        arguments["pro_argument"] = {
            "model": req.model_pro,
            "error": str(e),
            "argument": None
        }
    
    # Get con argument from Model Con
    try:
        con_arg = call_model(
            model=req.model_con,
            system_msg=con_system,
            user_msg=user_msg,
            api_key=req.api_key_con,
            params={"temperature": 0.7, "max_tokens": 800}
        )
        arguments["con_argument"] = {
            "model": req.model_con,
            "argument": con_arg
        }
    except Exception as e:
        arguments["con_argument"] = {
            "model": req.model_con,
            "error": str(e),
            "argument": None
        }
    
    return {
        "topic": req.topic,
        "pro_argument": arguments.get("pro_argument", {}).get("argument") or "No argument provided.",
        "con_argument": arguments.get("con_argument", {}).get("argument") or "No argument provided.",
        "model_pro": req.model_pro,
        "model_con": req.model_con,
        "arguments": arguments
    }

