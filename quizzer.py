# -*- coding: utf-8 -*-
import json
import sqlite3
import datetime
from rich import print
from llm import ask_gemini_cli

# Prompts for Gemini
# NOTE: Prompt for generating questions
GENERATE_QUIZ_PROMPT = """
You are a senior quiz master. Based on the following knowledge point, strictly generate {n} multiple-choice questions.
Each question should have a stem, four options (A, B, C, D), and a correct answer.
Strictly return a JSON array. If unable to generate, return an empty array.

Each JSON object should contain:
- "qtype": "choice"
- "stem": "Question stem content"
- "options": {{"A": "Option A content", "B": "Option B content", "C": "Option C content", "D": "Option D content"}}
- "answer": "Correct option letter (e.g., 'A')"
- "explanation": "Detailed explanation"

Knowledge Point: {kp_text}
"""

# NOTE: Prompt for grading answers
GRADE_PROMPT = """
You are a test grader. Based on the standard answer, strictly judge if the student's answer is correct.
Your output must be JSON and contain only the following keys:
- "is_correct": true or false
- "correct_answer": The correct answer
- "explanation": A brief explanation

Question Stem: {stem}
Standard Answer: {answer}
Student Answer: {user_answer}
"""

def generate_quiz(conn: sqlite3.Connection, kp_id: int, n: int = 5):
    """
    Generates n quiz questions based on a specific knowledge point ID and saves them to the database.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT kp FROM knowledge_points WHERE id = ?", (kp_id,))
    result = cursor.fetchone()
    if not result:
        print("[bold red]Error:[/bold red] Knowledge point not found.")
        return []
    
    kp_text = result[0]
    
    prompt = GENERATE_QUIZ_PROMPT.format(n=n, kp_text=kp_text)
    
    try:
        response_text = ask_gemini_cli(prompt)
        questions = json.loads(response_text)
    except json.JSONDecodeError as e:
        print(f"[bold red]Error:[/bold red] Failed to parse JSON from Gemini. {e}")
        print(f"Gemini raw output: {response_text}")
        return []
    except Exception as e:
        print(f"[bold red]Error:[/bold red] An error occurred while generating quiz: {e}")
        return []

    if not questions:
        print("[bold red]Error:[/bold red] Gemini did not generate any questions.")
        return []

    saved_questions = []
    for q in questions:
        try:
            # Get the source_chunk_id from the knowledge_points table
            cursor.execute("SELECT source_chunk_id FROM knowledge_points WHERE id = ?", (kp_id,))
            source_chunk_id = cursor.fetchone()[0]

            cursor.execute(
                "INSERT INTO questions (kp_id, qtype, stem, options, answer, explanation, source_chunk_id, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (kp_id, q.get("qtype"), q.get("stem"), json.dumps(q.get("options")), q.get("answer"), q.get("explanation"), source_chunk_id, datetime.datetime.now().isoformat())
            )
            q_id = cursor.lastrowid
            q["id"] = q_id
            saved_questions.append(q)
        except Exception as e:
            print(f"[bold red]Error:[/bold red] Failed to save question to DB: {e}")
            continue
            
    conn.commit()
    print(f"[green]Successfully generated and saved[/] [bold]{len(saved_questions)}[/bold] questions.")
    
    return saved_questions

def grade_and_log(conn: sqlite3.Connection, question: dict, user_answer: str) -> bool:
    """
    Grades the user's answer, logs the attempt, and updates the mistakes table.
    """
    is_correct = False
    explanation = "No explanation provided."
    correct_answer = question.get("answer", "N/A")
    
    prompt = GRADE_PROMPT.format(
        stem=question.get("stem"), 
        answer=question.get("answer"), 
        user_answer=user_answer
    )
    
    try:
        response = ask_gemini_cli(prompt)
        grading_result = json.loads(response)
        is_correct = grading_result.get("is_correct", False)
        explanation = grading_result.get("explanation", explanation)
        correct_answer = grading_result.get("correct_answer", correct_answer)
    except Exception as e:
        print(f"[bold red]Error:[/bold red] Failed to grade with Gemini: {e}. Defaulting to simple comparison.")
        if user_answer.strip().lower() == correct_answer.strip().lower():
            is_correct = True

    # Log the attempt
    conn.execute(
        "INSERT INTO attempts (question_id, user_answer, is_correct, created_at) VALUES (?, ?, ?, ?)",
        (question.get("id"), user_answer, 1 if is_correct else 0, datetime.datetime.now().isoformat())
    )

    if not is_correct:
        # Log the mistake
        cursor = conn.cursor()
        cursor.execute("SELECT id, times FROM mistakes WHERE question_id = ?", (question.get("id"),))
        row = cursor.fetchone()
        
        if row:
            # Update existing mistake
            mistake_id, times = row
            conn.execute(
                "UPDATE mistakes SET wrong_answer=?, correct_answer=?, last_seen_at=?, times=? WHERE id=?",
                (user_answer, correct_answer, datetime.datetime.now().isoformat(), times + 1, mistake_id)
            )
        else:
            # Insert new mistake
            conn.execute(
                "INSERT INTO mistakes (question_id, wrong_answer, correct_answer, kp_id, first_seen_at, last_seen_at, times) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (question.get("id"), user_answer, correct_answer, question.get("kp_id"), datetime.datetime.now().isoformat(), datetime.datetime.now().isoformat(), 1)
            )

        print(f"\n[bold red]Incorrect! The answer is: {correct_answer}[/]")
        print(f"[bold red]Explanation:[/][dim] {explanation}[/]")
    else:
        print("[bold green]✅ Correct![/]")

    conn.commit()
    return is_correct
