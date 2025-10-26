# How Tags Are Initialized for Each Model

## Overview

Tags are **not pre-initialized** for models. Instead, they are **dynamically created as votes occur**. Here's the complete flow:

---

## The Core Concept

### Models Start With No Tags
When a model first appears in the system, it has:
- ✅ An Elo rating (1500.0 by default)
- ❌ No tags yet
- ❌ No dimension scores yet

Tags are **accumulated** through voting, not created upfront.

---

## Step-by-Step Initialization Flow

### Step 1: Voter Casts a Vote with Tags
User votes on battle/debate and selects tags:
```javascript
// Frontend: js/battle.js
POST /api/vote-with-tags
{
    "winner_model": "gpt-4o",
    "loser_model": "gpt-3.5-turbo",
    "tags": ["empathetic", "cites_evidence", "logical_flow"]
}
```

### Step 2: Backend Endpoint Receives Request
`backend/api.py` - `vote_with_tags()` function:

```python
@app.post("/api/vote-with-tags")
def vote_with_tags(req: VoteWithTagsRequest):
    """Record vote with tag annotations and calculate dimension scores."""
    
    # 1. Validate all tags
    for tag in req.tags:
        if not validate_tag(tag):  # Check tag exists in TAGS_BY_CATEGORY
            raise HTTPException(status_code=400, detail=f"Invalid tag: {tag}")
    
    # 2. Initialize tags table if needed
    ensure_tags_table_exists()
    
    # 3. Update Elo ratings (models created if don't exist)
    new_winner_rating, new_loser_rating = update_ratings(
        req.winner_model, 
        req.loser_model
    )
```

### Step 3: Calculate Dimension Scores from Tags
`backend/tags.py` - `calculate_dimension_scores()`:

```python
# These tags map to dimension weights:
DIMENSION_WEIGHTS = {
    "empathetic": {
        "empathy": 0.8,         # Contributes +0.8 empathy
        "aggressiveness": -0.3  # Reduces aggressiveness
    },
    "cites_evidence": {
        "evidence_use": 0.9     # High evidence contribution
    },
    "logical_flow": {
        "evidence_use": 0.7     # Moderate evidence contribution
    },
    # ... more tags ...
}

# Algorithm:
# 1. Sum all weights for each dimension from selected tags
# 2. Average them
# 3. Map from [-1, 1] weight space to dimension range [min, max]
```

**Example Calculation:**
```
Selected tags: ["empathetic", "cites_evidence", "logical_flow"]

For "evidence_use":
  - cites_evidence contributes: 0.9
  - logical_flow contributes: 0.7
  - empathetic contributes: 0.0 (not listed)
  - Count: 2 (only 2 tags have evidence_use)
  - Average: (0.9 + 0.7) / 2 = 0.8
  - Map to dimension [0.0, 1.0]: 0.5 + (0.8 × 0.5) = 0.9
  → Result: evidence_use = 0.9

For "empathy":
  - empathetic contributes: 0.8
  - cites_evidence contributes: 0.0
  - logical_flow contributes: 0.0
  - Count: 1
  - Average: 0.8 / 1 = 0.8
  - Map to dimension [0.0, 1.0]: 0.5 + (0.8 × 0.5) = 0.9
  → Result: empathy = 0.9
```

### Step 4: Store Tags in Database
`backend/supabase_db.py` - `store_vote_tags()`:

```python
def store_vote_tags(winner_model: str, loser_model: str, 
                    tags: List[str], tag_categories: Dict):
    """
    For each tag, create ONE ROW in vote_tags table
    """
    for tag in tags:
        cursor.execute("""
            INSERT INTO vote_tags 
            (winner_model, loser_model, tag_name, tag_category)
            VALUES (%s, %s, %s, %s)
        """, (winner_model, loser_model, tag, category))
```

**Database Result** (vote_tags table):
```sql
id | winner_model  | loser_model      | tag_name        | tag_category | created_at
---|---------------|------------------|-----------------|--------------|----------
1  | gpt-4o        | gpt-3.5-turbo    | empathetic      | tone         | 2025-10-26
2  | gpt-4o        | gpt-3.5-turbo    | cites_evidence  | reasoning    | 2025-10-26
3  | gpt-4o        | gpt-3.5-turbo    | logical_flow    | reasoning    | 2025-10-26
```

