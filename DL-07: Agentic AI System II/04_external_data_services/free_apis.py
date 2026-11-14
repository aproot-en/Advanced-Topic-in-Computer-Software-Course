# free_apis.py
# Module 04 (simple version): functions that fetch data from free public APIs (no API key needed)
#
#   Open-Meteo      weather, rain, wind forecast / PM2.5 / river discharge / place search
#   USGS            earthquakes
#   GDACS           storms, floods, wildfires, volcanoes, droughts (global)
#   NASA EONET      wildfires, storms, volcanoes
#   RainViewer      rain radar images
#   OSRM            driving routes (demo server)
#   Nominatim       place search / reverse geocoding / nearby hospitals (max 1 request/second, see wait_for_nominatim)

import asyncio
import time
from datetime import datetime, timedelta, timezone

import httpx

HEADERS = {"User-Agent": "ProJ7-AgentII-student-project/0.1"}

# ---------- Simple cache: keep results in a dict so we don't call the APIs too often ----------
_cache = {}


def cache_get(key, allow_expired=False):
    """Return the cached value. With allow_expired=True old data is returned too (used as a backup)."""
    if key in _cache:
        expire, value = _cache[key]
        if allow_expired or time.time() < expire:
            return value
    return None


def cache_set(key, value, seconds):
    if len(_cache) > 5000:
        # remove items that expired more than 6 hours ago; if still too many, start again
        too_old = time.time() - 6 * 3600
        for old_key in [k for k, (expire, _) in _cache.items() if expire < too_old]:
            del _cache[old_key]
        if len(_cache) > 5000:
            _cache.clear()
    _cache[key] = (time.time() + seconds, value)


# ---------- Status of each API, shown on the web page when one is down ----------
provider_status = {}
_blocked_until = {}     # API name -> time when we may call it again (after HTTP 429 "too many requests")


_next_nominatim_time = 0.0


async def wait_for_nominatim():
    """Nominatim allows max 1 request per second. Each caller books the next free time slot."""
    global _next_nominatim_time
    now = time.time()
    my_time = max(now, _next_nominatim_time)
    _next_nominatim_time = my_time + 1.1
    await asyncio.sleep(my_time - now)


async def fetch_json(name, url, params=None, method="GET", data=None):
    """Call an API and return JSON. Retry once, but only for temporary problems
    (network error, timeout, HTTP 429 or 5xx). Other errors (e.g. 400) are not retried."""
    if time.time() < _blocked_until.get(name, 0):
        wait_min = int((_blocked_until[name] - time.time()) / 60) + 1
        raise RuntimeError(f"{name} ใช้งานไม่ได้: over quota (HTTP 429), try again in ~{wait_min} min")
    error = ""
    for attempt in range(2):
        if name == "nominatim":
            await wait_for_nominatim()
        try:
            async with httpx.AsyncClient(headers=HEADERS, timeout=20) as client:
                if method == "POST":
                    r = await client.post(url, data=data)
                else:
                    r = await client.get(url, params=params)
        except httpx.HTTPError as e:
            error = f"{e.__class__.__name__}: {str(e)[:100]}"
        else:
            if r.status_code < 400:
                try:
                    result = r.json()
                except ValueError:
                    error = "response is not JSON"
                    break
                provider_status[name] = {"status": "UP", "time": now_utc().isoformat()}
                return result
            error = f"HTTP {r.status_code}"
            if r.status_code == 429:
                # over the free quota: pause this API (Open-Meteo says if it is a minute/hour/day limit)
                text = r.text.lower()
                pause = 1800 if "daily" in text else 600 if "hourly" in text else 60
                _blocked_until[name] = time.time() + pause
                error = f"HTTP 429 over quota ({r.text[:80]})"
                break
            if r.status_code < 500:
                break   # client error: trying again will not help
        if attempt == 0:
            await asyncio.sleep(1)
    provider_status[name] = {"status": "DOWN", "time": now_utc().isoformat(), "error": error}
    raise RuntimeError(f"{name} ใช้งานไม่ได้: {error}")


def now_utc():
    return datetime.now(timezone.utc)


def to_utc_list(times):
    """Open-Meteo returns times like '2026-11-14T00:00' (GMT); convert to ISO with Z."""
    return [t + ":00Z" if len(t) == 16 else t for t in times]


