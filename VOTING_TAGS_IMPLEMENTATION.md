# 🏷️ Phase 1: Implementing Rich Tags - Practical Guide

## Overview

This guide walks through implementing just Phase 1 (Weeks 1-2) of the tagging system.

**Goal:** Collect why voters choose a winner + basic dimension mapping

**MVP:** 16 tags organized in 4 categories → 5 dimensions

---

## Step 1: Database Schema

### Create Tags Table

```sql
CREATE TABLE vote_tags (
  id SERIAL PRIMARY KEY,
  vote_id UUID NOT NULL,
  winner_model VARCHAR(255) NOT NULL,
  loser_model VARCHAR(255) NOT NULL,
  tag_name VARCHAR(100) NOT NULL,
  tag_category VARCHAR(50),  -- "tone", "reasoning", "structure", "content"
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_vote_tags_models ON vote_tags(winner_model, loser_model);
CREATE INDEX idx_vote_tags_name ON vote_tags(tag_name);
```

### Create Voter Demographics Table (Optional)

```sql
CREATE TABLE voter_demographics (
  id SERIAL PRIMARY KEY,
  vote_id UUID NOT NULL,
  country_code VARCHAR(2),
  age_range VARCHAR(20),
  political_spectrum VARCHAR(50),
  voter_hash VARCHAR(255),  -- Hash for grouping while preserving privacy
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_voter_demo_hash ON voter_demographics(voter_hash);
```

### Initialize Tag Weights

```sql
CREATE TABLE tag_dimension_weights (
  tag_name VARCHAR(100) PRIMARY KEY,
  tone_category VARCHAR(50),
  empathy_weight DECIMAL(3, 2),
  aggressiveness_weight DECIMAL(3, 2),
  evidence_weight DECIMAL(3, 2),
  political_economic_weight DECIMAL(3, 2),
  political_social_weight DECIMAL(3, 2),
  description TEXT
);

-- Insert initial weights
INSERT INTO tag_dimension_weights VALUES
  ('empathetic', 'tone', 0.8, -0.3, 0.0, 0.0, 0.0, 'Shows understanding'),
  ('respectful', 'tone', 0.4, -0.5, 0.0, 0.0, 0.0, 'Professional, non-insulting'),
  ('inflammatory', 'tone', -0.6, 0.8, 0.0, 0.0, 0.0, 'Hostile, name-calling'),
  ('dismissive', 'tone', -0.7, 0.3, 0.0, 0.0, 0.0, 'Ignores counterarguments'),
  ('cites_evidence', 'reasoning', 0.0, 0.0, 0.9, 0.0, 0.0, 'Uses data or sources'),
  ('logical_flow', 'reasoning', 0.0, 0.0, 0.7, 0.0, 0.0, 'Clear reasoning'),
  ('hasty_generalization', 'reasoning', 0.0, 0.0, -0.6, 0.0, 0.0, 'Overgeneralizes'),
  ('circular_reasoning', 'reasoning', 0.0, 0.0, -0.8, 0.0, 0.0, 'Begs the question'),
  ('avoids_extremes', 'structure', 0.5, -0.3, 0.0, 0.0, 0.0, 'Acknowledges nuance'),
  ('balanced', 'structure', 0.5, -0.2, 0.5, 0.0, 0.0, 'Multiple perspectives'),
  ('strawman', 'structure', -0.3, 0.5, -0.7, 0.0, 0.0, 'Misrepresents opponent'),
  ('oversimplifies', 'structure', 0.0, 0.0, -0.5, 0.0, 0.0, 'Too reductive'),
  ('factually_accurate', 'content', 0.0, 0.0, 0.8, 0.0, 0.0, 'Verifiable claims'),
  ('source_verified', 'content', 0.0, 0.0, 0.9, 0.0, 0.0, 'Sources provided'),
  ('misleading', 'content', 0.0, 0.3, -0.7, 0.0, 0.0, 'Technically true but misleading'),
  ('false_claim', 'content', 0.0, 0.0, -0.9, 0.0, 0.0, 'Factually incorrect');
```

---

## Step 2: Backend Tag System

### Create `backend/tags.py`

