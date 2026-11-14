### response_log.py - 07 response / log (used by 02)
### Builds the [C1] response, saves turns in a background task, stores feedback,
### and returns history to 02. It never talks to the web app or router directly.
### SQLite for local runs (Phase 1 plan: PostgreSQL + Redis)

import json
import logging
import sqlite3
import uuid
from datetime import datetime, timedelta, timezone

import config
import monitoring
from schemas import ChatResponse

log = logging.getLogger("response_log")
BANGKOK = timezone(timedelta(hours=7))

### short-term history in memory (stands in for Redis locally)
_recent = {}


def now():
    return datetime.now(BANGKOK).isoformat(timespec="seconds")


def db():
    conn = sqlite3.connect(config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    ### schema from 02_api_backend/03_process.txt
    with db() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, email TEXT, name TEXT, role TEXT,
            faculty TEXT, created_at TEXT);
        CREATE TABLE IF NOT EXISTS conversations (session_id TEXT PRIMARY KEY, user_id TEXT,
            title TEXT, created_at TEXT, updated_at TEXT);
        CREATE TABLE IF NOT EXISTS messages (id TEXT PRIMARY KEY, session_id TEXT, role TEXT,
            content TEXT, sources_json TEXT, response_json TEXT, response_type TEXT,
            engine_used TEXT, confidence REAL, latency_ms INTEGER, trace_id TEXT, created_at TEXT);
        CREATE TABLE IF NOT EXISTS uploaded_files (id TEXT PRIMARY KEY, user_id TEXT,
            filename TEXT, extracted_text TEXT, uploaded_at TEXT);
        CREATE TABLE IF NOT EXISTS feedback (id TEXT PRIMARY KEY, message_id TEXT, user_id TEXT,
            rating TEXT, comment TEXT, created_at TEXT);
        """)


def format_response(draft, session_id, trace_id, latency_ms, degraded):
    ### build the Unified Response Schema [C1]
    sources = draft["sources"]
    return ChatResponse(
        message_id=str(uuid.uuid4()),
        session_id=session_id,
        response_type=draft["response_type"],
        answer=draft["answer"],
        clarify_options=draft["clarify_options"] if draft["response_type"] == "clarify" else [],
        sources=sources,
        engine_used=draft["engine_used"],
        confidence=round(float(draft["confidence"]), 2),
        data_freshness=max((s["published_at"] for s in sources), default=None),
        degraded_services=sorted(set(degraded + draft["degraded"])),
        latency_ms=latency_ms,
        trace_id=trace_id,
        timestamp=now(),
    )


def remember(session_id, message, response):
    ### update short-term history now (the next follow-up won't wait for the DB)
    turns = _recent.setdefault(session_id, [])
    turns.append({"role": "user", "content": message})
    turns.append({"role": "assistant", "content": response.answer})
    _recent[session_id] = turns[-config.HISTORY_TURNS * 2:]


def save_turn(user_id, session_id, message, response, decision):
    ### runs as a background task, so it doesn't slow the answer
    try:
        ts = now()
        with db() as conn:
            conn.execute("""INSERT INTO conversations VALUES (?,?,?,?,?)
                ON CONFLICT(session_id) DO UPDATE SET updated_at=excluded.updated_at""",
                         (session_id, user_id, message[:60], ts, ts))
            conn.execute("INSERT INTO messages (id, session_id, role, content, created_at) "
                         "VALUES (?,?,?,?,?)", (str(uuid.uuid4()), session_id, "user", message, ts))
            conn.execute("INSERT INTO messages VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", (
                response.message_id, session_id, "assistant", response.answer,
                json.dumps([s.model_dump() for s in response.sources], ensure_ascii=False),
                response.model_dump_json(), response.response_type, response.engine_used,
                response.confidence, response.latency_ms, response.trace_id, ts))
        monitoring.record_turn(decision, response)
    except Exception as e:
        log.error("save_turn failed: %s", e)


def get_history(session_id, n=None):
    ### memory first, then the database
    n = n or config.HISTORY_TURNS
    if session_id in _recent:
        return _recent[session_id][-n * 2:]
    with db() as conn:
        rows = conn.execute("SELECT role, content FROM messages WHERE session_id=? "
                            "ORDER BY created_at, role DESC", (session_id,)).fetchall()
    turns = [{"role": r["role"], "content": r["content"]} for r in rows][-n * 2:]
    if turns:
        _recent[session_id] = turns
    return turns


def session_owner(session_id):
    with db() as conn:
        row = conn.execute("SELECT user_id FROM conversations WHERE session_id=?",
                           (session_id,)).fetchone()
    return row["user_id"] if row else None


def list_sessions(user_id):
    with db() as conn:
        rows = conn.execute("""SELECT c.session_id, c.title, c.updated_at, COUNT(m.id) AS n
            FROM conversations c LEFT JOIN messages m ON m.session_id = c.session_id
            WHERE c.user_id=? GROUP BY c.session_id ORDER BY c.updated_at DESC""",
                            (user_id,)).fetchall()
    return [{"session_id": r["session_id"], "title": r["title"], "updated_at": r["updated_at"],
             "message_count": r["n"]} for r in rows]


def get_session(session_id):
    with db() as conn:
        rows = conn.execute("SELECT role, content, response_json, created_at FROM messages "
                            "WHERE session_id=? ORDER BY created_at, role DESC",
                            (session_id,)).fetchall()
    turns = []
    for r in rows:
        turn = {"role": r["role"], "content": r["content"], "created_at": r["created_at"]}
        if r["response_json"]:
            turn["response"] = json.loads(r["response_json"])
        turns.append(turn)
    return {"session_id": session_id, "turns": turns}


def message_info(message_id):
    with db() as conn:
        row = conn.execute("""SELECT m.trace_id, m.engine_used, c.user_id FROM messages m
            JOIN conversations c ON c.session_id = m.session_id WHERE m.id=?""",
                           (message_id,)).fetchone()
    return dict(row) if row else None


def add_feedback(user_id, message_id, rating, comment, info):
    with db() as conn:
        conn.execute("DELETE FROM feedback WHERE message_id=? AND user_id=?", (message_id, user_id))
        conn.execute("INSERT INTO feedback VALUES (?,?,?,?,?,?)",
                     (str(uuid.uuid4()), message_id, user_id, rating, comment, now()))
    monitoring.record_feedback(info["engine_used"], rating)
    ### thumbs-down -> notify the team (message_id + trace_id only, no personal data)
    if rating == "down" and config.FEEDBACK_WEBHOOK_URL:
        try:
            import httpx
            httpx.post(config.FEEDBACK_WEBHOOK_URL, timeout=5,
                       json={"message_id": message_id, "trace_id": info["trace_id"]})
        except Exception as e:
            log.warning("feedback webhook failed: %s", e)


def save_upload(user_id, filename, text):
    file_id = str(uuid.uuid4())
    with db() as conn:
        conn.execute("INSERT INTO uploaded_files VALUES (?,?,?,?,?)",
                     (file_id, user_id, filename, text, now()))
    return file_id


def get_upload_text(user_id, file_id):
    with db() as conn:
        row = conn.execute("SELECT extracted_text FROM uploaded_files WHERE id=? AND user_id=?",
                           (file_id, user_id)).fetchone()
    return row["extracted_text"] if row else None


def purge_old_data():
    ### retention: chats 180 days, uploads 30 days
    conv_cut = (datetime.now(BANGKOK) - timedelta(days=config.RETENTION_DAYS_CONVERSATION)).isoformat()
    file_cut = (datetime.now(BANGKOK) - timedelta(days=config.RETENTION_DAYS_UPLOADS)).isoformat()
    with db() as conn:
        conn.execute("DELETE FROM messages WHERE created_at < ?", (conv_cut,))
        conn.execute("DELETE FROM conversations WHERE updated_at < ?", (conv_cut,))
        conn.execute("DELETE FROM uploaded_files WHERE uploaded_at < ?", (file_cut,))


def delete_user_history(user_id):
    ### PDPA right to erasure
    with db() as conn:
        ids = [r[0] for r in conn.execute("SELECT session_id FROM conversations WHERE user_id=?",
                                          (user_id,))]
        for sid in ids:
            conn.execute("DELETE FROM messages WHERE session_id=?", (sid,))
            _recent.pop(sid, None)
        conn.execute("DELETE FROM conversations WHERE user_id=?", (user_id,))
        conn.execute("DELETE FROM uploaded_files WHERE user_id=?", (user_id,))
    return len(ids)
