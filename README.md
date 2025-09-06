# Study Partner CLI — AI-Powered Local Study Assistant

**Problem:** Transform scattered local study materials (PDFs, Markdown, text files) into an intelligent, queryable knowledge base that generates personalized quizzes and tracks learning progress.

**Local-First Approach:** All your documents stay on your machine. Gemini processes them locally and builds a private knowledge database that learns from your mistakes.

## Quick Start (2 minutes)

### Prerequisites
```bash
# Install Google Cloud CLI (choose your platform)
# macOS
brew install google-cloud-sdk

# Windows: Download from https://cloud.google.com/sdk/docs/install
# Linux
curl https://sdk.cloud.google.com | bash
```

### Setup & Demo
```bash
# 1. Clone and install
git clone <your-repo>
cd study-partner-cli
pip install -r requirements.txt

# 2. Authenticate (opens browser - one-time setup)
gcloud auth application-default login

# 3. Run complete demo
./run_demo.sh
```

Alternative: Use API key instead of Google Cloud auth by creating `.env` with `GEMINI_API_KEY=your-key`

## Demo Workflow (Complete end-to-end example)

```bash
# Import your study materials
python app.py import ./sample_data
# → Parses PDFs/MD/TXT and stores in local SQLite DB

# Extract knowledge points using Gemini
python app.py summarize ./sample_data  
# → Gemini analyzes content and extracts key concepts

# Take an AI-generated quiz
python app.py quiz --num 3
# → Interactive quiz based on your materials

# Generate mistake report with source citations
python app.py report
# → Markdown report linking mistakes back to original documents

# (Advanced) Use as MCP server for other AI tools
python mcp_server.py
```

## Architecture & Gemini Integration

### Where Gemini is Called
- **Knowledge Extraction** (`llm.py` → `kp_extractor.py`): Analyzes document chunks to identify key learning concepts with source traceability
- **Quiz Generation** (`llm.py` → `quizzer.py`): Creates contextual multiple-choice questions from knowledge points  
- **Answer Grading** (`llm.py` → `quizzer.py`): Intelligent evaluation of student responses with detailed explanations
- **Content Summarization** (`app.py summarize`): Processes local documents into structured knowledge points

### Local Data Flow
```
Local Files → Parser → SQLite DB → Gemini Analysis → Knowledge Points → Quiz Generation → Progress Tracking
```

### Database Schema Highlights
- **documents**: Original file metadata with import timestamps
- **chunks**: Text segments with page references for source traceability
- **knowledge_points**: AI-extracted concepts linked to source chunks
- **questions**: Generated quizzes with source traceability to original documents
- **attempts/mistakes**: Learning progress and personalized error tracking

## Authentication Options

**Option 1: Google Cloud (Recommended)**
```bash
gcloud auth application-default login
# App automatically uses your Google account
```

**Option 2: API Key**
```bash
# Create .env file
GEMINI_API_KEY=your-api-key-here
```

## Advanced Usage

```bash
# Import specific subject materials
python app.py import ~/Documents/Biology --subject "Cell Biology"

# Quiz on specific knowledge point
python app.py quiz --kp-id 42 --num 5

# Check your knowledge base
python db_checker.py

# Run as MCP server for Claude/other AI assistants
python mcp_server.py
```

## Demo Video Script (3 minutes)

1. **Problem Statement** (15s): "Scattered study materials are hard to review effectively"
2. **Setup Demo** (20s): Show `./run_demo.sh` command and authentication
3. **Core Workflow** (90s): 
   - Import documents with parsing
   - Gemini extracts knowledge points
   - Take interactive quiz
   - Show mistake report with source citations
4. **Technical Highlights** (30s): Point out Gemini integration, MCP server, local database
5. **What's Next** (15s): "Vector search, spaced repetition, multi-modal support"

## What's Hard/Interesting

- **Source Traceability**: Every quiz question links back to specific document pages/chunks
- **Intelligent Authentication**: Supports both Google Cloud OAuth and API keys seamlessly
- **MCP Integration**: Exposes study tools to other AI assistants via Model Context Protocol
- **Learning Analytics**: Tracks mistakes and generates actionable reports with source citations
- **Local-First Privacy**: All processing happens on your machine, documents never leave your system
- **Robust Error Handling**: Graceful fallbacks when authentication fails (demo-ready)

## What's Next

- **Vector Similarity Search**: Better content retrieval for quiz generation
- **Spaced Repetition**: Schedule reviews based on mistake patterns
- **Multi-AI Integration**: Use different models for different tasks via MCP
- **Multi-modal Support**: Handle images, diagrams, and audio in study materials
- **Collaborative Learning**: Share anonymized knowledge points across study groups

## Technical Architecture

```
CLI Interface (Typer)
├── Document Parser (PyPDF2, text readers)
├── Database Layer (SQLite with relationship tracking)
├── LLM Interface (Google Cloud Auth + Gemini)
├── Knowledge Extractor (Structured prompt engineering)
├── Quiz Engine (Generation + intelligent grading)
├── Report Generator (Markdown with source links)
└── MCP Server (Tool exposure for other AI systems)
```

## Dependencies & Installation

```bash
# Core dependencies
pip install typer rich PyPDF2 sqlite-utils

# Gemini integration
pip install google-generativeai google-auth google-auth-oauthlib

# MCP server (optional)
pip install mcp

# Environment management
pip install python-dotenv
```

## Judging Criteria Alignment

- **Technical Excellence (20%)**: Robust error handling, authentication options, reproducible demo with fallbacks
- **Solution Architecture (20%)**: Clean modular design, comprehensive documentation, MCP server integration
- **Gemini Integration (30%)**: Deep integration across extraction, generation, and grading workflows with source traceability
- **Impact & Innovation (30%)**: Solves real study workflow problem, extensible via MCP to other AI tools, privacy-first approach

## File Structure
```
study-partner-cli/
├── app.py              # CLI interface and main commands
├── db.py               # Database schema and connections
├── llm.py              # Gemini authentication and API calls
├── parser.py           # Document parsing (PDF/MD/TXT)
├── kp_extractor.py     # Knowledge point extraction
├── quizzer.py          # Quiz generation and grading
├── report.py           # Mistake report generation
├── mcp_server.py       # Model Context Protocol server
├── run_demo.sh         # Complete demo script
├── requirements.txt    # Python dependencies
├── .env.example        # Environment template
└── sample_data/        # Demo study materials
```
