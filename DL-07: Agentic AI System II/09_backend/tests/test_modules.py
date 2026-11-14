# test_modules.py — tests for Module 05 / 06 (RAG) / 07 (LLM verify) / 08 (storage, recommendation)
# Run:  .venv\Scripts\python.exe -m pytest 09_backend\tests -q

import os
import sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for folder in ["05_data_integration", "06_risk_knowledge_services", "07_decision_llm_engine",
               "08_recommendation_feedback", os.path.join("09_backend", "shared")]:
    sys.path.append(os.path.join(ROOT, folder))

import integration as di            # noqa: E402
import llm_explainer as llm         # noqa: E402
import recommendation as rec        # noqa: E402
from rag import DisasterRAG, tokenize   # noqa: E402


# ---------------- Module 05 ----------------
def test_sample_route_has_start_and_end():
    coords = [[100.0, 13.0], [100.0, 13.5], [100.0, 14.0]]      # [lon, lat], about 111 km long
    samples = di.sample_route(coords, every_km=25)
    assert samples[0][:2] == (13.0, 100.0)
    assert samples[-1][:2] == (14.0, 100.0)
    assert 100 < samples[-1][2] < 120


def test_dedupe_events_keeps_gdacs():
    gdacs = [{"hazard": "FIRE", "lat": 18.0, "lon": 99.0, "source": "GDACS"}]
    eonet = [{"hazard": "FIRE", "lat": 18.1, "lon": 99.1, "source": "NASA EONET"},
             {"hazard": "FIRE", "lat": 10.0, "lon": 99.0, "source": "NASA EONET"}]
    merged, removed = di.dedupe_events(gdacs, eonet)
    assert removed == 1 and len(merged) == 2
    assert merged[0]["also_reported_by"] == ["NASA EONET"]


def test_events_near_route():
    events = [{"lat": 13.1, "lon": 100.1}, {"lat": 40.0, "lon": 140.0}]
    near = di.events_near(events, [(13.0, 100.0, 0)], 300)
    assert len(near) == 1 and near[0]["distance_to_route_km"] < 20


def test_grid_points_limit():
    step, points = di.grid_points(-180, -60, 180, 70, 1.5)
    assert len(points) <= 300 and step >= 15


# ---------------- Module 06: Disaster RAG ----------------
def test_thai_tokenizer_makes_bigrams():
    assert "น้" in tokenize("น้ำท่วม")


def test_rag_finds_flood_guidance_in_thai():
    rag = DisasterRAG()
    result = rag.search("น้ำท่วมบ้าน ต้องทำอย่างไร", ["FLOOD"], "th")
    assert result["evidence_found"]
    assert result["passages"][0]["document_id"] == "flood"


def test_rag_english_earthquake():
    result = DisasterRAG().search("what to do during an earthquake", ["EARTHQUAKE"], "en")
    assert result["passages"][0]["document_id"] == "earthquake"
    assert result["passages"][0]["lang"] == "en"


def test_rag_ignores_expired_documents():
    result = DisasterRAG().search("flood", ["FLOOD"], "en", today=date(2030, 1, 1))
    assert not result["evidence_found"]


# ---------------- Module 07: LLM answer verification ----------------
def test_llm_verify_blocks_contradiction():
    ok, _ = llm.verify("You can travel normally.", "AVOID", "heavy rain at km 120")
    assert not ok


def test_llm_verify_blocks_invented_numbers():
    ok, why = llm.verify("Heavy rain of 80 mm/h is expected.", "DELAY", "rain 35.0 mm/h at km 120")
    assert not ok and "80" in why


def test_llm_verify_accepts_grounded_text():
    ok, _ = llm.verify("Please delay: rain 35.0 mm/h near km 120.", "DELAY", "rain 35.0 mm/h at km 120")
    assert ok


# ---------------- Module 08 ----------------
def test_event_severity():
    assert rec.event_severity({"hazard": "EARTHQUAKE", "magnitude": 7.2}) == 4
    assert rec.event_severity({"hazard": "STORM", "alert_level": "Green", "wind_kmh": 130}) == 4
    assert rec.event_severity({"hazard": "FIRE", "alert_level": "Orange"}) == 3


def test_build_trip_response():
    route = {"route_id": "r1", "coordinates": [[100.5, 13.7], [99.0, 18.8]], "distance_km": 690, "duration_min": 520}
    seg = {"km": 300, "eta": "2026-11-15T09:00:00Z", "max_severity": 3, "top_hazard": "RAIN", "risk_level": "HIGH"}
    data = {"lang": "th", "departure": "2026-11-15T01:00:00+00:00",
            "decision": {"action": "DELAY", "risk_level": "HIGH", "confidence": 0.8, "rules_fired": ["P6"],
                         "selected_route_id": "r1", "delay_hours": 6, "emergency": True, "policy_version": "x"},
            "explanation": {"action_text": "เลื่อนการเดินทาง", "summary": "s", "reasons": ["r"]},
            "routes": [{"route": route, "eval": {"risk_level": "HIGH", "max_severity": 3, "segments": [seg]}}],
            "contacts": [{"name": "ปภ.", "phone": "1784"}]}
    resp = rec.build_trip(data)
    assert resp["action_code"] == "DELAY"
    assert resp["suggested_departure_time"].startswith("2026-11-15T07:00")
    assert resp["emergency_contacts"]
    types = [a["type"] for a in resp["ui_actions"]]
    assert types == ["FIT_BOUNDS", "ENABLE_LAYERS", "SET_TIME"]


def test_storage_subscription_and_notification(tmp_path, monkeypatch):
    import storage
    monkeypatch.setattr(storage, "DB_PATH", str(tmp_path / "test.db"))
    storage.init_db()
    sub_id = storage.add_subscription("บ้าน", 13.75, 100.5, 100, [], 3, "th")
    event = {"id": "e1", "hazard": "STORM", "title": "Storm", "lat": 14.0, "lon": 100.6}
    assert storage.last_severity(sub_id, "e1") == -1
    storage.add_notification(sub_id, event, 3, 30)
    assert storage.last_severity(sub_id, "e1") == 3
    assert storage.list_notifications()[0]["area_name"] == "บ้าน"
    assert storage.add_feedback("req1", "UNSAFE", None) == 1
    assert storage.feedback_summary()["counts"]["UNSAFE"] == 1
