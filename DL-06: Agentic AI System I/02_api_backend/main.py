### main.py - 02 API / Backend (the only gateway between the web app and the AI system)
### Phase 1 modular monolith: stages 02-07 run in one process as function calls
### Flow: Web App → 02 → 03 router → 04 engines (→ 05) → 06 generation → 07 format/persist → Web App
### Run: 09_backend/run_backend.bat, or here: python -m uvicorn main:app --port 8000

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "09_backend"))
import setup_path  ### add folders 02-09 to sys.path (must come first)
import asyncio
import io
import json
import time
import uuid
from collections import defaultdict

from fastapi import FastAPI, Request, HTTPException, BackgroundTasks, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, PlainTextResponse

import config
import engines
import generation
import monitoring
import response_log
import router_agent
from retrieval import get_retriever
from schemas import ChatRequest, FeedbackRequest

monitoring.setup_logging()
app = FastAPI(title="UniRAG Assistant API")
app.add_middleware(CORSMiddleware, allow_origins=config.CORS_ALLOWED_ORIGINS,
                   allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


@app.on_event("startup")
def startup():
    config.LOG_DATA_DIR.mkdir(exist_ok=True)
    response_log.init_db()
    response_log.purge_old_data()
    ### warm-up: load embedder, reranker and router model before the first question
    get_retriever().search("ลงทะเบียน", {"role": "student"})
    router_agent.decide("ลงทะเบียนเรียนได้กี่หน่วยกิต", [])


@app.middleware("http")
async def count_requests(request: Request, call_next):
    response = await call_next(request)
    monitoring.record_request(request.url.path.split("/sessions/")[0], response.status_code)
    return response


### ---------- Authentication + rate limit ----------
VALID_ROLES = {"student", "staff", "admin"}


def get_user(request: Request):
    ### AUTH_ENABLED=false (local): demo user, role can be set with the X-User-Role header
    if not config.AUTH_ENABLED:
        role = request.headers.get("X-User-Role", "student")
        if role not in VALID_ROLES:
            role = "student"
        return {"user_id": f"demo-{role}", "role": role, "faculty": "engineering"}
    import jwt
    token = request.cookies.get("access_token") or \
        request.headers.get("Authorization", "").replace("Bearer ", "")
    try:
        data = jwt.decode(token, config.JWT_SECRET_KEY, algorithms=[config.JWT_ALGORITHM])
    except Exception:
        raise HTTPException(401, "invalid or missing token")
    if not data.get("sub"):
        raise HTTPException(401, "token has no user id (sub)")
    role = data.get("role", "student")
    return {"user_id": data["sub"], "role": role if role in VALID_ROLES else "student",
            "faculty": data.get("faculty", "all")}


_calls = defaultdict(list)


def check_rate_limit(user=Depends(get_user)):
    now = time.time()
    _calls[user["user_id"]] = [t for t in _calls[user["user_id"]] if now - t < 60]
    if len(_calls[user["user_id"]]) >= config.RATE_LIMIT_PER_MINUTE:
        raise HTTPException(429, "rate limit exceeded, try again in a minute")
    _calls[user["user_id"]].append(now)
    return user


### ---------- main pipeline ----------
def answer_question(req: ChatRequest, user, background: BackgroundTasks):
    started = time.time()
    trace_id = uuid.uuid4().hex
    session_id = req.session_id or str(uuid.uuid4())
    if req.session_id:
        owner = response_log.session_owner(req.session_id)
        if owner and owner != user["user_id"]:
            raise HTTPException(403, "not your session")

    ### "#degraded" simulates a vector DB outage (for testing)
    message = req.message.strip()
    force_degraded = "#degraded" in message
    message = message.replace("#degraded", "").strip()

    ### follow-up: load history from 07 and pass it to the router (only here)
    history = router_agent.trim_history(response_log.get_history(session_id))
    file_text = "\n".join(t for t in (response_log.get_upload_text(user["user_id"], f)
                                      for f in req.attachments) if t)

    decision = router_agent.decide(message, history, req.locale)
    results, degraded = engines.run_engines(decision, user, req.method, req.top_k, force_degraded)
    draft = generation.generate(message, decision, results, history, file_text or None)

    latency = int((time.time() - started) * 1000)
    response = response_log.format_response(draft, session_id, trace_id, latency, degraded)
    response_log.remember(session_id, message, response)
    background.add_task(response_log.save_turn, user["user_id"], session_id, message,
                        response, decision)
    return response


@app.post("/api/chat")
def chat(req: ChatRequest, background: BackgroundTasks, user=Depends(check_rate_limit)):
    return answer_question(req, user, background)


@app.post("/api/chat/stream")
async def chat_stream(req: ChatRequest, background: BackgroundTasks,
                      user=Depends(check_rate_limit)):
    ### SSE: "delta" = text piece, "done" = full [C1] response
    response = await asyncio.to_thread(answer_question, req, user, background)

    async def events():
        text = response.answer
        for i in range(0, len(text), 6):
            yield f"event: delta\ndata: {json.dumps({'text': text[i:i + 6]}, ensure_ascii=False)}\n\n"
            await asyncio.sleep(0.01)
        yield f"event: done\ndata: {response.model_dump_json()}\n\n"

    return StreamingResponse(events(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache"})


### ---------- upload ----------
MAGIC = {b"%PDF": "application/pdf", b"\x89PNG": "image/png", b"\xff\xd8\xff": "image/jpeg",
         b"PK\x03\x04": "docx"}


def extract_text(data, kind):
    if kind == "application/pdf":
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(data))
        if reader.is_encrypted:
            raise HTTPException(400, "encrypted PDF is not allowed")
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    if kind == "docx":
        import docx
        return "\n".join(p.text for p in docx.Document(io.BytesIO(data)).paragraphs)
    ### images: Thai+English OCR (needs Tesseract and pytesseract)
    try:
        import pytesseract
        from PIL import Image
        return pytesseract.image_to_string(Image.open(io.BytesIO(data)), lang="tha+eng")
    except ImportError:
        raise HTTPException(400, "OCR is not installed on this server (pytesseract)")


@app.post("/api/upload")
async def upload(file: UploadFile = File(...), user=Depends(check_rate_limit)):
    data = await file.read()
    if len(data) > config.MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(413, f"file larger than {config.MAX_UPLOAD_MB} MB")
    ### check file type by magic bytes, not by extension
    kind = next((k for sig, k in MAGIC.items() if data.startswith(sig)), None)
    if kind is None:
        raise HTTPException(415, "only PDF, PNG, JPEG and DOCX files are allowed")
    ### broken or fake file (e.g. a zip that is not docx) -> 400, not 500
    try:
        text = extract_text(data, kind)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(400, "could not read this file (damaged or wrong format)")
    file_id = response_log.save_upload(user["user_id"], file.filename, text)
    return {"file_id": file_id, "filename": file.filename, "chars": len(text), "untrusted": True}


### ---------- history / feedback / status ----------
@app.get("/api/history")
def history(user=Depends(get_user)):
    return response_log.list_sessions(user["user_id"])


@app.get("/api/sessions/{session_id}")
def session(session_id: str, user=Depends(get_user)):
    owner = response_log.session_owner(session_id)
    if owner is None:
        raise HTTPException(404, "session not found")
    if owner != user["user_id"]:
        raise HTTPException(403, "not your session")
    return response_log.get_session(session_id)


@app.delete("/api/history")
def delete_history(user=Depends(get_user)):
    return {"deleted_sessions": response_log.delete_user_history(user["user_id"])}


@app.post("/api/feedback")
def feedback(req: FeedbackRequest, user=Depends(check_rate_limit)):
    info = response_log.message_info(req.message_id)
    if info is None:
        raise HTTPException(404, "message not found")
    if info["user_id"] != user["user_id"]:
        raise HTTPException(403, "not your message")
    response_log.add_feedback(user["user_id"], req.message_id, req.rating, req.comment, info)
    return {"ok": True}


@app.get("/api/status")
def status():
    documents, updated = get_retriever().documents_info()
    return {"mode": "live", "documents": documents, "kb_updated": updated}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/metrics", response_class=PlainTextResponse)
def metrics():
    return monitoring.metrics_text()
