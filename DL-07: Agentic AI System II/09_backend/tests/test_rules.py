# test_rules.py — tests for the core rules (no internet needed)
# Run:  .venv\Scripts\python.exe -m pytest 09_backend\tests -q

import os
import sys
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for folder in ["03_travel_ai_agent", "06_risk_knowledge_services", "07_decision_llm_engine",
               os.path.join("09_backend", "shared")]:
    sys.path.append(os.path.join(ROOT, folder))

import agent_logic as logic      # noqa: E402
import decision_rules as rules   # noqa: E402
import risk_rules as risk        # noqa: E402


# ---------------- Module 06: severity thresholds ----------------
def test_rain_thresholds():
    assert risk.rain_severity(0) == 0
    assert risk.rain_severity(12) == 2
    assert risk.rain_severity(35) == 3
    assert risk.rain_severity(70) == 4


def test_wind_and_storm_thresholds():
    assert risk.wind_severity(30) == 0
    assert risk.wind_severity(70) == 2
    assert risk.wind_severity(120) == 4
    assert risk.storm_severity(50) == 2     # tropical depression
    assert risk.storm_severity(90) == 3     # tropical storm
    assert risk.storm_severity(130) == 4    # typhoon


def test_pm25_thai_aqi():
    assert risk.pm25_severity(10) == 0
    assert risk.pm25_severity(30) == 1
    assert risk.pm25_severity(50) == 2
    assert risk.pm25_severity(80) == 3


def test_more_rain_never_lowers_severity():
    last = 0
    for mm in range(0, 100):
        sev = risk.rain_severity(mm)
        assert sev >= last
        last = sev


def test_aftershock_probability_goes_down_with_time():
    early = risk.aftershock_probability(7.0, hours_since=1)
    late = risk.aftershock_probability(7.0, hours_since=24 * 30)
    assert 0 < late < early < 1


def test_risk_from_severities():
    assert risk.risk_from_severities([0, 1]) == "LOW"
    assert risk.risk_from_severities([2]) == "MEDIUM"
    assert risk.risk_from_severities([3]) == "HIGH"


def test_route_eta_uses_travel_time():
    """Heavy rain at 10:00 must only affect the point the car reaches at 10:00 (not the whole route)."""
    start = datetime(2026, 11, 15, 8, 0, tzinfo=timezone.utc)
    times = [(start + timedelta(hours=h)).strftime("%Y-%m-%dT%H:%MZ") for h in range(6)]
    dry = {"time": times, "precipitation": [0] * 6, "wind_gusts_10m": [10] * 6, "visibility": [20000] * 6}
    wet = {"time": times, "precipitation": [0, 0, 40, 0, 0, 0], "wind_gusts_10m": [10] * 6, "visibility": [20000] * 6}
    route = {"distance_km": 200, "duration_min": 240}
    samples = [(13.0, 100.0, 0), (13.5, 100.0, 100), (14.0, 100.0, 200)]
    result = risk.assess_route(route, samples, [dry, wet, dry], start, events=[])
    assert result["segments"][1]["max_severity"] == 3     # reaches km 100 exactly at 10:00
    assert result["segments"][0]["max_severity"] == 0
    assert result["risk_level"] == "HIGH"


# ---------------- Module 07: decision rules ----------------
def make(route_id, minutes, risk_level, max_sev):
    return {"route": {"route_id": route_id, "duration_min": minutes},
            "eval": {"risk_level": risk_level, "max_severity": max_sev, "segments": []}}


def test_low_risk_is_normal():
    d = rules.decide(make("r1", 300, "LOW", 0), [], [], [], 2)
    assert d["action"] == "NORMAL"


def test_high_risk_with_delay_option_is_delay():
    delay = [{"hours": 6, "eval": {"risk_level": "LOW", "max_severity": 1}}]
    d = rules.decide(make("r1", 300, "HIGH", 3), [], delay, [], 2)
    assert d["action"] == "DELAY" and d["delay_hours"] == 6


def test_high_risk_with_safe_alternative_is_change_route():
    d = rules.decide(make("r1", 300, "HIGH", 3), [make("r2", 320, "LOW", 0)], [], [], 2)
    assert d["action"] == "CHANGE_ROUTE" and d["selected_route_id"] == "r2"


