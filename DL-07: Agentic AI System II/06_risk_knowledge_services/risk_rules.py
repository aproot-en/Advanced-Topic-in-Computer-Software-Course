# risk_rules.py
# Module 06 (simple version): turn forecast data into hazard severity and risk level
# Thresholds follow proj-prompt Appendix C (defaults; verify with official agencies before real use)
#
# Severity: 0 normal, 1 advisory, 2 watch, 3 warning, 4 emergency
# Risk level: LOW / MEDIUM / HIGH

import math
from datetime import datetime, timedelta, timezone

QUAKE_NOTE_TH = "แผ่นดินไหวไม่สามารถพยากรณ์ล่วงหน้าได้ ข้อมูลนี้คือความน่าจะเป็นทางสถิติและข้อมูลจากหน่วยงานทางการ"
QUAKE_NOTE_EN = "Earthquakes cannot be predicted; these are statistical probabilities and official observations."


# ---------------------------------------------------------------- Basic helpers
def distance_km(lat1, lon1, lat2, lon2):
    """Distance on the Earth surface (haversine formula)."""
    r = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def parse_time(text):
    t = datetime.fromisoformat(text.replace("Z", "+00:00"))
    if t.tzinfo is None:
        t = t.replace(tzinfo=timezone.utc)
    return t


def nearest_hour_index(times, when):
    """Index of the hour closest to `when` (times are hourly). Always returns a valid index."""
    first = parse_time(times[0])
    index = round((when - first).total_seconds() / 3600)
    return min(max(index, 0), len(times) - 1)


def hour_index_or_none(times, when):
    """Like nearest_hour_index, but returns None when `when` is outside the forecast period."""
    first = parse_time(times[0])
    index = round((when - first).total_seconds() / 3600)
    if index < 0 or index >= len(times):
        return None
    return index


# ---------------------------------------------------------------- Severity thresholds (Appendix C)
def rain_severity(mm_per_hour):
    if mm_per_hour is None:
        return 0
    if mm_per_hour >= 60:
        return 4
    if mm_per_hour >= 30:
        return 3
    if mm_per_hour >= 10:
        return 2
    if mm_per_hour >= 2:
        return 1
    return 0


def rain24_severity(mm):   # 24 h rainfall, Thai Meteorological Department thresholds
    if mm > 90:
        return 3
    if mm > 35:
        return 2
    if mm > 10:
        return 1
    return 0


def wind_severity(gust_kmh):
    if gust_kmh is None:
        return 0
    if gust_kmh >= 118:
        return 4
    if gust_kmh >= 89:
        return 3
    if gust_kmh >= 62:
        return 2
    if gust_kmh >= 40:
        return 1
    return 0


def heat_index(temp_c, rh):
    """Heat index (NWS Rothfusz formula), used when temperature >= 27°C."""
    if temp_c is None or rh is None or temp_c < 27:
        return temp_c
    t = temp_c * 9 / 5 + 32
    hi = (-42.379 + 2.04901523 * t + 10.14333127 * rh - 0.22475541 * t * rh - 0.00683783 * t * t
          - 0.05481717 * rh * rh + 0.00122874 * t * t * rh + 0.00085282 * t * rh * rh - 0.00000199 * t * t * rh * rh)
    return round((hi - 32) * 5 / 9, 1)


def heat_severity(hi_c):
    if hi_c is None:
        return 0
    if hi_c > 54:
        return 4
    if hi_c > 41:
        return 3
    if hi_c > 32:
        return 2
    if hi_c > 27:
        return 1
    return 0


def pm25_severity(pm):     # Thai AQI thresholds (Pollution Control Department, 2023)
    if pm is None:
        return 0
    if pm >= 150:
        return 4
    if pm > 75:
        return 3
    if pm > 37.5:
        return 2
    if pm > 25:
        return 1
    return 0


def fog_severity(visibility_m):
    if visibility_m is None:
        return 0
    if visibility_m < 50:
        return 4
    if visibility_m < 200:
        return 3
    if visibility_m < 500:
        return 2
    if visibility_m < 1000:
        return 1
    return 0


def quake_severity(magnitude):
    if magnitude is None:
        return 0
    if magnitude >= 7:
        return 4
    if magnitude >= 6:
        return 3
    if magnitude >= 4:
        return 2
    return 1


