
# mcp_server.py
# Minimal MCP wrapper for your existing Study Partner modules.
# Run with: python mcp_server.py  (stdio server)
# Requires: pip install mcp

import os
import json
import sqlite3
from typing import Optional, Dict, Any, List

from mcp.server.fastmcp import FastMCP

# Import your local modules
from db import get_db
from parser import import_path
from kp_extractor import extract_knowledge_points as kp_extract_llm, save_knowledge_points
from quizzer import generate_quiz, grade_and_log
from report import generate_report

DB_PATH = os.getenv("DB_PATH", "study.db")

mcp = FastMCP("Study Partner")

def _conn() -> sqlite3.Connection:
    # Your get_db() already initializes schema if needed
    return get_db(DB_PATH)

# ---------- Tools ----------

@mcp.tool()
def import_documents(path: str, subject: Optional[str] = None) -> Dict[str, int]:
    """Walk a path, parse PDF/MD/TXT into SQLite (documents/chunks). Return counts."""
    conn = _conn()
    docs, chunks = import_path(conn, path, subject)
    return {"docs": docs, "chunks": chunks}

@mcp.tool()
def extract_kps(subject: Optional[str] = None, limit: int = 50) -> Dict[str, int]:
    """Aggregate DB chunks -> LLM extraction -> save into knowledge_points (with source_chunk_id when available)."""
    conn = _conn()
    cur = conn.cursor()
    if subject:
        cur.execute(
            """SELECT c.id, c.content
               FROM chunks c
               JOIN documents d ON d.id = c.document_id
               WHERE d.subject = ?""",
            (subject,)
        )
    else:
        cur.execute("SELECT id, content FROM chunks")
    rows = cur.fetchall()
    if not rows:
        return {"inserted": 0, "note": "No chunks found. Run import_documents first."}

    # Build a big string that preserves chunk ids (your extractor can use this)
    doc = ""
    for chunk_id, content in rows:
        doc += f"[CHUNK_ID:{chunk_id}] {content}\n\n"

    kp_list = []
    try:
        kp_list = kp_extract_llm(doc, limit=limit) or []
    except Exception as e:
        return {"inserted": 0, "error": f"extractor failed: {e}"}

    # Prefer storing source_chunk_id if provided by the extractor
    inserted = 0
    for item in kp_list:
        subject_val = item.get("subject")
        topic_val = item.get("topic")
        kp_text = item.get("kp")
        chunk_id = item.get("chunk_id")  # optional

        if chunk_id is not None:
            conn.execute(
                "INSERT INTO knowledge_points (subject, topic, kp, source_chunk_id) VALUES (?, ?, ?, ?)",
                (subject_val, topic_val, kp_text, int(chunk_id))
            )
        else:
            # fall back to legacy saver (no chunk linkage)
            conn.execute(
                "INSERT INTO knowledge_points (subject, topic, kp) VALUES (?, ?, ?)",
                (subject_val, topic_val, kp_text)
            )
        inserted += 1
    conn.commit()
    return {"inserted": inserted}

@mcp.tool()
def generate_quiz_tool(kp_id: int, n: int = 5) -> List[Dict[str, Any]]:
    """Generate questions for a given knowledge point id. Returns question metadata (answer hidden)."""
    conn = _conn()
    items = generate_quiz(conn, kp_id=kp_id, n=n) or []
    # Hide answers to avoid leaking through UI
    out = []
    for it in items:
        out.append({
            "id": it.get("id"),
            "qtype": it.get("qtype"),
            "stem": it.get("stem"),
            "options": it.get("options"),
        })
    return out

@mcp.tool()
def grade(question_id: int, user_answer: str) -> Dict[str, Any]:
    """Grade an answer and log to attempts/mistakes. Returns correctness and brief explanation."""
    conn = _conn()
    row = conn.execute(
        "SELECT id, stem, options, answer, explanation FROM questions WHERE id=?",
        (question_id,)
    ).fetchone()
    if not row:
        return {"is_correct": False, "error": f"Question {question_id} not found"}

    q = {
        "id": row[0],
        "stem": row[1],
        "options": json.loads(row[2]) if row[2] else None,
        "answer": row[3],
        "explanation": row[4] or ""
    }
    is_right = grade_and_log(conn, q, user_answer)
    return {"is_correct": bool(is_right)}

@mcp.tool()
def export_report_tool() -> Dict[str, str]:
    """Render the Markdown mistakes report and return its file path."""
    conn = _conn()
    message = generate_report(conn)  # your function returns a human message containing the path
    # Attempt to extract a path
    path = None
    for token in message.split():
        if token.endswith(".md"):
            path = token
            break
    return {"message": message, "path": path or ""}

@mcp.tool()
def list_kps(subject: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
    """List knowledge points for easier selection in clients."""
    conn = _conn()
    if subject:
        rows = conn.execute(
            "SELECT id, subject, topic, kp, source_chunk_id FROM knowledge_points WHERE subject=? LIMIT ?",
            (subject, limit)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT id, subject, topic, kp, source_chunk_id FROM knowledge_points ORDER BY id DESC LIMIT ?",
            (limit,)
        ).fetchall()
    return [
        {"id": r[0], "subject": r[1], "topic": r[2], "kp": r[3], "source_chunk_id": r[4]}
        for r in rows
    ]

# ---------- Resources (read-only) ----------

@mcp.resource("study://kp/{kp_id}")
def get_kp(kp_id: int) -> Dict[str, Any]:
    """Return a knowledge point object (with chunk linkage)."""
    conn = _conn()
    r = conn.execute(
        "SELECT id, subject, topic, kp, source_chunk_id FROM knowledge_points WHERE id=?",
        (kp_id,)
    ).fetchone()
    if not r:
        return {}
    return {"id": r[0], "subject": r[1], "topic": r[2], "kp": r[3], "source_chunk_id": r[4]}

@mcp.resource("study://chunks/{chunk_id}")
def get_chunk(chunk_id: int) -> Dict[str, Any]:
    """Return chunk text, page numbers and source file path."""
    conn = _conn()
    r = conn.execute(
        """SELECT c.id, c.content, c.page_from, c.page_to, d.path
           FROM chunks c JOIN documents d ON d.id = c.document_id
           WHERE c.id=?""",
        (chunk_id,)
    ).fetchone()
    if not r:
        return {}
    return {"id": r[0], "content": r[1], "page_from": r[2], "page_to": r[3], "path": r[4]}

if __name__ == "__main__":
    import asyncio
    # Start stdio server (works well for local dev and Gemini CLI)
    asyncio.run(mcp.run(transport="stdio"))