### Step 5: Store Dimension Scores in Database
`backend/supabase_db.py` - `store_dimension_scores()`:

```python
def store_dimension_scores(winner_model, loser_model, 
                          winner_scores, loser_scores):
    """
    Store the calculated dimension scores
    """
    cursor.execute("""
        INSERT INTO vote_dimension_scores 
        (winner_model, loser_model,
         winner_empathy, winner_aggressiveness, winner_evidence_use,
         winner_political_economic, winner_political_social,
         loser_empathy, loser_aggressiveness, loser_evidence_use,
         loser_political_economic, loser_political_social)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (winner_model, loser_model, ...scores...))
```

**Database Result** (vote_dimension_scores table):
```sql
id | winner_model | loser_model   | winner_empathy | winner_aggressiveness | ... | loser_empathy | ...
---|--------------|---------------|----------------|----------------------|-----|---------------|-----
1  | gpt-4o       | gpt-3.5-turbo | 0.9            | 0.35                 | ... | 0.1           | ...
```

---

## Aggregation: How Models Get Tag Profiles

### Per-Model Tag Frequencies
`backend/supabase_db.py` - `get_model_tag_distribution()`:

After multiple votes, we query to get tag frequencies:

```python
def get_model_tag_distribution(model: str, as_winner: bool = True):
    """Count how often each tag was applied to this model"""
    
    cursor.execute("""
        SELECT tag_name, COUNT(*) as count
        FROM vote_tags
        WHERE winner_model = %s
        GROUP BY tag_name
        ORDER BY count DESC
    """, (model,))
    
    # Returns normalized to 0.0-1.0:
    # {"empathetic": 0.35, "cites_evidence": 0.28, ...}
```

### Per-Model Dimension Scores
`backend/supabase_db.py` - `get_aggregated_dimension_scores()`:

Averages dimension scores across ALL votes:

```python
def get_aggregated_dimension_scores(model_name=None):
    """
    Average all dimension scores for a model across its votes
    """
    cursor.execute("""
        SELECT 
            winner_model,
            AVG(winner_empathy) as empathy,
            AVG(winner_aggressiveness) as aggressiveness,
            AVG(winner_evidence_use) as evidence_use,
            ...
        FROM vote_dimension_scores
        WHERE winner_model = %s
        GROUP BY winner_model
    """)
    
    # Also aggregate votes where it LOST (use loser columns)
    # Combine both to get complete picture
```

**Result** (after 10 votes for gpt-4o):
```json
{
    "gpt-4o": {
        "empathy": 0.72,
        "aggressiveness": 0.38,
        "evidence_use": 0.81,
        "political_economic": 0.05,
        "political_social": -0.08,
        "vote_count": 10
    }
}
```

---

## Complete Data Flow Diagram

```
INITIALIZATION → VOTING → CALCULATION → STORAGE → AGGREGATION → DISPLAY

1. Model has Elo rating
   (created on first vote if needed)
   
2. Voter selects tags on battle/debate
   ↓
3. /api/vote-with-tags endpoint called
   ↓
4. Backend:
   a) Validate tags exist in TAGS_BY_CATEGORY
   b) Update Elo ratings
   c) Calculate dimension scores from DIMENSION_WEIGHTS
   d) Store individual tags in vote_tags table
   e) Store dimension scores in vote_dimension_scores table
   ↓
5. After multiple votes, analytics query:
   a) GET /api/dimension-scores → Aggregated dimensions per model
   b) Get dimension leaderboards ranked by score
   c) Display in Tag Analytics dashboard
```

---

## Key Data Structures

### 1. TAGS_BY_CATEGORY (Static)
Defined in `backend/tags.py` - never changes:

