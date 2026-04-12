# database.py
import sqlite3

def create_database():
    conn = sqlite3.connect("voters.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS voters (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            voter_id    TEXT UNIQUE NOT NULL,
            name        TEXT NOT NULL,
            photo_path  TEXT NOT NULL,
            has_voted   INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()
    print("Database created successfully!")

if __name__ == "__main__":
    create_database()