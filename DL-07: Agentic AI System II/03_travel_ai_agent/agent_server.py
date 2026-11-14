# agent_server.py
# Module 03: Travel AI Agent — runs on port 8001
# The orchestrator: calls the other modules in the order shown in proposed-agent-ii.png
#
#   understand the request (agent_logic.py)
#     -> 04 fetch data (places, routes)      -> 05 integrate data (forecast + hazards along the route)
#     -> 06 risk assessment + Disaster RAG    -> 07 decide + explain
#     -> 08 build the final recommendation -> return to 02
#
# Run:  python 03_travel_ai_agent/agent_server.py

import asyncio
import os
import sys
import time
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path += [HERE, os.path.join(ROOT, "09_backend", "shared")]

import agent_logic as logic                     # noqa: E402
import service_client as svc                    # noqa: E402
from common import create_app, fail             # noqa: E402
from schemas import ChatRequest, TripRequest    # noqa: E402

app = create_app("ProJ-7 Travel AI Agent (Module 03)", "travel_ai_agent")
MAX_SECONDS = 75          # max time per request (the agent can never run forever)
MAX_STEPS = 15            # max number of steps


class Run:
    """State of one request (a simple AgentState)."""

    def __init__(self, lang):
        self.lang = lang
        self.steps = []
        self.degraded = []
        self.limitations = []

    async def call(self, name, coro, default=None, critical=False):
        """Call another module and log the step; on failure, mark that service as degraded."""
        if len(self.steps) >= MAX_STEPS:
            raise RuntimeError("เกินจำนวนขั้นตอนสูงสุดของ agent")
        start = time.time()
        try:
            result = await coro
            self.steps.append({"step": name, "ok": True, "ms": int((time.time() - start) * 1000)})
            return result
        except svc.ServiceError as e:
            self.steps.append({"step": name, "ok": False, "note": str(e)[:150]})
            self.degraded.append(name)
            if critical:
                raise
            return default

    def finish(self, resp):
        resp["steps"] = self.steps
        resp["degraded_services"] = sorted(set(resp.get("degraded_services", []) + self.degraded))
        resp["limitations"] = resp.get("limitations", []) + self.limitations
        return resp


async def simple_reply(run, intent, summary, response_type="CLARIFICATION"):
    payload = {"intent": intent, "response_type": response_type, "summary": summary, "lang": run.lang}
    resp = await run.call("08:simple", svc.post("rf", "/recommendation/simple", payload))
    if resp is None:   # Module 08 unavailable: build a short reply here
        resp = {"response_type": response_type, "intent": intent, "summary": summary, "reasons": [], "routes": [],
                "immediate_actions": [], "ui_actions": [], "fetched_at": datetime.now(timezone.utc).isoformat()}
    return run.finish(resp)


async def geocode(run, text):
    places = await run.call(f"04:geocode:{text}", svc.get("eds", "/places/search", {"q": text, "lang": run.lang}), [])
    return places[0] if places else None


async def tips_and_evidence(run, hazards, query):
    tips, rag = await asyncio.gather(
        run.call("06:tips", svc.get("rks", "/tips", {"hazards": ",".join(hazards), "lang": run.lang}), []),
        run.call("06:rag", svc.post("rks", "/rag/search", {"query": query, "hazards": hazards, "lang": run.lang}), None),
    )
    tip_list = [t for item in tips for t in item["tips"][:2]]
    passages = rag["passages"] if rag and rag["evidence_found"] else []
    return tip_list, passages


def to_citations(passages):
    """Turn RAG passages into a short citation list for the answer."""
    citations = []
    for p in passages:
        citations.append({"evidence_id": p["evidence_id"], "title": p["title"], "section": p["section"], "url": p["url"]})
    return citations


def numbered_steps(text):
    """Get the lines that start with '1.', '2.', ... from a guidance passage."""
    steps = []
    for line in text.splitlines():
        line = line.strip()
        number, dot, rest = line.partition(".")
        if dot and number.isdigit():
            steps.append(rest.strip())
    return steps


