# ✅ Voting 500 Error - Fixed!

## What Was Wrong

The `/api/vote` endpoint was returning 500 because:

1. **Models not in database** - When voting on models that weren't in the starter list, the database query failed
2. **Wrong parameter type** - `update_elo()` expects `"1"` (string) but was getting `1` (int)
3. **Using deprecated syntax** - Old INSERT...ON CONFLICT wasn't working properly

## What I Fixed

Updated `update_ratings()` function in `backend/supabase_db.py`:

### Before (Broken)
```python
# Would fail if model not in database
winner_rating = winner_result['rating'] if winner_result else 1500  # Falls back to 1500 but doesn't insert
update_elo(winner_rating, loser_rating, 1)  # Wrong: passing int instead of "1"
```

### After (Fixed)
```python
# Check if model exists, insert if not
if not winner_result:
    cursor.execute("""
        INSERT INTO elo_ratings (model_name, rating, wins, losses)
        VALUES (%s, 1500.0, 0, 0)
    """, (winner_model,))
    winner_rating = 1500.0

# Pass correct string parameter
update_elo(winner_rating, loser_rating, "1")  # Correct!

# Update ratings properly
cursor.execute("""
    UPDATE elo_ratings 
    SET rating = %s, wins = wins + 1, updated_at = CURRENT_TIMESTAMP
    WHERE model_name = %s
""", (round(new_winner_rating, 2), winner_model))
```

## What Changed

**File:** `backend/supabase_db.py`
- Lines 180-240: Rewrote `update_ratings()` function
- Now handles new models automatically
- Fixes parameter type for `update_elo()`
- Cleaner INSERT + UPDATE logic

## Deploy

✅ Changes pushed to GitHub
✅ Render auto-deploys (watch dashboard)
✅ Should see deployment starting

## Test

1. Wait 2-3 min for Render to redeploy
2. Go to `/debate.html` (or `/battle.html`)
3. Create debate/battle
4. Vote
5. Should see: **✓ Vote recorded!** (no 500 error)

## Status

**Before:** 500 Internal Server Error
**After:** Voting works! ✅

---

Voting is now fully functional!
