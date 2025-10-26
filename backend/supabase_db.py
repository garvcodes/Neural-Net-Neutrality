"""
Supabase PostgreSQL database connection and utilities.

Requires environment variables:
  - SUPABASE_URL: Your Supabase project URL
  - SUPABASE_KEY: Your Supabase anon/public key
  - DATABASE_URL: PostgreSQL connection string (optional, for direct psycopg2 connection)
"""

#** hopefully everyhing works now **#

import os
from typing import Optional, Dict, List
import psycopg2
from psycopg2.extras import RealDictCursor
import json
from dotenv import load_dotenv

# Load environment variables from .env (for local development)
load_dotenv()

# Get connection details from environment variable
# This should be set in Render environment variables for production
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError(
        "❌ DATABASE_URL environment variable not set!\n"
        "Local: Add DATABASE_URL to .env file\n"
        "Production: Add DATABASE_URL to Render environment variables"
    )

# Track if we've already checked/initialized the database
_db_initialized = False

def get_db_connection():
    """Create and return a database connection."""
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        raise

def calc_prob(r1, r2): # From classic elo model. 
    return 1/(1 + 10**((r2 - r1)/400))

def update_elo(p1_elo, p2_elo, winner):
    if winner == "1":
      prob_opposite = calc_prob(p2_elo, p1_elo)
      S_0, S_1 = 1, -1
    else:
      prob_opposite = calc_prob(p1_elo, p2_elo)
      S_0, S_1 = -1, 1
    p1_new = p1_elo + 32 * S_0 * (prob_opposite)
    p2_new = p2_elo + 32 * S_1 * (prob_opposite)
    return p1_new, p2_new

