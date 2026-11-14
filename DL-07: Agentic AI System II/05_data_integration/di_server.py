# di_server.py
# Module 05: Data Integration — runs on port 8003
# request -> fetch data from Module 04 -> clean/combine -> return a snapshot for Module 06 risk assessment
#
# Run:  python 05_data_integration/di_server.py

import asyncio
import os
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path += [HERE, os.path.join(ROOT, "09_backend", "shared")]

from fastapi import Query             # noqa: E402
from pydantic import BaseModel        # noqa: E402

import integration as di              # noqa: E402
import service_client as svc          # noqa: E402
from common import create_app, fail   # noqa: E402

app = create_app("ProJ-7 Data Integration (Module 05)", "data_integration")


class RouteIntegrationRequest(BaseModel):
    routes: list[dict]          # from Module 04 /routes: route_id, coordinates, distance_km, duration_min
    departure: str              # ISO UTC


class PointIntegrationRequest(BaseModel):
    lat: float
    lon: float


async def try_get(name, coro, degraded, default=None):
    """If a source fails, do not crash; record that this data is missing."""
    try:
        return await coro
    except svc.ServiceError:
        degraded.append(name)
        return default


@app.post("/integrate/route")
async def integrate_route(req: RouteIntegrationRequest):
    if not req.routes:
        fail(422, "VALIDATION_FAILED", "ต้องมีอย่างน้อย 1 เส้นทาง")
    departure = datetime.fromisoformat(req.departure.replace("Z", "+00:00"))
    degraded = []

    # 1) sample points on every route, then request the forecast once
    all_samples = [di.sample_route(r["coordinates"]) for r in req.routes]
    points = [[s[0], s[1]] for samples in all_samples for s in samples]
    forecasts, gdacs, eonet, quakes = await asyncio.gather(
        try_get("weather", svc.post("eds", "/weather/forecast-many", {"points": points}), degraded),
        try_get("gdacs", svc.get("eds", "/events/gdacs"), degraded, []),
        try_get("nasa-eonet", svc.get("eds", "/events/eonet"), degraded, []),
        try_get("usgs", svc.get("eds", "/earthquakes", {"window": "7d"}), degraded, []),
    )
    if forecasts is None:
        fail(503, "UPSTREAM_UNAVAILABLE", "ไม่มีข้อมูลพยากรณ์อากาศ")

    # 2) combine + remove duplicate events
    events, removed = di.dedupe_events(gdacs, eonet)

    # 3) split forecasts back per route + keep events near the route
    routes_out, i = [], 0
    flags = []
    for route, samples in zip(req.routes, all_samples):
        fc = forecasts[i:i + len(samples)]
        i += len(samples)
        flags += di.forecast_quality(fc, departure, route["duration_min"])
        routes_out.append({"route": route, "samples": samples, "forecasts": fc})
    primary_samples = all_samples[0]
    route_events = di.events_near(events, primary_samples, 400)   # used by Module 06 for the risk check
    near_events = di.events_near(events, primary_samples, 300)    # shown on the map
    near_quakes = di.events_near(quakes, primary_samples, 300)
    if removed:
        flags.append(f"DEDUPED:{removed}")

    return di.make_snapshot("route", {
        "departure": req.departure, "routes": routes_out,
        "events": route_events, "near_events": near_events, "quakes": near_quakes,
        "lineage": ["open-meteo", "gdacs", "nasa-eonet", "usgs", "osrm"],
    }, sorted(set(flags)), degraded)


@app.post("/integrate/point")
async def integrate_point(req: PointIntegrationRequest):
    degraded = []
    forecast, air, flood, quakes, gdacs, eonet = await asyncio.gather(
        try_get("weather", svc.get("eds", "/weather/forecast", {"lat": req.lat, "lon": req.lon}), degraded),
        try_get("air-quality", svc.get("eds", "/air", {"lat": req.lat, "lon": req.lon}), degraded),
        try_get("flood", svc.get("eds", "/flood", {"lat": req.lat, "lon": req.lon}), degraded),
        try_get("usgs", svc.get("eds", "/earthquakes/near", {"lat": req.lat, "lon": req.lon}), degraded, []),
        try_get("gdacs", svc.get("eds", "/events/gdacs"), degraded, []),
        try_get("nasa-eonet", svc.get("eds", "/events/eonet"), degraded, []),
    )
    if forecast is None:
        fail(503, "UPSTREAM_UNAVAILABLE", "ไม่มีข้อมูลพยากรณ์อากาศ")
    events, _ = di.dedupe_events(gdacs, eonet)
    events = di.events_near(events, [(req.lat, req.lon, 0)], 500)
    return di.make_snapshot("point", {
        "lat": req.lat, "lon": req.lon, "forecast": forecast, "air": air, "flood": flood,
        "quakes": quakes, "events": events, "lineage": ["open-meteo", "usgs", "gdacs", "nasa-eonet"],
    }, [], degraded)


@app.get("/context/{context_id}")
async def get_context(context_id: str):
    snap = di.get_snapshot(context_id)
    if not snap:
        fail(404, "NOT_FOUND", "ไม่พบ snapshot (อาจหมดอายุแล้ว)")
    return snap


@app.get("/hazards/events")
async def hazard_events(window: str = "7d"):
    """Global hazard events, combined and de-duplicated (for the map)."""
    degraded = []
    quakes, gdacs, eonet = await asyncio.gather(
        try_get("usgs", svc.get("eds", "/earthquakes", {"window": window}), degraded, []),
        try_get("gdacs", svc.get("eds", "/events/gdacs"), degraded, []),
        try_get("nasa-eonet", svc.get("eds", "/events/eonet"), degraded, []),
    )
    events, removed = di.dedupe_events(gdacs, eonet)
    return {"earthquakes": quakes, "events": events, "deduplicated": removed, "degraded": degraded,
            "fetched_at": datetime.now(timezone.utc).isoformat()}


@app.get("/map/grid")
async def map_grid(variable: str = "temperature", west: float = -180, south: float = -60,
                   east: float = 180, north: float = 70, zoom: float = 2):
    """Forecast grid (instead of map tiles) for coloring the map."""
    keys = {"temperature": "temperature_2m", "precipitation": "precipitation", "wind": "wind_speed_10m",
            "gust": "wind_gusts_10m", "pm25": "pm2_5"}
    if variable not in keys:
        fail(422, "VALIDATION_FAILED", "variable ไม่ถูกต้อง")
    step, points = di.grid_points(west, south, east, north, zoom)
    if variable == "pm25":
        rows = await svc.post("eds", "/air/pm25-many", {"points": points})
    else:
        rows = await svc.post("eds", "/weather/forecast-many", {
            "points": points, "variables": "temperature_2m,precipitation,wind_speed_10m,wind_direction_10m,wind_gusts_10m"})
    cells = []
    for (lat, lon), row in zip(points, rows):
        cell = {"lat": lat, "lon": lon, "values": row.get(keys[variable], [])}
        if variable == "wind":
            cell["dir"] = row.get("wind_direction_10m", [])
        cells.append(cell)
    return {"variable": variable, "step": step, "times": rows[0]["time"] if rows else [], "cells": cells,
            "source": "Open-Meteo"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", "8003")))
