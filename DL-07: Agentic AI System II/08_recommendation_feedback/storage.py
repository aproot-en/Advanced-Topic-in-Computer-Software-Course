# storage.py
# Module 08 storage using SQLite (built into Python, nothing to install)
#   feedback       user feedback on recommendations (no personal data)
#   subscriptions  areas the user wants alerts for
#   notifications  notifications already created (prevents duplicates)

import os
import sqlite3
import uuid
from datetime import datetime, timedelta, timezone

DB_PATH = os.getenv("RF_DB_PATH", os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "app.db"))
FEEDBACK_RETENTION_DAYS = int(os.getenv("FEEDBACK_RETENTION_DAYS", "180"))


def connect():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def run_sql(sql, params=(), fetch=False):
    """Run one SQL statement, save it, and always close the connection."""
    conn = connect()
    try:
        cursor = conn.execute(sql, params)     # always run the statement
        rows = None
        if fetch:
            rows = cursor.fetchall()
        conn.commit()
        return rows
    finally:
        conn.close()


def init_db():
    conn = connect()
    try:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS feedback (
            id TEXT PRIMARY KEY, request_id TEXT, category TEXT, comment TEXT,
            needs_review INTEGER DEFAULT 0, created_at TEXT);
        CREATE TABLE IF NOT EXISTS subscriptions (
            id TEXT PRIMARY KEY, name TEXT, lat REAL, lon REAL, radius_km REAL,
            hazards TEXT, min_severity INTEGER, lang TEXT, created_at TEXT);
        CREATE TABLE IF NOT EXISTS notifications (
            id TEXT PRIMARY KEY, subscription_id TEXT, event_id TEXT, severity INTEGER,
            hazard TEXT, title TEXT, distance_km REAL, lat REAL, lon REAL, url TEXT, created_at TEXT);
        """)
        conn.commit()
    finally:
        conn.close()


def now():
    return datetime.now(timezone.utc).isoformat()


# ---------------- feedback ----------------
def add_feedback(request_id, category, comment):
    # "unsafe" or "incorrect" reports must be checked by a person (safety review queue)
    needs_review = 1 if category in ("UNSAFE", "INCORRECT") else 0
    run_sql("INSERT INTO feedback VALUES (?,?,?,?,?,?)",
            (str(uuid.uuid4()), request_id, category, comment, needs_review, now()))
    return needs_review


def feedback_summary():
    rows = run_sql("SELECT category, COUNT(*) AS n FROM feedback GROUP BY category", fetch=True)
    review = run_sql("SELECT request_id, category, comment, created_at FROM feedback "
                     "WHERE needs_review = 1 ORDER BY created_at DESC LIMIT 20", fetch=True)
    counts = {}
    for r in rows:
        counts[r["category"]] = r["n"]
    return {"counts": counts, "review_queue": [dict(r) for r in review]}


def delete_old_feedback():
    cutoff = (datetime.now(timezone.utc) - timedelta(days=FEEDBACK_RETENTION_DAYS)).isoformat()
    run_sql("DELETE FROM feedback WHERE created_at < ?", (cutoff,))


# ---------------- subscriptions ----------------
def add_subscription(name, lat, lon, radius_km, hazards, min_severity, lang):
    sub_id = str(uuid.uuid4())
    run_sql("INSERT INTO subscriptions VALUES (?,?,?,?,?,?,?,?,?)",
            (sub_id, name, round(lat, 3), round(lon, 3), radius_km, ",".join(hazards), min_severity, lang, now()))
    return sub_id


def list_subscriptions():
    rows = run_sql("SELECT * FROM subscriptions ORDER BY created_at DESC", fetch=True)
    result = []
    for r in rows:
        item = dict(r)
        item["hazards"] = [h for h in r["hazards"].split(",") if h]   # stored as "RAIN,FLOOD"
        result.append(item)
    return result


def delete_subscription(sub_id):
    run_sql("DELETE FROM subscriptions WHERE id = ?", (sub_id,))
    run_sql("DELETE FROM notifications WHERE subscription_id = ?", (sub_id,))


# ---------------- notifications ----------------
def last_severity(sub_id, event_id):
    rows = run_sql("SELECT MAX(severity) AS s FROM notifications WHERE subscription_id=? AND event_id=?",
                   (sub_id, event_id), fetch=True)
    if rows and rows[0]["s"] is not None:
        return rows[0]["s"]
    return -1


def add_notification(sub_id, event, severity, distance):
    run_sql("INSERT INTO notifications VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (str(uuid.uuid4()), sub_id, event["id"], severity, event["hazard"], event.get("title"),
             round(distance, 1), event["lat"], event["lon"], event.get("url"), now()))


def list_notifications(limit=50):
    rows = run_sql("""SELECT n.*, s.name AS area_name FROM notifications n
                      LEFT JOIN subscriptions s ON s.id = n.subscription_id
                      ORDER BY n.created_at DESC LIMIT ?""", (limit,), fetch=True)
    return [dict(r) for r in rows]
