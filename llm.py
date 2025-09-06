# import os
# import subprocess
# import json

# def ask_gemini_cli(prompt: str, system_instruction: str = "") -> str:
#     """
#     Mocks a call to the Gemini CLI.
#     During the hackathon, this will be replaced with actual code.
#     """
#     # For now, we'll just return a mock JSON response.
#     # In the actual hackathon, we'll use a subprocess to call the CLI.
#     if "quiz" in prompt.lower() or "generate" in prompt.lower():
#         mock_output = [
#             {
#                 "qtype": "choice",
#                 "stem": "What model does Bitcoin use for transactions?",
#                 "options": {"A": "Balance model", "B": "UTXO model", "C": "Account model", "D": "State model"},
#                 "answer": "B",
#                 "explanation": "Bitcoin uses the UTXO (Unspent Transaction Output) model where transactions reference previous outputs."
#             }
#         ]
#     elif "knowledge points" in prompt.lower():
#         mock_output = [
#             {"subject": "Cryptocurrencies", "topic": "Bitcoin", "kp": "Bitcoin uses UTXO model for transactions", "chunk_id": 1},
#             {"subject": "Cryptocurrencies", "topic": "Blockchain", "kp": "Transactions are recorded in blocks", "chunk_id": 2}
#         ]
#     elif "grader" in prompt.lower() or "judge" in prompt.lower():
#         mock_output = {
#             "is_correct": True,
#             "correct_answer": "B",
#             "explanation": "This is the correct answer because Bitcoin uses the UTXO model."
#         }
#     else:
#         mock_output = {"summary": "This is a mock summary of the document."}
    
#     return json.dumps(mock_output)

import os
import subprocess
import json
import tempfile

def ask_gemini_cli(prompt: str, system_instruction: str = "") -> str:
    """
    Calls the actual Gemini CLI with the provided prompt.
    Requires GEMINI_API_KEY environment variable to be set.
    """
    # Check if API key is available
    if not os.getenv("GEMINI_API_KEY"):
        raise ValueError("GEMINI_API_KEY environment variable not set")
    
    try:
        # Create a temporary file for the prompt (handles special characters better)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(prompt)
            prompt_file = f.name
        
        # Build the gemini CLI command
        cmd = ["gemini", "chat"]
        
        if system_instruction:
            cmd.extend(["--system", system_instruction])
        
        # Use the prompt file
        cmd.extend(["--prompt-file", prompt_file])
        
        # Execute the command
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60  # 60 second timeout
        )
        
        # Clean up the temporary file
        os.unlink(prompt_file)
        
        if result.returncode != 0:
            raise RuntimeError(f"Gemini CLI failed: {result.stderr}")
            
        return result.stdout.strip()
        
    except subprocess.TimeoutExpired:
        raise RuntimeError("Gemini CLI call timed out")
    except FileNotFoundError:
        raise RuntimeError("Gemini CLI not found. Please install it first.")
    except Exception as e:
        # Fallback to mock for development/testing
        print(f"Warning: Gemini CLI call failed ({e}), using mock response")
        return _get_mock_response(prompt)

def _get_mock_response(prompt: str) -> str:
    """Fallback mock responses for development"""
    if "quiz" in prompt.lower() or "generate" in prompt.lower():
        return json.dumps([
            {
                "qtype": "choice",
                "stem": "What model does Bitcoin use for transactions?",
                "options": {"A": "Balance model", "B": "UTXO model", "C": "Account model", "D": "State model"},
                "answer": "B",
                "explanation": "Bitcoin uses the UTXO (Unspent Transaction Output) model where transactions reference previous outputs."
            }
        ])
    elif "knowledge points" in prompt.lower():
        return json.dumps([
            {"subject": "Cryptocurrencies", "topic": "Bitcoin", "kp": "Bitcoin uses UTXO model for transactions", "chunk_id": 1},
            {"subject": "Cryptocurrencies", "topic": "Blockchain", "kp": "Transactions are recorded in blocks", "chunk_id": 2}
        ])
    elif "grader" in prompt.lower() or "judge" in prompt.lower():
        return json.dumps({
            "is_correct": True,
            "correct_answer": "B",
            "explanation": "This is the correct answer because Bitcoin uses the UTXO model."
        })
    else:
        return json.dumps({"summary": "This is a mock summary of the document."})