import os
from pathlib import Path
from typing import List, Optional, Dict

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .services import nim_client
from .services.resume_parser import extract_text
from .services.mcp_client import JobsMCPClient, jobs_client

ROOT = Path(__file__).resolve().parents[2]
MCP_SERVER_PATH = ROOT / "mcp-servers" / "jobs_server.py"

app = FastAPI(title="AI Career Coach (NIM + MCP)")

# CORS
allow_origins = os.getenv("ALLOW_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    attach_jobs: bool = False
    job_query: Optional[str] = None
    location: Optional[str] = ""
    resume_text: Optional[str] = None

@app.on_event("startup")
async def startup_event():
    global jobs_client
    jobs_client = JobsMCPClient(str(MCP_SERVER_PATH))

@app.on_event("shutdown")
async def shutdown_event():
    global jobs_client
    if jobs_client:
        await jobs_client.aclose()

@app.get("/health")
async def health():
    return {"ok": True}

@app.post("/api/resume")
async def upload_resume(file: UploadFile = File(...)):
    tmp_dir = ROOT / "tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    dest = tmp_dir / file.filename
    content = await file.read()
    dest.write_bytes(content)

    try:
        text, mime = extract_text(str(dest))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    system_path = ROOT / "backend" / "app" / "prompts" / "system.txt"
    system_prompt = system_path.read_text(encoding="utf-8")

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Extract and critique this resume. Return JSON with keys: summary, strengths[], gaps[], edits[], ats_tips[], extracted_skills[], extracted_roles[]\n\nRESUME:\n{text}"},
    ]

    try:
        content = await nim_client.chat_completion(messages, max_tokens=900, temperature=0.1)
        return JSONResponse({"resume_text": text, "analysis": content})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"NIM error: {e}")

@app.post("/api/chat")
async def chat(req: ChatRequest):
    system_path = ROOT / "backend" / "app" / "prompts" / "system.txt"
    system_prompt = system_path.read_text(encoding="utf-8")

    messages: List[Dict[str, str]] = [{"role":"system", "content": system_prompt}]
    for m in req.messages:
        messages.append({"role": m.role, "content": m.content})

    job_blob = None
    if req.attach_jobs and req.job_query:
        try:
            global jobs_client
            job_blob = await jobs_client.search_jobs(req.job_query, req.location or "", limit=8)
            messages.append({
                "role": "system",
                "content": f"Context: Here are live job leads based on query='{req.job_query}', location='{req.location}'. JSON follows:\n{job_blob}"
            })
        except Exception as e:
            messages.append({"role":"system","content":f"Context: jobs unavailable ({e}). Continue without."})

    if req.resume_text:
        messages.append({"role":"system","content":f"Context: Candidate resume text follows:\n{req.resume_text}"})

    try:
        content = await nim_client.chat_completion(messages, max_tokens=800, temperature=0.2)
        return JSONResponse({"reply": content, "jobs": job_blob})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"NIM error: {e}")
