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


# Note: Do NOT define FastAPI app here. This is a utility module only.
# All endpoints are defined in backend/api.py
