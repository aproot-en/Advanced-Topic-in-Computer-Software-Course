# eds_server.py
# Module 04: External Data Services — runs on port 8002
# Internal API so other modules can get weather / transport / hazard data without knowing which provider it comes from
# (the functions that call the free APIs are in free_apis.py)
#
# Run:  python 04_external_data_services/eds_server.py

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path += [HERE, os.path.join(ROOT, "09_backend", "shared")]

from fastapi import Query           # noqa: E402
from pydantic import BaseModel      # noqa: E402

import free_apis as api             # noqa: E402
from common import create_app       # noqa: E402

app = create_app("ProJ-7 External Data Services (Module 04)", "external_data_services")


class PointsRequest(BaseModel):
    points: list[tuple[float, float]]          # [(lat, lon), ...]
    variables: str = api.HOURLY_VARS


class RouteRequest(BaseModel):
    origin: tuple[float, float]                # (lat, lon)
    destination: tuple[float, float]


# ---------------- Weather / rain / wind ----------------
@app.get("/weather/forecast")
async def weather_forecast(lat: float = Query(ge=-90, le=90), lon: float = Query(ge=-180, le=180)):
    return await api.get_forecast(lat, lon)


@app.post("/weather/forecast-many")
async def weather_forecast_many(req: PointsRequest):
    return await api.get_forecast_many(req.points[:600], req.variables)


@app.get("/air")
async def air(lat: float = Query(ge=-90, le=90), lon: float = Query(ge=-180, le=180)):
    return await api.get_air_quality(lat, lon)


@app.post("/air/pm25-many")
async def air_many(req: PointsRequest):
    return await api.get_pm25_many(req.points[:600])


@app.get("/flood")
async def flood(lat: float = Query(ge=-90, le=90), lon: float = Query(ge=-180, le=180)):
    return await api.get_flood(lat, lon)


@app.get("/radar")
async def radar():
    return await api.get_radar_frames()


# ---------------- Hazards ----------------
@app.get("/earthquakes")
async def earthquakes(window: str = "7d"):
    return await api.get_earthquakes(window)


@app.get("/earthquakes/near")
async def earthquakes_near(lat: float, lon: float, radius_km: float = 300, days: int = 7):
    return await api.get_earthquakes_near(lat, lon, radius_km, days)


@app.get("/events/gdacs")
async def gdacs():
    return await api.get_gdacs_events()


@app.get("/events/eonet")
async def eonet():
    return await api.get_eonet_events()


# ---------------- Places / routes ----------------
@app.get("/places/search")
async def places_search(q: str = Query(min_length=1, max_length=100), lang: str = "th"):
    return await api.search_place(q, lang)


@app.get("/places/reverse")
async def places_reverse(lat: float, lon: float, lang: str = "th"):
    return await api.reverse_place(lat, lon, lang)


@app.get("/places/nearby")
async def places_nearby(lat: float, lon: float):
    return await api.get_nearby_places(lat, lon)


@app.post("/routes")
async def routes(req: RouteRequest):
    return await api.get_routes(req.origin, req.destination)


# ---------------- Provider status ----------------
@app.get("/providers/health")
async def providers_health():
    return api.provider_status


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", "8002")))