def storm_severity(wind_kmh):
    if not wind_kmh:
        return 2
    if wind_kmh >= 118:
        return 4    # typhoon
    if wind_kmh >= 63:
        return 3    # tropical storm
    return 2        # tropical depression


def flood_severity(discharge, p95):
    """Compare forecast discharge with the 95th percentile of the past 2 years."""
    if discharge is None or not p95:
        return 0
    ratio = discharge / p95
    if ratio >= 1.5:
        return 3
    if ratio >= 1.0:
        return 2
    if ratio >= 0.8:
        return 1
    return 0


def aftershock_probability(mainshock_mag, hours_since, days_ahead=7, min_mag=5.0):
    """Probability of an aftershock >= min_mag within days_ahead days (Reasenberg-Jones, generic parameters)."""
    a, b, p, c = -1.67, 0.91, 1.08, 0.05
    t1 = max(hours_since / 24, 0.0)
    t2 = t1 + days_ahead
    k = 10 ** (a + b * (mainshock_mag - min_mag))
    n = k * ((t1 + c) ** (1 - p) - (t2 + c) ** (1 - p)) / (p - 1)
    return round(1 - math.exp(-n), 3)


def mmi_estimate(magnitude, distance, depth_km=10):
    """Rough shaking intensity (MMI) estimate from magnitude and distance."""
    r = math.sqrt(distance ** 2 + depth_km ** 2)
    mmi = 1.5 * magnitude - 3.0 * math.log10(max(r, 1)) + 3.0
    return max(1, min(10, round(mmi, 1)))


def mmi_severity(mmi):
    if mmi >= 7:
        return 4
    if mmi >= 6:
        return 3
    if mmi >= 5:
        return 2
    if mmi >= 4:
        return 1
    return 0


def risk_from_severities(severities):
    """Convert a list of severities into a risk level."""
    if not severities:
        return "LOW"
    top = max(severities)
    if top >= 3:
        return "HIGH"
    if top == 2:
        return "MEDIUM"
    return "LOW"


