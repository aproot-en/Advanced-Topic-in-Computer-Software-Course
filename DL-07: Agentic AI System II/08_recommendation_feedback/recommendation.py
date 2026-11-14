# recommendation.py
# Build the final recommendation sent to the user (same format for trip / hazard info / emergency)
# together with commands that move the map (ui_actions)

import uuid
from datetime import datetime, timedelta, timezone

SCHEMA_VERSION = "recommendation-1.0"
LAYER_FOR_HAZARD = {"RAIN": "precipitation", "WIND": "wind", "STORM": "storms", "FIRE": "fires",
                    "FLOOD": "floods", "EARTHQUAKE": "earthquakes", "AIR_QUALITY": "pm25",
                    "HEAT": "temperature", "WEATHER": "temperature", "FOG": "precipitation", "VOLCANO": "volcanoes"}


def empty_response(intent, response_type, lang):
    return {
        "request_id": str(uuid.uuid4()), "response_type": response_type, "intent": intent, "lang": lang,
        "action_code": None, "action_text": None, "risk_level": None, "confidence": None,
        "summary": "", "reasons": [], "immediate_actions": [], "hazards": [], "routes": [],
        "suggested_departure_time": None, "emergency_contacts": [], "nearby_places": [], "events": [],
        "citations": [], "sources": [], "limitations": [], "degraded_services": [], "ui_actions": [],
        "steps": [], "rules_fired": [], "versions": {"schema": SCHEMA_VERSION},
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }


def build_trip(data):
    """data: decision, explanation, routes (from 06), tips, contacts, events, departure, ..."""
    th = data["lang"] == "th"
    d, ex = data["decision"], data["explanation"]
    resp = empty_response("PLAN_TRIP", "RECOMMENDATION", data["lang"])
    resp.update({
        "action_code": d["action"], "action_text": ex["action_text"], "risk_level": d["risk_level"],
        "confidence": d["confidence"], "summary": ex["summary"], "reasons": ex["reasons"],
        "rules_fired": d["rules_fired"], "citations": ex.get("citations", []),
        "degraded_services": data.get("degraded_services", []), "limitations": data.get("limitations", []),
        "steps": data.get("steps", []), "events": data.get("events", []),
    })
    resp["versions"].update({"policy": d.get("policy_version"), "prompt": ex.get("prompt_version"),
                             "generator": ex.get("generator"), "lock_hash": d.get("lock_hash")})
    if d.get("delay_hours"):
        dep = datetime.fromisoformat(data["departure"].replace("Z", "+00:00"))
        resp["suggested_departure_time"] = (dep + timedelta(hours=d["delay_hours"])).isoformat()

    # route list (original order, first = main route)
    routes = data["routes"]
    fastest = min(r["route"]["duration_min"] for r in routes)
    for n, r in enumerate(routes):
        resp["routes"].append({
            "route_id": r["route"]["route_id"],
            "label": ("เส้นทางหลัก" if th else "Main route") if n == 0 else (f"ทางเลือก {n}" if th else f"Alternative {n}"),
            "coordinates": r["route"]["coordinates"], "distance_km": r["route"]["distance_km"],
            "duration_min": r["route"]["duration_min"], "extra_minutes": r["route"]["duration_min"] - fastest,
            "risk_level": r["eval"]["risk_level"], "max_severity": r["eval"]["max_severity"],
            "exposure": r["eval"].get("exposure", {}), "segments": r["eval"].get("segments", []),
            "selected": r["route"]["route_id"] == d["selected_route_id"],
        })

    # what to do: safety tips for the hazards found
    tips = list(data.get("tips", []))
    if not tips:
        tips = (["ตรวจสภาพรถก่อนออกเดินทาง", "ติดตามประกาศจากกรมอุตุนิยมวิทยาและ ปภ."] if th
                else ["Check your vehicle before leaving", "Follow official weather and disaster updates"])
    resp["immediate_actions"] = tips[:5]
    for q in data.get("quake_cautions", []):
        resp["reasons"].append(f"{q['title']} — " + (q["note_th"] if th else q["note_en"]))
    if d.get("emergency") or d["action"] == "AVOID":
        resp["emergency_contacts"] = data.get("contacts", [])
    resp["sources"] = ["Open-Meteo", "OSRM / OpenStreetMap", "GDACS", "NASA EONET", "USGS"] + \
        sorted({c["title"] for c in resp["citations"]})

    # ui_actions: zoom to the route / enable related hazard layers / move the timeline to the most dangerous time
    primary = routes[0]
    lons = [c[0] for c in primary["route"]["coordinates"]]
    lats = [c[1] for c in primary["route"]["coordinates"]]
    resp["ui_actions"].append({"type": "FIT_BOUNDS", "bbox": [min(lons), min(lats), max(lons), max(lats)]})
    segs = [s for s in primary["eval"].get("segments", []) if s["max_severity"] >= 1]
    hazards = sorted({s["top_hazard"] for s in segs if s["top_hazard"]})
    layers = sorted({LAYER_FOR_HAZARD[h] for h in hazards if h in LAYER_FOR_HAZARD}) or ["precipitation"]
    resp["ui_actions"].append({"type": "ENABLE_LAYERS", "layers": layers})
    if segs:
        worst = max(segs, key=lambda s: s["max_severity"])
        resp["ui_actions"].append({"type": "SET_TIME", "time": worst["eta"]})
    return resp


