import os
import typer
import json
from rich import print
import json
import sqlite3

# Local imports
from db import get_db
from parser import import_path
from llm import ask_gemini_cli
from quizzer import generate_quiz, grade_and_log
from kp_extractor import extract_knowledge_points, save_knowledge_points
from report import generate_report

app = typer.Typer(help="Study Partner CLI")

# NOTE: Command to import local documents
@app.command(name="import")
def import_command(
    path: str = typer.Argument(..., help="Path to the directory with your study files.")
):
    """Imports documents from a local path into the database."""
    # Check if the database file exists and if db.py is accessible
    if not os.path.exists("study.db"):
        try:
            get_db()
            print("[green]Database initialized successfully.[/]")
        except NameError:
            print("[bold red]Error:[/] Could not initialize database. Make sure db.py is in the same directory.")
            return
            
    conn = get_db()
    n_docs, n_chunks = import_path(conn, path)
    print(f"[green]Successfully imported[/] [bold]{n_docs}[/bold] documents with [bold]{n_chunks}[/bold] text chunks.")

# NOTE: Command to summarize and extract knowledge points
@app.command(name="summarize")
def summarize_command():
    """Generates a summary of the documents in a local path."""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get chunks AND check if documents have user-provided subjects
    cursor.execute("""
        SELECT c.id, c.content, d.subject 
        FROM chunks c 
        JOIN documents d ON d.id = c.document_id
    """)
    all_chunks = cursor.fetchall()

    if not all_chunks:
        print("[bold red]Error:[/] No text found in the database. Please run the 'import' command first.")
        return

    # Check if user provided subjects during import
    user_subjects = set(row[2] for row in all_chunks if row[2] is not None)
    has_user_subjects = len(user_subjects) > 0

    # Create document string with chunk IDs
    doc_string = ""
    for chunk_id, content, doc_subject in all_chunks:
        doc_string += f"[CHUNK_ID:{chunk_id}] {content}\n\n"
    
    print("[yellow]Extracting knowledge points from documents...[/]")
    
    # Adapt prompt based on whether user provided subjects
    if has_user_subjects:
        prompt_template = """
        You are extracting knowledge points from documents that users have categorized into subjects: {subjects}
        
        For each knowledge point, use the appropriate subject from the user's categories: {subjects}
        Only use these subjects - do not create new ones.
        
        Extract 3-10 knowledge points. Return valid JSON array with:
        - "subject": One of these user-provided subjects: {subjects}
        - "topic": Specific subtopic within that subject
        - "kp": Knowledge point statement
        - "chunk_id": The ID from [CHUNK_ID:X] markers
        
        Documents:
        ---
        {docs}
        ---
        """
        prompt = prompt_template.format(
            subjects=list(user_subjects), 
            docs=doc_string
        )
    else:
        prompt_template = """
        You are extracting knowledge points from documents. Since no subject categories were provided, analyze the content and determine appropriate subjects.
        
        Extract 3-10 knowledge points. Return valid JSON array with:
        - "subject": Your best guess at the main subject (e.g., "Physics", "Computer Science", "Biology")
        - "topic": Specific subtopic within that subject
        - "kp": Knowledge point statement  
        - "chunk_id": The ID from [CHUNK_ID:X] markers
        
        Documents:
        ---
        {docs}
        ---
        """
        prompt = prompt_template.format(docs=doc_string)
    
    # Rest of your existing code...
    response = ask_gemini_cli(prompt)
 
    try:
        kp_list = json.loads(response)
        if kp_list:
            for kp_item in kp_list:
                # NEW: Save the chunk_id from the JSON response
                conn.execute(
                    "INSERT INTO knowledge_points (subject, topic, kp, source_chunk_id) VALUES (?, ?, ?, ?)",
                    (kp_item.get("subject"), kp_item.get("topic"), kp_item.get("kp"), kp_item.get("chunk_id"))
                )
            conn.commit()
            print(f"[green]Successfully extracted and saved[/] [bold]{len(kp_list)}[/bold] knowledge points.")
        else:
            print("[bold red]Error:[/] No knowledge points were extracted.")
    except json.JSONDecodeError:
        print("[bold red]Error:[/] Failed to parse JSON from Gemini. Check the model's output.")

# NOTE: Command to generate and run a quiz
@app.command(name="quiz")
def quiz_command(
    n: int = typer.Option(5, "--num", "-n", help="Number of questions to generate."),
    kp_id: int = typer.Option(None, "--kp-id", "-k", help="ID of a specific knowledge point to quiz on.")
):
    """
    Generates and runs a quiz based on knowledge points.
    """
    db_conn = get_db()
    
    if kp_id is None:
        # If no specific KP is selected, choose a random one from the database.
        cursor = db_conn.cursor()
        cursor.execute("SELECT id FROM knowledge_points ORDER BY RANDOM() LIMIT 1")
        result = cursor.fetchone()
        if not result:
            print("[bold red]Error:[/] No knowledge points found. Please run the 'summarize' command first.")
            raise typer.Exit()
        kp_id = result[0]
        print(f"[bold cyan]Quizzing on a random knowledge point (ID: {kp_id}).[/bold cyan]")
    
    # Generate the quiz questions
    questions = generate_quiz(db_conn, kp_id, n)

    if not questions:
        print("[bold yellow]No questions were generated. Exiting quiz.[/bold yellow]")
        db_conn.close()
        raise typer.Exit()

    print(f"\n[bold]Starting Quiz! (Total questions: {len(questions)})[/bold]")

    # Run the quiz
    for i, q in enumerate(questions, 1):
        print("\n---")
        print(f"[bold]Question {i}:[/bold] {q.get('stem')}")
        options = q.get('options', {})
        for key, value in options.items():
            print(f"[cyan]{key})[/cyan] {value}")
        
        user_answer = typer.prompt("Your answer")
        
        grade_and_log(db_conn, q, user_answer)
        
    print("\n---")
    print("[bold green]Quiz finished![/bold green]")
    db_conn.close()

# CLI Command: Report
@app.command(name="report")
def report_command():
    """Generates a Markdown report of all mistakes."""
    conn = get_db()
    message = generate_report(conn)
    print(message)
    conn.close()

if __name__ == "__main__":
    app()
