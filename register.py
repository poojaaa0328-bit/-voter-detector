import sqlite3
import os

def register_voter(voter_id, name, photo_path):
    if not os.path.exists(photo_path):
        print(f"ERROR: Photo not found at {photo_path}")
        return
    conn = sqlite3.connect("voters.db")
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO voters (voter_id, name, photo_path, has_voted)
            VALUES (?, ?, ?, 0)
        """, (voter_id, name, photo_path))
        conn.commit()
        print(f"Voter '{name}' registered successfully!")
    except sqlite3.IntegrityError:
        print(f"ERROR: Voter ID '{voter_id}' already exists!")
    finally:
        conn.close()

def list_voters():
    conn = sqlite3.connect("voters.db")
    cursor = conn.cursor()
    cursor.execute("SELECT voter_id, name, has_voted FROM voters")
    rows = cursor.fetchall()
    conn.close()
    print("\n--- Registered Voters ---")
    for row in rows:
        status = "VOTED" if row[2] == 1 else "Not voted"
        print(f"  ID: {row[0]} | Name: {row[1]} | Status: {status}")
    print("-------------------------\n")

if __name__ == "__main__":
    os.makedirs("photos", exist_ok=True)
    register_voter("VOT001", "Lionel Messi",  "photos/messi.jpeg")
    register_voter("VOT002", "MS Dhoni",      "photos/ms dhoni.jpeg")
    register_voter("VOT003", "Neymar Jr",     "photos/Neymar Jr.jpeg")
    register_voter("VOT004", "Narendra Modi", "photos/narendra modi.jpeg")
    register_voter("VOT005", "Elon Musk",     "photos/Elon Musk.jpeg")
    list_voters()