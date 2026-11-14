// layers.js — basemaps, colors and drawing hazard layers on the map (MapLibre GL)

// ---------------- Basemaps (free) ----------------
const GLYPHS = "https://tiles.openfreemap.org/fonts/{fontstack}/{range}.pbf";
const FONT = ["Noto Sans Regular"];
const BASEMAPS = {
  streets: "https://tiles.openfreemap.org/styles/liberty",
  dark: "https://tiles.openfreemap.org/styles/dark",
  satellite: {
    version: 8,
    glyphs: GLYPHS,
    sources: {
      esri: {
        type: "raster", tileSize: 256, maxzoom: 18,
        tiles: ["https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"],
        attribution: "Imagery © Esri, Maxar, Earthstar Geographics",
      },
    },
    layers: [{ id: "esri", type: "raster", source: "esri" }],
  },
};

// ---------------- Color scales ----------------
const COLOR_SCALES = {
  temperature: { unit: "°C", stops: [[-20, "#313695"], [-5, "#4575b4"], [5, "#74add1"], [15, "#abd9e9"], [22, "#fee090"],
                                    [28, "#fdae61"], [33, "#f46d43"], [38, "#d73027"], [45, "#a50026"]] },
  precipitation: { unit: "mm/h", stops: [[0.2, "#c6dbef"], [2, "#6baed6"], [10, "#2171b5"], [30, "#08306b"], [60, "#54278f"]] },
  wind: { unit: "km/h", stops: [[0, "#e0f3f8"], [20, "#abd9e9"], [40, "#fee090"], [62, "#fdae61"], [89, "#f46d43"], [118, "#a50026"]] },
  pm25: { unit: "µg/m³", stops: [[0, "#3fa9f5"], [15, "#5cb85c"], [25, "#ffd500"], [37.5, "#ff8c00"], [75, "#e53935"], [150, "#7b1fa2"]] },
};
const SEV_COLORS = ["#2e7d32", "#f9a825", "#ef6c00", "#c62828", "#6a1b9a"];
const HAZARD_COLORS = { STORM: "#7b1fa2", FIRE: "#e65100", FLOOD: "#0277bd", VOLCANO: "#5d4037", DROUGHT: "#a1887f" };
const RISK_COLORS = { LOW: "#2e7d32", MEDIUM: "#f9a825", HIGH: "#c62828" };

function hexToRgb(hex) {
  const n = parseInt(hex.slice(1), 16);
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
}

function colorFor(variable, value) {
  const stops = COLOR_SCALES[variable].stops;
  if (value <= stops[0][0]) return stops[0][1];
  for (let i = 1; i < stops.length; i++) {
    if (value <= stops[i][0]) {
      const [v0, c0] = stops[i - 1], [v1, c1] = stops[i];
      const f = (value - v0) / (v1 - v0);
      const a = hexToRgb(c0), b = hexToRgb(c1);
      return `rgb(${a.map((x, k) => Math.round(x + (b[k] - x) * f)).join(",")})`;
    }
  }
  return stops[stops.length - 1][1];
}

// Loaded data (kept so layers can be redrawn after a basemap change)
const DATA = { grid: null, events: [], storms: [], radarFrames: [], routes: [], selectedRoute: null, poi: [] };
const EMPTY = { type: "FeatureCollection", features: [] };

