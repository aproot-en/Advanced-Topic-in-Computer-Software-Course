# api_server.py
# Module 02: API / Backend — runs on port 8000 (the only API the web page calls)
#   - map data -> Modules 04 / 05 / 06
#   - trip planning / chat -> Module 03 (Travel AI Agent)
#   - feedback / alerts -> Module 08
#
# Run:  python 02_api_/api_server.py

import asyncio
import os
import sys
import time
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path += [HERE, os.path.join(ROOT, "09_backend", "shared")]

from fastapi import Query, Request                              # noqa: E402
from fastapi.middleware.cors import CORSMiddleware              # noqa: E402
from fastapi.responses import JSONResponse                      # noqa: E402
from pydantic import BaseModel, Field                           # noqa: E402

import service_client as svc                                    # noqa: E402
from common import create_app                                   # noqa: E402
from schemas import ChatRequest, FeedbackRequest, TripRequest   # noqa: E402

app = create_app("ProJ-7 API / Backend (Module 02)", "api_backend")

# Allow the web page to call the API (add more origins in CORS_ORIGINS, comma-separated)
ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
app.add_middleware(CORSMiddleware, allow_origins=ORIGINS, allow_methods=["GET", "POST", "DELETE"], allow_headers=["*"])

# ---------------- Simple rate limit: 120 requests/minute per IP ----------------
request_log = {}


@app.middleware("http")
async def rate_limit(request: Request, call_next):
    ip = request.client.host if request.client else "unknown"
    now = time.time()
    history = [t for t in request_log.get(ip, []) if now - t < 60]
    if len(history) >= 120:
        return JSONResponse(status_code=429, headers={"Retry-After": "30"},
                            content={"error": {"code": "RATE_LIMITED", "message": "คำขอมากเกินไป กรุณารอสักครู่"}})
    history.append(now)
    request_log[ip] = history
    return await call_next(request)


@app.on_event("startup")
async def warm_up():
    """On start-up, prefetch hazard data so the web page loads faster."""
    async def warm():
        await asyncio.sleep(3)
        try:
            await svc.get("di", "/hazards/events", {"window": "7d"}, timeout=90)
        except svc.ServiceError:
            pass
    asyncio.create_task(warm())


# =====================================================================
# System status
# =====================================================================
@app.get("/api/health")
async def health():
    names = ["agent", "eds", "di", "rks", "dle", "rf"]
    status = await asyncio.gather(*(svc.is_up(n) for n in names))
    return {"status": "ok", "services": {n: ("up" if s else "down") for n, s in zip(names, status)},
            "time": datetime.now(timezone.utc).isoformat()}


@app.get("/api/providers/health")
async def providers_health():
    return await svc.get("eds", "/providers/health")


# =====================================================================
# Places
# =====================================================================
@app.get("/api/places/search")
async def places_search(q: str = Query(min_length=1, max_length=100), lang: str = "th"):
    return await svc.get("eds", "/places/search", {"q": q, "lang": lang})


@app.get("/api/places/reverse")
async def places_reverse(lat: float = Query(ge=-90, le=90), lon: float = Query(ge=-180, le=180), lang: str = "th"):
    return await svc.get("eds", "/places/reverse", {"lat": lat, "lon": lon, "lang": lang})


@app.get("/api/places/nearby")
async def places_nearby(lat: float = Query(ge=-90, le=90), lon: float = Query(ge=-180, le=180)):
    return await svc.get("eds", "/places/nearby", {"lat": lat, "lon": lon})


# =====================================================================
# Hazard and forecast data for the map
# =====================================================================
@app.get("/api/hazards/events")
async def hazard_events(window: str = "7d"):
    return await svc.get("di", "/hazards/events", {"window": window}, timeout=90)


@app.get("/api/alerts")
async def alerts():
    return await svc.get("rf", "/alerts/latest", timeout=90)


@app.get("/api/forecast/point")
async def forecast_point(lat: float = Query(ge=-90, le=90), lon: float = Query(ge=-180, le=180), lang: str = "th"):
    context, place = await asyncio.gather(
        svc.post("di", "/integrate/point", {"lat": lat, "lon": lon}),
        svc.get("eds", "/places/reverse", {"lat": lat, "lon": lon, "lang": lang}),
        return_exceptions=True,
    )
    if isinstance(context, Exception):
        raise context
    risk = await svc.post("rks", "/risk/point", {"context": context})
    return {"lat": lat, "lon": lon, "place": place if isinstance(place, dict) else {"name": "", "label": ""},
            "forecast": context["forecast"], "hazards": risk["hazards"], "risk_level": risk["risk_level"],
            "degraded": context["data_quality"]["degraded_services"], "context_id": context["context_id"],
            "fetched_at": context["created_at"]}


@app.get("/api/map/grid")
async def map_grid(variable: str = "temperature", west: float = -180, south: float = -60,
                   east: float = 180, north: float = 70, zoom: float = 2):
    return await svc.get("di", "/map/grid", {"variable": variable, "west": west, "south": south,
                                             "east": east, "north": north, "zoom": zoom})


@app.get("/api/map/radar")
async def map_radar():
    return await svc.get("eds", "/radar")


# =====================================================================
# Trip planning / chat -> Travel AI Agent
# =====================================================================
@app.post("/api/trip")
async def trip(req: TripRequest):
    return await svc.post("agent", "/agent/trip", req.model_dump(), timeout=90)


@app.post("/api/chat")
async def chat(req: ChatRequest):
    return await svc.post("agent", "/agent/chat", req.model_dump(), timeout=90)


# =====================================================================
# Feedback / alerts -> Module 08
# =====================================================================
class SubscriptionRequest(BaseModel):
    name: str = Field(default="พื้นที่ของฉัน", max_length=100)
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)
    radius_km: float = Field(default=100, ge=5, le=1000)
    hazards: list[str] = []
    min_severity: int = Field(default=3, ge=1, le=4)
    lang: str = "th"


@app.post("/api/feedback")
async def feedback(req: FeedbackRequest):
    return await svc.post("rf", "/feedback", req.model_dump())


@app.post("/api/subscriptions")
async def add_subscription(req: SubscriptionRequest):
    return await svc.post("rf", "/subscriptions", req.model_dump())


@app.get("/api/subscriptions")
async def list_subscriptions():
    return await svc.get("rf", "/subscriptions")


@app.delete("/api/subscriptions/{sub_id}")
async def delete_subscription(sub_id: str):
    return await svc.call("rf", "DELETE", f"/subscriptions/{sub_id}")


@app.get("/api/notifications")
async def notifications():
    return await svc.get("rf", "/notifications")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", "8000")))