# =====================================================================
# Open-Meteo: weather forecast
# =====================================================================
HOURLY_VARS = ("temperature_2m,apparent_temperature,relative_humidity_2m,precipitation,"
               "precipitation_probability,weather_code,wind_speed_10m,wind_gusts_10m,"
               "wind_direction_10m,visibility")


async def get_forecast(lat, lon):
    """Hourly forecast for one point (past 1 day + next 3 days)."""
    key = f"forecast:{lat:.2f}:{lon:.2f}"
    data = cache_get(key)
    if data:
        return data
    try:
        raw = await fetch_json("open-meteo", "https://api.open-meteo.com/v1/forecast", {
            "latitude": round(lat, 3), "longitude": round(lon, 3), "hourly": HOURLY_VARS,
            "timezone": "GMT", "past_days": 1, "forecast_days": 3, "wind_speed_unit": "kmh",
        })
    except RuntimeError:
        old = cache_get(key, allow_expired=True)    # old data is better than nothing
        if old is None:
            raise
        return old
    hourly = raw["hourly"]
    hourly["time"] = to_utc_list(hourly["time"])
    cache_set(key, hourly, 900)  # 15 minutes
    return hourly


async def get_many_points(name, url, points, variables, extra_params=None):
    """Hourly data for many points [(lat, lon), ...].
    Each point is cached on its own (30 min), so moving the map only downloads new points.
    If the API is down or over quota, old cached data is used as a backup."""
    results = {}
    missing = []
    for lat, lon in points:
        key = f"pt:{url}:{variables}:{lat:.2f}:{lon:.2f}"
        cached = cache_get(key)
        if cached is not None:
            results[(lat, lon)] = cached
        else:
            missing.append((lat, lon))

    for i in range(0, len(missing), 100):        # max 100 points per request
        batch = missing[i:i + 100]
        params = {
            "latitude": ",".join(str(round(p[0], 2)) for p in batch),
            "longitude": ",".join(str(round(p[1], 2)) for p in batch),
            "hourly": variables, "timezone": "GMT", "past_days": 1, "forecast_days": 3,
        }
        params.update(extra_params or {})
        try:
            raw = await fetch_json(name, url, params)
        except RuntimeError:
            # use old data if we have it for every point, otherwise report the problem
            for lat, lon in batch:
                old = cache_get(f"pt:{url}:{variables}:{lat:.2f}:{lon:.2f}", allow_expired=True)
                if old is None:
                    raise
                results[(lat, lon)] = old
            continue
        if isinstance(raw, dict):  # with a single point the API returns a dict, not a list
            raw = [raw]
        for (lat, lon), item in zip(batch, raw):
            hourly = item["hourly"]
            hourly["time"] = to_utc_list(hourly["time"])
            cache_set(f"pt:{url}:{variables}:{lat:.2f}:{lon:.2f}", hourly, 1800)
            results[(lat, lon)] = hourly
    return [results[p] for p in points]


async def get_forecast_many(points, variables=HOURLY_VARS):
    """Weather forecast for many points."""
    points = [(round(lat, 2), round(lon, 2)) for lat, lon in points]
    return await get_many_points("open-meteo", "https://api.open-meteo.com/v1/forecast", points, variables,
                                 {"wind_speed_unit": "kmh"})


async def get_air_quality(lat, lon):
    key = f"aq:{lat:.2f}:{lon:.2f}"
    data = cache_get(key)
    if data:
        return data
    raw = await fetch_json("open-meteo-air", "https://air-quality-api.open-meteo.com/v1/air-quality", {
        "latitude": round(lat, 2), "longitude": round(lon, 2), "hourly": "pm2_5,pm10",
        "timezone": "GMT", "past_days": 1, "forecast_days": 3,
    })
    hourly = raw["hourly"]
    hourly["time"] = to_utc_list(hourly["time"])
    cache_set(key, hourly, 1800)
    return hourly


async def get_pm25_many(points):
    """PM2.5 forecast for many points."""
    points = [(round(lat, 2), round(lon, 2)) for lat, lon in points]
    return await get_many_points("open-meteo-air", "https://air-quality-api.open-meteo.com/v1/air-quality",
                                 points, "pm2_5")


