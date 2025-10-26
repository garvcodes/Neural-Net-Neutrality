#!/usr/bin/env python3
import os

# Set the database URL
os.environ['DATABASE_URL'] = 'postgresql://postgres:Garvsoham1115!@db.tvsyvfkereavzztcmkkq.supabase.co:5432/postgres'

try:
    from backend.supabase_db import init_database, get_all_ratings
    
    print("Testing Supabase connection...")
    init_database()
    print("✅ Database initialized successfully!")
    
    ratings = get_all_ratings()
    print(f"✅ Current ratings: {ratings}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
