import sqlite3
import os

DB_PATH = "study.db"

def check_knowledge_points():
    """Connects to the database and prints all knowledge points."""
    if not os.path.exists(DB_PATH):
        print(f"Error: Database file not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id, subject, topic, kp, source_chunk_id FROM knowledge_points")
        rows = cursor.fetchall()

        if not rows:
            print("No knowledge points found in the database.")
            return

        print("--- Knowledge Points in Database ---")
        for row in rows:
            kp_id, subject, topic, kp, chunk_id = row
            print(f"ID: {kp_id}")
            print(f"  Subject: {subject}")
            print(f"  Topic: {topic}")
            print(f"  KP: {kp}")
            print(f"  Source Chunk ID: {chunk_id}")
            print("---")

    except sqlite3.OperationalError as e:
        print(f"Error: {e}. Is the 'knowledge_points' table created?")
    finally:
        conn.close()

if __name__ == "__main__":
    check_knowledge_points()


