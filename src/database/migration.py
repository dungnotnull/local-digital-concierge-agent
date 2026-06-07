import sqlite3
import os
from pathlib import Path
from .db_client import db

MIGRATIONS_DIR = Path(__file__).parent / "migrations"

async def init_db():
    """Initialize the database: create tables if not exist, set up version tracking."""
    # Ensure the database file exists
    os.makedirs(os.path.dirname(db.db_path), exist_ok=True)
    
    # Create a connection to check/set version
    conn = sqlite3.connect(db.db_path)
    try:
        # Create schema_version table if it doesn't exist
        conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER PRIMARY KEY,
                applied_at TEXT DEFAULT (datetime('now'))
            )
        """)
        conn.commit()
        
        # Get current version
        cursor = conn.execute("SELECT MAX(version) FROM schema_version")
        row = cursor.fetchone()
        current_version = row[0] if row[0] is not None else 0
        
        # If no version yet, apply the initial schema
        if current_version == 0:
            # Read the schema.sql file
            schema_path = Path(__file__).parent / "schema.sql"
            if schema_path.exists():
                with open(schema_path, 'r', encoding='utf-8') as f:
                    schema_sql = f.read()
                # Execute the schema (split by statements if needed)
                # For simplicity, we execute the whole script
                conn.executescript(schema_sql)
                # Record version 1
                conn.execute("INSERT INTO schema_version (version) VALUES (1)")
                conn.commit()
                print("Initialized database with schema version 1")
            else:
                print("Warning: schema.sql not found")
        else:
            print(f"Database already at version {current_version}")
    finally:
        conn.close()

async def get_db_version() -> int:
    """Get the current schema version."""
    conn = sqlite3.connect(db.db_path)
    try:
        cursor = conn.execute("SELECT MAX(version) FROM schema_version")
        row = cursor.fetchone()
        return row[0] if row[0] is not None else 0
    finally:
        conn.close()

# For simplicity, we don't implement automatic migration scripts here.
# In a real project, you would have numbered SQL files in migrations/
# and apply them sequentially.