# ---------------------------------------------------------------- Assess one point
def assess_point(lat, lon, forecast, air=None, flood=None, quakes=None, events=None, hours=48):
    """Hazards for this point in the next `hours` hours (peak value + peak time)."""
    results = []
    now = datetime.now(timezone.utc)
    start = nearest_hour_index(forecast["time"], now)
    end = min(len(forecast["time"]), start + hours)

    def peak(values):
        best_i, best_v = None, None
        for i in range(start, end):
            v = values[i] if i < len(values) else None
            if v is not None and (best_v is None or v > best_v):
                best_i, best_v = i, v
        return best_i, best_v

    # rain
    i, rain = peak(forecast["precipitation"])
    rain24 = sum(v or 0 for v in forecast["precipitation"][start:start + 24])
    sev = max(rain_severity(rain), rain24_severity(rain24))
    results.append({"hazard": "RAIN", "severity": sev, "value": rain, "unit": "mm/h",
                    "time": forecast["time"][i] if i is not None else None,
                    "text_th": f"ฝนสูงสุด {rain or 0:.1f} มม./ชม. รวม 24 ชม. {rain24:.0f} มม.",
                    "text_en": f"Peak rain {rain or 0:.1f} mm/h, 24 h total {rain24:.0f} mm", "source": "Open-Meteo"})
    # wind
    i, gust = peak(forecast["wind_gusts_10m"])
    results.append({"hazard": "WIND", "severity": wind_severity(gust), "value": gust, "unit": "km/h",
                    "time": forecast["time"][i] if i is not None else None,
                    "text_th": f"ลมกระโชกสูงสุด {gust or 0:.0f} กม./ชม.",
                    "text_en": f"Peak gust {gust or 0:.0f} km/h", "source": "Open-Meteo"})
    # heat
    his = [heat_index(t, h) for t, h in zip(forecast["temperature_2m"], forecast["relative_humidity_2m"])]
    i, hi = peak(his)
    results.append({"hazard": "HEAT", "severity": heat_severity(hi), "value": hi, "unit": "°C",
                    "time": forecast["time"][i] if i is not None else None,
                    "text_th": f"ดัชนีความร้อนสูงสุด {hi or 0:.0f}°C", "text_en": f"Peak heat index {hi or 0:.0f}°C",
                    "source": "Open-Meteo"})
    # general weather (current temperature + fog)
    vis = [v for v in forecast["visibility"][start:end] if v is not None]
    min_vis = min(vis) if vis else None
    results.append({"hazard": "WEATHER", "severity": fog_severity(min_vis), "value": forecast["temperature_2m"][start],
                    "unit": "°C", "time": forecast["time"][start],
                    "text_th": f"อุณหภูมิตอนนี้ {forecast['temperature_2m'][start]}°C ทัศนวิสัยต่ำสุด {(min_vis or 0) / 1000:.1f} กม.",
                    "text_en": f"Now {forecast['temperature_2m'][start]}°C, min visibility {(min_vis or 0) / 1000:.1f} km",
                    "source": "Open-Meteo"})
    # PM2.5
    if air:
        a_start = nearest_hour_index(air["time"], now)
        pm_values = [v for v in air["pm2_5"][a_start:a_start + hours] if v is not None]
        pm = max(pm_values) if pm_values else None
        results.append({"hazard": "AIR_QUALITY", "severity": pm25_severity(pm), "value": pm, "unit": "µg/m³",
                        "time": None, "text_th": f"PM2.5 สูงสุด {pm or 0:.0f} µg/m³",
                        "text_en": f"Peak PM2.5 {pm or 0:.0f} µg/m³", "source": "Open-Meteo (CAMS)"})
    # river discharge
    if flood and flood.get("forecast"):
        top = max(flood["forecast"], key=lambda d: d["discharge"] or 0)
        sev = flood_severity(top["discharge"], flood.get("p95"))
        results.append({"hazard": "FLOOD", "severity": sev, "value": top["discharge"], "unit": "m³/s",
                        "time": top["date"],
                        "text_th": f"ปริมาณน้ำในแม่น้ำใกล้เคียงสูงสุด {top['discharge'] or 0:.0f} ลบ.ม./วิ (ค่าปกติสูง {flood.get('p95') or 0:.0f})",
                        "text_en": f"Nearby river discharge peak {top['discharge'] or 0:.0f} m³/s (high normal {flood.get('p95') or 0:.0f})",
                        "source": "Open-Meteo Flood (GloFAS)"})
    # earthquakes (observed events + aftershock probability)
    if quakes:
        worst = None
        for q in quakes:
            d = distance_km(lat, lon, q["lat"], q["lon"])
            mmi = mmi_estimate(q["magnitude"] or 0, d, q.get("depth_km") or 10)
            if worst is None or mmi > worst["mmi"]:
                worst = {"q": q, "mmi": mmi, "d": d}
        q = worst["q"]
        hours_since = (now - parse_time(q["time"])).total_seconds() / 3600
        prob = aftershock_probability(q["magnitude"] or 0, hours_since) if (q["magnitude"] or 0) >= 5 else 0
        sev = mmi_severity(worst["mmi"]) if hours_since < 72 else 0
        results.append({"hazard": "EARTHQUAKE", "severity": sev, "value": q["magnitude"], "unit": "M",
                        "time": q["time"],
                        "text_th": f"แผ่นดินไหว M{q['magnitude']} ห่าง {worst['d']:.0f} กม. แรงสั่นที่นี่ประมาณ MMI {worst['mmi']}"
                                   f" โอกาสอาฟเตอร์ช็อก M5+ ใน 7 วัน {prob * 100:.0f}% — {QUAKE_NOTE_TH}",
                        "text_en": f"M{q['magnitude']} quake {worst['d']:.0f} km away, est. shaking here MMI {worst['mmi']},"
                                   f" chance of M5+ aftershock in 7 days {prob * 100:.0f}% — {QUAKE_NOTE_EN}",
                        "source": "USGS"})
    # nearby events (storms / wildfires / volcanoes / GDACS floods)
    for e in (events or []):
        d = event_distance_km(e, lat, lon)
        sev = event_severity_at_distance(e, d)
        if sev > 0:
            results.append({"hazard": e["hazard"], "severity": sev, "value": round(d), "unit": "km",
                            "time": e.get("time"),
                            "text_th": f"{e['title']} ห่างประมาณ {d:.0f} กม.",
                            "text_en": f"{e['title']} about {d:.0f} km away", "source": e["source"]})
    return results