# =====================================================================
# 1) Trip planning
# =====================================================================
async def run_trip(origin_text, dest_text, departure, mode, lang):
    run = Run(lang)
    th = lang == "th"

    origin, dest = await asyncio.gather(geocode(run, origin_text), geocode(run, dest_text))
    if not origin or not dest:
        missing = origin_text if not origin else dest_text
        return await simple_reply(run, "PLAN_TRIP", f"ไม่พบสถานที่ \"{missing}\" กรุณาพิมพ์ชื่อให้ชัดเจนขึ้น เช่น ชื่อจังหวัดหรืออำเภอ"
                                  if th else f"Could not find \"{missing}\". Please type a clearer place name.")

    routes = await run.call("04:routes", svc.post("eds", "/routes", {"origin": [origin["lat"], origin["lon"]],
                                                                     "destination": [dest["lat"], dest["lon"]]}), [])
    data_problems = []   # only problems with hazard/route data lower the confidence
    if not routes:   # routing failed: use a straight line (and report the limitation)
        d = logic.distance_km(origin["lat"], origin["lon"], dest["lat"], dest["lon"])
        data_problems.append("routing")
        routes = [{"route_id": "r1", "coordinates": [[origin["lon"], origin["lat"]], [dest["lon"], dest["lat"]]],
                   "distance_km": round(d, 1), "duration_min": round(d / 70 * 60)}]
        run.limitations.append("คำนวณเส้นทางถนนไม่ได้ ใช้เส้นตรงแทน" if th else "Road routing unavailable; using a straight line")
    if mode in ("TRAIN", "FLIGHT", "BOAT"):
        run.limitations.append("ใช้เส้นทางถนนเป็นตัวแทนเส้นทางของรถไฟ/เครื่องบิน/เรือ" if th
                               else "Road route is used as a proxy for train/flight/boat")

    dep_iso = departure.isoformat()
    context = await run.call("05:integrate", svc.post("di", "/integrate/route", {"routes": routes, "departure": dep_iso}))
    if context is None:
        return await simple_reply(run, "PLAN_TRIP", "ไม่สามารถดึงข้อมูลพยากรณ์ได้ในขณะนี้ กรุณาลองใหม่ และติดตามประกาศกรมอุตุนิยมวิทยา"
                                  if th else "Forecast data is unavailable right now. Please try again later.", "RECOMMENDATION")
    data_problems += context["data_quality"]["degraded_services"]
    run.degraded += data_problems

    risk = await run.call("06:risk", svc.post("rks", "/risk/route", {"context": context}))
    if risk is None:
        return await simple_reply(run, "PLAN_TRIP", "ประเมินความเสี่ยงไม่ได้ในขณะนี้" if th else "Risk assessment unavailable",
                                  "RECOMMENDATION")
    primary = risk["routes"][0]
    missing = primary["eval"].get("segments_without_forecast", 0)
    if missing == len(primary["eval"]["segments"]):
        return await simple_reply(run, "PLAN_TRIP", "เวลาเดินทางเกินช่วงพยากรณ์อากาศ (ประมาณ 3 วันล่วงหน้า) กรุณาเลือกเวลาที่ใกล้กว่านี้"
                                  if th else "The travel time is beyond the forecast period (about 3 days ahead). "
                                             "Please choose an earlier time.")
    if missing:
        data_problems.append("forecast-range")
        run.degraded.append("forecast-range")
        run.limitations.append("บางช่วงของการเดินทางเกินช่วงพยากรณ์อากาศ จึงไม่มีข้อมูลสำหรับช่วงนั้น" if th
                               else "Part of the trip is beyond the forecast period, so there is no weather data for it")
    hazards = sorted({s["top_hazard"] for s in primary["eval"]["segments"] if s["top_hazard"] and s["max_severity"] >= 1})
    (tips, passages), contacts = await asyncio.gather(
        tips_and_evidence(run, hazards or ["RAIN"], " ".join(hazards) + " ขับรถ เดินทาง driving"),
        run.call("06:contacts", svc.get("rks", "/contacts", {"country": dest.get("country") or "TH"}), []),
    )

    decision = await run.call("07:decide", svc.post("dle", "/decide", {
        "routes": risk["routes"], "delay_options": risk["delay_options"],
        "degraded_services": data_problems, "departure": dep_iso}), critical=True)
    explanation = await run.call("07:explain", svc.post("dle", "/explain/trip", {
        "decision": decision, "primary": primary, "origin_name": origin["name"], "destination_name": dest["name"],
        "departure": dep_iso, "lang": lang, "evidence": passages}), critical=True)

    final = await run.call("08:recommendation", svc.post("rf", "/recommendation/trip", {
        "decision": decision, "explanation": explanation, "routes": risk["routes"], "lang": lang,
        "departure": dep_iso, "tips": tips, "contacts": contacts, "events": context.get("near_events", []) + context.get("quakes", []),
        "quake_cautions": risk.get("quake_cautions", []), "degraded_services": run.degraded,
        "limitations": run.limitations}), critical=True)
    final["context_id"] = context["context_id"]
    run.limitations = []   # already included in final
    return run.finish(final)


