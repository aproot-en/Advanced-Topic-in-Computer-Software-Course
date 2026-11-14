# test_quota.py — the free forecast API has a quota (HTTP 429). These tests check that we use it carefully.
# (No real API calls: respx fakes the answers.)
# Run:  .venv\Scripts\python.exe -m pytest 09_backend\tests -q

import asyncio
import os
import sys

import httpx
import respx

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for folder in ["04_external_data_services", "05_data_integration"]:
    sys.path.append(os.path.join(ROOT, folder))

import free_apis as api       # noqa: E402
import integration as di      # noqa: E402

URL = "https://api.open-meteo.com/v1/forecast"


def fake_answer(request):
    """Answer like Open-Meteo: one item per requested point."""
    count = len(request.url.params["latitude"].split(","))
    item = {"hourly": {"time": ["2026-11-15T00:00"], "precipitation": [1.0]}}
    return httpx.Response(200, json=[item] * count if count > 1 else item)


def reset():
    api._cache.clear()
    api._blocked_until.clear()


@respx.mock
def test_each_point_is_cached_so_panning_only_downloads_new_points():
    reset()
    route = respx.get(URL).mock(side_effect=fake_answer)
    asyncio.run(api.get_forecast_many([(13.0, 100.0), (14.0, 100.0)], "precipitation"))
    asyncio.run(api.get_forecast_many([(14.0, 100.0), (15.0, 100.0)], "precipitation"))   # map moved a bit
    assert route.call_count == 2
    second_request = route.calls[1].request
    assert second_request.url.params["latitude"] == "15.0"      # only the new point was downloaded


@respx.mock
def test_429_pauses_the_api_and_old_data_is_used():
    reset()
    respx.get(URL).mock(side_effect=fake_answer)
    asyncio.run(api.get_forecast_many([(13.0, 100.0)], "precipitation"))
    # make the cached data "expired", then the API starts answering 429
    for key in list(api._cache):
        api._cache[key] = (0, api._cache[key][1])
    respx.get(URL).mock(return_value=httpx.Response(429, text='{"reason":"Hourly API request limit exceeded"}'))
    rows = asyncio.run(api.get_forecast_many([(13.0, 100.0)], "precipitation"))
    assert rows[0]["precipitation"] == [1.0]                  # old data used as backup
    assert api._blocked_until["open-meteo"] > 0                # API paused, no more calls for a while
    reset()


@respx.mock
def test_paused_api_is_not_called():
    reset()
    route = respx.get(URL).mock(side_effect=fake_answer)
    import time
    api._blocked_until["open-meteo"] = time.time() + 600
    try:
        asyncio.run(api.get_forecast_many([(20.0, 100.0)], "precipitation"))
        assert False, "should raise"
    except RuntimeError as e:
        assert "429" in str(e)
    assert route.call_count == 0
    reset()


def test_world_grid_is_small():
    step, points = di.grid_points(-180, -60, 180, 70, 1.6)
    assert len(points) <= 150


def test_same_storm_from_two_sources_is_merged():
    gdacs = [{"hazard": "STORM", "lat": 30.2, "lon": 154.1, "title": "Tropical Cyclone CEMPAKA-26", "source": "GDACS"}]
    eonet = [{"hazard": "STORM", "lat": 21.0, "lon": 140.2, "title": "Typhoon Cempaka", "source": "NASA EONET"},
             {"hazard": "STORM", "lat": 10.0, "lon": 120.0, "title": "Tropical Storm Other", "source": "NASA EONET"}]
    merged, removed = di.dedupe_events(gdacs, eonet)
    assert removed == 1 and len(merged) == 2