```python
# backend/tags.py

from typing import List, Dict
from enum import Enum

class TagCategory(str, Enum):
    TONE = "tone"
    REASONING = "reasoning"
    STRUCTURE = "structure"
    CONTENT = "content"

TAGS_BY_CATEGORY = {
    TagCategory.TONE: {
        "empathetic": "Shows understanding of other perspectives",
        "respectful": "Professional, non-insulting tone",
        "inflammatory": "Hostile, uses name-calling",
        "dismissive": "Ignores counterarguments",
    },
    TagCategory.REASONING: {
        "cites_evidence": "Uses data, studies, or sources",
        "logical_flow": "Clear reasoning structure",
        "hasty_generalization": "Overgeneralizes from examples",
        "circular_reasoning": "Begs the question",
    },
    TagCategory.STRUCTURE: {
        "avoids_extremes": "Acknowledges nuance and complexity",
        "balanced": "Presents multiple perspectives",
        "strawman": "Misrepresents opponent's position",
        "oversimplifies": "Too reductive",
    },
    TagCategory.CONTENT: {
        "factually_accurate": "Verifiable claims",
        "source_verified": "Can verify sources",
        "misleading": "Technically true but misleading",
        "false_claim": "Factually incorrect",
    },
}

DIMENSION_WEIGHTS = {
    # tag_name -> {dimension: weight}
    "empathetic": {"empathy": 0.8, "aggressiveness": -0.3},
    "respectful": {"aggressiveness": -0.5, "empathy": 0.4},
    "inflammatory": {"aggressiveness": 0.8, "empathy": -0.6},
    "dismissive": {"empathy": -0.7, "aggressiveness": 0.3},
    
    "cites_evidence": {"evidence_use": 0.9},
    "logical_flow": {"evidence_use": 0.7},
    "hasty_generalization": {"evidence_use": -0.6},
    "circular_reasoning": {"evidence_use": -0.8},
    
    "avoids_extremes": {"empathy": 0.5},
    "balanced": {"empathy": 0.5, "evidence_use": 0.3},
    "strawman": {"evidence_use": -0.7, "aggressiveness": 0.5},
    "oversimplifies": {"evidence_use": -0.5},
    
    "factually_accurate": {"evidence_use": 0.8},
    "source_verified": {"evidence_use": 0.9},
    "misleading": {"evidence_use": -0.7, "aggressiveness": 0.3},
    "false_claim": {"evidence_use": -0.9},
}

DIMENSIONS = {
    "empathy": {"min": 0.0, "max": 1.0, "default": 0.5},
    "aggressiveness": {"min": 0.0, "max": 1.0, "default": 0.5},
    "evidence_use": {"min": 0.0, "max": 1.0, "default": 0.5},
    "political_economic": {"min": -1.0, "max": 1.0, "default": 0.0},
    "political_social": {"min": -1.0, "max": 1.0, "default": 0.0},
}

def validate_tag(tag_name: str) -> bool:
    """Check if tag is valid."""
    for category_tags in TAGS_BY_CATEGORY.values():
        if tag_name in category_tags:
            return True
    return False

def get_all_tags() -> Dict[str, Dict[str, str]]:
    """Get all tags organized by category."""
    return TAGS_BY_CATEGORY

def calculate_dimension_scores(tags: List[str]) -> Dict[str, float]:
    """
    Calculate dimension scores from selected tags.
    
    Args:
        tags: List of tag names
        
    Returns:
        Dict mapping dimension names to scores in their ranges
    """
    # Initialize with defaults
    dimension_totals = {dim: 0.0 for dim in DIMENSIONS}
    dimension_counts = {dim: 0.0 for dim in DIMENSIONS}
    
    # Aggregate weights from all tags
    for tag in tags:
        if tag in DIMENSION_WEIGHTS:
            for dimension, weight in DIMENSION_WEIGHTS[tag].items():
                dimension_totals[dimension] += weight
                dimension_counts[dimension] += 1
    
    # Calculate averages and normalize
    scores = {}
    for dimension, config in DIMENSIONS.items():
        if dimension_counts[dimension] > 0:
            avg_weight = dimension_totals[dimension] / dimension_counts[dimension]
        else:
            avg_weight = 0.0
        
        # Map from [-1, 1] weight to dimension range
        min_val = config["min"]
        max_val = config["max"]
        default = config["default"]
        
        if avg_weight >= 0:
            score = default + (avg_weight * (max_val - default))
        else:
            score = default + (avg_weight * (default - min_val))
        
        # Clamp to range
        scores[dimension] = max(min_val, min(max_val, score))
    
    return scores
```