# =====================================================================
# 2) Hazard questions, e.g. "rain in Chiang Mai tomorrow" / "latest earthquakes"
# =====================================================================
async def run_hazard_info(text, lang, map_lat, map_lon, asked, area, latest):
    run = Run(lang)
    th = lang == "th"

    if asked == ["EARTHQUAKE"] and latest:
        quakes = await run.call("04:earthquakes", svc.get("eds", "/earthquakes", {"window": "24h"}), [])
        quakes = sorted(quakes, key=lambda q: q["time"], reverse=True)
        big = [q for q in quakes if (q["magnitude"] or 0) >= 4.5][:5] or quakes[:5]
        if not big:
            return await simple_reply(run, "HAZARD_INFO", "ไม่พบข้อมูลแผ่นดินไหวใน 24 ชั่วโมงที่ผ่านมา" if th
                                      else "No earthquakes found in the last 24 hours", "HAZARD_INFO")
        lines = [f"M{q['magnitude']} — {q['place']} ({logic.to_local_text(q['time'], lang)})" for q in big]
        lines.append("แผ่นดินไหวไม่สามารถพยากรณ์ล่วงหน้าได้ ข้อมูลนี้มาจากหน่วยงานทางการ" if th
                     else "Earthquakes cannot be predicted; this is official observed data.")
        tips, passages = await tips_and_evidence(run, ["EARTHQUAKE"], "แผ่นดินไหว earthquake")
        final = await run.call("08:recommendation", svc.post("rf", "/recommendation/hazard", {
            "lang": lang, "summary": ("แผ่นดินไหวล่าสุด (24 ชม.): " if th else "Latest earthquakes (24 h): ") + lines[0],
            "reasons": lines, "tips": tips, "events": big, "asked_hazards": ["EARTHQUAKE"],
            "lat": big[0]["lat"], "lon": big[0]["lon"], "zoom": 5, "sources": ["USGS"],
            "citations": to_citations(passages)}), critical=True)
        return run.finish(final)

    place = await geocode(run, area) if area else None
    if place:
        lat, lon, name = place["lat"], place["lon"], place["name"]
    elif map_lat is not None:
        lat, lon = map_lat, map_lon
        rev = await run.call("04:reverse", svc.get("eds", "/places/reverse", {"lat": lat, "lon": lon, "lang": lang}))
        name = rev["name"] if rev and rev.get("name") else f"{lat:.2f}, {lon:.2f}"
    else:
        return await simple_reply(run, "HAZARD_INFO", "อยากทราบข้อมูลของพื้นที่ไหนคะ? พิมพ์ชื่อจังหวัดหรือคลิกบนแผนที่" if th
                                  else "Which area do you mean? Type a place or click on the map.")

    context = await run.call("05:integrate", svc.post("di", "/integrate/point", {"lat": lat, "lon": lon}))
    if context is None:
        return await simple_reply(run, "HAZARD_INFO", "ดึงข้อมูลพยากรณ์ไม่ได้ในขณะนี้" if th else "Forecast unavailable", "HAZARD_INFO")
    run.degraded += context["data_quality"]["degraded_services"]
    risk = await run.call("06:risk", svc.post("rks", "/risk/point", {"context": context}), {"hazards": []})
    hazards = risk["hazards"]
    if asked and asked != ["WEATHER"]:
        hazards = [h for h in hazards if h["hazard"] in asked or h["hazard"] == "WEATHER"] or hazards
    hazards.sort(key=lambda h: -h["severity"])
    text_out = await run.call("07:explain", svc.post("dle", "/explain/hazard", {"place_name": name, "hazards": hazards,
                                                                                 "lang": lang}),
                              {"summary": name, "reasons": []})
    tips, passages = await tips_and_evidence(run, [h["hazard"] for h in hazards if h["severity"] >= 1][:3] or (asked or ["RAIN"]),
                                             text)
    focus = next((h["time"] for h in hazards if h.get("time") and "T" in str(h["time"])), None)
    final = await run.call("08:recommendation", svc.post("rf", "/recommendation/hazard", {
        "lang": lang, "summary": text_out["summary"], "reasons": text_out["reasons"], "hazards": hazards,
        "tips": tips, "lat": lat, "lon": lon, "asked_hazards": asked or ["WEATHER"], "focus_time": focus,
        "sources": sorted({h["source"] for h in hazards}),
        "citations": to_citations(passages)}), critical=True)
    final["context_id"] = context["context_id"]
    return run.finish(final)