def test_alternative_too_slow_means_avoid():
    d = rules.decide(make("r1", 300, "HIGH", 3), [make("r2", 600, "LOW", 0)], [], [], 2)
    assert d["action"] == "AVOID"


def test_extreme_hazard_is_avoid():
    d = rules.decide(make("r1", 300, "HIGH", 4), [], [], [], 2)
    assert d["action"] == "AVOID" and d["emergency"]


def test_missing_data_caps_confidence():
    d = rules.decide(make("r1", 300, "LOW", 0), [], [], ["open-meteo"], 2)
    assert d["confidence"] <= 0.6


# ---------------- Module 03: understanding Thai/English requests ----------------
def test_detect_intent():
    assert logic.detect_intent("พรุ่งนี้เช้าจากกรุงเทพไปเชียงใหม่ปลอดภัยไหม") == "PLAN_TRIP"
    assert logic.detect_intent("แผ่นดินไหวล่าสุดอยู่ที่ไหน") == "HAZARD_INFO"
    assert logic.detect_intent("น้ำเข้าบ้านแล้ว ต้องทำยังไง") == "EMERGENCY_NOW"
    assert logic.detect_intent("from Bangkok to Pattaya tomorrow") == "PLAN_TRIP"
    assert logic.detect_intent("สวัสดี") == "OUT_OF_SCOPE"


def test_extract_places():
    assert logic.extract_places("พรุ่งนี้เช้าจากกรุงเทพไปเชียงใหม่ปลอดภัยไหม") == ("กรุงเทพ", "เชียงใหม่")
    assert logic.extract_places("from Bangkok to Chiang Mai tomorrow") == ("Bangkok", "Chiang Mai")


def test_extract_departure_tomorrow_morning():
    now = datetime(2026, 11, 14, 20, 0, tzinfo=logic.THAI_TZ)
    dep = logic.extract_departure("พรุ่งนี้เช้า", now)
    assert dep.day == 15 and dep.hour == 7


def test_detect_hazards():
    assert "FLOOD" in logic.detect_hazards("น้ำท่วมรังสิตไหม")
    assert logic.detect_hazards("พายุฝนฟ้าคะนอง") == ["RAIN"]


# ---------------- Module 03: Llama answer checks (no real API call) ----------------
def test_llama_answer_cannot_invent_places():
    answer = {"intent": "PLAN_TRIP", "origin": "Bangkok", "destination": "Paris", "hazards": ["RAIN", "ALIENS"]}
    result = logic.clean_llm_answer(answer, "from Bangkok to Chiang Mai")
    assert result["origin"] == "Bangkok"
    assert result["destination"] is None          # "Paris" is not in the message
    assert result["hazards"] == ["RAIN"]          # unknown hazard removed


def test_llama_bad_intent_is_ignored():
    assert logic.clean_llm_answer({"intent": "BOOK_HOTEL"}, "hello") is None
    assert logic.clean_llm_answer(None, "hello") is None


def test_emergency_from_rules_always_wins(monkeypatch):
    import asyncio
    import llm_client

    async def fake_chat_json(system_text, user_text, max_tokens=300):
        return {"intent": "HAZARD_INFO", "hazards": ["FLOOD"], "latest": False}

    monkeypatch.setattr(llm_client, "LLM_API_KEY", "test-key")
    monkeypatch.setattr(llm_client, "chat_json", fake_chat_json)
    result = asyncio.run(logic.understand("น้ำเข้าบ้านแล้ว ต้องทำยังไง"))
    assert result["understood_by"] == "llama"
    assert result["intent"] == "EMERGENCY_NOW"


def test_understand_without_key_uses_rules(monkeypatch):
    import asyncio
    import llm_client
    monkeypatch.setattr(llm_client, "LLM_API_KEY", "")
    result = asyncio.run(logic.understand("พรุ่งนี้เช้าจากกรุงเทพไปเชียงใหม่ปลอดภัยไหม"))
    assert result["understood_by"] == "rules"
    assert (result["origin"], result["destination"]) == ("กรุงเทพ", "เชียงใหม่")
