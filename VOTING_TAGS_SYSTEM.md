# 🏷️ Enhanced Voting System - Rich Labels & Dimension Tracking

## Vision

Currently voting is binary (A vs B). We want to collect:
1. **Why** (tags: empathetic, cites evidence, avoids extremes, etc.)
2. **Who** (optional demographics: country, age, political-ID - anonymized)
3. **Map to dimensions** (Political-economic, Social, Empathy, Aggressiveness, Evidence)

---

## Phase 1: Core Tag System (Week 1)

### Database Schema

Add to `elo_ratings` table:
```sql
-- Track argument qualities
CREATE TABLE argument_tags (
  id SERIAL PRIMARY KEY,
  battle_id UUID NOT NULL,
  winner_model VARCHAR(255),
  loser_model VARCHAR(255),
  tag_name VARCHAR(100),  -- "empathetic", "cites_evidence", etc.
  tag_category VARCHAR(50),  -- "tone", "reasoning", "structure", etc.
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Track voter demographics (optional, anonymized)
CREATE TABLE voter_demographics (
  id SERIAL PRIMARY KEY,
  vote_id UUID NOT NULL,
  country_code VARCHAR(2),  -- e.g., "US", "UK"
  age_range VARCHAR(20),    -- e.g., "18-25", "26-35"
  political_spectrum VARCHAR(50),  -- e.g., "left", "center", "right"
  anonymized_hash VARCHAR(255),  -- Hash for grouping while preserving privacy
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tag→Dimension mapping (weights)
CREATE TABLE tag_dimension_weights (
  id SERIAL PRIMARY KEY,
  tag_name VARCHAR(100),
  dimension_name VARCHAR(100),  -- "political_economic", "empathy", etc.
  weight DECIMAL(4, 2),  -- -1.0 to 1.0
  description TEXT
);
```

### Available Tags

**Tone Tags:**
- `empathetic` - Shows understanding of other perspectives
- `respectful` - Professional, non-insulting
- `inflammatory` - Hostile, name-calling
- `dismissive` - Ignores counterarguments

**Reasoning Tags:**
- `cites_evidence` - Uses data, studies, sources
- `logical_flow` - Clear reasoning structure
- `hasty_generalization` - Overgeneralizes
- `circular_reasoning` - Begs the question

**Structure Tags:**
- `avoids_extremes` - Acknowledges nuance
- `balanced` - Presents multiple sides
- `strawman` - Misrepresents opponent
- `oversimplifies` - Too reductive

**Content Tags:**
- `factually_accurate` - Verifiable claims
- `source_verified` - Can verify sources
- `misleading` - Technically true but misleading
- `false_claim` - Factually incorrect

---

## Phase 2: Frontend Tag Selection (Week 1)

### Updated Vote UI

```html
<div id="vote-modal" class="modal">
  <h3>Who won this debate?</h3>
  
  <button class="vote-btn pro">Vote: Pro Wins</button>
  <button class="vote-btn con">Vote: Con Wins</button>
  
  <!-- Tag selection (appears after vote) -->
  <div id="tag-selection" class="hidden">
    <h4>Why did they win? (select all that apply)</h4>
    
    <fieldset class="tag-group">
      <legend>Tone</legend>
      <label><input type="checkbox" value="empathetic"> Empathetic</label>
      <label><input type="checkbox" value="respectful"> Respectful</label>
      <label><input type="checkbox" value="inflammatory"> Inflammatory</label>
      <label><input type="checkbox" value="dismissive"> Dismissive</label>
    </fieldset>
    
    <fieldset class="tag-group">
      <legend>Reasoning</legend>
      <label><input type="checkbox" value="cites_evidence"> Cites evidence</label>
      <label><input type="checkbox" value="logical_flow"> Clear logic</label>
      <label><input type="checkbox" value="hasty_generalization"> Hasty generalization</label>
      <label><input type="checkbox" value="circular_reasoning"> Circular reasoning</label>
    </fieldset>
    
    <fieldset class="tag-group">
      <legend>Structure</legend>
      <label><input type="checkbox" value="avoids_extremes"> Avoids extremes</label>
      <label><input type="checkbox" value="balanced"> Balanced</label>
      <label><input type="checkbox" value="strawman"> Strawman</label>
      <label><input type="checkbox" value="oversimplifies"> Oversimplifies</label>
    </fieldset>
    
    <fieldset class="tag-group">
      <legend>Content</legend>
      <label><input type="checkbox" value="factually_accurate"> Factually accurate</label>
      <label><input type="checkbox" value="source_verified"> Sources verified</label>
      <label><input type="checkbox" value="misleading"> Misleading</label>
      <label><input type="checkbox" value="false_claim"> False claim</label>
    </fieldset>
    
    <!-- Optional: Demographics (collapsible) -->
    <details>
      <summary>Optional: Tell us about yourself (anonymized)</summary>
      <label>
        Country:
        <input type="text" name="country" placeholder="e.g., US, UK, CA">
      </label>
      <label>
        Age range:
        <select name="age_range">
          <option>Prefer not to say</option>
          <option>18-25</option>
          <option>26-35</option>
          <option>36-50</option>
          <option>51-65</option>
          <option>65+</option>
        </select>
      </label>
      <label>
        Political spectrum:
        <select name="political_spectrum">
          <option>Prefer not to say</option>
          <option>Far left</option>
          <option>Left</option>
          <option>Center-left</option>
          <option>Center</option>
          <option>Center-right</option>
          <option>Right</option>
          <option>Far right</option>
        </select>
      </label>
    </details>
    
    <button id="submit-tags">Submit Vote & Tags</button>
  </div>
</div>
```

