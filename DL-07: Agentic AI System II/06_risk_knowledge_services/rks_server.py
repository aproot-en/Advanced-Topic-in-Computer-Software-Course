# rks_server.py
# Module 06: Risk & Knowledge Services — runs on port 8004
#   - Local Risk Model (threshold rules in risk_rules.py): assess a point, or a route at arrival time
#   - Disaster RAG (rag.py): search safety guidance with citations
#   - Route information: compare routes + try later departure times
#
# Run:  python 06_risk_knowledge_services/rks_server.py

import os
import sys
from datetime import datetime, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path += [HERE, os.path.join(ROOT, "09_backend", "shared")]

from typing import Optional            # noqa: E402

from pydantic import BaseModel         # noqa: E402

import risk_rules as risk              # noqa: E402
from common import create_app, fail    # noqa: E402
from rag import DisasterRAG            # noqa: E402

app = create_app("ProJ-7 Risk & Knowledge Services (Module 06)", "risk_knowledge_services")
knowledge = DisasterRAG()
MODEL_VERSION = "risk-rules-1.0"


class ContextRequest(BaseModel):
    context: dict                      # snapshot from Module 05


class RagRequest(BaseModel):
    query: str = ""
    hazards: list[str] = []
    lang: str = "th"
    top_k: int = 3


@app.post("/risk/point")
async def risk_point(req: ContextRequest):
    c = req.context
    if "forecast" not in c:
        fail(422, "VALIDATION_FAILED", "context ต้องเป็นชนิด point จาก Module 05")
    hazards = risk.assess_point(c["lat"], c["lon"], c["forecast"], c.get("air"), c.get("flood"),
                                c.get("quakes"), c.get("events"))
    hazards.sort(key=lambda h: -h["severity"])
    return {"hazards": hazards, "risk_level": risk.risk_from_severities([h["severity"] for h in hazards]),
            "model_version": MODEL_VERSION, "context_id": c.get("context_id")}


@app.post("/risk/route")
async def risk_route(req: ContextRequest):
    """Assess every route + try departing 1/3/6/12/24 h later on the main route."""
    c = req.context
    if not c.get("routes"):
        fail(422, "VALIDATION_FAILED", "context ต้องเป็นชนิด route จาก Module 05")
    departure = datetime.fromisoformat(c["departure"].replace("Z", "+00:00"))
    events = c.get("events", [])
    results = []
    for r in c["routes"]:
        ev = risk.assess_route(r["route"], r["samples"], r["forecasts"], departure, events)
        results.append({"route": r["route"], "eval": ev})

    primary = c["routes"][0]
    delay_options = []
    last_time = risk.parse_time(primary["forecasts"][0]["time"][-1])
    for hours in [1, 3, 6, 12, 24]:
        new_dep = departure + timedelta(hours=hours)
        if new_dep + timedelta(minutes=primary["route"]["duration_min"]) > last_time:
            break
        ev = risk.assess_route(primary["route"], primary["samples"], primary["forecasts"], new_dep, events)
        short_eval = {"risk_level": ev["risk_level"], "max_severity": ev["max_severity"], "exposure": ev["exposure"]}
        delay_options.append({"hours": hours, "eval": short_eval})

    # large earthquake near the route in the last 72 h -> add a caution (not a prediction)
    quake_notes = []
    for q in c.get("quakes", []):
        hours_since = (datetime.now(departure.tzinfo) - risk.parse_time(q["time"])).total_seconds() / 3600
        if (q.get("magnitude") or 0) >= 6 and hours_since < 72:
            prob = risk.aftershock_probability(q["magnitude"], hours_since)
            quake_notes.append({"title": q["title"], "aftershock_prob_7d": prob, "note_th": risk.QUAKE_NOTE_TH,
                                "note_en": risk.QUAKE_NOTE_EN})
    return {"routes": results, "delay_options": delay_options, "quake_cautions": quake_notes,
            "model_version": MODEL_VERSION, "context_id": c.get("context_id")}


@app.post("/rag/search")
async def rag_search(req: RagRequest):
    return knowledge.search(req.query, req.hazards, "en" if req.lang.startswith("en") else "th", min(req.top_k, 10))


@app.get("/tips")
async def tips(hazards: str = "", lang: str = "th"):
    lang = "en" if lang.startswith("en") else "th"
    out = []
    for hz in [h for h in hazards.split(",") if h]:
        if hz in risk.SAFETY_TIPS:
            out.append({"hazard": hz, "tips": risk.SAFETY_TIPS[hz][lang], "source": risk.SAFETY_TIPS[hz]["source"]})
    return out


@app.get("/contacts")
async def contacts(country: Optional[str] = "TH"):
    # only Thailand for now; other countries get the local emergency number
    if (country or "").upper() == "TH":
        return risk.EMERGENCY_CONTACTS_TH
    return [{"name": "Local emergency number / เบอร์ฉุกเฉินท้องถิ่น", "phone": "112"}]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", "8004")))