// ---------------- Add all sources/layers (called every time a style loads) ----------------
function addAllLayers(map) {
  // Wind arrow (drawn on a canvas and used as an icon)
  if (!map.hasImage("arrow")) {
    const size = 32, c = document.createElement("canvas");
    c.width = c.height = size;
    const g = c.getContext("2d");
    g.fillStyle = "#000";
    g.beginPath(); g.moveTo(16, 2); g.lineTo(26, 18); g.lineTo(19, 16); g.lineTo(19, 30); g.lineTo(13, 30); g.lineTo(13, 16); g.lineTo(6, 18);
    g.closePath(); g.fill();
    map.addImage("arrow", g.getImageData(0, 0, size, size), { sdf: true });
  }

  map.addSource("grid", { type: "geojson", data: EMPTY });
  map.addLayer({ id: "grid-fill", type: "fill", source: "grid",
                 paint: { "fill-color": ["get", "color"], "fill-opacity": ["get", "opacity"] } });
  map.addSource("wind-arrows", { type: "geojson", data: EMPTY });
  map.addLayer({ id: "wind-arrows", type: "symbol", source: "wind-arrows",
                 layout: { "icon-image": "arrow", "icon-size": ["interpolate", ["linear"], ["get", "speed"], 0, 0.35, 60, 0.8],
                           "icon-rotate": ["get", "rotation"], "icon-rotation-alignment": "map", "icon-allow-overlap": true },
                 paint: { "icon-color": ["get", "color"], "icon-halo-color": "#000", "icon-halo-width": 1 } });

  map.addSource("radar", { type: "raster", tiles: ["https://tilecache.rainviewer.com/v2/radar/0/256/{z}/{x}/{y}/2/1_1.png"],
                           tileSize: 256, maxzoom: 7, attribution: "Radar © RainViewer" });
  map.addLayer({ id: "radar", type: "raster", source: "radar", paint: { "raster-opacity": 0.75 }, layout: { visibility: "none" } });

  map.addSource("storm-tracks", { type: "geojson", data: EMPTY });
  map.addLayer({ id: "storm-cone", type: "fill", source: "storm-tracks", filter: ["!=", ["get", "kind"], "track"],
                 paint: { "fill-color": ["match", ["get", "level"], "red", "#c62828", "orange", "#ef6c00", "#f9a825"], "fill-opacity": 0.15 } });
  map.addLayer({ id: "storm-track", type: "line", source: "storm-tracks", filter: ["==", ["get", "kind"], "track"],
                 paint: { "line-color": "#7b1fa2", "line-width": 2, "line-dasharray": [2, 1] } });

  map.addSource("events", { type: "geojson", data: EMPTY });
  map.addLayer({ id: "ev-other", type: "circle", source: "events", filter: ["!=", ["get", "hazard"], "EARTHQUAKE"],
                 paint: { "circle-radius": ["interpolate", ["linear"], ["zoom"], 1, 5, 8, 9],
                          "circle-color": ["match", ["get", "hazard"], "STORM", HAZARD_COLORS.STORM, "FIRE", HAZARD_COLORS.FIRE,
                                           "FLOOD", HAZARD_COLORS.FLOOD, "VOLCANO", HAZARD_COLORS.VOLCANO, "#888"],
                          "circle-stroke-color": "#fff", "circle-stroke-width": 1.5 } });
  map.addLayer({ id: "ev-quakes", type: "circle", source: "events", filter: ["==", ["get", "hazard"], "EARTHQUAKE"],
                 paint: { "circle-radius": ["interpolate", ["exponential", 2], ["get", "mag"], 2.5, 3, 5, 8, 7, 22, 8, 34],
                          "circle-color": ["step", ["get", "ageHours"], "#d32f2f", 1, "#f57c00", 24, "#fbc02d", 168, "#9e9e9e"],
                          "circle-opacity": 0.75, "circle-stroke-color": "#fff", "circle-stroke-width": 1 } });

  map.addSource("routes", { type: "geojson", data: EMPTY });
  map.addLayer({ id: "routes-alt", type: "line", source: "routes", filter: ["==", ["get", "selected"], false],
                 layout: { "line-cap": "round", "line-join": "round" }, paint: { "line-color": "#757575", "line-width": 5, "line-opacity": 0.8 } });
  map.addSource("route-risk", { type: "geojson", data: EMPTY });
  map.addLayer({ id: "route-casing", type: "line", source: "route-risk", layout: { "line-cap": "round", "line-join": "round" },
                 paint: { "line-color": "#fff", "line-width": 9 } });
  map.addLayer({ id: "route-risk", type: "line", source: "route-risk", layout: { "line-cap": "round", "line-join": "round" },
                 paint: { "line-color": ["get", "color"], "line-width": 6 } });

  map.addSource("poi", { type: "geojson", data: EMPTY });
  map.addLayer({ id: "poi", type: "circle", source: "poi",
                 paint: { "circle-radius": 7, "circle-color": ["match", ["get", "kind"], "hospital", "#d32f2f", "police", "#1565c0", "#ef6c00"],
                          "circle-stroke-color": "#fff", "circle-stroke-width": 2 } });
  map.addLayer({ id: "poi-label", type: "symbol", source: "poi",
                 layout: { "text-field": ["get", "name"], "text-font": FONT, "text-size": 11, "text-offset": [0, 1.2], "text-anchor": "top" },
                 paint: { "text-color": "#202124", "text-halo-color": "#fff", "text-halo-width": 1.5 } });
}

// ---------------- Update each layer ----------------
function drawGrid(map, timeIndex) {
  const grid = DATA.grid;
  if (!grid || !map.getSource("grid")) return;
  const half = grid.step / 2;
  const scale = grid.variable === "gust" ? "wind" : grid.variable;
  const cells = [], arrows = [];
  for (const c of grid.cells) {
    const v = c.values[timeIndex];
    if (v === null || v === undefined) continue;
    const hide = grid.variable === "precipitation" && v < 0.2;
    cells.push({ type: "Feature", properties: { color: colorFor(scale, v), opacity: hide ? 0 : 0.45, value: v },
                 geometry: { type: "Polygon", coordinates: [[[c.lon - half, c.lat - half], [c.lon + half, c.lat - half],
                             [c.lon + half, c.lat + half], [c.lon - half, c.lat + half], [c.lon - half, c.lat - half]]] } });
    if (grid.variable === "wind" && c.dir) {
      arrows.push({ type: "Feature", properties: { rotation: (c.dir[timeIndex] + 180) % 360, speed: v, color: colorFor("wind", v) },
                    geometry: { type: "Point", coordinates: [c.lon, c.lat] } });
    }
  }
  map.getSource("grid").setData({ type: "FeatureCollection", features: cells });
  map.getSource("wind-arrows").setData({ type: "FeatureCollection", features: arrows });
}