# =====================================================================
# 3) Emergency: answer fast, no routing
# =====================================================================
async def run_emergency(text, lang, lat, lon, hazards):
    run = Run(lang)
    if "ไฟไหม้" in text:
        hazards = ["FIRE"]
    if not hazards:
        hazards = ["FLOOD"]
    calls = [tips_and_evidence(run, hazards, text), run.call("06:contacts", svc.get("rks", "/contacts", {"country": "TH"}), [])]
    if lat is not None:
        calls.append(run.call("04:nearby", svc.get("eds", "/places/nearby", {"lat": lat, "lon": lon}, timeout=20), []))
    results = await asyncio.gather(*calls)
    (tips, passages), contacts = results[0], results[1]
    places = results[2] if len(results) > 2 else []
    # emergency steps come from the guidance documents (RAG) first, otherwise use tips
    steps = []
    for p in passages:   # use the first passage that has numbered steps (1. 2. 3.)
        steps = numbered_steps(p["text"])
        if steps:
            break
    if not steps:
        steps = tips
    final = await run.call("08:recommendation", svc.post("rf", "/recommendation/emergency", {
        "lang": lang, "steps": steps, "contacts": contacts, "nearby_places": places[:8], "lat": lat, "lon": lon,
        "sources": sorted({p["title"] for p in passages}),
        "citations": to_citations(passages)}), critical=True)
    return run.finish(final)


# =====================================================================
# Agent API (called by Module 02)
# =====================================================================
def timeout_reply(lang):
    return {"response_type": "CLARIFICATION", "summary": "ระบบใช้เวลานานเกินไป กรุณาลองใหม่" if lang == "th"
            else "The request took too long. Please try again.", "reasons": [], "routes": [], "ui_actions": [],
            "limitations": ["timeout"], "fetched_at": datetime.now(timezone.utc).isoformat()}


@app.post("/agent/trip")
async def agent_trip(req: TripRequest):
    if req.departure_time:
        try:
            dep = datetime.fromisoformat(req.departure_time)
        except ValueError:
            fail(422, "VALIDATION_FAILED", "departure_time must look like 2026-11-15T08:00")
        if dep.tzinfo is None:
            dep = dep.replace(tzinfo=logic.THAI_TZ)
    else:
        dep = datetime.now(timezone.utc)
    dep = max(dep, datetime.now(timezone.utc) - timedelta(minutes=30)).astimezone(timezone.utc)
    try:
        return await asyncio.wait_for(run_trip(req.origin, req.destination, dep, req.travel_mode, req.lang), MAX_SECONDS)
    except asyncio.TimeoutError:
        return timeout_reply(req.lang)


@app.post("/agent/chat")
async def agent_chat(req: ChatRequest):
    th = req.lang == "th"
    u = await logic.understand(req.text)       # rules + (optional) free Llama API
    intent = u["intent"]
    try:
        if intent == "EMERGENCY_NOW":
            resp = await asyncio.wait_for(run_emergency(req.text, req.lang, req.map_lat, req.map_lon, u["hazards"]),
                                          MAX_SECONDS)
        elif intent == "PLAN_TRIP":
            resp = await chat_trip(req, u)
        elif intent == "HAZARD_INFO":
            resp = await asyncio.wait_for(run_hazard_info(req.text, req.lang, req.map_lat, req.map_lon,
                                                          u["hazards"], u["area"], u["latest"]), MAX_SECONDS)
        else:
            resp = await simple_reply(Run(req.lang), "OUT_OF_SCOPE",
                                      "ฉันช่วยเรื่องความปลอดภัยในการเดินทางและภัยธรรมชาติได้ ลองถามเช่น "
                                      "\"พรุ่งนี้เช้าจากกรุงเทพไปเชียงใหม่ปลอดภัยไหม\" หรือ \"ฝนที่ภูเก็ต\" หรือ \"แผ่นดินไหวล่าสุด\""
                                      if th else "I can help with travel safety and natural hazards. Try \"from Bangkok to "
                                                 "Chiang Mai tomorrow morning\", \"rain in Phuket\" or \"latest earthquakes\".")
    except asyncio.TimeoutError:
        resp = timeout_reply(req.lang)
    resp["understood_by"] = u["understood_by"]   # "rules" or "llama"
    return resp


async def chat_trip(req, u):
    """Trip question typed in the chat, e.g. 'from Bangkok to Chiang Mai tomorrow morning'."""
    th = req.lang == "th"
    run = Run(req.lang)
    origin, dest = u["origin"], u["destination"]
    if not dest:
        return await simple_reply(run, "PLAN_TRIP", "จะเดินทางไปที่ไหนคะ?" if th else "Where are you going?")
    if not origin:
        if req.map_lat is None:
            return await simple_reply(run, "PLAN_TRIP", f"จะเดินทางไป{dest}จากที่ไหนคะ?" if th
                                      else f"Where will you start your trip to {dest}?")
        rev = await run.call("04:reverse", svc.get("eds", "/places/reverse",
                                                   {"lat": req.map_lat, "lon": req.map_lon, "lang": req.lang}))
        origin = (rev or {}).get("name") or f"{req.map_lat:.3f},{req.map_lon:.3f}"
    departure = logic.extract_departure(req.text).astimezone(timezone.utc)
    return await asyncio.wait_for(run_trip(origin, dest, departure, logic.detect_mode(req.text), req.lang), MAX_SECONDS)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", "8001")))
