
# Study Partner  
**Team: Procastinators**  
AI Tinkerers – New York City Hackathon (Building with Gemini CLI)  

---

## Problem Statement  
Right before exams, students often feel **overwhelmed by scattered notes, lecture slides, and textbooks**.  
They waste precious time organizing instead of focusing on actual learning.  

Our **Study_partner** solves this by turning messy study material into **structured knowledge points, quizzes, and progress reports**—all powered by **Gemini CLI** and a local-first workflow. Everything will be done in command lines. The only thing you need is an Gemini API.

---

## Features
- **Import**: Chunk long files into chunks. 
- **Summarization**: AI-generated knowledge points that highlight the most important details.  
- **Quiz Generator**: AI-generated practice quizzes targeting included knowledge points.  
- **Progress Reports**: AI-generated insights into what’s covered and what’s weak, also linking to the original slides.  
- **Self-defined Subjects**: Users can define their own subject focus.  
- **Local + Gemini**: Mixes local parsing with Gemini’s advanced summarization and reasoning.  

---

## Installation

### 1. Clone repo
```bash
git clone https://github.com/siyansw/study_partner.git
cd study_partner
```

## 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate     # macOS/Linux
venv\Scripts\activate        # Windows
```

## 3. Install dependencies
```bash
pip install -r requirements.txt
```

## Environment Variables
Create a .env file in the root folder with:
```bash
GEMINI_API_KEY=AIzaSyC-your-actual-api-key-here-dont-share-this 
DB_PATH=study.db
```

## Important:
Do not commit your actual key.
Add .env to .gitignore.
Use .env.example for sharing.

## Usage
Import your study materials:
```bash
python app.py import [file_path]
```
Turn them into knowledge points:
```bash
python app.py summarize
```

(Optional) If you want to see what knowledge points are summarized:
```bash
sqlite3 study.db
select * from knowledge_points;
```
Generate quiz questions:
```bash
python app.py quiz (optional: --kp-id [knowledge point id] --num [the number of questions you want Gemini to generate] )
```
Review your previous mistakes and identify the original source files where these topics are covered：
```bash
python app.py report
```

## (Add-on) MCP
Add procrastinator to your MCP server：
```bash
gemini mcp add procrastinator "mcp_server.py"
```

## Workflow Example
1. Place your lecture notes or text files into test_data/
2. Import files (parser.py) → parse and chunk long files for further review.
3. Run summarization (kp_extractor.py) → Gemini condenses your notes into structured knowledge points.
4. Generate quizzes (quizzer.py) → Gemini generates practice questions and grades your quiz answers.
5. View reports in reports (report.py) → progress and insights are saved locally.
6. (Optional) Add our app to your MCP server.

## 📂 Project Structure
```markdown
study_partner/
│── app.py # Main entry point (Gemini + workflow integration)
│── db.py # Database setup
│── db_checker.py # DB verification helpers
│── kp_extractor.py # Extracts key points from study materials
│── llm.py # function hub
│── mcp_server.py # MCP modules Intergration
│── parser.py # User subject definitions
│── quizzer.py # Generates quizzes from extracted notes
│── report.py # Creates progress reports
│── requirements.txt # Dependencies
│── README.md # Documentation
│
├── reports/ # Auto-generated reports
├── test_data/ # Example input study files
└── pycache/ # Compiled Python files
```


## Where Gemini CLI is Used
1. llm.py: Summarization of notes via Gemini CLI.
2. app.py: End-to-end pipeline orchestration using Gemini.
3. quizzer.py + report.py: Chain Gemini outputs into actionable quizzes/reports.
4. mcp_server.py: Manages and integrates MCP modules, acting as a server to coordinate data flow between components.
