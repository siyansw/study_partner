# 📚 Study Partner  
**Team: Procastinators**  
AI Tinkerers – New York City Hackathon (Building with Gemini CLI)  

---

## 📝 Problem Statement  
Right before exams, students often feel **overwhelmed by scattered notes, lecture slides, and textbooks**.  
They waste precious time organizing instead of focusing on actual learning.  

Our **Study_partner** solves this by turning messy study material into **concise summaries, key points, quizzes, and progress reports**—all powered by **Gemini CLI** and a local-first workflow.  

---

## 🚀 Features
- **Summarization**: Condense large lecture notes into concise takeaways.  
- **Key Point Extraction**: Automatically highlight the most important details.  
- **Quiz Generator**: Create practice quizzes directly from notes.  
- **Progress Reports**: AI-generated insights into what’s covered and what’s weak.  
- **Self-defined Subjects**: Users can define their own subject focus.  
- **Local + Gemini**: Mixes local parsing with Gemini’s advanced summarization and reasoning.  

---

## 🛠️ Installation

### 1. Clone repo
```bash
git clone https://github.com/siyansw/study_partner.git
cd study_partner

### 2. Create virtual environment
python -m venv venv
source venv/bin/activate     # macOS/Linux
venv\Scripts\activate        # Windows

3. Install dependencies
pip install -r requirements.txt

🔑 Environment Variables

Create a .env file in the root folder with:

GEMINI_API_KEY=your_api_key_here


⚠️ Important:

Do not commit your actual key.

Add .env to .gitignore.

Use .env.example for sharing.

▶️ Usage
Run the app end-to-end:
python app.py

Workflow Example

Place your lecture notes or text files into test_data/.

Run summarization (llm.py) → Gemini condenses your notes.

Generate quizzes (quizzer.py) → practice questions are created.

View reports in reports/ → progress and insights are saved locally.

📂 Project Structure
study_partner/
│── app.py             # Main entry point (Gemini + workflow integration)
│── db.py              # Database setup
│── db_checker.py      # DB verification helpers
│── kp_extractor.py    # Extracts key points from study materials
│── llm.py             # Summarization with Gemini
│── mcp_server.py      # Local server orchestration
│── parser.py          # User subject definitions
│── quizzer.py         # Generates quizzes from extracted notes
│── report.py          # Creates progress reports
│── requirements.txt   # Dependencies
│── README.md          # Documentation
│
├── reports/           # Auto-generated reports
├── test_data/         # Example input study files
└── __pycache__/       # Compiled Python files

📊 Where Gemini is Used

llm.py: Summarization of notes via Gemini CLI.

app.py: End-to-end pipeline orchestration using Gemini.

quizzer.py + report.py: Chain Gemini outputs into actionable quizzes/reports.
