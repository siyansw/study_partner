import json
from llm import ask_gemini_cli
from db import get_db

PROMPT = """
You are a subject matter expert. Your task is to analyze the provided text documents and extract key knowledge points. The output must be a single JSON array, where each object has the following keys:
- "subject": The main subject or topic (e.g., "Cryptography", "Physics").
- "topic": A sub-topic or chapter title (e.g., "Hash Functions", "Quantum Mechanics").
- "kp": A concise statement of the knowledge point.

The JSON array should contain at least 5 knowledge points. Ensure the output is a single, valid JSON array.

Example of expected output:
[
  {{ "subject": "Physics", "topic": "Quantum", "kp": "Schrödinger's equation describes how the quantum state of a physical system changes over time." }}
]

Text to analyze:\n{content}
"""

def extract_knowledge_points(text_content, limit=5):
    """
    Extracts knowledge points from text using the Gemini CLI.
    """
    prompt_with_content = PROMPT.format(content=text_content)
    response = ask_gemini_cli(prompt_with_content)
    
    try:
        # Extract JSON from markdown code blocks if present
        if response.strip().startswith('```json'):
            # Find the JSON content between ```json and ```
            start = response.find('```json') + 7
            end = response.find('```', start)
            json_content = response[start:end].strip()
        elif response.strip().startswith('```'):
            # Handle generic code blocks
            start = response.find('```') + 3
            end = response.find('```', start)
            json_content = response[start:end].strip()
        else:
            json_content = response.strip()
        
        knowledge_points = json.loads(json_content)
        if isinstance(knowledge_points, list):
            return knowledge_points
        else:
            print("[bold red]Error:[/] Gemini response was not a JSON array.")
            return []
    except json.JSONDecodeError:
        print("[bold red]Error:[/] Failed to parse JSON from Gemini. Check the model's output for invalid characters.")
        return []

def save_knowledge_points(conn, kp_list):
    """Saves extracted knowledge points to the database."""
    n_inserted = 0
    for kp_item in kp_list:
        conn.execute(
            "INSERT INTO knowledge_points (subject, topic, kp) VALUES (?, ?, ?)",
            (kp_item.get("subject"), kp_item.get("topic"), kp_item.get("kp"))
        )
        n_inserted += 1
    conn.commit()
    return n_inserted