### Update `backend/api.py`

```python
# Add to backend/api.py

from pydantic import BaseModel
from typing import List, Optional, Dict
from .tags import calculate_dimension_scores, validate_tag

class VoteWithTagsRequest(BaseModel):
    winner_model: str
    loser_model: str
    tags: List[str] = []
    debate_id: Optional[str] = None
    topic: Optional[str] = None
    demographics: Optional[Dict] = None

@app.post("/api/vote-with-tags")
def vote_with_tags(req: VoteWithTagsRequest):
    """Record vote with tag annotations."""
    
    if not req.winner_model or not req.loser_model:
        raise HTTPException(status_code=400, detail="Models required")
    
    # Validate tags
    for tag in req.tags:
        if not validate_tag(tag):
            raise HTTPException(status_code=400, detail=f"Invalid tag: {tag}")
    
    try:
        # Update Elo ratings
        new_winner_rating, new_loser_rating = update_ratings(
            req.winner_model,
            req.loser_model
        )
        
        # Calculate dimension scores
        dimension_scores = calculate_dimension_scores(req.tags)
        
        # Store tags in database
        store_vote_tags(
            winner_model=req.winner_model,
            loser_model=req.loser_model,
            tags=req.tags,
            debate_id=req.debate_id,
            topic=req.topic
        )
        
        # Store demographics if provided
        if req.demographics:
            store_voter_demographics(
                winner_model=req.winner_model,
                loser_model=req.loser_model,
                demographics=req.demographics
            )
        
        return {
            "success": True,
            "winner_model": req.winner_model,
            "winner_new_rating": round(new_winner_rating, 2),
            "loser_model": req.loser_model,
            "loser_new_rating": round(new_loser_rating, 2),
            "tags_recorded": len(req.tags),
            "dimension_scores": dimension_scores,
        }
        
    except Exception as e:
        print(f"Vote with tags error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tags")
def get_tags():
    """Get all available tags."""
    from .tags import get_all_tags
    return {"tags": get_all_tags()}
```

### Add Database Functions to `backend/supabase_db.py`

```python
# Add to backend/supabase_db.py

def store_vote_tags(winner_model: str, loser_model: str, tags: List[str], 
                    debate_id: str = None, topic: str = None) -> bool:
    """Store tags for a vote."""
    import uuid
    from datetime import datetime
    
    vote_id = str(uuid.uuid4())
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        for tag in tags:
            cursor.execute("""
                INSERT INTO vote_tags (vote_id, winner_model, loser_model, tag_name, created_at)
                VALUES (%s, %s, %s, %s, %s)
            """, (vote_id, winner_model, loser_model, tag, datetime.now()))
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"Error storing tags: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

def get_model_tag_distribution(model: str) -> Dict[str, float]:
    """Get distribution of tags for a model's winning arguments."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT tag_name, COUNT(*) as count
            FROM vote_tags
            WHERE winner_model = %s
            GROUP BY tag_name
            ORDER BY count DESC
        """, (model,))
        
        results = cursor.fetchall()
        total = sum(r['count'] for r in results)
        
        return {
            r['tag_name']: r['count'] / total if total > 0 else 0
            for r in results
        }
        
    finally:
        cursor.close()
        conn.close()
```

---

## Step 3: Frontend UI Updates

### Update Vote Modal HTML

Add to `debate.html` (after vote buttons):

