"""
Supabase PostgreSQL database connection and utilities.

Requires environment variables:
  - SUPABASE_URL: Your Supabase project URL
  - SUPABASE_KEY: Your Supabase anon/public key
  - DATABASE_URL: PostgreSQL connection string (optional, for direct psycopg2 connection)
"""

import os
from typing import Optional, Dict, List
import psycopg2
from psycopg2.extras import RealDictCursor
import json

# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Get connection details from environment
DATABASE_URL = "postgresql://postgres.xzsbfdeduchwgtzbwhfp:sxhg5ay73039041371@aws-1-us-east-2.pooler.supabase.com:5432/postgres"

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
      S_0, S_1 = -1, 1
    else:
      prob_opposite = calc_prob(p1_elo, p2_elo)
      S_0, S_1 = 1, -1
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
        
        # Get current ratings
        cursor.execute("SELECT rating FROM elo_ratings WHERE model_name = %s", (winner_model,))
        winner_result = cursor.fetchone()
        winner_rating = winner_result['rating'] if winner_result else 1500
        
        cursor.execute("SELECT rating FROM elo_ratings WHERE model_name = %s", (loser_model,))
        loser_result = cursor.fetchone()
        loser_rating = loser_result['rating'] if loser_result else 1500
        
        # Calculate new ratings
        new_winner_rating, new_loser_rating = update_elo(winner_rating, loser_rating, 1)
        
        # Upsert winner
        cursor.execute("""
            INSERT INTO elo_ratings (model_name, rating, wins, updated_at)
            VALUES (%s, %s, 1, CURRENT_TIMESTAMP)
            ON CONFLICT (model_name) DO UPDATE
            SET rating = %s, wins = elo_ratings.wins + 1, updated_at = CURRENT_TIMESTAMP
        """, (winner_model, round(new_winner_rating, 2), round(new_winner_rating, 2)))
        
        # Upsert loser
        cursor.execute("""
            INSERT INTO elo_ratings (model_name, rating, losses, updated_at)
            VALUES (%s, %s, 1, CURRENT_TIMESTAMP)
            ON CONFLICT (model_name) DO UPDATE
            SET rating = %s, losses = elo_ratings.losses + 1, updated_at = CURRENT_TIMESTAMP
        """, (loser_model, round(new_loser_rating, 2), round(new_loser_rating, 2)))
        
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

app = FastAPI()

# Enable CORS so frontend can access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or restrict to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/ratings")
def fetch_ratings():
    """Return all model ratings as JSON."""
    try:
        ratings = get_all_ratings()
        return {"success": True, "data": ratings}
    except Exception as e:
        return {"success": False, "error": str(e)}
@app.post("/api/vote")
def handle_vote(vote_data: dict):
    """Handle a vote and update Elo ratings."""
    try:
        winner = vote_data.get("winner_model")
        loser = vote_data.get("loser_model")
        prompt = vote_data.get("prompt")
        
        if not winner or not loser:
            return {"success": False, "error": "Missing winner or loser model"}
        
        # Update Elo ratings in database
        new_winner_rating, new_loser_rating = update_ratings(winner, loser)
        
        return {
            "success": True,
            "new_ratings": {
                "winner": new_winner_rating,
                "loser": new_loser_rating
            },
            "message": f"{winner} won against {loser}"
        }
    except Exception as e:
        print(f"Vote error: {e}")
        return {"success": False, "error": str(e)}