def build_hazard_info(data):
    resp = empty_response("HAZARD_INFO", "HAZARD_INFO", data["lang"])
    resp.update({"summary": data["summary"], "reasons": data.get("reasons", []), "hazards": data.get("hazards", []),
                 "immediate_actions": data.get("tips", [])[:5], "events": data.get("events", []),
                 "citations": data.get("citations", []), "sources": data.get("sources", []),
                 "degraded_services": data.get("degraded_services", []), "steps": data.get("steps", [])})
    lat, lon = data.get("lat"), data.get("lon")
    if lat is not None:
        resp["ui_actions"].append({"type": "FLY_TO", "center": {"lat": lat, "lon": lon}, "zoom": data.get("zoom", 8)})
    layers = sorted({LAYER_FOR_HAZARD[h] for h in data.get("asked_hazards", []) if h in LAYER_FOR_HAZARD})
    if layers:
        resp["ui_actions"].append({"type": "ENABLE_LAYERS", "layers": layers})
    if data.get("focus_time"):
        resp["ui_actions"].append({"type": "SET_TIME", "time": data["focus_time"]})
    return resp


def build_emergency(data):
    th = data["lang"] == "th"
    resp = empty_response("EMERGENCY_NOW", "EMERGENCY", data["lang"])
    resp.update({
        "summary": ("ทำตามขั้นตอนด้านล่างทันที และโทรขอความช่วยเหลือ 1784 (ปภ.) หรือ 1669 (เจ็บป่วยฉุกเฉิน)" if th
                    else "Follow the steps below now and call for help: 1784 (DDPM) or 1669 (medical) in Thailand."),
        "immediate_actions": data.get("steps", [])[:5], "emergency_contacts": data.get("contacts", []),
        "nearby_places": data.get("nearby_places", []), "citations": data.get("citations", []),
        "sources": data.get("sources", []), "degraded_services": data.get("degraded_services", []),
    })
    if data.get("lat") is not None:
        resp["ui_actions"].append({"type": "FLY_TO", "center": {"lat": data["lat"], "lon": data["lon"]}, "zoom": 13})
    return resp


def event_severity(event):
    """Severity of an event (used by the alert checks)."""
    if event["hazard"] == "EARTHQUAKE":
        m = event.get("magnitude") or 0
        return 4 if m >= 7 else 3 if m >= 6 else 2 if m >= 4 else 1
    level = str(event.get("alert_level", "")).lower()
    sev = {"red": 4, "orange": 3, "green": 1}.get(level, 2)
    wind = event.get("wind_kmh")
    if event["hazard"] == "STORM" and wind:
        sev = max(sev, 4 if wind >= 118 else 3 if wind >= 63 else 2)
    return sev