def storm_track_points(event):
    """All [lon, lat] points of a storm's forecast track lines (from GDACS)."""
    points = []
    for feature in event.get("track") or []:
        geometry = feature.get("geometry") or {}
        if feature.get("properties", {}).get("kind") == "track" and geometry.get("type") == "LineString":
            points += geometry["coordinates"]
    return points


def event_distance_km(event, lat, lon):
    """Distance from a point to an event. For storms, the closest point of the storm track counts."""
    d = distance_km(lat, lon, event["lat"], event["lon"])
    if event["hazard"] == "STORM":
        for track_lon, track_lat in storm_track_points(event):
            d = min(d, distance_km(lat, lon, track_lat, track_lon))
    return d


def event_severity_at_distance(event, d):
    """How much an event d km away matters (simple thresholds)."""
    hz = event["hazard"]
    level = str(event.get("alert_level", "green")).lower()
    if hz == "STORM":
        if d <= 150:
            return storm_severity(event.get("wind_kmh"))
        if d <= 400:
            return 2
    if hz == "FIRE":
        if d <= 5:
            return 3
        if d <= 25:
            return 2
    if hz == "FLOOD" and d <= 80:
        return {"red": 4, "orange": 3}.get(level, 2)
    if hz == "VOLCANO" and d <= 100:
        return {"red": 4, "orange": 3}.get(level, 2)
    return 0


# ---------------------------------------------------------------- Assess a route
def assess_route(route, samples, forecasts, departure, events):
    """
    Assess each part of the route at the time you will reach it (ETA), not only now.
    route: {distance_km, duration_min, ...}
    samples: [(lat, lon, km), ...] from Module 05   forecasts: forecast for each point (same order)
    """
    segments = []
    total_km = samples[-1][2] or 1
    for (lat, lon, km), fc in zip(samples, forecasts):
        eta = departure + timedelta(minutes=route["duration_min"] * km / total_km)
        i = hour_index_or_none(fc["time"], eta)
        notes = []
        if i is None:
            rain, gust, vis = None, None, None
            no_forecast = True
            notes.append("no forecast for this time")
        else:
            rain = fc["precipitation"][i]
            gust = fc["wind_gusts_10m"][i]
            vis = fc["visibility"][i] if "visibility" in fc else None
            no_forecast = False
        hazards = {"RAIN": rain_severity(rain), "WIND": wind_severity(gust), "FOG": fog_severity(vis)}
        for e in events:
            d = event_distance_km(e, lat, lon)
            sev = event_severity_at_distance(e, d)
            if sev > hazards.get(e["hazard"], 0):
                hazards[e["hazard"]] = sev
                notes.append(f"{e['title']} ({d:.0f} km)")
        top_hazard = max(hazards, key=hazards.get)
        max_sev = hazards[top_hazard]
        segments.append({
            "lat": lat, "lon": lon, "km": km, "eta": eta.isoformat(),
            "rain_mm_h": rain, "gust_kmh": gust, "hazards": hazards,
            "max_severity": max_sev, "top_hazard": top_hazard if max_sev > 0 else None,
            "risk_level": risk_from_severities([max_sev]), "notes": notes, "no_forecast": no_forecast,
        })
    all_sev = [s["max_severity"] for s in segments]
    exposure = {}
    for s in segments:
        for hz, sev in s["hazards"].items():
            if sev >= 2:
                exposure[hz] = exposure.get(hz, 0) + 1
    missing = sum(1 for s in segments if s["no_forecast"])
    return {"segments": segments, "max_severity": max(all_sev) if all_sev else 0,
            "risk_level": risk_from_severities(all_sev), "exposure": exposure,
            "segments_without_forecast": missing}


