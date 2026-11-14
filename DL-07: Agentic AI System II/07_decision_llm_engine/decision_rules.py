# decision_rules.py
# Module 07 (simple version): choose one recommendation with if/else rules (short version of proj-prompt Appendix F)
# and build the explanation from templates (an LLM, if used, may never change the recommendation)

from datetime import timedelta

POLICY_VERSION = "dp-simple-1.0"

ACTION_TEXT = {
    "NORMAL": ("เดินทางได้ตามปกติ", "Travel normally"),
    "CHANGE_ROUTE": ("เปลี่ยนเส้นทาง", "Change route"),
    "DELAY": ("เลื่อนการเดินทาง", "Delay travel"),
    "AVOID": ("หลีกเลี่ยงการเดินทาง", "Avoid travel"),
}
RISK_TEXT = {"LOW": ("ต่ำ", "Low"), "MEDIUM": ("ปานกลาง", "Medium"), "HIGH": ("สูง", "High")}
HAZARD_TH = {"RAIN": "ฝนตกหนัก", "WIND": "ลมแรง", "FOG": "หมอก/ทัศนวิสัยต่ำ", "STORM": "พายุ", "FIRE": "ไฟป่า",
             "FLOOD": "น้ำท่วม", "VOLCANO": "ภูเขาไฟ", "EARTHQUAKE": "แผ่นดินไหว", "HEAT": "อากาศร้อนจัด",
             "AIR_QUALITY": "ฝุ่น PM2.5", "WEATHER": "สภาพอากาศ"}
HAZARD_EN = {"RAIN": "heavy rain", "WIND": "strong wind", "FOG": "low visibility", "STORM": "storm", "FIRE": "wildfire",
             "FLOOD": "flooding", "VOLCANO": "volcano", "EARTHQUAKE": "earthquake", "HEAT": "extreme heat",
             "AIR_QUALITY": "PM2.5", "WEATHER": "weather"}


def extra_minutes_ok(alt_minutes, primary_minutes):
    """An alternative may be slower by at most 30 min or 25% of the original time (whichever is larger)."""
    return alt_minutes - primary_minutes <= max(30, 0.25 * primary_minutes)


def decide(primary, alternatives, delay_options, degraded_services, hours_ahead):
    """
    primary / alternatives: {"route": {...}, "eval": {...}}  (eval comes from risk_rules.assess_route)
    delay_options: [{"hours": 3, "eval": {...}}, ...]  (main route assessed with a later departure)
    returns: action, risk_level, confidence, rules_fired, selected_route_id, delay_hours
    """
    risk = primary["eval"]["risk_level"]
    max_sev = primary["eval"]["max_severity"]
    rules = []
    action, selected, delay_hours = "NORMAL", primary["route"]["route_id"], None

    def best_alt(ok_levels):
        good = [a for a in alternatives
                if a["eval"]["risk_level"] in ok_levels
                and extra_minutes_ok(a["route"]["duration_min"], primary["route"]["duration_min"])]
        good.sort(key=lambda a: (a["eval"]["max_severity"], a["route"]["duration_min"]))
        return good[0] if good else None

    def best_delay(max_hours, ok_levels):
        for d in delay_options:
            if d["hours"] <= max_hours and d["eval"]["risk_level"] in ok_levels:
                return d
        return None

    if max_sev >= 4:
        alt = best_alt(["LOW", "MEDIUM"])
        if alt and alt["eval"]["max_severity"] <= 2:
            action, selected = "CHANGE_ROUTE", alt["route"]["route_id"]
            rules.append("P5_EXTREME_ON_ROUTE_ALT_OK")
        else:
            action = "AVOID"
            rules.append("P5_EXTREME_ON_ROUTE")
    elif risk == "HIGH":
        delay = best_delay(24, ["LOW"])
        alt = best_alt(["LOW", "MEDIUM"])
        if delay:
            action, delay_hours = "DELAY", delay["hours"]
            rules.append("P6_HIGH_DELAY_HELPS")
        elif alt:
            action, selected = "CHANGE_ROUTE", alt["route"]["route_id"]
            rules.append("P7_HIGH_ALT_ROUTE")
        else:
            action = "AVOID"
            rules.append("P8_HIGH_OTHERWISE")
    elif risk == "MEDIUM":
        alt = best_alt(["LOW"])
        delay = best_delay(12, ["LOW"])
        if alt:
            action, selected = "CHANGE_ROUTE", alt["route"]["route_id"]
            rules.append("P9_MEDIUM_SAFER_ALT")
        elif delay:
            action, delay_hours = "DELAY", delay["hours"]
            rules.append("P10_MEDIUM_TIME_DEPENDENT")
        else:
            action = "NORMAL"
            rules.append("P10_MEDIUM_NORMAL_WITH_CAUTION")
    else:
        rules.append("P12_LOW_NORMAL")

    # confidence: start at 0.85, lower it when data is missing or the forecast is far ahead
    confidence = 0.85
    confidence -= 0.1 * len(degraded_services)
    if hours_ahead > 48:
        confidence -= 0.15
    elif hours_ahead > 24:
        confidence -= 0.05
    if degraded_services:
        rules.append("DEGRADED_CAP")
        confidence = min(confidence, 0.6)
    confidence = round(max(0.2, min(confidence, 0.95)), 2)

    return {"action": action, "risk_level": risk, "confidence": confidence, "rules_fired": rules,
            "selected_route_id": selected, "delay_hours": delay_hours, "emergency": max_sev >= 3,
            "policy_version": POLICY_VERSION}


