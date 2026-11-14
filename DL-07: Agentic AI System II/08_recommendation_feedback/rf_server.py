# rf_server.py
# Module 08: Recommendation & Feedback — runs on port 8006
#   - build the final recommendation (recommendation.py)
#   - receive feedback and send "unsafe" reports to a human review queue
#   - area alerts (subscriptions) + an alert watcher that checks new events every 5 minutes
#
# Run:  python 08_recommendation_feedback/rf_server.py

import asyncio
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path += [HERE, os.path.join(ROOT, "09_backend", "shared")]

from typing import Optional               # noqa: E402

from pydantic import BaseModel, Field     # noqa: E402

import recommendation as rec              # noqa: E402
import service_client as svc              # noqa: E402
import storage                            # noqa: E402
from common import create_app, fail       # noqa: E402

app = create_app("ProJ-7 Recommendation & Feedback (Module 08)", "recommendation_feedback")
ALERT_REFRESH_SECONDS = int(os.getenv("ALERT_REFRESH_SECONDS", "300"))
storage.init_db()


class FeedbackIn(BaseModel):
    request_id: str
    category: str = Field(pattern="^(HELPFUL|INCORRECT|STALE|UNSAFE|ROUTE_ISSUE|SOURCE_ISSUE)$")
    comment: Optional[str] = Field(default=None, max_length=1000)


class SubscriptionIn(BaseModel):
    name: str = Field(default="พื้นที่ของฉัน", max_length=100)
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)
    radius_km: float = Field(default=100, ge=5, le=1000)
    hazards: list[str] = []            # empty = all hazards
    min_severity: int = Field(default=3, ge=1, le=4)
    lang: str = "th"


# ---------------- Build recommendations ----------------
@app.post("/recommendation/trip")
async def recommendation_trip(data: dict):
    for key in ("decision", "explanation", "routes", "lang", "departure"):
        if key not in data:
            fail(422, "VALIDATION_FAILED", f"ขาดข้อมูล {key}")
    return rec.build_trip(data)


@app.post("/recommendation/hazard")
async def recommendation_hazard(data: dict):
    return rec.build_hazard_info(data)


@app.post("/recommendation/emergency")
async def recommendation_emergency(data: dict):
    return rec.build_emergency(data)


@app.post("/recommendation/simple")
async def recommendation_simple(data: dict):
    """Short reply, e.g. a clarification question (CLARIFICATION)."""
    resp = rec.empty_response(data.get("intent"), data.get("response_type", "CLARIFICATION"), data.get("lang", "th"))
    resp["summary"] = data.get("summary", "")
    resp["limitations"] = data.get("limitations", [])
    return resp


# ---------------- feedback ----------------
@app.post("/feedback")
async def feedback(req: FeedbackIn):
    needs_review = storage.add_feedback(req.request_id, req.category, req.comment)
    if needs_review:
        print(f"[safety-review] request {req.request_id} reported as {req.category}")
    return {"ok": True, "sent_to_review": bool(needs_review)}


@app.get("/feedback/summary")
async def feedback_summary():
    return storage.feedback_summary()


# ---------------- Area alerts ----------------
@app.post("/subscriptions")
async def add_subscription(req: SubscriptionIn):
    sub_id = storage.add_subscription(req.name, req.lat, req.lon, req.radius_km, req.hazards, req.min_severity, req.lang)
    asyncio.create_task(check_alerts_once())   # check once right away
    return {"id": sub_id}


@app.get("/subscriptions")
async def list_subscriptions():
    return storage.list_subscriptions()


@app.delete("/subscriptions/{sub_id}")
async def delete_subscription(sub_id: str):
    storage.delete_subscription(sub_id)
    return {"ok": True}


@app.get("/notifications")
async def notifications(limit: int = 50):
    return storage.list_notifications(min(limit, 200))


@app.get("/alerts/latest")
async def latest_alerts():
    """Warning-level (or higher) events in the last 24 h, most severe first, then newest first."""
    data = await svc.get("di", "/hazards/events", {"window": "24h"}, timeout=90)
    items = []
    for e in data["earthquakes"] + data["events"]:
        sev = rec.event_severity(e)
        if sev >= 3:
            items.append({**e, "severity": sev})
    items.sort(key=lambda x: str(x.get("time")), reverse=True)
    items.sort(key=lambda x: -x["severity"])
    return {"alerts": items[:50], "degraded": data["degraded"]}


def distance_km(lat1, lon1, lat2, lon2):
    r = 6371
    dlat, dlon = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


async def check_alerts_once():
    """Check for new events in subscribed areas (no duplicates, but always notify when severity increases)."""
    subs = storage.list_subscriptions()
    if not subs:
        return 0
    try:
        data = await svc.get("di", "/hazards/events", {"window": "24h"})
    except svc.ServiceError as e:
        print("[alert-watcher] ดึงเหตุการณ์ไม่ได้:", e)
        return 0
    events = data["earthquakes"] + data["events"]
    created = 0
    for sub in subs:
        for e in events:
            if sub["hazards"] and e["hazard"] not in sub["hazards"]:
                continue
            sev = rec.event_severity(e)
            if sev < sub["min_severity"]:
                continue
            d = distance_km(sub["lat"], sub["lon"], e["lat"], e["lon"])
            if d > sub["radius_km"]:
                continue
            if sev > storage.last_severity(sub["id"], e["id"]):
                storage.add_notification(sub["id"], e, sev, d)
                created += 1
                print(f"[alert-watcher] แจ้งเตือน '{sub['name']}': {e.get('title')} ({d:.0f} km, ระดับ {sev})")
    return created


async def alert_watcher_loop():
    await asyncio.sleep(10)
    while True:
        try:
            await check_alerts_once()
            storage.delete_old_feedback()
        except Exception as e:   # the loop must never die
            print("[alert-watcher] error:", e)
        await asyncio.sleep(ALERT_REFRESH_SECONDS)


@app.on_event("startup")
async def start_watcher():
    asyncio.create_task(alert_watcher_loop())


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", "8006")))
