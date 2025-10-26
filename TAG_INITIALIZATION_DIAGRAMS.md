# Tag Initialization Architecture - Visual Guide

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         STATIC DEFINITIONS (Backend)                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  backend/tags.py:                                                           │
│  ┌────────────────────┐  ┌──────────────────┐  ┌────────────────────┐     │
│  │  TAGS_BY_CATEGORY  │  │ DIMENSION_WEIGHTS│  │    DIMENSIONS      │     │
│  │                    │  │                  │  │                    │     │
│  │ "tone" → [         │  │ "empathetic" →   │  │ "empathy" →        │     │
│  │   empathetic       │  │   {empathy: 0.8, │  │   {min: 0.0,       │     │
│  │   respectful       │  │    aggressiveness│  │    max: 1.0,       │     │
│  │   inflammatory     │  │    -0.3}         │  │    default: 0.5}   │     │
│  │   dismissive       │  │                  │  │                    │     │
│  │ ]                  │  │ "cites_evidence"→│  │ "evidence_use" →   │     │
│  │                    │  │   {evidence_use: │  │   {min: 0.0,       │     │
│  │ "reasoning" → [    │  │    0.9}          │  │    max: 1.0,       │     │
│  │   cites_evidence   │  │                  │  │    default: 0.5}   │     │
│  │   logical_flow     │  │ ... 16 tags ...  │  │                    │     │
│  │   hasty_general...│  │                  │  │ "political_economic"│     │
│  │   circular_reason..│ │                  │  │   {min: -1.0,      │     │
│  │ ]                  │  │                  │  │    max: 1.0,       │     │
│  │                    │  │                  │  │    default: 0.0}   │     │
│  │ ... (more tags)    │  │                  │  │                    │     │
│  └────────────────────┘  └──────────────────┘  └────────────────────┘     │
│                                                                              │
│  ☝️  NEVER CHANGES - Loaded at backend startup                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                         VOTING FLOW (Request)                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Frontend (battle.html / debate.html):                                     │
│  ┌──────────────────────────────────┐                                      │
│  │ User clicks Vote button           │                                      │
│  │ Tag modal appears                 │                                      │
│  │ User selects tags:                │                                      │
│  │  ☑ empathetic                    │                                      │
│  │  ☑ cites_evidence                │                                      │
│  │  ☑ logical_flow                  │                                      │
│  │ (selected 3 tags from 16 total)  │                                      │
│  └──────────────────────────────────┘                                      │
│           ↓                                                                  │
│  POST /api/vote-with-tags                                                   │
│  {                                                                           │
│    "winner_model": "gpt-4o",                                                │
│    "loser_model": "gpt-3.5-turbo",                                          │
│    "tags": ["empathetic", "cites_evidence", "logical_flow"]               │
│  }                                                                           │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                     BACKEND PROCESSING (api.py)                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1. VALIDATE                                                                 │
│     For each tag, check: tag in TAGS_BY_CATEGORY? ✅ ✅ ✅                │
│     All valid → continue                                                     │
│                                                                              │
│  2. UPDATE RATINGS (elo.py)                                                 │
│     gpt-4o: 1500 → 1508                                                     │
│     gpt-3.5-turbo: 1500 → 1492                                              │
│                                                                              │
│  3. CALCULATE DIMENSION SCORES (tags.py)                                    │
│     Selected tags: ["empathetic", "cites_evidence", "logical_flow"]       │
│                                                                              │
│     For each dimension:                                                      │
│     ┌──────────────┬─────────────────────────────────────────────────────┐ │
│     │ Dimension    │ Calculation                                         │ │
│     ├──────────────┼─────────────────────────────────────────────────────┤ │
│     │ empathy      │ empathetic(0.8) / 1 = 0.8 → map to 0.9            │ │
│     │ aggressiv.   │ empathetic(-0.3) / 1 = -0.3 → map to 0.35         │ │
│     │ evidence_use │ (0.9 + 0.7)/2 = 0.8 → map to 0.9                │ │
│     │ pol_econ     │ no tags → 0.0 (default)                            │ │
│     │ pol_social   │ no tags → 0.0 (default)                            │ │
│     └──────────────┴─────────────────────────────────────────────────────┘ │
│                                                                              │
│     Result: {                                                                │
│       "empathy": 0.9,                                                        │
│       "aggressiveness": 0.35,                                               │
│       "evidence_use": 0.9,                                                  │
│       "political_economic": 0.0,                                            │
│       "political_social": 0.0                                               │
│     }                                                                        │
│                                                                              │
│  4. STORE TAGS (supabase_db.py)                                             │
│     For each tag, insert row:                                                │
│                                                                              │
│     vote_tags table:                                                        │
│     ┌─────────────────────────────────────────────────────────────────┐   │
│     │ id│winner      │loser            │tag_name       │category    │   │
│     ├───┼────────────┼─────────────────┼───────────────┼────────────┤   │
│     │ 1 │gpt-4o      │gpt-3.5-turbo    │empathetic     │tone        │   │
│     │ 2 │gpt-4o      │gpt-3.5-turbo    │cites_evidence │reasoning   │   │
│     │ 3 │gpt-4o      │gpt-3.5-turbo    │logical_flow   │reasoning   │   │
│     └─────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  5. STORE DIMENSION SCORES (supabase_db.py)                                 │
│                                                                              │
│     vote_dimension_scores table:                                            │
│     ┌──────────────────────────────────────────────────────────────────┐   │
│     │id│winner │loser      │w_empathy│w_aggr│w_evid│l_empathy│l_aggr│   │
│     ├──┼───────┼───────────┼─────────┼──────┼──────┼─────────┼───────┤   │
│     │1 │gpt-4o │gpt-3.5t..│0.9      │0.35  │0.9   │0.1      │0.65   │   │
│     └──────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│     (Loser scores calculated as: 1.0 - winner_score)                       │
│     Winner empathy 0.9 → Loser empathy 0.1                                  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                       DATABASE STORAGE (Supabase)                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Table 1: vote_tags                                                         │
│  ┌────────────────────────────────────────────────────────────────┐        │
│  │ Stores individual tag selections per vote                     │        │
│  │ 3 rows inserted for this vote (one per tag)                   │        │
│  │ Used to build tag frequency profiles                          │        │
│  └────────────────────────────────────────────────────────────────┘        │
│                                                                              │
│  Table 2: vote_dimension_scores                                             │
│  ┌────────────────────────────────────────────────────────────────┐        │
│  │ Stores calculated dimension scores                            │        │
│  │ 1 row inserted per vote (contains all 5 dimensions)           │        │
│  │ Used to aggregate dimension profiles                          │        │
│  └────────────────────────────────────────────────────────────────┘        │
│                                                                              │
│  Table 3: elo_ratings (updated)                                             │
│  ┌────────────────────────────────────────────────────────────────┐        │
│  │ gpt-4o: 1500 → 1508 (winner)                                  │        │
│  │ gpt-3.5-turbo: 1500 → 1492 (loser)                            │        │
│  └────────────────────────────────────────────────────────────────┘        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                    AGGREGATION (Analytics Queries)                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  After 10+ votes, analytics queries aggregate:                              │
│                                                                              │
│  1. GET /api/dimension-scores → Aggregates vote_dimension_scores            │
│     ┌──────────────────────────────────────────────────────────────┐       │
│     │ gpt-4o:                                                      │       │
│     │  - empathy: AVG(0.9, 0.87, 0.92, ...) = 0.89               │       │
│     │  - aggressiveness: AVG(0.35, 0.40, 0.32, ...) = 0.36       │       │
│     │  - evidence_use: AVG(0.9, 0.88, 0.95, ...) = 0.91          │       │
│     │  - vote_count: 10                                           │       │
│     │                                                              │       │
│     │ gpt-3.5-turbo:                                              │       │
│     │  - empathy: AVG(0.1, 0.13, 0.08, ...) = 0.11               │       │
│     │  - aggressiveness: AVG(0.65, 0.60, 0.68, ...) = 0.64       │       │
│     │  - evidence_use: AVG(0.1, 0.12, 0.05, ...) = 0.09          │       │
│     │  - vote_count: 10                                           │       │
│     └──────────────────────────────────────────────────────────────┘       │
│                                                                              │
│  2. GET /api/tag-distribution/gpt-4o → Aggregates vote_tags                │
│     ┌──────────────────────────────────────────────────────────────┐       │
│     │ Tag frequencies:                                             │       │
│     │  - empathetic: 0.35 (7 of 20 tags)                         │       │
│     │  - cites_evidence: 0.28 (5 of 20 tags)                     │       │
│     │  - logical_flow: 0.22 (4 of 20 tags)                       │       │
│     │  - balanced: 0.15 (3 of 20 tags)                           │       │
│     └──────────────────────────────────────────────────────────────┘       │
│                                                                              │
│  3. GET /api/dimension-leaderboard/empathy?limit=10 → Ranks models          │
│     ┌──────────────────────────────────────────────────────────────┐       │
│     │ #1: gpt-4o → 0.89 empathy                                  │       │
│     │ #2: claude-3-sonnet → 0.87 empathy                         │       │
│     │ #3: gemini-2.0-flash → 0.81 empathy                        │       │
│     │ ... (7 more models)                                         │       │
│     └──────────────────────────────────────────────────────────────┘       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                     FRONTEND DISPLAY (Analytics)                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Tag Analytics Dashboard (tag-analytics.html):                              │
│                                                                              │
│  Quality Dimensions Section:                                                │
│  ┌──────────────────────────────────────────────────────────────┐          │
│  │ 💜 Empathy                                                   │          │
│  │ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐               │          │
│  │ │ gpt4o│ │claude│ │gemini│ │openai│ │meta  │ ...           │          │
│  │ │ 0.89 │ │ 0.87 │ │ 0.81 │ │ 0.75 │ │ 0.72 │               │          │
│  │ └──────┘ └──────┘ └──────┘ └──────┘ └──────┘               │          │
│  │ Leaderboard:                                                │          │
│  │ #1 gpt-4o         0.89                                      │          │
│  │ #2 claude-3       0.87                                      │          │
│  │ #3 gemini         0.81                                      │          │
│  └──────────────────────────────────────────────────────────────┘          │
│                                                                              │
│  Model Comparison:                                                          │
│  ┌──────────────────────────────────────────────────────────────┐          │
│  │ gpt-4o          vs        gpt-3.5-turbo                      │          │
│  │ ├─ Empathy    ────────┤   ├─ Empathy  ──────┤               │          │
│  │ ├─ Aggressiv  ───┤        ├─ Aggressiv ────────┤            │          │
│  │ ├─ Evidence   ────────┤   ├─ Evidence  ───┤                 │          │
│  │ └─ Pol Econ   ──┤        └─ Pol Econ   ──┤                 │          │
│  └──────────────────────────────────────────────────────────────┘          │
│                                                                              │
│  All data is REAL, aggregated from actual voter tags & assessments ✅      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Dimension Score Calculation Algorithm