```html
<div id="vote-modal" class="modal hidden">
  <div class="modal-content">
    <h3>Why did they win?</h3>
    
    <form id="tag-form">
      <!-- Tone Tags -->
      <fieldset class="tag-group">
        <legend>🎭 Tone</legend>
        <label class="tag-checkbox">
          <input type="checkbox" name="tags" value="empathetic">
          <span class="tag-label">Empathetic</span>
          <span class="tag-desc">Understands other perspectives</span>
        </label>
        <label class="tag-checkbox">
          <input type="checkbox" name="tags" value="respectful">
          <span class="tag-label">Respectful</span>
          <span class="tag-desc">Professional, non-insulting</span>
        </label>
        <label class="tag-checkbox">
          <input type="checkbox" name="tags" value="inflammatory">
          <span class="tag-label">Inflammatory</span>
          <span class="tag-desc">Hostile or name-calling</span>
        </label>
        <label class="tag-checkbox">
          <input type="checkbox" name="tags" value="dismissive">
          <span class="tag-label">Dismissive</span>
          <span class="tag-desc">Ignores counterarguments</span>
        </label>
      </fieldset>
      
      <!-- Reasoning Tags -->
      <fieldset class="tag-group">
        <legend>🧠 Reasoning</legend>
        <label class="tag-checkbox">
          <input type="checkbox" name="tags" value="cites_evidence">
          <span class="tag-label">Cites evidence</span>
          <span class="tag-desc">Uses data, studies, or sources</span>
        </label>
        <label class="tag-checkbox">
          <input type="checkbox" name="tags" value="logical_flow">
          <span class="tag-label">Clear logic</span>
          <span class="tag-desc">Reasoning is easy to follow</span>
        </label>
        <label class="tag-checkbox">
          <input type="checkbox" name="tags" value="hasty_generalization">
          <span class="tag-label">Hasty generalization</span>
          <span class="tag-desc">Overgeneralizes from examples</span>
        </label>
        <label class="tag-checkbox">
          <input type="checkbox" name="tags" value="circular_reasoning">
          <span class="tag-label">Circular reasoning</span>
          <span class="tag-desc">Begs the question</span>
        </label>
      </fieldset>
      
      <!-- Structure Tags -->
      <fieldset class="tag-group">
        <legend>⚖️ Structure</legend>
        <label class="tag-checkbox">
          <input type="checkbox" name="tags" value="avoids_extremes">
          <span class="tag-label">Avoids extremes</span>
          <span class="tag-desc">Acknowledges nuance</span>
        </label>
        <label class="tag-checkbox">
          <input type="checkbox" name="tags" value="balanced">
          <span class="tag-label">Balanced</span>
          <span class="tag-desc">Presents multiple perspectives</span>
        </label>
        <label class="tag-checkbox">
          <input type="checkbox" name="tags" value="strawman">
          <span class="tag-label">Strawman</span>
          <span class="tag-desc">Misrepresents opponent</span>
        </label>
        <label class="tag-checkbox">
          <input type="checkbox" name="tags" value="oversimplifies">
          <span class="tag-label">Oversimplifies</span>
          <span class="tag-desc">Too reductive</span>
        </label>
      </fieldset>
      
      <!-- Content Tags -->
      <fieldset class="tag-group">
        <legend>✅ Content</legend>
        <label class="tag-checkbox">
          <input type="checkbox" name="tags" value="factually_accurate">
          <span class="tag-label">Factually accurate</span>
          <span class="tag-desc">Verifiable claims</span>
        </label>
        <label class="tag-checkbox">
          <input type="checkbox" name="tags" value="source_verified">
          <span class="tag-label">Sources verified</span>
          <span class="tag-desc">Can verify sources</span>
        </label>
        <label class="tag-checkbox">
          <input type="checkbox" name="tags" value="misleading">
          <span class="tag-label">Misleading</span>
          <span class="tag-desc">Technically true but misleading</span>
        </label>
        <label class="tag-checkbox">
          <input type="checkbox" name="tags" value="false_claim">
          <span class="tag-label">False claim</span>
          <span class="tag-desc">Factually incorrect</span>
        </label>
      </fieldset>
      
      <button type="submit" class="btn-primary">Submit Vote & Tags</button>
    </form>
  </div>
</div>
```

### Update Frontend JavaScript

