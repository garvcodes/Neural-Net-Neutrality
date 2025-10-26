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
from urllib.parse import quote_plus

# Get connection details from environment
# Format: postgresql://user:password@host:port/database
DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    # Fallback: construct from individual env vars if DATABASE_URL not set
    db_user = os.environ.get("DB_USER", "postgres")
    db_password = os.environ.get("DB_PASSWORD", "")
    db_host = os.environ.get("DB_HOST", "db.tvsyvfkereavzztcmkkq.supabase.co")
    db_port = os.environ.get("DB_PORT", "5432")
    db_name = os.environ.get("DB_NAME", "postgres")
    
    # URL encode the password if it contains special characters
    encoded_password = quote_plus(db_password)
    DATABASE_URL = f"postgresql://{db_user}:{encoded_password}@{db_host}:{db_port}/{db_name}"

def get_db_connection():
    """Create and return a database connection."""
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        raise


def init_database():
    """Initialize the elo_ratings table if it doesn't exist."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Create table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS elo_ratings (
                id SERIAL PRIMARY KEY,
                model_name VARCHAR(255) UNIQUE NOT NULL,
                rating DECIMAL(10, 2) DEFAULT 1600.0,
                wins INTEGER DEFAULT 0,
                losses INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create index on model_name for fast lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_elo_model_name ON elo_ratings(model_name);
        """)
        
        conn.commit()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"Database initialization error: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def get_rating(model: str) -> float:
    """Get the current Elo rating for a model."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT rating FROM elo_ratings WHERE model_name = %s", (model,))
        result = cursor.fetchone()
        return result['rating'] if result else 1600.0
    except Exception as e:
        print(f"Error getting rating: {e}")
        return 1600.0
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
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get current ratings
        cursor.execute("SELECT rating FROM elo_ratings WHERE model_name = %s", (winner_model,))
        winner_result = cursor.fetchone()
        winner_rating = winner_result['rating'] if winner_result else 1600.0
        
        cursor.execute("SELECT rating FROM elo_ratings WHERE model_name = %s", (loser_model,))
        loser_result = cursor.fetchone()
        loser_rating = loser_result['rating'] if loser_result else 1600.0
        
        # Calculate expected results
        winner_expected = 1 / (1 + 10 ** ((loser_rating - winner_rating) / 400))
        loser_expected = 1 / (1 + 10 ** ((winner_rating - loser_rating) / 400))
        
        # Calculate new ratings
        new_winner_rating = winner_rating + k_factor * (1 - winner_expected)
        new_loser_rating = loser_rating + k_factor * (0 - loser_expected)
        
        # Upsert winner
        cursor.execute("""
            INSERT INTO elo_ratings (model_name, rating, wins, updated_at)
            VALUES (%s, %s, 1, CURRENT_TIMESTAMP)
            ON CONFLICT (model_name) DO UPDATE
            SET rating = %s, wins = wins + 1, updated_at = CURRENT_TIMESTAMP
        """, (winner_model, round(new_winner_rating, 2), round(new_winner_rating, 2)))
        
        # Upsert loser
        cursor.execute("""
            INSERT INTO elo_ratings (model_name, rating, losses, updated_at)
            VALUES (%s, %s, 1, CURRENT_TIMESTAMP)
            ON CONFLICT (model_name) DO UPDATE
            SET rating = %s, losses = losses + 1, updated_at = CURRENT_TIMESTAMP
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
    """Reset all ratings to default 1600."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE elo_ratings
            SET rating = 1600.0, wins = 0, losses = 0, updated_at = CURRENT_TIMESTAMP
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