```
STEP 1: Collect Weights
┌─────────────────────────────────────────────┐
│ Selected tags: ["empathetic", "cites_evidence", "logical_flow"]           │
│                                              │
│ DIMENSION_WEIGHTS mapping:                   │
│                                              │
│ "empathetic" → {                             │
│   "empathy": 0.8,                           │
│   "aggressiveness": -0.3                    │
│ }                                           │
│                                              │
│ "cites_evidence" → {                         │
│   "evidence_use": 0.9                       │
│ }                                           │
│                                              │
│ "logical_flow" → {                           │
│   "evidence_use": 0.7                       │
│ }                                           │
└─────────────────────────────────────────────┘

STEP 2: Aggregate by Dimension
┌─────────────────────────────────────────────┐
│ empathy: [0.8]               count=1        │
│ aggressiveness: [-0.3]       count=1        │
│ evidence_use: [0.9, 0.7]     count=2        │
│ political_economic: []       count=0        │
│ political_social: []         count=0        │
└─────────────────────────────────────────────┘

STEP 3: Calculate Averages
┌─────────────────────────────────────────────┐
│ empathy: 0.8 / 1 = 0.8                     │
│ aggressiveness: -0.3 / 1 = -0.3            │
│ evidence_use: (0.9 + 0.7) / 2 = 0.8        │
│ political_economic: 0 / 0 = 0.0 (default)  │
│ political_social: 0 / 0 = 0.0 (default)    │
└─────────────────────────────────────────────┘

STEP 4: Map to Dimension Ranges
┌─────────────────────────────────────────────────────────────────┐
│ For each dimension with avg_weight:                            │
│                                                                │
│ if avg_weight >= 0:                                            │
│   score = default + (avg_weight × (max - default))             │
│ else:                                                           │
│   score = default + (avg_weight × (default - min))             │
│                                                                │
│ empathy (min=0.0, max=1.0, default=0.5):                      │
│   avg_weight = 0.8 ≥ 0                                        │
│   score = 0.5 + (0.8 × (1.0 - 0.5)) = 0.5 + 0.4 = 0.9 ✅    │
│                                                                │
│ aggressiveness (min=0.0, max=1.0, default=0.5):               │
│   avg_weight = -0.3 < 0                                       │
│   score = 0.5 + (-0.3 × (0.5 - 0.0)) = 0.5 - 0.15 = 0.35 ✅ │
│                                                                │
│ evidence_use (min=0.0, max=1.0, default=0.5):                 │
│   avg_weight = 0.8 ≥ 0                                        │
│   score = 0.5 + (0.8 × (1.0 - 0.5)) = 0.5 + 0.4 = 0.9 ✅    │
│                                                                │
│ political_economic (min=-1.0, max=1.0, default=0.0):          │
│   avg_weight = 0.0 = 0                                        │
│   score = 0.0 + (0.0 × ...) = 0.0 ✅                          │
│                                                                │
│ political_social (min=-1.0, max=1.0, default=0.0):            │
│   avg_weight = 0.0 = 0                                        │
│   score = 0.0 + (0.0 × ...) = 0.0 ✅                          │
└─────────────────────────────────────────────────────────────────┘

FINAL RESULT:
┌──────────────────────────────┐
│ {                            │
│   "empathy": 0.9,           │
│   "aggressiveness": 0.35,   │
│   "evidence_use": 0.9,      │
│   "political_economic": 0.0,│
│   "political_social": 0.0   │
│ }                            │
└──────────────────────────────┘
```