async def get_flood(lat, lon):
    """River discharge (GloFAS) for the next 7 days, compared with the past 2 years."""
    key = f"flood:{lat:.2f}:{lon:.2f}"
    data = cache_get(key)
    if data:
        return data
    today = now_utc().date()
    raw = await fetch_json("open-meteo-flood", "https://flood-api.open-meteo.com/v1/flood", {
        "latitude": round(lat, 2), "longitude": round(lon, 2), "daily": "river_discharge",
        "start_date": str(today - timedelta(days=730)), "end_date": str(today + timedelta(days=7)),
    })
    days = raw["daily"]["time"]
    values = raw["daily"]["river_discharge"]
    history = sorted(v for d, v in zip(days, values) if v is not None and d < str(today))
    forecast = [{"date": d, "discharge": v} for d, v in zip(days, values) if d >= str(today)]
    p95 = history[int(len(history) * 0.95)] if history else None
    data = {"forecast": forecast, "p95": p95, "median": history[len(history) // 2] if history else None}
    cache_set(key, data, 6 * 3600)
    return data


# =====================================================================
# USGS: earthquakes
# =====================================================================
def quake_from_usgs(f):
    p = f["properties"]
    lon, lat, depth = f["geometry"]["coordinates"][:3]
    return {
        "id": "usgs-" + f["id"], "hazard": "EARTHQUAKE",
        "lat": lat, "lon": lon, "magnitude": p.get("mag"), "depth_km": depth,
        "title": p.get("title"), "place": p.get("place"),
        "time": datetime.fromtimestamp(p["time"] / 1000, tz=timezone.utc).isoformat(),
        "tsunami": p.get("tsunami") == 1, "url": p.get("url"), "source": "USGS",
    }


async def get_earthquakes(window="7d"):
    feed = {"1h": "all_hour", "24h": "2.5_day", "7d": "2.5_week", "30d": "4.5_month"}.get(window, "2.5_week")
    key = "quakes:" + feed
    data = cache_get(key)
    if data is not None:
        return data
    raw = await fetch_json("usgs", f"https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/{feed}.geojson")
    data = [quake_from_usgs(f) for f in raw["features"] if f.get("geometry")]
    cache_set(key, data, 60)
    return data


async def get_earthquakes_near(lat, lon, radius_km=300, days=7):
    key = f"quakenear:{lat:.1f}:{lon:.1f}"
    data = cache_get(key)
    if data is not None:
        return data
    start = (now_utc() - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%S")
    raw = await fetch_json("usgs", "https://earthquake.usgs.gov/fdsnws/event/1/query", {
        "format": "geojson", "latitude": round(lat, 2), "longitude": round(lon, 2),
        "maxradiuskm": radius_km, "starttime": start, "minmagnitude": 2.5, "limit": 100,
    })
    data = [quake_from_usgs(f) for f in raw["features"] if f.get("geometry")]
    cache_set(key, data, 120)
    return data


# =====================================================================
# GDACS: storms / floods / wildfires / volcanoes / droughts
# =====================================================================
GDACS_HAZARD = {"TC": "STORM", "FL": "FLOOD", "WF": "FIRE", "VO": "VOLCANO", "DR": "DROUGHT"}


def clean_place_list(text):
    """GDACS sometimes sends 'Aruba, , Brazil' -> 'Aruba, Brazil'."""
    parts = [part.strip() for part in (text or "").split(",")]
    return ", ".join(part for part in parts if part)


async def get_gdacs_events():
    data = cache_get("gdacs")
    if data is not None:
        return data
    data = []
    start = (now_utc() - timedelta(days=14)).strftime("%Y-%m-%d")
    end = (now_utc() + timedelta(days=1)).strftime("%Y-%m-%d")

    async def fetch_type(code):
        try:
            return await fetch_json("gdacs", "https://www.gdacs.org/gdacsapi/api/events/geteventlist/SEARCH", {
                "eventlist": code, "alertlevel": "green;orange;red", "fromdate": start, "todate": end,
            })
        except RuntimeError:
            return {}

    # call all event types in parallel (faster than one by one)
    codes = list(GDACS_HAZARD)
    raws = await asyncio.gather(*(fetch_type(c) for c in codes))
    storms = []
    for code, raw in zip(codes, raws):
        hazard = GDACS_HAZARD[code]
        for f in raw.get("features", []):
            p = f.get("properties") or {}
            geometry = f.get("geometry") or {}
            if str(p.get("iscurrent")).lower() != "true" or geometry.get("type") != "Point":
                continue
            lon, lat = geometry["coordinates"][:2]
            event = {
                "id": f"gdacs-{code}-{p['eventid']}", "hazard": hazard, "lat": lat, "lon": lon,
                "title": p.get("name"), "place": clean_place_list(p.get("country")),
                "alert_level": p.get("alertlevel", "Green"),
                "severity_text": (p.get("severitydata") or {}).get("severitytext"),
                "wind_kmh": (p.get("severitydata") or {}).get("severity") if code == "TC" else None,
                "time": p.get("fromdate"), "url": (p.get("url") or {}).get("report"), "source": "GDACS",
            }
            if code == "TC":
                storms.append((event, p["eventid"], p["episodeid"]))
            data.append(event)
    # fetch storm tracks in parallel
    tracks = await asyncio.gather(*(get_storm_track(eid, epi) for _, eid, epi in storms))
    for (event, _, _), track in zip(storms, tracks):
        event["track"] = track
    cache_set("gdacs", data, 600)
    return data


async def get_storm_track(event_id, episode_id):
    """Storm track + forecast cone from GDACS (returned as GeoJSON features)."""
    try:
        raw = await fetch_json("gdacs", "https://www.gdacs.org/gdacsapi/api/polygons/getgeometry", {
            "eventtype": "TC", "eventid": event_id, "episodeid": episode_id,
        })
    except RuntimeError:
        return []
    features = []
    for f in raw.get("features", []):
        cls = f["properties"].get("Class", "")
        if cls.startswith("Line_"):
            features.append({"type": "Feature", "geometry": f["geometry"], "properties": {"kind": "track"}})
        elif cls.startswith("Poly_"):
            label = str(f["properties"].get("polygonlabel", ""))
            kind = "wind" if "km/h" in label else "cone"
            features.append({"type": "Feature", "geometry": f["geometry"],
                             "properties": {"kind": kind, "level": cls.replace("Poly_", "").lower(), "label": label}})
    return features


# =====================================================================
# NASA EONET: open wildfires / storms / volcanoes
# =====================================================================
async def get_eonet_events():
    data = cache_get("eonet")
    if data is not None:
        return data
    raw = await fetch_json("nasa-eonet", "https://eonet.gsfc.nasa.gov/api/v3/events/geojson", {
        "status": "open", "days": 20, "category": "wildfires,severeStorms,volcanoes",
    })
    names = {"wildfires": "FIRE", "severeStorms": "STORM", "volcanoes": "VOLCANO"}
    # EONET sends one feature per position, so a storm comes as many points -> group them by event id
    groups = {}
    for f in raw["features"]:
        g = f.get("geometry")
        if not g or g["type"] != "Point":
            continue
        p = f["properties"]
        category = p["categories"][0]["id"] if p.get("categories") else ""
        if category not in names:
            continue
        groups.setdefault(p["id"], []).append((p.get("date") or "", g["coordinates"], p, names[category]))
    data = []
    for event_id, items in groups.items():
        items.sort(key=lambda item: item[0])            # oldest -> newest
        date, (lon, lat), p, hazard = items[-1]          # newest position
        event = {"id": "eonet-" + event_id, "hazard": hazard, "lat": lat, "lon": lon, "title": p.get("title"),
                 "time": date, "url": p.get("link"), "source": "NASA EONET"}
        if hazard == "STORM" and len(items) > 1:
            path = [item[1] for item in items]
            event["track"] = [{"type": "Feature", "properties": {"kind": "track"},
                               "geometry": {"type": "LineString", "coordinates": path}}]
        data.append(event)
    cache_set("eonet", data, 900)
    return data


# =====================================================================
# RainViewer: rain radar
# =====================================================================
async def get_radar_frames():
    data = cache_get("radar")
    if data:
        return data
    raw = await fetch_json("rainviewer", "https://api.rainviewer.com/public/weather-maps.json")
    frames = []
    for frame in raw["radar"].get("past", []) + raw["radar"].get("nowcast", []):
        frames.append({
            "time": datetime.fromtimestamp(frame["time"], tz=timezone.utc).isoformat(),
            "tiles": raw["host"] + frame["path"] + "/256/{z}/{x}/{y}/2/1_1.png",
        })
    data = {"frames": frames, "max_zoom": 7}
    cache_set("radar", data, 300)
    return data


# =====================================================================
# Places / routes / nearby points of interest
# =====================================================================
async def search_place(text, lang="th"):
    key = f"search:{text}:{lang}"
    data = cache_get(key)
    if data is not None:
        return data
    try:
        raw = await fetch_json("open-meteo-geocoding", "https://geocoding-api.open-meteo.com/v1/search", {
            "name": text, "count": 6, "language": lang, "format": "json",
        })
    except RuntimeError:
        raw = {}   # try Nominatim below
    data = []
    for r in raw.get("results", []):
        detail = ", ".join(x for x in [r.get("admin1"), r.get("country")] if x)
        data.append({"name": r["name"], "label": r["name"] + (" — " + detail if detail else ""),
                     "lat": r["latitude"], "lon": r["longitude"], "country": r.get("country_code")})
    if not data:
        # if Open-Meteo finds nothing (e.g. small places), try Nominatim
        raw = await fetch_json("nominatim", "https://nominatim.openstreetmap.org/search", {
            "q": text, "format": "jsonv2", "limit": 5, "accept-language": lang,
        })
        for r in raw:
            data.append({"name": r["display_name"].split(",")[0], "label": r["display_name"],
                         "lat": float(r["lat"]), "lon": float(r["lon"]), "country": None})
    cache_set(key, data, 86400)
    return data


async def reverse_place(lat, lon, lang="th"):
    key = f"reverse:{lat:.3f}:{lon:.3f}:{lang}"
    data = cache_get(key)
    if data:
        return data
    raw = await fetch_json("nominatim", "https://nominatim.openstreetmap.org/reverse", {
        "lat": round(lat, 3), "lon": round(lon, 3), "format": "jsonv2", "zoom": 12, "accept-language": lang,
    })
    a = raw.get("address", {})
    name = a.get("suburb") or a.get("town") or a.get("city") or a.get("county") or a.get("state") or raw.get("name")
    data = {"name": name or "", "label": raw.get("display_name", ""), "country": a.get("country_code", "").upper()}
    cache_set(key, data, 86400)
    return data


async def get_routes(origin, dest):
    """Driving routes from OSRM, origin/dest = (lat, lon); may return several routes."""
    coords = f"{origin[1]:.5f},{origin[0]:.5f};{dest[1]:.5f},{dest[0]:.5f}"
    key = "route:" + coords
    data = cache_get(key)
    if data is not None:
        return data
    raw = await fetch_json("osrm", "https://router.project-osrm.org/route/v1/driving/" + coords, {
        "alternatives": 3, "overview": "full", "geometries": "geojson",
    })
    data = []
    for i, r in enumerate(raw.get("routes", [])):
        data.append({"route_id": f"r{i + 1}", "coordinates": r["geometry"]["coordinates"],
                     "distance_km": round(r["distance"] / 1000, 1), "duration_min": round(r["duration"] / 60)})
    cache_set(key, data, 1800)
    return data


async def get_nearby_places(lat, lon):
    """Nearby hospitals, police and fire stations (OpenStreetMap via Nominatim).
    Overpass was used first, but the free servers were slow / timed out often."""
    key = f"poi:{lat:.2f}:{lon:.2f}"
    data = cache_get(key)
    if data is not None:
        return data
    box = f"{lon - 0.12},{lat + 0.12},{lon + 0.12},{lat - 0.12}"   # box of about 13 km around the point
    data = []
    for kind, word in [("hospital", "hospital"), ("police", "police"), ("fire_station", "fire station")]:
        raw = await fetch_json("nominatim", "https://nominatim.openstreetmap.org/search", {
            "q": word, "format": "jsonv2", "limit": 8, "viewbox": box, "bounded": 1, "accept-language": "th",
        })
        for r in raw:
            data.append({"name": r.get("name") or r["display_name"].split(",")[0], "kind": kind,
                         "lat": float(r["lat"]), "lon": float(r["lon"]), "address": r.get("display_name")})
    cache_set(key, data, 86400)
    return data
