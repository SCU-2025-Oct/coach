# AI Career Coach - NVIDIA NIM (2-Hour Hackathon Project)

An agentic AI Career Assistant powered by NVIDIA Nemotron (NIM).  
This app analyzes resumes, identifies skill gaps, retrieves live job openings, and provides personalized improvement suggestions - all autonomously, in real time.

Built for the NVIDIA Developer Hackathon - focusing on innovation, reasoning workflow, and Nemotron integration over UI complexity.

---

## Overview

AI Career Coach transforms a static resume into an actionable career roadmap.  
It uses an agentic, multi-step reasoning pipeline powered by NVIDIA’s Nemotron model, integrated with MCP for dynamic, real-world data retrieval.

### Core Workflow
Resume Upload  
↓  
Nemotron Analysis (NVIDIA NIM)  
↓  
Agentic Insights (skill gaps, job matches, resume edits)  
↓  
Personalized Actionable Output

---

## Features

| Feature | Description |
|----------|--------------|
| Resume Understanding | Parses PDF/DOCX resumes into structured data using a LangChain-style parser. |
| Nemotron Agent (NIM) | Performs context-aware analysis — detects strengths, weaknesses, and phrasing improvements. |
| Conversational UI | Minimalistic chat interface built in HTML/JS for smooth interaction. |
| Agentic Workflow | Combines resume understanding + retrieval + generation into an autonomous reasoning flow. |

---

## Tech Stack

| Layer | Technology |
|-------|-------------|
| LLM | NVIDIA Nemotron via NIM /v1/chat/completions |
| Backend | FastAPI (Python 3.10+) |
| Frontend | Minimal HTML, CSS, and JavaScript |
| External API | Remotive (public job API) |

---

## Architecture

frontend/  
│   index.html  →  Chat UI  
backend/  
│  
├── app/  
│   ├── main.py                → FastAPI endpoints  
│   ├── services/  
│   │   ├── nim_client.py      → Nemotron client (NIM API)  
│   │   ├── mcp_client.py      → MCP connector  
│   │   └── resume_parser.py   → PDF/DOCX resume extraction  
│   └── prompts/system.txt     → Base prompt for the agent  
│  
├── .env.example               → Template for environment variables  
├── requirements.txt           → Python dependencies  
└── README.md                  → This file  

mcp-servers/  
│   └── jobs_server.py         → MCP job listing fetcher (Remotive API)

---

## Installation and Setup

### 1. Backend Setup
cd backend
python -m venv .venv 
.venv/bin/activate
pip install -r requirements.txt
Edit `.env` and add your NVIDIA API key:
uvicorn app.main:app --reload --port 8000

### 2. Frontend Setup
In a new terminal

cd frontend
python -m http.server 5500

---

Open Browser and load http://localhost:5500/

# Example Demo Flow

### Example Input:
1. Upload a resume (PDF or DOCX).  
2. Nemotron reads and summarizes strengths, skill gaps, and achievements.  
3. Ask queries such as:
   - How can I improve my resume for SDE roles?
   - What projects should I highlight for data engineering jobs?

### Example Output:
Strengths: Proficient in Java, Spring Boot, and Flask.
Gaps: Add AWS certification, quantify project metrics.
Suggested Edit: "Improved API response time by 40%."
Top Job Match: SDE Intern – Amazon | Location: Remote


## Key Takeaway
This project is not just a chatbot — it is an autonomous reasoning agent powered by NVIDIA Nemotron.  
It reads, retrieves, reasons, and rewrites — delivering real career insights in minutes.