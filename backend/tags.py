# backend/tags.py
"""
Tag system for rich voting annotations.

Collects voter perspective through tags explaining why an argument won,
and maps those tags to numerical dimensions for analysis.
"""

from typing import List, Dict
from enum import Enum


class TagCategory(str, Enum):
    TONE = "tone"
    REASONING = "reasoning"
    STRUCTURE = "structure"
    CONTENT = "content"


# Tags organized by category
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

# Map tags to their impact on each dimension
# Positive = increases dimension, Negative = decreases dimension
DIMENSION_WEIGHTS = {
    # Tone tags
    "empathetic": {"empathy": 0.8, "aggressiveness": -0.3},
    "respectful": {"aggressiveness": -0.5, "empathy": 0.4},
    "inflammatory": {"aggressiveness": 0.8, "empathy": -0.6},
    "dismissive": {"empathy": -0.7, "aggressiveness": 0.3},
    
    # Reasoning tags
    "cites_evidence": {"evidence_use": 0.9},
    "logical_flow": {"evidence_use": 0.7},
    "hasty_generalization": {"evidence_use": -0.6},
    "circular_reasoning": {"evidence_use": -0.8},
    
    # Structure tags
    "avoids_extremes": {"empathy": 0.5},
    "balanced": {"empathy": 0.5, "evidence_use": 0.3},
    "strawman": {"evidence_use": -0.7, "aggressiveness": 0.5},
    "oversimplifies": {"evidence_use": -0.5},
    
    # Content tags
    "factually_accurate": {"evidence_use": 0.8},
    "source_verified": {"evidence_use": 0.9},
    "misleading": {"evidence_use": -0.7, "aggressiveness": 0.3},
    "false_claim": {"evidence_use": -0.9},
}

# Dimension definitions: what each dimension means and its valid range
DIMENSIONS = {
    "empathy": {
        "min": 0.0,
        "max": 1.0,
        "default": 0.5,
        "description": "How well the argument acknowledges other perspectives",
    },
    "aggressiveness": {
        "min": 0.0,
        "max": 1.0,
        "default": 0.5,
        "description": "How combative vs collaborative the tone is",
    },
    "evidence_use": {
        "min": 0.0,
        "max": 1.0,
        "default": 0.5,
        "description": "How well-supported the argument is with facts/logic",
    },
    "political_economic": {
        "min": -1.0,
        "max": 1.0,
        "default": 0.0,
        "description": "Political lean on economic issues (-1=left, +1=right)",
    },
    "political_social": {
        "min": -1.0,
        "max": 1.0,
        "default": 0.0,
        "description": "Political lean on social issues (-1=progressive, +1=conservative)",
    },
}


def validate_tag(tag_name: str) -> bool:
    """
    Check if a tag name is valid.
    
    Args:
        tag_name: The tag to validate
        
    Returns:
        True if tag exists, False otherwise
    """
    for category_tags in TAGS_BY_CATEGORY.values():
        if tag_name in category_tags:
            return True
    return False


def get_all_tags() -> Dict[str, Dict[str, str]]:
    """
    Get all tags organized by category.
    
    Returns:
        Dict mapping category names to dicts of tag_name -> description
    """
    return {cat.value: tags for cat, tags in TAGS_BY_CATEGORY.items()}


def get_tag_description(tag_name: str) -> str:
    """Get description for a specific tag."""
    for category_tags in TAGS_BY_CATEGORY.values():
        if tag_name in category_tags:
            return category_tags[tag_name]
    return ""


def calculate_dimension_scores(tags: List[str]) -> Dict[str, float]:
    """
    Calculate dimension scores from selected tags.
    
    This function:
    1. Collects all weights from selected tags
    2. Averages them for each dimension
    3. Maps from weight range to dimension range
    
    Args:
        tags: List of tag names (e.g., ["empathetic", "cites_evidence"])
        
    Returns:
        Dict mapping dimension names to scores in their valid ranges
        
    Example:
        >>> scores = calculate_dimension_scores(["empathetic", "cites_evidence"])
        >>> scores["empathy"]  # Will be high (0.8-1.0 range)
        >>> scores["evidence_use"]  # Will be high (0.8-1.0 range)
    """
    # Initialize accumulation for each dimension
    dimension_totals = {dim: 0.0 for dim in DIMENSIONS}
    dimension_counts = {dim: 0 for dim in DIMENSIONS}
    
    # Aggregate weights from all selected tags
    for tag in tags:
        if tag in DIMENSION_WEIGHTS:
            for dimension, weight in DIMENSION_WEIGHTS[tag].items():
                dimension_totals[dimension] += weight
                dimension_counts[dimension] += 1
    
    # Calculate averages and normalize to dimension ranges
    scores = {}
    for dimension, config in DIMENSIONS.items():
        if dimension_counts[dimension] > 0:
            avg_weight = dimension_totals[dimension] / dimension_counts[dimension]
        else:
            avg_weight = 0.0
        
        # Map from weight space [-1, 1] to dimension range
        min_val = config["min"]
        max_val = config["max"]
        default = config["default"]
        
        # If weight is positive, map from [0, 1] to [default, max]
        # If weight is negative, map from [-1, 0] to [min, default]
        if avg_weight >= 0:
            score = default + (avg_weight * (max_val - default))
        else:
            score = default + (avg_weight * (default - min_val))
        
        # Clamp to valid range (just to be safe)
        scores[dimension] = max(min_val, min(max_val, score))
    
    return scores


def get_tag_category(tag_name: str) -> str:
    """Get the category of a tag."""
    for category, tags in TAGS_BY_CATEGORY.items():
        if tag_name in tags:
            return category.value
    return ""
