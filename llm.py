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

def check_auth_status():
    """Check if user has valid Google Cloud authentication"""
    try:
        result = subprocess.run([
            'gcloud', 'auth', 'application-default', 'print-access-token'
        ], capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def setup_authentication():
    """Guide user through authentication setup"""
    print("Setting up Google Cloud authentication...")
    print("This will open your browser to sign in with Google.")
    
    try:
        # Check if gcloud is installed
        subprocess.run(['gcloud', '--version'], 
                      capture_output=True, text=True, check=True)
        
        # Run authentication
        result = subprocess.run([
            'gcloud', 'auth', 'application-default', 'login'
        ], timeout=120)
        
        return result.returncode == 0
        
    except subprocess.CalledProcessError:
        print("Error: Google Cloud CLI not found.")
        print("Please install from: https://cloud.google.com/sdk/docs/install")
        return False
    except subprocess.TimeoutExpired:
        print("Authentication timed out.")
        return False

def ask_gemini_cli(prompt: str, system_instruction: str = "") -> str:
    """
    Call Gemini using Google Cloud authentication or fallback to mock
    """
    # First try environment variable (backwards compatibility)
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        return _call_gemini_with_api_key(prompt, system_instruction, api_key)
    
    # Try Google Cloud authentication
    if not check_auth_status():
        print("Google Cloud authentication required.")
        if not setup_authentication():
            print("Warning: Using mock responses for demo. Set up authentication for real Gemini calls.")
            return _get_mock_response(prompt)
    
    try:
        return _call_gemini_with_gcloud(prompt, system_instruction)
    except Exception as e:
        print(f"Warning: Gemini call failed ({e}), using mock response")
        return _get_mock_response(prompt)

def _call_gemini_with_api_key(prompt: str, system_instruction: str, api_key: str) -> str:
    """Call Gemini CLI with API key"""
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            full_prompt = f"System: {system_instruction}\n\nUser: {prompt}" if system_instruction else prompt
            f.write(full_prompt)
            prompt_file = f.name
        
        env = os.environ.copy()
        env['GEMINI_API_KEY'] = api_key
        
        result = subprocess.run([
            'gemini', 'chat', '--prompt-file', prompt_file
        ], capture_output=True, text=True, timeout=60, env=env)
        
        os.unlink(prompt_file)
        
        if result.returncode != 0:
            raise RuntimeError(f"Gemini CLI failed: {result.stderr}")
            
        return result.stdout.strip()
        
    except Exception as e:
        raise RuntimeError(f"Gemini API call failed: {e}")

def _call_gemini_with_gcloud(prompt: str, system_instruction: str) -> str:
    """Call Gemini using Google Cloud SDK"""
    try:
        import google.generativeai as genai
        
        # Configure with default credentials
        genai.configure()
        model = genai.GenerativeModel('gemini-pro')
        
        full_prompt = f"System: {system_instruction}\n\nUser: {prompt}" if system_instruction else prompt
        response = model.generate_content(full_prompt)
        
        return response.text
        
    except ImportError:
        raise RuntimeError("google-generativeai package not installed")
    except Exception as e:
        raise RuntimeError(f"Gemini API call failed: {e}")

def _get_mock_response(prompt: str) -> str:
    """Mock responses for development/demo"""
    if "quiz" in prompt.lower() or "generate" in prompt.lower():
        return json.dumps([
            {
                "qtype": "choice",
                "stem": "What authentication method does this app use?",
                "options": {
                    "A": "API keys only", 
                    "B": "Google Cloud authentication", 
                    "C": "No authentication", 
                    "D": "Username/password"
                },
                "answer": "B",
                "explanation": "The app uses Google Cloud authentication for secure, user-friendly access to Gemini."
            }
        ])
    elif "knowledge points" in prompt.lower():
        return json.dumps([
            {
                "subject": "Authentication", 
                "topic": "Google Cloud", 
                "kp": "Google Cloud authentication provides secure API access without managing API keys", 
                "chunk_id": 1
            },
            {
                "subject": "Security", 
                "topic": "OAuth", 
                "kp": "OAuth tokens allow controlled access to services without sharing passwords", 
                "chunk_id": 2
            }
        ])
    elif "grader" in prompt.lower() or "judge" in prompt.lower():
        return json.dumps({
            "is_correct": True,
            "correct_answer": "B",
            "explanation": "This demonstrates the authentication system working correctly."
        })
    else:
        return json.dumps({"summary": "This is a demo response showing the authentication system."})