def worst_segments(evaluation, limit=3):
    segs = [s for s in evaluation["segments"] if s["max_severity"] >= 2]
    segs.sort(key=lambda s: -s["max_severity"])
    return segs[:limit]


def build_trip_text(decision, primary, origin_name, dest_name, departure, lang, to_local):
    """Build the summary + reasons from templates (never invent facts that are not in the assessment)."""
    th = lang == "th"
    action_name = ACTION_TEXT[decision["action"]][0 if th else 1]
    reasons = []
    for s in worst_segments(primary["eval"]):
        hz = s["top_hazard"]
        when = to_local(s["eta"])
        if th:
            detail = f"ฝน {s['rain_mm_h'] or 0:.1f} มม./ชม." if hz == "RAIN" else (
                f"ลมกระโชก {s['gust_kmh'] or 0:.0f} กม./ชม." if hz == "WIND" else ", ".join(s["notes"]) or HAZARD_TH.get(hz, hz))
            reasons.append(f"คาดว่าจะมี{HAZARD_TH.get(hz, hz)}ที่กิโลเมตรที่ {s['km']:.0f} ประมาณ {when} ({detail})")
        else:
            detail = f"rain {s['rain_mm_h'] or 0:.1f} mm/h" if hz == "RAIN" else (
                f"gusts {s['gust_kmh'] or 0:.0f} km/h" if hz == "WIND" else ", ".join(s["notes"]) or HAZARD_EN.get(hz, hz))
            reasons.append(f"Expected {HAZARD_EN.get(hz, hz)} at km {s['km']:.0f} around {when} ({detail})")
    if not reasons:
        reasons.append("ไม่พบภัยที่มีนัยสำคัญตลอดเส้นทางในช่วงเวลาที่จะเดินทาง" if th
                       else "No significant hazard found along the route during your travel time")

    if decision["action"] == "DELAY":
        new_time = to_local((departure + timedelta(hours=decision["delay_hours"])).isoformat())
        summary = (f"แนะนำให้เลื่อนออกเดินทางไปประมาณ {new_time} เพื่อหลีกเลี่ยงภัยบนเส้นทาง {origin_name} → {dest_name}"
                   if th else f"Delay departure to about {new_time} to avoid hazards on {origin_name} → {dest_name}")
    elif decision["action"] == "CHANGE_ROUTE":
        summary = (f"แนะนำให้ใช้เส้นทางทางเลือก เพราะเส้นทางหลักจาก {origin_name} ไป {dest_name} มีความเสี่ยงมากกว่า"
                   if th else f"Use the alternative route; the main route from {origin_name} to {dest_name} is riskier")
    elif decision["action"] == "AVOID":
        summary = (f"ควรหลีกเลี่ยงการเดินทางจาก {origin_name} ไป {dest_name} ในช่วงเวลานี้ ความเสี่ยงสูง"
                   if th else f"Avoid travelling from {origin_name} to {dest_name} at this time; risk is high")
    else:
        summary = (f"เดินทางจาก {origin_name} ไป {dest_name} ได้ตามปกติ ขับขี่ด้วยความระมัดระวัง"
                   if th else f"You can travel from {origin_name} to {dest_name} normally; drive carefully")
    return {"action_text": action_name, "summary": summary, "reasons": reasons}
