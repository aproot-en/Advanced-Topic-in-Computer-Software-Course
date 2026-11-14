# dle_server.py
# Module 07: Decision Agent + LLM API — runs on port 8005
#   1) /decide   choose one recommendation with rules (decision_rules.py) and lock it
#   2) /explain  explain it in plain language (template, or a verified LLM answer)
#
# Run:  python 07_decision_llm_engine/dle_server.py

import hashlib
import json
import os
import sys
from datetime import datetime, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path += [HERE, os.path.join(ROOT, "09_backend", "shared")]

from pydantic import BaseModel          # noqa: E402

import decision_rules as rules          # noqa: E402
import llm_explainer as llm             # noqa: E402
from common import create_app, fail     # noqa: E402
from schemas import SEVERITY_EN, SEVERITY_TH   # noqa: E402

app = create_app("ProJ-7 Decision & LLM Engine (Module 07)", "decision_llm_engine")
AUDIT_FILE = os.path.join(HERE, "data", "decisions.jsonl")


class DecideRequest(BaseModel):
    routes: list[dict]                 # [{"route": {...}, "eval": {...}}, ...] from Module 06 (first = main route)
    delay_options: list[dict] = []
    degraded_services: list[str] = []
    departure: str


class ExplainTripRequest(BaseModel):
    decision: dict
    primary: dict                      # {"route":..., "eval":...}
    origin_name: str
    destination_name: str
    departure: str
    lang: str = "th"
    evidence: list[dict] = []          # passages from Disaster RAG


class ExplainHazardRequest(BaseModel):
    place_name: str
    hazards: list[dict]
    lang: str = "th"


def lock_hash(decision):
    """Fingerprint of the decision, used to check nobody changed it after it was made."""
    important = {"action": decision["action"], "risk_level": decision["risk_level"],
                 "selected_route_id": decision["selected_route_id"], "delay_hours": decision["delay_hours"]}
    key = json.dumps(important, sort_keys=True)
    return hashlib.sha256(key.encode()).hexdigest()[:16]


def save_audit(record):
    os.makedirs(os.path.dirname(AUDIT_FILE), exist_ok=True)
    with open(AUDIT_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


@app.post("/decide")
async def decide(req: DecideRequest):
    if not req.routes:
        fail(422, "VALIDATION_FAILED", "ต้องมีผลประเมินอย่างน้อย 1 เส้นทาง")
    departure = datetime.fromisoformat(req.departure.replace("Z", "+00:00"))
    hours_ahead = (departure - datetime.now(departure.tzinfo)).total_seconds() / 3600
    decision = rules.decide(req.routes[0], req.routes[1:], req.delay_options, req.degraded_services, hours_ahead)
    decision["lock_hash"] = lock_hash(decision)
    save_audit({"time": datetime.now().isoformat(), "rules_fired": decision["rules_fired"], "action": decision["action"],
                "risk": decision["risk_level"], "confidence": decision["confidence"],
                "policy_version": decision["policy_version"], "degraded": req.degraded_services})
    return decision


@app.post("/explain/trip")
async def explain_trip(req: ExplainTripRequest):
    d = req.decision
    if d.get("lock_hash") != lock_hash(d):
        fail(409, "DECISION_CHANGED", "คำแนะนำถูกแก้ไขหลังตัดสินใจ — ไม่อธิบายให้")
    departure = datetime.fromisoformat(req.departure.replace("Z", "+00:00"))
    text = rules.build_trip_text(d, req.primary, req.origin_name, req.destination_name, departure, req.lang,
                                 lambda iso: llm.to_local(iso, req.lang))
    facts = "\n".join(text["reasons"])
    if d.get("delay_hours"):
        facts += "\n" + llm.to_local((departure + timedelta(hours=d["delay_hours"])).isoformat(), req.lang)
    summary, generator = await llm.polish_with_llm(text["summary"], d["action"], facts, req.lang)
    citations = [{"evidence_id": e["evidence_id"], "title": e["title"], "section": e.get("section"), "url": e.get("url")}
                 for e in req.evidence]
    return {"action_text": text["action_text"], "summary": summary, "reasons": text["reasons"],
            "citations": citations, "generator": generator, "prompt_version": llm.PROMPT_VERSION,
            "lock_hash": d["lock_hash"]}


@app.post("/explain/hazard")
async def explain_hazard(req: ExplainHazardRequest):
    names = SEVERITY_TH if req.lang == "th" else SEVERITY_EN
    return llm.hazard_info_text(req.place_name, req.hazards, req.lang, names)


@app.get("/policy")
async def policy():
    return {"policy_version": rules.POLICY_VERSION, "llm_api_enabled": llm_client.enabled(),
            "llm_model": llm_client.LLM_MODEL, "prompt_version": llm.PROMPT_VERSION}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", "8005")))
