import os
import sqlite3
import datetime
from PyPDF2 import PdfReader
from db import get_db

def _insert_doc(conn, path, subject):
    """Inserts a document into the database if it doesn't exist."""
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO documents(path, title, subject, imported_at) VALUES(?,?,?,?)",
                (path, os.path.basename(path), subject, datetime.datetime.now().isoformat()))
    conn.commit()
    cur.execute("SELECT id FROM documents WHERE path=?", (path,))
    return cur.fetchone()[0]

def _insert_chunk(conn, doc_id, page_from, page_to, content):
    """Inserts a text chunk into the database."""
    conn.execute("INSERT INTO chunks(document_id, page_from, page_to, content) VALUES(?,?,?,?)",
                 (doc_id, page_from, page_to, content))
    conn.commit()

def import_path(conn, path, subject=None):
    """Parses files from a given path and imports them into the database."""
    n_docs = 0
    n_chunks = 0
    for root, _, files in os.walk(path):
        for f in files:
            p = os.path.join(root, f)
            if f.lower().endswith('.pdf'):
                try:
                    reader = PdfReader(p)
                    doc_id = _insert_doc(conn, p, subject)
                    for i, page in enumerate(reader.pages, 1):
                        text = page.extract_text() or ""
                        if text.strip():
                            _insert_chunk(conn, doc_id, i, i, text)
                            n_chunks += 1
                    n_docs += 1
                except Exception as e:
                    print(f"Warning: Could not process PDF {p}. Skipping. Error: {e}")
            elif f.lower().endswith(('.md', '.txt')):
                doc_id = _insert_doc(conn, p, subject)
                try:
                    with open(p, 'r', encoding='utf-8', errors='ignore') as rf:
                        text = rf.read()
                    _insert_chunk(conn, doc_id, 1, 1, text)
                    n_docs += 1
                    n_chunks += 1
                except Exception as e:
                    print(f"Warning: Could not process text file {p}. Skipping. Error: {e}")
    return n_docs, n_chunks