### Frontend Logic

```javascript
async function submitVoteWithTags(winnerModel, loserModel, selectedTags, demographics) {
  const response = await fetch(`${API_CONFIG.BACKEND_URL}/api/vote-with-tags`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      winner_model: winnerModel,
      loser_model: loserModel,
      tags: selectedTags,  // e.g., ["empathetic", "cites_evidence"]
      demographics: demographics || null,  // Optional
      debate_id: currentDebateId,
      topic: currentTopic
    })
  });
  
  const data = await response.json();
  
  if (data.success) {
    // Show dimension scores
    showDimensionScores(data.dimension_scores);
    showConfirmation("Vote recorded with tags!");
  }
}
```

---

## Phase 3: Backend Tag→Dimension Mapping (Week 2)

### Tag Weights Matrix

```python
# backend/tag_weights.py

TAG_DIMENSION_WEIGHTS = {
    # Tone tags
    "empathetic": {
        "empathy": 0.8,
        "aggressiveness": -0.3,
    },
    "respectful": {
        "aggressiveness": -0.5,
        "empathy": 0.4,
    },
    "inflammatory": {
        "aggressiveness": 0.8,
        "empathy": -0.6,
    },
    "dismissive": {
        "empathy": -0.7,
        "aggressiveness": 0.3,
    },
    
    # Reasoning tags
    "cites_evidence": {
        "evidence_use": 0.9,
        "political_economic": 0.1,  # Neutral by default
    },
    "logical_flow": {
        "evidence_use": 0.7,
    },
    "hasty_generalization": {
        "evidence_use": -0.6,
    },
    "circular_reasoning": {
        "evidence_use": -0.8,
    },
    
    # Structure tags
    "avoids_extremes": {
        "political_economic": 0.0,  # Center
        "political_social": 0.0,
    },
    "balanced": {
        "empathy": 0.5,
        "political_economic": 0.0,  # Balanced
    },
    "strawman": {
        "evidence_use": -0.7,
        "aggressiveness": 0.5,
    },
    "oversimplifies": {
        "evidence_use": -0.5,
    },
    
    # Content tags
    "factually_accurate": {
        "evidence_use": 0.8,
    },
    "source_verified": {
        "evidence_use": 0.9,
    },
    "misleading": {
        "evidence_use": -0.7,
        "aggressiveness": 0.3,  # Often used aggressively
    },
    "false_claim": {
        "evidence_use": -0.9,
    },
}

DIMENSIONS = {
    "political_economic": {
        "description": "Left ← → Right",
        "min": -1.0,
        "max": 1.0,
        "default": 0.0,
    },
    "political_social": {
        "description": "Libertarian ← → Authoritarian",
        "min": -1.0,
        "max": 1.0,
        "default": 0.0,
    },
    "empathy": {
        "description": "Low ← → High",
        "min": 0.0,
        "max": 1.0,
        "default": 0.5,
    },
    "aggressiveness": {
        "description": "Low ← → High",
        "min": 0.0,
        "max": 1.0,
        "default": 0.5,
    },
    "evidence_use": {
        "description": "Low ← → High",
        "min": 0.0,
        "max": 1.0,
        "default": 0.5,
    },
}

def calculate_dimension_scores(tags: List[str]) -> Dict[str, float]:
    """
    Convert tag selections into dimension scores.
    
    Args:
        tags: List of selected tag names
        
    Returns:
        Dict mapping dimension names to scores [0, 1] or [-1, 1]
    """
    dimension_scores = {dim: DIMENSIONS[dim]["default"] 
                       for dim in DIMENSIONS}
    
    # Sum weights from all selected tags
    tag_weights = {}
    for tag in tags:
        if tag in TAG_DIMENSION_WEIGHTS:
            for dimension, weight in TAG_DIMENSION_WEIGHTS[tag].items():
                if dimension not in tag_weights:
                    tag_weights[dimension] = 0
                tag_weights[dimension] += weight
    
    # Normalize: average the weights and map to dimension range
    for dimension in dimension_scores:
        if dimension in tag_weights:
            avg_weight = tag_weights[dimension] / max(len(tags), 1)
            
            # Map from [-1, 1] to dimension range
            dim_config = DIMENSIONS[dimension]
            min_val = dim_config["min"]
            max_val = dim_config["max"]
            
            # Linear mapping: avg_weight ∈ [-1, 1] → [min_val, max_val]
            if avg_weight >= 0:
                score = dim_config["default"] + (avg_weight * (max_val - dim_config["default"]))
            else:
                score = dim_config["default"] + (avg_weight * (dim_config["default"] - min_val))
            
            dimension_scores[dimension] = max(min_val, min(max_val, score))
    
    return dimension_scores
```