def init_database():
    """Initialize the elo_ratings table with starter models."""
    global _db_initialized
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Drop existing table if it exists
        cursor.execute("DROP TABLE IF EXISTS elo_ratings;")
        
        # Create table
        cursor.execute("""
            CREATE TABLE elo_ratings (
                id SERIAL PRIMARY KEY,
                model_name VARCHAR(255) UNIQUE NOT NULL,
                rating DECIMAL(10, 2) DEFAULT 1500.0,
                wins INTEGER DEFAULT 0,
                losses INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create index on model_name for fast lookups
        cursor.execute("""
            CREATE INDEX idx_elo_model_name ON elo_ratings(model_name);
        """)
        
        # Insert starter models
        starter_models = [
            "OpenAI GPT-4o Mini",
            "OpenAI GPT-4o",
            "OpenAI GPT-3.5 Turbo",
            "Claude 3 Haiku",
            "Claude 3 Sonnet",
            "Gemini 1.5 Pro",
            "Gemini 2.0 Flash"
        ]
        
        for model in starter_models:
            cursor.execute("""
                INSERT INTO elo_ratings (model_name, rating, wins, losses)
                VALUES (%s, 1500.0, 0, 0);
            """, (model,))
        
        conn.commit()
        _db_initialized = True
        print(f"✅ Database initialized with {len(starter_models)} models")
    except Exception as e:
        print(f"Database initialization error: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

def ensure_table_exists():
    """Check if table exists, initialize if not."""
    global _db_initialized
    
    if _db_initialized:
        return
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        # Check if table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'elo_ratings'
            );
        """)
        exists = cursor.fetchone()[0]
        
        if not exists:
            print("⚠️  Table not found, initializing database...")
            # Create the table in the same connection
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS elo_ratings (
                    id SERIAL PRIMARY KEY,
                    model_name VARCHAR(255) UNIQUE NOT NULL,
                    rating DECIMAL(10, 2) DEFAULT 1500.0,
                    wins INTEGER DEFAULT 0,
                    losses INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_elo_model_name ON elo_ratings(model_name);
            """)
            
            conn.commit()
            print("✅ Database table created successfully")
        
        _db_initialized = True
            
    except Exception as e:
        print(f"Error with table: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def get_rating(model: str) -> float:
    """Get the current Elo rating for a model."""
    ensure_table_exists()
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT rating FROM elo_ratings WHERE model_name = %s", (model,))
        result = cursor.fetchone()
        return result['rating'] if result else 1500.0
    except Exception as e:
        print(f"Error getting rating: {e}")
        return 1500.0
    finally:
        cursor.close()
        conn.close()


def update_ratings(winner_model: str, loser_model: str, k_factor: int = 32) -> tuple:
    """
    Update Elo ratings after a battle result.
    
    Args:
        winner_model: Model that won the vote
        loser_model: Model that lost the vote
        k_factor: Points per game (default 32)
        
    Returns:
        (new_winner_rating, new_loser_rating)
    """
    ensure_table_exists()
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get current ratings - if model doesn't exist, insert it first with default 1500
        cursor.execute("SELECT rating FROM elo_ratings WHERE model_name = %s", (winner_model,))
        winner_result = cursor.fetchone()
        
        if not winner_result:
            # Insert new model with default rating
            cursor.execute("""
                INSERT INTO elo_ratings (model_name, rating, wins, losses)
                VALUES (%s, 1500.0, 0, 0)
            """, (winner_model,))
            winner_rating = 1500.0
        else:
            winner_rating = float(winner_result['rating'])
        
        cursor.execute("SELECT rating FROM elo_ratings WHERE model_name = %s", (loser_model,))
        loser_result = cursor.fetchone()
        
        if not loser_result:
            # Insert new model with default rating
            cursor.execute("""
                INSERT INTO elo_ratings (model_name, rating, wins, losses)
                VALUES (%s, 1500.0, 0, 0)
            """, (loser_model,))
            loser_rating = 1500.0
        else:
            loser_rating = float(loser_result['rating'])
        
        # Calculate new ratings (pass "1" as string for winner)
        new_winner_rating, new_loser_rating = update_elo(winner_rating, loser_rating, "1")
        
        # Update winner
        cursor.execute("""
            UPDATE elo_ratings 
            SET rating = %s, wins = wins + 1, updated_at = CURRENT_TIMESTAMP
            WHERE model_name = %s
        """, (round(new_winner_rating, 2), winner_model))
        
        # Update loser
        cursor.execute("""
            UPDATE elo_ratings 
            SET rating = %s, losses = losses + 1, updated_at = CURRENT_TIMESTAMP
            WHERE model_name = %s
        """, (round(new_loser_rating, 2), loser_model))
        
        conn.commit()
        return new_winner_rating, new_loser_rating
        
    except Exception as e:
        print(f"Error updating ratings: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def get_all_ratings() -> Dict[str, Dict]:
    """Get all model ratings sorted by rating (highest first)."""
    ensure_table_exists()
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT model_name, rating, wins, losses
            FROM elo_ratings
            ORDER BY rating DESC
        """)
        
        ratings = {}
        for row in cursor.fetchall():
            ratings[row['model_name']] = {
                'rating': float(row['rating']),
                'wins': int(row['wins']),
                'losses': int(row['losses'])
            }
        return ratings
        
    except Exception as e:
        print(f"Error fetching ratings: {e}")
        return {}
    finally:
        cursor.close()
        conn.close()


