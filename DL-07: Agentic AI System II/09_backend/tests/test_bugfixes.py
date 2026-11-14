# test_bugfixes.py — one test for each bug that was found and fixed (so the bugs do not come back)
# Run:  .venv\Scripts\python.exe -m pytest 09_backend\tests -q

import asyncio
import os
import sys
import time
from datetime import datetime, timedelta, timezone

import httpx
import respx

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for folder in ["04_external_data_services", "06_risk_knowledge_services", "08_recommendation_feedback",
               os.path.join("09_backend", "shared")]:
    sys.path.append(os.path.join(ROOT, folder))

import free_apis as api     # noqa: E402
import risk_rules as risk   # noqa: E402

START = datetime(2026, 11, 15, 0, 0, tzinfo=timezone.utc)
TIMES = [(START + timedelta(hours=h)).strftime("%Y-%m-%dT%H:%MZ") for h in range(6)]


# ---------------- Module 06 ----------------
def test_time_outside_forecast_is_none():
    assert risk.hour_index_or_none(TIMES, START + timedelta(hours=2)) == 2
    assert risk.hour_index_or_none(TIMES, START + timedelta(hours=30)) is None
    assert risk.nearest_hour_index(TIMES, START + timedelta(hours=30)) == 5   # still a valid index


def test_route_beyond_forecast_is_marked_not_guessed():
    fc = {"time": TIMES, "precipitation": [50] * 6, "wind_gusts_10m": [10] * 6, "visibility": [20000] * 6}
    route = {"distance_km": 100, "duration_min": 60}
    samples = [(13.0, 100.0, 0), (13.5, 100.0, 100)]
    result = risk.assess_route(route, samples, [fc, fc], START + timedelta(days=2), events=[])
    assert result["segments_without_forecast"] == 2
    assert result["segments"][0]["rain_mm_h"] is None     # not the last forecast hour
    assert result["segments"][0]["no_forecast"] is True


def test_three_watch_points_is_medium_not_high():
    assert risk.risk_from_severities([2, 2, 2, 2]) == "MEDIUM"
    assert risk.risk_from_severities([2, 3]) == "HIGH"


def test_storm_uses_forecast_track():
    storm = {"hazard": "STORM", "lat": 10.0, "lon": 130.0, "wind_kmh": 130, "title": "Typhoon X",
             "track": [{"type": "Feature", "properties": {"kind": "track"},
                        "geometry": {"type": "LineString", "coordinates": [[130.0, 10.0], [101.0, 13.5]]}}]}
    d = risk.event_distance_km(storm, 13.5, 100.9)
    assert d < 20                                          # the track passes close to this point
    assert risk.event_severity_at_distance(storm, d) == 4


# ---------------- Module 04 ----------------
@respx.mock
def test_fetch_json_does_not_retry_client_errors():
    route = respx.get("https://api.open-meteo.com/v1/forecast").mock(return_value=httpx.Response(400, json={}))
    try:
        asyncio.run(api.fetch_json("open-meteo", "https://api.open-meteo.com/v1/forecast"))
        assert False, "should raise"
    except RuntimeError:
        pass
    assert route.call_count == 1


@respx.mock
def test_fetch_json_retries_server_errors():
    route = respx.get("https://api.open-meteo.com/v1/forecast").mock(
        side_effect=[httpx.Response(503), httpx.Response(200, json={"ok": True})])
    assert asyncio.run(api.fetch_json("open-meteo", "https://api.open-meteo.com/v1/forecast")) == {"ok": True}
    assert route.call_count == 2


def test_nominatim_calls_are_spaced_even_in_parallel():
    api._next_nominatim_time = 0.0

    async def three_calls():
        start = time.time()
        await asyncio.gather(api.wait_for_nominatim(), api.wait_for_nominatim(), api.wait_for_nominatim())
        return time.time() - start

    assert asyncio.run(three_calls()) >= 2.0     # 3 calls need at least ~2.2 s


def test_cache_does_not_grow_forever():
    api._cache.clear()
    for i in range(5100):
        api.cache_set(f"k{i}", i, 60)
    assert len(api._cache) <= 5001
    api._cache.clear()


def test_empty_list_is_cached():
    api.cache_set("quakes:2.5_week", [], 60)
    assert api.cache_get("quakes:2.5_week") == []
    api._cache.clear()


# ---------------- Module 08 ----------------
def test_storage_closes_connections(tmp_path, monkeypatch):
    import storage
    db_file = tmp_path / "close.db"
    monkeypatch.setattr(storage, "DB_PATH", str(db_file))
    storage.init_db()
    storage.add_feedback("r1", "HELPFUL", None)
    storage.feedback_summary()
    os.remove(db_file)          # on Windows this fails if a connection is still open
    assert not db_file.exists()
