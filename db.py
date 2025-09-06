import sqlite3
import os

SCHEMA = """
-- documents: stores metadata for source files
CREATE TABLE IF NOT EXISTS documents (
  id INTEGER PRIMARY KEY,
  path TEXT UNIQUE,
  title TEXT,
  subject TEXT,
  imported_at TEXT
);

-- chunks: stores text from each page/section
CREATE TABLE IF NOT EXISTS chunks (
  id INTEGER PRIMARY KEY,
  document_id INTEGER,
  page_from INTEGER,
  page_to INTEGER,
  content TEXT,
  FOREIGN KEY(document_id) REFERENCES documents(id)
);

-- knowledge_points: key concepts extracted by Gemini
CREATE TABLE IF NOT EXISTS knowledge_points (
  id INTEGER PRIMARY KEY,
  subject TEXT,
  topic TEXT,
  kp TEXT,
  source_chunk_id INTEGER,
  importance INTEGER DEFAULT 1,
  FOREIGN KEY(source_chunk_id) REFERENCES chunks(id)
);

-- questions: question bank
CREATE TABLE IF NOT EXISTS questions (
  id INTEGER PRIMARY KEY,
  kp_id INTEGER,
  qtype TEXT,
  stem TEXT,
  options TEXT,
  answer TEXT,
  explanation TEXT,
  source_chunk_id INTEGER,
  created_at TEXT,
  FOREIGN KEY(kp_id) REFERENCES knowledge_points(id),
  FOREIGN KEY(source_chunk_id) REFERENCES chunks(id)
);

-- attempts: record of user's answers
CREATE TABLE IF NOT EXISTS attempts (
  id INTEGER PRIMARY KEY,
  question_id INTEGER,
  user_answer TEXT,
  is_correct INTEGER,
  created_at TEXT,
  FOREIGN KEY(question_id) REFERENCES questions(id)
);

-- mistakes: the user's personal "mistake log"
CREATE TABLE IF NOT EXISTS mistakes (
  id INTEGER PRIMARY KEY,
  question_id INTEGER,
  wrong_answer TEXT,
  correct_answer TEXT,
  kp_id INTEGER,
  first_seen_at TEXT,
  last_seen_at TEXT,
  times INTEGER DEFAULT 1,
  FOREIGN KEY(question_id) REFERENCES questions(id),
  FOREIGN KEY(kp_id) REFERENCES knowledge_points(id)
);
"""

def get_db(path: str = "study.db"):
    """
    Connects to the SQLite database and initializes the schema if the file does not exist.
    
    Args:
        path (str): The path to the database file.
        
    Returns:
        sqlite3.Connection: The database connection object.
    """
    init = not os.path.exists(path)
    conn = sqlite3.connect(path)
    if init:
        conn.executescript(SCHEMA)
        conn.commit()
    return conn