def reset_ratings():
    """Reset all ratings to default 1500."""
    ensure_table_exists()
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE elo_ratings
            SET rating = 1500.0, wins = 0, losses = 0, updated_at = CURRENT_TIMESTAMP
        """)
        conn.commit()
        print("✅ Ratings reset successfully")
    except Exception as e:
        print(f"Error resetting ratings: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def ensure_tags_table_exists():
    """Check if vote_tags table exists, create if not."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        # Check if table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'vote_tags'
            );
        """)
        exists = cursor.fetchone()[0]
        
        if not exists:
            print("⚠️  vote_tags table not found, creating...")
            cursor.execute("""
                CREATE TABLE vote_tags (
                    id SERIAL PRIMARY KEY,
                    winner_model VARCHAR(255) NOT NULL,
                    loser_model VARCHAR(255) NOT NULL,
                    tag_name VARCHAR(100) NOT NULL,
                    tag_category VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            cursor.execute("""
                CREATE INDEX idx_vote_tags_models ON vote_tags(winner_model, loser_model);
            """)
            
            cursor.execute("""
                CREATE INDEX idx_vote_tags_name ON vote_tags(tag_name);
            """)
            
            conn.commit()
            print("✅ vote_tags table created successfully")
        
    except Exception as e:
        print(f"Error with vote_tags table: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def store_vote_tags(winner_model: str, loser_model: str, tags: List[str], 
                    tag_categories: Dict[str, str] = None) -> bool:
    """
    Store tags for a vote.
    
    Args:
        winner_model: Model that won
        loser_model: Model that lost
        tags: List of tag names
        tag_categories: Optional dict mapping tag names to categories
        
    Returns:
        True if successful
    """
    ensure_tags_table_exists()
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        for tag in tags:
            category = tag_categories.get(tag, "unknown") if tag_categories else "unknown"
            cursor.execute("""
                INSERT INTO vote_tags (winner_model, loser_model, tag_name, tag_category)
                VALUES (%s, %s, %s, %s)
            """, (winner_model, loser_model, tag, category))
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"Error storing tags: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def get_model_tag_distribution(model: str, as_winner: bool = True) -> Dict[str, float]:
    """
    Get distribution of tags for a model's arguments.
    
    Args:
        model: Model name
        as_winner: If True, get tags where model won. If False, tags where it lost.
        
    Returns:
        Dict mapping tag names to their frequency (0.0-1.0)
    """
    ensure_tags_table_exists()
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        if as_winner:
            cursor.execute("""
                SELECT tag_name, COUNT(*) as count
                FROM vote_tags
                WHERE winner_model = %s
                GROUP BY tag_name
                ORDER BY count DESC
            """, (model,))
        else:
            cursor.execute("""
                SELECT tag_name, COUNT(*) as count
                FROM vote_tags
                WHERE loser_model = %s
                GROUP BY tag_name
                ORDER BY count DESC
            """, (model,))
        
        results = cursor.fetchall()
        total = sum(r['count'] for r in results)
        
        if total == 0:
            return {}
        
        return {
            r['tag_name']: r['count'] / total
            for r in results
        }
        
    except Exception as e:
        print(f"Error fetching tag distribution: {e}")
        return {}
    finally:
        cursor.close()
        conn.close()


def ensure_vote_dimension_scores_table_exists():
    """Create vote_dimension_scores table if it doesn't exist."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'vote_dimension_scores'
            );
        """)
        exists = cursor.fetchone()[0]
        
        if not exists:
            print("⚠️  vote_dimension_scores table not found, creating...")
            cursor.execute("""
                CREATE TABLE vote_dimension_scores (
                    id SERIAL PRIMARY KEY,
                    winner_model VARCHAR(255) NOT NULL,
                    loser_model VARCHAR(255) NOT NULL,
                    winner_empathy FLOAT DEFAULT 0.5,
                    winner_aggressiveness FLOAT DEFAULT 0.5,
                    winner_evidence_use FLOAT DEFAULT 0.5,
                    winner_political_economic FLOAT DEFAULT 0.0,
                    winner_political_social FLOAT DEFAULT 0.0,
                    loser_empathy FLOAT DEFAULT 0.5,
                    loser_aggressiveness FLOAT DEFAULT 0.5,
                    loser_evidence_use FLOAT DEFAULT 0.5,
                    loser_political_economic FLOAT DEFAULT 0.0,
                    loser_political_social FLOAT DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            cursor.execute("""
                CREATE INDEX idx_vote_dim_winner ON vote_dimension_scores(winner_model);
            """)
            
            cursor.execute("""
                CREATE INDEX idx_vote_dim_loser ON vote_dimension_scores(loser_model);
            """)
            
            conn.commit()
            print("✅ vote_dimension_scores table created successfully")
        
    except Exception as e:
        print(f"Error with vote_dimension_scores table: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def store_dimension_scores(winner_model: str, loser_model: str,
                          winner_scores: Dict[str, float],
                          loser_scores: Dict[str, float]) -> bool:
    """
    Store dimension scores for both models in a vote.
    
    Args:
        winner_model: Name of winning model
        loser_model: Name of losing model
        winner_scores: Dict of dimension scores for winner
        loser_scores: Dict of dimension scores for loser
        
    Returns:
        True if successful, False otherwise
    """
    ensure_vote_dimension_scores_table_exists()
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO vote_dimension_scores 
            (winner_model, loser_model, 
             winner_empathy, winner_aggressiveness, winner_evidence_use,
             winner_political_economic, winner_political_social,
             loser_empathy, loser_aggressiveness, loser_evidence_use,
             loser_political_economic, loser_political_social)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            winner_model, loser_model,
            winner_scores.get('empathy', 0.5),
            winner_scores.get('aggressiveness', 0.5),
            winner_scores.get('evidence_use', 0.5),
            winner_scores.get('political_economic', 0.0),
            winner_scores.get('political_social', 0.0),
            loser_scores.get('empathy', 0.5),
            loser_scores.get('aggressiveness', 0.5),
            loser_scores.get('evidence_use', 0.5),
            loser_scores.get('political_economic', 0.0),
            loser_scores.get('political_social', 0.0)
        ))
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"❌ Error storing dimension scores: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()


def get_aggregated_dimension_scores(model_name: str = None) -> Dict:
    """
    Get aggregated dimension scores for models.
    
    Args:
        model_name: Optional specific model to get scores for.
                   If None, returns scores for all models.
        
    Returns:
        Dict mapping model names to averaged dimension scores
        Example:
        {
            "gpt-4o": {
                "empathy": 0.72,
                "aggressiveness": 0.38,
                "evidence_use": 0.81,
                "political_economic": 0.05,
                "political_social": -0.08,
                "vote_count": 24
            },
            ...
        }
    """
    ensure_vote_dimension_scores_table_exists()
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Query for winner scores
        if model_name:
            cursor.execute("""
                SELECT 
                    winner_model as model_name,
                    COUNT(*) as vote_count,
                    AVG(winner_empathy) as empathy,
                    AVG(winner_aggressiveness) as aggressiveness,
                    AVG(winner_evidence_use) as evidence_use,
                    AVG(winner_political_economic) as political_economic,
                    AVG(winner_political_social) as political_social
                FROM vote_dimension_scores
                WHERE winner_model = %s
                GROUP BY winner_model
                UNION ALL
                SELECT 
                    loser_model as model_name,
                    COUNT(*) as vote_count,
                    AVG(loser_empathy) as empathy,
                    AVG(loser_aggressiveness) as aggressiveness,
                    AVG(loser_evidence_use) as evidence_use,
                    AVG(loser_political_economic) as political_economic,
                    AVG(loser_political_social) as political_social
                FROM vote_dimension_scores
                WHERE loser_model = %s
                GROUP BY loser_model
            """, (model_name, model_name))
        else:
            cursor.execute("""
                SELECT 
                    winner_model as model_name,
                    COUNT(*) as vote_count,
                    AVG(winner_empathy) as empathy,
                    AVG(winner_aggressiveness) as aggressiveness,
                    AVG(winner_evidence_use) as evidence_use,
                    AVG(winner_political_economic) as political_economic,
                    AVG(winner_political_social) as political_social
                FROM vote_dimension_scores
                GROUP BY winner_model
                UNION ALL
                SELECT 
                    loser_model as model_name,
                    COUNT(*) as vote_count,
                    AVG(loser_empathy) as empathy,
                    AVG(loser_aggressiveness) as aggressiveness,
                    AVG(loser_evidence_use) as evidence_use,
                    AVG(loser_political_economic) as political_economic,
                    AVG(loser_political_social) as political_social
                FROM vote_dimension_scores
                GROUP BY loser_model
                ORDER BY vote_count DESC
            """)
        
        results = cursor.fetchall()
        
        # Aggregate winner and loser scores for each model
        aggregated = {}
        for row in results:
            model = row['model_name']
            if model not in aggregated:
                aggregated[model] = {
                    'vote_count': 0,
                    'scores': {'empathy': [], 'aggressiveness': [], 'evidence_use': [],
                              'political_economic': [], 'political_social': []}
                }
            
            aggregated[model]['vote_count'] += row['vote_count']
            aggregated[model]['scores']['empathy'].append(row['empathy'])
            aggregated[model]['scores']['aggressiveness'].append(row['aggressiveness'])
            aggregated[model]['scores']['evidence_use'].append(row['evidence_use'])
            aggregated[model]['scores']['political_economic'].append(row['political_economic'])
            aggregated[model]['scores']['political_social'].append(row['political_social'])
        
        # Average the scores
        final_result = {}
        for model, data in aggregated.items():
            scores = data['scores']
            final_result[model] = {
                'empathy': round(sum(scores['empathy']) / len(scores['empathy']), 3),
                'aggressiveness': round(sum(scores['aggressiveness']) / len(scores['aggressiveness']), 3),
                'evidence_use': round(sum(scores['evidence_use']) / len(scores['evidence_use']), 3),
                'political_economic': round(sum(scores['political_economic']) / len(scores['political_economic']), 3),
                'political_social': round(sum(scores['political_social']) / len(scores['political_social']), 3),
                'vote_count': data['vote_count']
            }
        
        return final_result
        
    except Exception as e:
        print(f"❌ Error getting aggregated dimension scores: {e}")
        return {}
    finally:
        cursor.close()
        conn.close()


def get_dimension_leaderboard(dimension: str, limit: int = 10) -> List[Dict]:
    """
    Get leaderboard for a specific dimension.
    
    Args:
        dimension: Name of dimension (empathy, aggressiveness, evidence_use, etc.)
        limit: Number of top models to return
        
    Returns:
        List of dicts with model_name, score, and rank
    """
    ensure_vote_dimension_scores_table_exists()
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Map dimension name to column names
        dim_columns = {
            'empathy': ('winner_empathy', 'loser_empathy'),
            'aggressiveness': ('winner_aggressiveness', 'loser_aggressiveness'),
            'evidence_use': ('winner_evidence_use', 'loser_evidence_use'),
            'political_economic': ('winner_political_economic', 'loser_political_economic'),
            'political_social': ('winner_political_social', 'loser_political_social')
        }
        
        if dimension not in dim_columns:
            return []
        
        winner_col, loser_col = dim_columns[dimension]
        
        cursor.execute(f"""
            SELECT 
                model_name,
                AVG(score) as avg_score,
                COUNT(*) as vote_count,
                ROW_NUMBER() OVER (ORDER BY AVG(score) DESC) as rank
            FROM (
                SELECT winner_model as model_name, {winner_col} as score FROM vote_dimension_scores
                UNION ALL
                SELECT loser_model as model_name, {loser_col} as score FROM vote_dimension_scores
            ) combined
            GROUP BY model_name
            ORDER BY avg_score DESC
            LIMIT %s
        """, (limit,))
        
        results = cursor.fetchall()
        return [
            {
                'rank': row['rank'],
                'model_name': row['model_name'],
                'score': round(float(row['avg_score']), 3),
                'vote_count': row['vote_count']
            }
            for row in results
        ]
    except Exception as e:
        print(f"❌ Error getting dimension leaderboard: {e}")
        return []
    finally:
        cursor.close()
        conn.close()


# Note: Do NOT define FastAPI app here. This is a utility module only.
# All endpoints are defined in backend/api.py