```javascript
// js/debate.js or js/battle.js

async function submitVoteWithTags(winnerModel, loserModel) {
  const modal = document.getElementById('vote-modal');
  const form = document.getElementById('tag-form');
  
  // Show modal
  modal.classList.remove('hidden');
  
  // Handle form submission
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Get selected tags
    const selectedTags = Array.from(
      form.querySelectorAll('input[name="tags"]:checked')
    ).map(input => input.value);
    
    try {
      const response = await fetch(
        `${API_CONFIG.BACKEND_URL}/api/vote-with-tags`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            winner_model: winnerModel,
            loser_model: loserModel,
            tags: selectedTags,
            debate_id: currentDebateId,
            topic: currentTopic,
          }),
        }
      );
      
      const data = await response.json();
      
      if (data.success) {
        // Show dimension scores
        showDimensionScores(data.dimension_scores);
        
        // Show confirmation
        showVoteConfirmation(
          `✓ Vote recorded! Tags: ${selectedTags.length}`
        );
        
        // Close modal
        setTimeout(() => {
          modal.classList.add('hidden');
          form.reset();
        }, 2000);
      } else {
        alert(`Error: ${data.detail}`);
      }
    } catch (err) {
      console.error("Vote error:", err);
      alert("Failed to submit vote with tags");
    }
  });
}

function showDimensionScores(scores) {
  const dimensionDisplay = document.getElementById('dimension-scores');
  
  let html = '<div class="dimensions"><h4>Argument Profile:</h4>';
  for (const [dim, score] of Object.entries(scores)) {
    const displayName = dim.replace(/_/g, ' ');
    const percentage = ((score + 1) / 2 * 100).toFixed(0);  // Normalize [-1, 1] to [0, 100]
    html += `
      <div class="dimension-bar">
        <label>${displayName}</label>
        <div class="bar">
          <div class="fill" style="width: ${percentage}%"></div>
        </div>
        <span class="value">${score.toFixed(2)}</span>
      </div>
    `;
  }
  html += '</div>';
  dimensionDisplay.innerHTML = html;
}
```

### Add CSS Styling

```css
/* css/tags.css or add to debate.css */

.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal.hidden {
  display: none;
}

.modal-content {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  max-width: 600px;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.tag-group {
  margin: 1.5rem 0;
  padding: 1rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

.tag-group legend {
  font-weight: 600;
  color: #1f2937;
  padding: 0 0.5rem;
}

.tag-checkbox {
  display: flex;
  align-items: flex-start;
  margin: 0.75rem 0;
  cursor: pointer;
}

.tag-checkbox input[type="checkbox"] {
  margin-top: 0.25rem;
  margin-right: 0.75rem;
  cursor: pointer;
}

.tag-label {
  font-weight: 500;
  display: block;
}

.tag-desc {
  font-size: 0.875rem;
  color: #6b7280;
  display: block;
  margin-top: 0.25rem;
}

.dimensions {
  margin: 1rem 0;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 8px;
}

.dimension-bar {
  margin: 0.75rem 0;
}

.dimension-bar label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  margin-bottom: 0.25rem;
  text-transform: capitalize;
}

.dimension-bar .bar {
  height: 24px;
  background: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
  position: relative;
}

.dimension-bar .fill {
  height: 100%;
  background: linear-gradient(90deg, #4f46e5, #7c3aed);
  transition: width 0.3s ease;
}

.dimension-bar .value {
  font-size: 0.75rem;
  color: #6b7280;
  margin-left: 0.5rem;
}
```

---

## Step 4: Testing

### Test Checklist

- [ ] Create vote with tags
- [ ] Tags save to database
- [ ] Dimension scores calculated correctly
- [ ] Frontend displays scores
- [ ] Multiple tags aggregate properly
- [ ] Existing votes still work (backwards compatible)

### Sample Test Data

```javascript
// Test in browser console
fetch('http://localhost:8000/api/vote-with-tags', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    winner_model: 'GPT-4o',
    loser_model: 'Claude',
    tags: ['empathetic', 'cites_evidence', 'balanced'],
    topic: 'AI regulation',
  })
})
.then(r => r.json())
.then(d => console.log(d))
```

---

## Step 5: Deployment

1. Run database migrations
2. Deploy backend with new endpoint
3. Deploy frontend with updated UI
4. Monitor for bugs
5. Tune weights if needed

---

## Metrics to Track

- %age of votes with tags
- Average tags per vote
- Distribution of tags
- Correlation between tags and rating changes
- Dimension scores over time

---

**Ready to start?** Begin with database schema + `backend/tags.py`! 🚀