function drawEvents(map, enabled) {
  if (!map.getSource("events")) return;
  const now = Date.now();
  const show = { EARTHQUAKE: enabled.has("earthquakes"), STORM: enabled.has("storms"), FIRE: enabled.has("fires"),
                 FLOOD: enabled.has("floods"), VOLCANO: enabled.has("volcanoes") };
  const features = DATA.events.filter(e => show[e.hazard]).map(e => ({
    type: "Feature", geometry: { type: "Point", coordinates: [e.lon, e.lat] },
    properties: { id: e.id, hazard: e.hazard, title: e.title || "", place: e.place || "", mag: e.magnitude || 0, source: e.source,
                  url: e.url || "", time: e.time || "", extra: e.severity_text || e.alert_level || "",
                  ageHours: e.time ? (now - new Date(e.time.endsWith("Z") || e.time.includes("+") ? e.time : e.time + "Z")) / 3.6e6 : 999 },
  }));
  map.getSource("events").setData({ type: "FeatureCollection", features });
  const tracks = enabled.has("storms") ? DATA.storms.flatMap(s => s.track || []) : [];
  map.getSource("storm-tracks").setData({ type: "FeatureCollection", features: tracks });
}

function drawRadar(map, enabled, timeMs) {
  if (!map.getLayer("radar")) return;
  if (!enabled.has("radar") || DATA.radarFrames.length === 0) {
    map.setLayoutProperty("radar", "visibility", "none");
    return;
  }
  // Pick the radar frame closest to the selected time (radar covers only the last ~2 h)
  let best = DATA.radarFrames[DATA.radarFrames.length - 1], bestDiff = Infinity;
  for (const f of DATA.radarFrames) {
    const d = Math.abs(new Date(f.time).getTime() - timeMs);
    if (d < bestDiff) { best = f; bestDiff = d; }
  }
  map.getSource("radar").setTiles([best.tiles]);
  map.setLayoutProperty("radar", "visibility", bestDiff > 3 * 3.6e6 ? "none" : "visible");
}

function distKm(a, b) {
  const R = 6371, toRad = x => x * Math.PI / 180;
  const dLat = toRad(b[1] - a[1]), dLon = toRad(b[0] - a[0]);
  const h = Math.sin(dLat / 2) ** 2 + Math.cos(toRad(a[1])) * Math.cos(toRad(b[1])) * Math.sin(dLon / 2) ** 2;
  return 2 * R * Math.asin(Math.sqrt(h));
}

function drawRoutes(map) {
  if (!map.getSource("routes")) return;
  const lines = DATA.routes.map(r => ({ type: "Feature", properties: { id: r.route_id, selected: r.route_id === DATA.selectedRoute },
                                        geometry: { type: "LineString", coordinates: r.coordinates } }));
  map.getSource("routes").setData({ type: "FeatureCollection", features: lines });

  // Color the selected route by the risk level of each segment
  const route = DATA.routes.find(r => r.route_id === DATA.selectedRoute);
  const chunks = [];
  if (route) {
    const segs = route.segments || [];
    let km = 0, current = [route.coordinates[0]], segIndex = 0;
    const riskAt = i => (segs[i] ? segs[i].risk_level : "LOW");
    for (let i = 1; i < route.coordinates.length; i++) {
      km += distKm(route.coordinates[i - 1], route.coordinates[i]);
      current.push(route.coordinates[i]);
      if (segs[segIndex + 1] && km >= segs[segIndex + 1].km) {
        chunks.push({ type: "Feature", properties: { color: RISK_COLORS[riskAt(segIndex + 1)] },
                      geometry: { type: "LineString", coordinates: current } });
        current = [route.coordinates[i]];
        segIndex++;
      }
    }
    if (current.length > 1) {
      chunks.push({ type: "Feature", properties: { color: RISK_COLORS[riskAt(segIndex)] }, geometry: { type: "LineString", coordinates: current } });
    }
  }
  map.getSource("route-risk").setData({ type: "FeatureCollection", features: chunks });
}

function drawPoi(map) {
  if (!map.getSource("poi")) return;
  map.getSource("poi").setData({ type: "FeatureCollection", features: DATA.poi.map(p => ({
    type: "Feature", properties: { name: p.name, kind: p.kind }, geometry: { type: "Point", coordinates: [p.lon, p.lat] } })) });
}

function showLegend(variable) {
  const box = document.getElementById("legend");
  if (!variable) { box.classList.add("hidden"); return; }
  const scale = COLOR_SCALES[variable === "gust" ? "wind" : variable];
  const stops = scale.stops;
  box.innerHTML = `<b>${escapeHtml(TEXT[LANG].chips[variable] || variable)}</b> (${scale.unit})
    <div class="bar">${stops.map(s => `<span style="background:${s[1]}"></span>`).join("")}</div>
    <div class="labels"><span>${stops[0][0]}</span><span>${stops[Math.floor(stops.length / 2)][0]}</span><span>${stops[stops.length - 1][0]}+</span></div>`;
  box.classList.remove("hidden");
}

function escapeHtml(text) {
  return String(text ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}