---

## When Do Tags Get "Initialized"?

### Timeline for a New Model (e.g., "gpt-4o")

```
Before First Vote:
  gpt-4o: Not in any database table
  Status: Doesn't exist in system yet
  
First Vote (gpt-4o wins):
  ✅ Model created in elo_ratings (1500 rating)
  ✅ 3 tags added to vote_tags table (for vote)
  ✅ Dimension scores added to vote_dimension_scores
  ✅ Now in database with profile beginning to form
  
After 5 Votes:
  ✅ elo_ratings: Shows current Elo score
  ✅ vote_tags: 15 total tag records across 5 votes
  ✅ vote_dimension_scores: 5 dimension records
  ✅ Analytics can aggregate and show initial profile
  
After 20+ Votes:
  ✅ Clear dimension score profile forms
  ✅ Tag frequency distribution stabilizes
  ✅ Leaderboards include model with meaningful rankings
  ✅ Model comparison shows real voter-assessed characteristics
```

---

## Key Takeaways

### ❌ NOT Pre-initialized
- Models don't have predefined tag profiles
- No "artificial" data injected
- No default tag distributions

### ✅ Dynamically Built
- First appearance: Model created on first vote
- Tags collected as votes occur
- Scores calculated from voter-selected tags
- Profiles build through aggregation

### ✅ Voter-Driven
- Voters select tags (16 to choose from)
- Backend calculates impact on dimensions
- Multiple votes aggregate into profiles
- Analytics show voter consensus patterns

### ✅ Data-Driven Analytics
- All displayed metrics come from real votes
- No mock data generation
- Profiles update in real-time as votes come in
- Leaderboards reflect actual voter assessments
