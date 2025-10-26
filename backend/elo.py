"""
Elo rating system for model battles.

Standard chess Elo formula:
  new_rating = old_rating + K * (result - expected_result)
  
Where:
  - K = 32 (points per game; can adjust for volatility)
  - result = 1 for win, 0 for loss, 0.5 for draw
  - expected_result = 1 / (1 + 10^((opponent_rating - player_rating) / 400))
"""

import json
import os
from pathlib import Path
from typing import Dict, Tuple

# Path to store Elo ratings
ELO_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "elo_ratings.json")

# Default K factor (points awarded/deducted per game)
K_FACTOR = 32

# Initial rating for new models
DEFAULT_RATING = 1600


def ensure_elo_file():
    """Create elo_ratings.json if it doesn't exist."""
    Path(ELO_FILE).parent.mkdir(parents=True, exist_ok=True)
    if not os.path.exists(ELO_FILE):
        with open(ELO_FILE, "w") as f:
            json.dump({}, f, indent=2)


def load_ratings() -> Dict[str, Dict]:
    """Load Elo ratings from file."""
    ensure_elo_file()
    try:
        with open(ELO_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}


def save_ratings(ratings: Dict[str, Dict]):
    """Save Elo ratings to file."""
    ensure_elo_file()
    with open(ELO_FILE, "w") as f:
        json.dump(ratings, f, indent=2)


def get_rating(model: str) -> float:
    """Get the current Elo rating for a model."""
    ratings = load_ratings()
    if model not in ratings:
        return DEFAULT_RATING
    return ratings[model].get("rating", DEFAULT_RATING)


def expected_result(player_rating: float, opponent_rating: float) -> float:
    """Calculate expected result (win probability) for a player.
    
    Formula: 1 / (1 + 10^((opponent_rating - player_rating) / 400))
    """
    return 1 / (1 + 10 ** ((opponent_rating - player_rating) / 400))


def update_ratings(winner_model: str, loser_model: str) -> Tuple[float, float]:
    """Update Elo ratings after a battle result.
    
    Args:
        winner_model: Model that won the vote
        loser_model: Model that lost the vote
        
    Returns:
        (new_winner_rating, new_loser_rating)
    """
    ratings = load_ratings()
    
    # Get current ratings
    winner_rating = get_rating(winner_model)
    loser_rating = get_rating(loser_model)
    
    # Calculate expected results
    winner_expected = expected_result(winner_rating, loser_rating)
    loser_expected = expected_result(loser_rating, winner_rating)
    
    # Calculate new ratings
    new_winner_rating = winner_rating + K_FACTOR * (1 - winner_expected)
    new_loser_rating = loser_rating + K_FACTOR * (0 - loser_expected)
    
    # Update ratings dict
    if winner_model not in ratings:
        ratings[winner_model] = {"rating": 0, "wins": 0, "losses": 0}
    if loser_model not in ratings:
        ratings[loser_model] = {"rating": 0, "wins": 0, "losses": 0}
    
    ratings[winner_model]["rating"] = round(new_winner_rating, 1)
    ratings[winner_model]["wins"] = ratings[winner_model].get("wins", 0) + 1
    
    ratings[loser_model]["rating"] = round(new_loser_rating, 1)
    ratings[loser_model]["losses"] = ratings[loser_model].get("losses", 0) + 1
    
    # Save updated ratings
    save_ratings(ratings)
    
    return new_winner_rating, new_loser_rating


def get_all_ratings() -> Dict[str, Dict]:
    """Get all model ratings sorted by rating (highest first)."""
    ratings = load_ratings()
    # Sort by rating descending
    sorted_ratings = dict(sorted(
        ratings.items(),
        key=lambda x: x[1].get("rating", DEFAULT_RATING),
        reverse=True
    ))
    return sorted_ratings