# ---------------------------------------------------------------- Short safety tips (used together with Disaster RAG)
# General advice summarised from DDPM / Thai Meteorological Department / USGS / WHO guidance
SAFETY_TIPS = {
    "RAIN": {"th": ["ลดความเร็วและเปิดไฟหน้ารถเมื่อฝนตกหนัก", "หลีกเลี่ยงถนนที่มีน้ำท่วมขัง", "ติดตามประกาศกรมอุตุนิยมวิทยา"],
             "en": ["Slow down and turn on headlights in heavy rain", "Avoid flooded roads", "Follow Thai Meteorological Department updates"],
             "source": "กรมอุตุนิยมวิทยา / ปภ."},
    "FLOOD": {"th": ["ห้ามขับรถหรือเดินผ่านน้ำไหลเชี่ยว", "ย้ายขึ้นที่สูงหากน้ำเพิ่มขึ้นเร็ว", "ตัดไฟที่เบรกเกอร์หลักหากทำได้อย่างปลอดภัย"],
              "en": ["Never drive or walk through moving water", "Move to higher ground if water rises fast", "Switch off main power if safe"],
              "source": "ปภ. (DDPM)"},
    "WIND": {"th": ["ระวังลมแรงบนสะพานและทางยกระดับ", "หลีกเลี่ยงการจอดใต้ต้นไม้หรือป้ายโฆษณา"],
             "en": ["Beware of strong crosswinds on bridges and expressways", "Do not park under trees or billboards"],
             "source": "กรมอุตุนิยมวิทยา"},
    "STORM": {"th": ["งดการเดินทางในพื้นที่ที่พายุเคลื่อนผ่าน", "เตรียมน้ำ อาหาร ไฟฉาย และชาร์จโทรศัพท์", "ติดตามประกาศเตือนภัยอย่างใกล้ชิด"],
              "en": ["Avoid travelling through the storm path", "Prepare water, food, flashlight and charged phone", "Follow official warnings closely"],
              "source": "ปภ. / กรมอุตุนิยมวิทยา"},
    "FIRE": {"th": ["หลีกเลี่ยงพื้นที่ไฟป่าและควัน", "สวมหน้ากาก N95 หากต้องอยู่ในพื้นที่ควัน", "อพยพตามทิศที่สวนทางกับลม"],
             "en": ["Avoid wildfire and smoke areas", "Wear an N95 mask in smoke", "Evacuate upwind"],
             "source": "กรมป่าไม้ / WHO"},
    "EARTHQUAKE": {"th": ["หมอบ ป้อง เกาะ (Drop, Cover, Hold On)", "อยู่ห่างจากกระจกและสิ่งของที่อาจล้ม", "หลังหยุดสั่นให้ออกไปที่โล่งและระวังอาฟเตอร์ช็อก"],
                   "en": ["Drop, Cover, Hold On", "Stay away from glass and falling objects", "After shaking stops, move to open space and expect aftershocks"],
                   "source": "USGS / ปภ."},
    "AIR_QUALITY": {"th": ["ลดกิจกรรมกลางแจ้ง", "สวมหน้ากาก N95", "ปิดหน้าต่างรถและเปิดระบบหมุนเวียนอากาศภายใน"],
                    "en": ["Reduce outdoor activity", "Wear an N95 mask", "Close car windows and use recirculation"],
                    "source": "กรมควบคุมมลพิษ / WHO"},
    "HEAT": {"th": ["ดื่มน้ำบ่อย ๆ", "หลีกเลี่ยงแดดจัดช่วง 11:00–15:00 น.", "ห้ามทิ้งเด็กหรือสัตว์เลี้ยงไว้ในรถ"],
             "en": ["Drink water often", "Avoid strong sun 11:00–15:00", "Never leave children or pets in the car"],
             "source": "กรมอนามัย"},
    "FOG": {"th": ["เปิดไฟตัดหมอกและลดความเร็ว", "เว้นระยะห่างจากรถคันหน้ามากขึ้น"],
            "en": ["Use fog lights and slow down", "Keep a longer distance from the car ahead"],
            "source": "กรมทางหลวง"},
    "VOLCANO": {"th": ["หลีกเลี่ยงพื้นที่ใกล้ภูเขาไฟและเถ้าถ่าน"], "en": ["Avoid areas near the volcano and ash fall"],
                "source": "GDACS"},
}

# Emergency numbers in Thailand
EMERGENCY_CONTACTS_TH = [
    {"name": "ศูนย์ ปภ. (สาธารณภัย)", "phone": "1784"},
    {"name": "เจ็บป่วยฉุกเฉิน", "phone": "1669"},
    {"name": "ตำรวจ", "phone": "191"},
    {"name": "ดับเพลิง", "phone": "199"},
    {"name": "ตำรวจท่องเที่ยว", "phone": "1155"},
]