### Backend Endpoint

```python
# backend/api.py

class VoteWithTagsRequest(BaseModel):
    winner_model: str
    loser_model: str
    tags: List[str] = []
    demographics: Optional[Dict] = None
    debate_id: Optional[str] = None
    topic: Optional[str] = None

@app.post("/api/vote-with-tags")
def vote_with_tags(req: VoteWithTagsRequest):
    """Record vote with tag annotations and optional demographics."""
    
    try:
        # Update Elo ratings (existing logic)
        new_winner_rating, new_loser_rating = update_ratings(
            req.winner_model, 
            req.loser_model
        )
        
        # Calculate dimension scores from tags
        from .tag_weights import calculate_dimension_scores
        dimension_scores = calculate_dimension_scores(req.tags)
        
        # Store tags in database
        store_vote_tags(
            winner_model=req.winner_model,
            loser_model=req.loser_model,
            tags=req.tags,
            dimensions=dimension_scores,
            debate_id=req.debate_id,
            topic=req.topic
        )
        
        # Store demographics if provided (anonymized)
        if req.demographics:
            store_voter_demographics(
                demographics=req.demographics,
                anonymized=True  # Hash sensitive info
            )
        
        return {
            "success": True,
            "winner_model": req.winner_model,
            "winner_new_rating": new_winner_rating,
            "loser_model": req.loser_model,
            "loser_new_rating": new_loser_rating,
            "tags_recorded": len(req.tags),
            "dimension_scores": dimension_scores,
        }
        
    except Exception as e:
        print(f"Vote with tags error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

---

## Phase 4: Analytics & Visualization (Week 2-3)

### New Endpoints

```python
@app.get("/api/model-profile/{model_name}")
def get_model_profile(model_name: str):
    """Get detailed model profile with dimension scores."""
    return {
        "model": model_name,
        "rating": get_rating(model_name),
        "dimensions": get_model_dimensions(model_name),  # Avg across all votes
        "tag_distribution": get_model_tag_distribution(model_name),
        "win_rate": get_win_rate(model_name),
    }

@app.get("/api/subgroup-analysis")
def subgroup_analysis(dimension: str, subgroup: str):
    """Analyze voting patterns by demographic subgroup."""
    return {
        "dimension": dimension,
        "subgroup": subgroup,
        "model_scores": get_model_scores_by_subgroup(dimension, subgroup),
        "sample_size": get_subgroup_sample_size(subgroup),
    }

