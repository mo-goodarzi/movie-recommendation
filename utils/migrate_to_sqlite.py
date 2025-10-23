"""
Migration script to convert JSON movie data to SQLite database.

This script:
1. Creates a SQLite database with proper schema
2. Reads the JSON data file
3. Populates the database with movies and their text entries
4. Creates indexes for fast querying
"""

import sqlite3
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

def create_database_schema(db_path):
    """Create the SQLite database schema with tables and indexes."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create movies table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movies (
            item_id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            year INTEGER,
            director TEXT,
            stars TEXT,
            avg_rating REAL,
            imdb_id TEXT
        )
    """)

    # Create movie_texts table for storing multiple text entries per movie
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movie_texts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            txt TEXT NOT NULL,
            FOREIGN KEY (item_id) REFERENCES movies(item_id)
        )
    """)

    # Create indexes for fast lookups
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_title ON movies(title)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_imdb_id ON movies(imdb_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_item_id ON movies(item_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_movie_texts_item_id ON movie_texts(item_id)")

    conn.commit()
    print("✓ Database schema created successfully")
    return conn

def migrate_json_to_sqlite(json_path, db_path):
    """Migrate data from JSON file to SQLite database."""

    # Create database and schema
    conn = create_database_schema(db_path)
    cursor = conn.cursor()

    # Read JSON data
    print(f"Reading JSON data from {json_path}...")
    df = pd.read_json(json_path, lines=True)
    print(f"✓ Loaded {len(df)} rows from JSON")

    # Group by item_id to handle multiple text entries per movie
    grouped = df.groupby('item_id')

    movies_inserted = 0
    texts_inserted = 0

    print("Migrating data to SQLite...")
    for item_id, group in grouped:
        # Get the first row for movie metadata (same for all rows with same item_id)
        first_row = group.iloc[0]

        # Insert into movies table (using INSERT OR IGNORE to handle duplicates)
        cursor.execute("""
            INSERT OR IGNORE INTO movies (item_id, title, year, director, stars, avg_rating, imdb_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            int(item_id),
            first_row['title'],
            int(first_row['year']) if pd.notna(first_row['year']) else None,
            first_row.get('directedBy', None),
            first_row.get('starring', None),
            float(first_row['avgRating']) if pd.notna(first_row['avgRating']) else None,
            str(int(first_row['imdbId'])) if pd.notna(first_row['imdbId']) else None
        ))

        if cursor.rowcount > 0:
            movies_inserted += 1

        # Insert all text entries for this movie
        for _, row in group.iterrows():
            cursor.execute("""
                INSERT INTO movie_texts (item_id, txt)
                VALUES (?, ?)
            """, (int(item_id), row['txt']))
            texts_inserted += 1

    conn.commit()

    print(f"✓ Migration completed:")
    print(f"  - {movies_inserted} unique movies inserted")
    print(f"  - {texts_inserted} text entries inserted")

    # Verify the migration
    cursor.execute("SELECT COUNT(*) FROM movies")
    movie_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM movie_texts")
    text_count = cursor.fetchone()[0]

    print(f"\nDatabase statistics:")
    print(f"  - Total movies: {movie_count}")
    print(f"  - Total text entries: {text_count}")
    print(f"  - Average texts per movie: {text_count/movie_count:.2f}")

    conn.close()
    print(f"\n✓ Database saved to: {db_path}")

def main():
    # Get paths from environment or use defaults
    json_path = os.getenv('DATABASE_PATH', 'data/merged_data_untill_1990.json')
    db_path = os.getenv('SQLITE_DB_PATH', 'data/movies.db')

    # Check if JSON file exists
    if not os.path.exists(json_path):
        print(f"Error: JSON file not found at {json_path}")
        return

    # Create data directory if it doesn't exist
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    # Warn if database already exists
    if os.path.exists(db_path):
        response = input(f"Database already exists at {db_path}. Overwrite? (y/n): ")
        if response.lower() != 'y':
            print("Migration cancelled.")
            return
        os.remove(db_path)

    # Run migration
    migrate_json_to_sqlite(json_path, db_path)

if __name__ == "__main__":
    main()
