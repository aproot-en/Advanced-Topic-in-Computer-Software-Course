# integration.py
# Module 05 (logic): combine many sources into one data set (Clean / Combine)
#   - pick points along the route every N km (route sampling)
#   - remove duplicate events reported by several sources (GDACS and NASA EONET)
#   - keep only events near the route
#   - add data-quality flags (missing / stale) and build a versioned snapshot

import json
import math
import os
import uuid
from datetime import datetime, timedelta, timezone

SNAPSHOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "snapshots")
SCHEMA_VERSION = "context-1.0"
_snapshots = {}   # also keep recent snapshots in memory


def distance_km(lat1, lon1, lat2, lon2):
    r = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def sample_route(coordinates, every_km=25, max_points=40):
    """Pick a point every `every_km` km along the route; returns [(lat, lon, km_from_start), ...].
    `coordinates` use GeoJSON order [lon, lat]."""
    total = 0
    for i in range(1, len(coordinates)):
        total += distance_km(coordinates[i - 1][1], coordinates[i - 1][0], coordinates[i][1], coordinates[i][0])
    every_km = max(every_km, total / max_points)
    samples = [(coordinates[0][1], coordinates[0][0], 0.0)]
    run, next_mark = 0, every_km
    for i in range(1, len(coordinates)):
        lon1, lat1 = coordinates[i - 1]
        lon2, lat2 = coordinates[i]
        run += distance_km(lat1, lon1, lat2, lon2)
        if run >= next_mark:
            samples.append((lat2, lon2, round(run, 1)))
            next_mark += every_km
    last = coordinates[-1]
    if len(coordinates) > 1:
        samples.append((last[1], last[0], round(run, 1)))
    return samples


def dedupe_events(gdacs, eonet):
    """If EONET and GDACS report the same hazard type within 50 km, keep only the GDACS event."""
    result = list(gdacs)
    removed = 0
    for e in eonet:
        duplicate = None
        for g in gdacs:
            if g["hazard"] != e["hazard"]:
                continue
            if distance_km(g["lat"], g["lon"], e["lat"], e["lon"]) <= 50 or same_storm_name(g, e):
                duplicate = g
                break
        if duplicate:
            duplicate.setdefault("also_reported_by", []).append(e["source"])
            removed += 1
        else:
            result.append(e)
    return result, removed


def same_storm_name(a, b):
    """True if both titles contain the same storm name, e.g. 'Tropical Cyclone CEMPAKA-26' and 'Typhoon Cempaka'."""
    if a["hazard"] != "STORM":
        return False
    words_a = {w for w in a.get("title", "").replace("-", " ").upper().split() if len(w) >= 4}
    words_b = {w for w in b.get("title", "").replace("-", " ").upper().split() if len(w) >= 4}
    common_words = {"TROPICAL", "CYCLONE", "TYPHOON", "STORM", "DEPRESSION", "HURRICANE", "SUPER"}
    return bool((words_a & words_b) - common_words)


def events_near(events, samples, max_km=300):
    """Keep only events close to at least one point on the route."""
    near = []
    for e in events:
        d = min(distance_km(e["lat"], e["lon"], s[0], s[1]) for s in samples)
        if d <= max_km:
            near.append({**e, "distance_to_route_km": round(d, 1)})
    return near


def forecast_quality(forecasts, departure, duration_min):
    """Check forecast quality: is it complete, and does it cover the travel time?"""
    flags = []
    missing = sum(1 for f in forecasts if not f or not f.get("time"))
    if missing:
        flags.append(f"MISSING:{missing}")
    if forecasts and forecasts[0] and forecasts[0].get("time"):
        last = datetime.fromisoformat(forecasts[0]["time"][-1].replace("Z", "+00:00"))
        if departure + timedelta(minutes=duration_min) > last:
            flags.append("INCOMPLETE:travel_time_beyond_forecast")
    return flags


def make_snapshot(kind, payload, quality_flags, degraded):
    """Build an auditable snapshot (id / version / created time / data quality)."""
    score = 1 - 0.15 * len(quality_flags) - 0.2 * len(degraded)
    snap = {
        "context_id": str(uuid.uuid4()),
        "kind": kind,
        "schema_version": SCHEMA_VERSION,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "data_quality": {"flags": quality_flags, "degraded_services": degraded, "score": round(max(0.0, score), 2)},
    }
    snap.update(payload)

    # keep the last 100 snapshots in memory
    _snapshots[snap["context_id"]] = snap
    if len(_snapshots) > 100:
        oldest_id = list(_snapshots)[0]
        del _snapshots[oldest_id]

    # save a short summary to disk (for checking later); big forecast data is not saved
    summary = {
        "context_id": snap["context_id"], "kind": kind, "created_at": snap["created_at"],
        "data_quality": snap["data_quality"], "lineage": payload.get("lineage", []),
        "route_count": len(payload.get("routes", [])), "event_count": len(payload.get("events", [])),
    }
    try:
        os.makedirs(SNAPSHOT_DIR, exist_ok=True)
        with open(os.path.join(SNAPSHOT_DIR, snap["context_id"] + ".json"), "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False)
        clean_old_snapshots()
    except OSError:
        pass   # saving the summary is optional
    return snap


def get_snapshot(context_id):
    return _snapshots.get(context_id)


def clean_old_snapshots(keep=50):
    files = sorted((os.path.join(SNAPSHOT_DIR, f) for f in os.listdir(SNAPSHOT_DIR)), key=os.path.getmtime)
    for path in files[:-keep]:
        os.remove(path)


# ---------------- Forecast grid for the map ----------------
def grid_step(zoom):
    for z, step in [(2, 20), (3, 10), (4, 5), (5, 3), (6, 2), (7, 1), (8.5, 0.5)]:
        if zoom < z:
            return step
    return 0.25


def grid_points(west, south, east, north, zoom, max_points=150):
    south, north = max(south, -70), min(north, 70)
    if east - west >= 300:
        west, east = -180, 180
    step = grid_step(zoom)
    while ((north - south) / step + 1) * ((east - west) / step + 1) > max_points:
        step *= 2
    points = []
    lat = math.floor(south / step) * step + step / 2
    while lat <= north + step / 2:
        lon = math.floor(west / step) * step + step / 2
        while lon <= east + step / 2:
            points.append((round(lat, 3), round(((lon + 180) % 360) - 180, 3)))
            lon += step
        lat += step
    return step, points