@app.get("/api/topic-dimensions/{topic}")
def topic_dimensions(topic: str):
    """What dimensions does this topic reveal?"""
    return {
        "topic": topic,
        "dimension_variance": calculate_topic_variance(topic),
        "tag_frequency": get_topic_tag_frequency(topic),
        "models_involved": get_models_for_topic(topic),
    }
```

### Dashboard Visualization

```html
<!-- New analysis dashboard -->
<div class="dimension-radar">
  <!-- Radar chart: 5 dimensions for each model -->
  <canvas id="dimension-chart"></canvas>
</div>

<div class="tag-heatmap">
  <!-- Heatmap: which tags appear most for winning arguments? -->
  <canvas id="tag-heatmap"></canvas>
</div>

<div class="subgroup-comparison">
  <!-- How do different countries rate models? -->
  <div id="subgroup-analysis"></div>
</div>

<div class="topic-analysis">
  <!-- Which topics trigger strong dimension variation? -->
  <table id="topic-dimensions"></table>
</div>
```

---

## Phase 5: Tuning & Refinement (Ongoing)

### Learning Loop

```python
def auto-tune_weights():
    """
    Periodically re-calibrate tag weights based on:
    1. Correlation with model Elo changes
    2. Subgroup consistency
    3. Voter feedback
    """
    # If "empathetic" tagged arguments consistently win,
    # increase empathy weight
    
    # If dimension predictions don't match outcomes,
    # adjust weights
    
    # Log before/after for A/B testing
```

### A/B Testing Tags

You could test which tags matter most:
- **Control:** No tags (current system)
- **Variant A:** Basic 4 tags (tone, reasoning, structure, content)
- **Variant B:** Detailed 16 tags (current proposal)
- **Variant C:** ML-generated tags (use LLM to suggest)

---

## Implementation Roadmap

### Week 1: Core Infrastructure
- [ ] Database schema (tags, demographics, weights)
- [ ] Tag selection UI
- [ ] Basic tag→dimension mapping
- [ ] `/api/vote-with-tags` endpoint

### Week 2: Analytics
- [ ] Model profile endpoint
- [ ] Subgroup analysis endpoint
- [ ] Topic analysis endpoint
- [ ] Basic visualizations

### Week 3: Polish & Launch
- [ ] Mobile-friendly tag UI
- [ ] Tutorial for voters (why tags matter)
- [ ] Documentation
- [ ] Launch with initial weights

### Ongoing: Tuning
- [ ] Monitor tag correlation with outcomes
- [ ] Refine weights monthly
- [ ] Add subgroup-specific weights
- [ ] A/B test new tags

---

## Quick Start (Simplified Version)

If you want to start simple:

### MVP (Minimal Viable Product)

Just 4 tags to start:
1. **empathetic** - Understands other side
2. **cites_evidence** - Uses data
3. **avoids_extremes** - Balanced
4. **respectful** - Professional tone

These map to 3 dimensions:
- Empathy: 0-1
- Evidence use: 0-1
- Aggressiveness: 0-1

Ship this first, then expand!

---

## Privacy Considerations

✅ **Good:**
- Demographics are optional
- Hash voter IDs (can't track individuals)
- Aggregate at country/age group level
- Only use for research, not targeting

❌ **Avoid:**
- Don't track individual voters
- Don't combine with IP data
- Don't sell voter data
- Clearly document privacy policy

---

## Questions to Answer

1. **Should we weight tags equally or use ML to learn weights?**
   - Start equal, tune by hand, eventually use ML

2. **How many people need to vote before we trust dimension scores?**
   - Probably 10-20 votes per argument type

3. **Should dimension scores affect Elo, or are they just analytics?**
   - Keep separate initially. They provide context, not rankings.

4. **How do we handle disagreement (voters disagree on tags)?**
   - Take majority vote or track distribution

5. **Can viewers see tags/dimensions?**
   - Yes! Shows what makes arguments strong

---

## Success Metrics

📊 **Track these over time:**

- Average tags per vote (adoption)
- Correlation between tags and Elo change (validity)
- Subgroup differences (interesting insights)
- Tag distribution (which attributes matter)
- Dimension variance by topic (which topics are divisive)

---

**Ready to implement?** Start with Phase 1 + Phase 2 for Week 1! 🚀