```python
{
    "tone": {
        "empathetic": "Shows understanding...",
        "respectful": "Professional tone...",
        "inflammatory": "Hostile...",
        "dismissive": "Ignores counterarguments..."
    },
    "reasoning": {
        "cites_evidence": "Uses data, studies...",
        "logical_flow": "Clear reasoning...",
        "hasty_generalization": "Overgeneralizes...",
        "circular_reasoning": "Begs the question..."
    },
    "structure": { /* ... */ },
    "content": { /* ... */ }
}
```

### 2. DIMENSION_WEIGHTS (Static)
Maps each tag to its impact on dimensions:

```python
{
    "empathetic": {
        "empathy": 0.8,
        "aggressiveness": -0.3
    },
    "cites_evidence": {
        "evidence_use": 0.9
    },
    # ... 16 tags total ...
}
```

### 3. DIMENSIONS (Static)
Defines dimension ranges and properties:

```python
{
    "empathy": {
        "min": 0.0,
        "max": 1.0,
        "default": 0.5,
        "description": "How well the argument acknowledges other perspectives"
    },
    "aggressiveness": {
        "min": 0.0,
        "max": 1.0,
        "default": 0.5,
        "description": "How combative vs collaborative the tone is"
    },
    # ... 5 dimensions total ...
}
```

---

## Dynamic vs Static Initialization

| Aspect | Type | Initialized | How |
|--------|------|-------------|-----|
| **Tags** (TAGS_BY_CATEGORY) | Static | At startup | Hard-coded in backend/tags.py |
| **Dimension Weights** | Static | At startup | Hard-coded in backend/tags.py |
| **Dimension Definitions** | Static | At startup | Hard-coded in backend/tags.py |
| **Model Elo Rating** | Dynamic | On first vote | Auto-created in elo_ratings table |
| **Model Tag History** | Dynamic | Per vote | One row per tag in vote_tags table |
| **Model Dimension Scores** | Dynamic | Per vote | One row per vote in vote_dimension_scores table |
| **Aggregated Tag Profile** | Computed | On query | Aggregates from vote_tags table |
| **Aggregated Dimension Profile** | Computed | On query | Averages from vote_dimension_scores table |

---

## Example: Complete Vote Lifecycle

### Initial State
```
gpt-4o: Not in database yet
gpt-3.5-turbo: Not in database yet
```

### Vote 1: User selects tags
```json
{
    "winner": "gpt-4o",
    "loser": "gpt-3.5-turbo",
    "tags": ["empathetic", "cites_evidence"]
}
```

### Backend Processing
1. ✅ Tags validated (both exist in TAGS_BY_CATEGORY)
2. ✅ Create gpt-4o with 1500 rating (auto-created)
3. ✅ Create gpt-3.5-turbo with 1500 rating (auto-created)
4. ✅ Calculate scores:
   - empathy = 0.9
   - evidence_use = 0.9
   - others = 0.5 (default)
5. ✅ Insert into vote_tags (2 rows):
   - (gpt-4o, gpt-3.5-turbo, empathetic)
   - (gpt-4o, gpt-3.5-turbo, cites_evidence)
6. ✅ Insert into vote_dimension_scores (1 row with all 5 dimensions)

### Vote 2: Different voter, same models
```json
{
    "winner": "gpt-4o",
    "loser": "gpt-3.5-turbo",
    "tags": ["empathetic", "balanced", "source_verified"]
}
```

### After Vote 2
Tag Analytics can now show:
```json
{
    "gpt-4o": {
        "empathy": 0.88,           // Average of votes 1 & 2
        "aggressiveness": 0.35,    // Default + balanced effect
        "evidence_use": 0.92,      // Average of votes 1 & 2
        "vote_count": 2
    }
}
```

---

## Summary

✅ **Tags are NOT pre-initialized** - they're built dynamically from votes

✅ **Tag definitions are static** - hardcoded in backend/tags.py

✅ **Models are created on first vote** - with default 1500 Elo rating

✅ **Dimension scores calculated real-time** - from selected tags using DIMENSION_WEIGHTS

✅ **Aggregation happens on query** - averaging across all votes per model

✅ **Analytics show real voter data** - not mocked or generated
