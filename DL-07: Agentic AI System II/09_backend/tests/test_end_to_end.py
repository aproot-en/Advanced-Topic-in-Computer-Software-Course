# test_end_to_end.py — tests the whole system 02 -> 03 -> 04 -> 05 -> 06 -> 07 -> 08 without starting servers
# All services are loaded into one process and call each other through httpx.ASGITransport instead of real HTTP
# Needs internet (calls the real free APIs) — skipped when offline
#
# Run:  .venv\Scripts\python.exe -m pytest 09_backend\tests\test_end_to_end.py -q

import asyncio
import importlib.util
import os
import socket
import sys

import httpx
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(ROOT, "09_backend", "shared"))

import service_client as svc   # noqa: E402

SERVERS = {
    "api": "02_api_/api_server.py", "agent": "03_travel_ai_agent/agent_server.py",
    "eds": "04_external_data_services/eds_server.py", "di": "05_data_integration/di_server.py",
    "rks": "06_risk_knowledge_services/rks_server.py", "dle": "07_decision_llm_engine/dle_server.py",
    "rf": "08_recommendation_feedback/rf_server.py",
}


def internet_ok():
    try:
        socket.create_connection(("api.open-meteo.com", 443), timeout=5).close()
        return True
    except OSError:
        return False


pytestmark = pytest.mark.skipif(not internet_ok(), reason="ต้องต่ออินเทอร์เน็ต")


@pytest.fixture(scope="module")
def apps(tmp_path_factory):
    os.environ["RF_DB_PATH"] = str(tmp_path_factory.mktemp("rf") / "test.db")
    loaded = {}
    for name, path in SERVERS.items():
        spec = importlib.util.spec_from_file_location(f"e2e_{name}", os.path.join(ROOT, path))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        loaded[name] = module.app
    return loaded


@pytest.fixture(autouse=True)
def route_calls_in_process(apps, monkeypatch):
    """Replace HTTP calls between services with in-process app calls."""
    original = httpx.AsyncClient

    async def call(service, method, path, params=None, json=None, timeout=60):
        transport = httpx.ASGITransport(app=apps[service])
        async with original(transport=transport, base_url="http://test", timeout=timeout) as client:
            r = await client.request(method, path, params=params, json=json)
        if r.status_code >= 400:
            raise svc.ServiceError(service, r.text[:200], r.status_code)
        return r.json()

    async def is_up(service):
        return service in apps

    monkeypatch.setattr(svc, "call", call)
    monkeypatch.setattr(svc, "is_up", is_up)


def api_request(apps, method, path, **kwargs):
    async def run():
        transport = httpx.ASGITransport(app=apps["api"])
        async with httpx.AsyncClient(transport=transport, base_url="http://test", timeout=120) as client:
            return await client.request(method, path, **kwargs)
    return asyncio.run(run())


def test_health_shows_all_services(apps):
    r = api_request(apps, "GET", "/api/health")
    assert r.status_code == 200
    assert set(r.json()["services"].values()) == {"up"}


def test_trip_bangkok_to_chiang_mai(apps):
    r = api_request(apps, "POST", "/api/trip", json={"origin": "กรุงเทพมหานคร", "destination": "เชียงใหม่", "lang": "th"})
    assert r.status_code == 200, r.text
    d = r.json()
    assert d["response_type"] == "RECOMMENDATION"
    assert d["action_code"] in ("NORMAL", "CHANGE_ROUTE", "DELAY", "AVOID")
    assert d["routes"] and d["routes"][0]["segments"]
    assert [s["step"] for s in d["steps"]][-1] == "08:recommendation"
    assert d["ui_actions"][0]["type"] == "FIT_BOUNDS"
    print("\nTRIP:", d["action_code"], d["risk_level"], d["summary"])


def test_chat_hazard_info(apps):
    r = api_request(apps, "POST", "/api/chat", json={"text": "พรุ่งนี้ฝนจะตกที่ภูเก็ตไหม", "lang": "th"})
    d = r.json()
    assert d["response_type"] == "HAZARD_INFO", d
    assert "ภูเก็ต" in d["summary"]
    print("\nHAZARD:", d["summary"], "| citations:", [c["evidence_id"] for c in d["citations"]])


def test_chat_latest_earthquakes(apps):
    d = api_request(apps, "POST", "/api/chat", json={"text": "latest earthquakes", "lang": "en"}).json()
    assert d["response_type"] == "HAZARD_INFO"
    assert any("cannot be predicted" in r for r in d["reasons"])


def test_chat_emergency_uses_rag_steps(apps):
    d = api_request(apps, "POST", "/api/chat", json={"text": "น้ำเข้าบ้านแล้ว ต้องทำยังไง", "lang": "th",
                                                    "map_lat": 13.99, "map_lon": 100.62}).json()
    assert d["response_type"] == "EMERGENCY"
    assert any(c["phone"] == "1784" for c in d["emergency_contacts"])
    assert d["citations"] and d["citations"][0]["evidence_id"].startswith("flood")
    print("\nEMERGENCY steps:", d["immediate_actions"][:2], "| nearby:", len(d["nearby_places"]))


def test_point_forecast_and_grid(apps):
    d = api_request(apps, "GET", "/api/forecast/point", params={"lat": 18.79, "lon": 98.98}).json()
    assert d["hazards"] and d["forecast"]["time"]
    g = api_request(apps, "GET", "/api/map/grid", params={"variable": "wind", "west": 95, "south": 5,
                                                         "east": 106, "north": 21, "zoom": 5}).json()
    assert g["cells"] and "dir" in g["cells"][0]


def test_subscription_flow(apps):
    r = api_request(apps, "POST", "/api/subscriptions", json={"name": "บ้าน", "lat": 13.75, "lon": 100.5})
    assert r.status_code == 200
    subs = api_request(apps, "GET", "/api/subscriptions").json()
    assert subs[0]["name"] == "บ้าน"
    assert api_request(apps, "DELETE", f"/api/subscriptions/{subs[0]['id']}").status_code == 200
    fb = api_request(apps, "POST", "/api/feedback", json={"request_id": "x", "category": "UNSAFE"}).json()
    assert fb["sent_to_review"] is True


def test_alerts_endpoint(apps):
    d = api_request(apps, "GET", "/api/alerts").json()
    assert "alerts" in d
    assert all(a["severity"] >= 3 for a in d["alerts"])
