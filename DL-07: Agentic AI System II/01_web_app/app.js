// app.js — main code of the web page (Module 01)
// The page only displays results; it never calculates risk itself. Everything comes from the API (Module 02)

const API = (window.APP_CONFIG && window.APP_CONFIG.API_BASE) || "http://127.0.0.1:8000/api";
const GRID_LAYERS = ["temperature", "precipitation", "wind", "pm25"];   // only one grid layer at a time
const CHIP_ORDER = ["temperature", "precipitation", "radar", "floods", "wind", "storms", "fires", "earthquakes", "pm25", "volcanoes"];

const state = {
  enabled: new Set(["temperature", "earthquakes", "storms"]),
  basemap: "streets",
  globe: true,
  times: [],
  timeIndex: 0,
  playing: null,
  userMoved: false,
  lastTrip: null,
  gridError: null,
};

// ======================================================================
// API calls
// ======================================================================
async function getJson(path) {
  const r = await fetch(API + path);
  const data = await r.json();
  if (!r.ok) throw new Error(data.error ? data.error.message : r.statusText);
  return data;
}

async function postJson(path, body, method = "POST") {
  const r = await fetch(API + path, { method, headers: { "Content-Type": "application/json" }, body: body ? JSON.stringify(body) : undefined });
  const data = await r.json();
  if (!r.ok) throw new Error(data.error ? data.error.message : r.statusText);
  return data;
}

// ======================================================================
// Create the map (starts as a globe, zoom in to a street map)
// ======================================================================
const map = new maplibregl.Map({
  container: "map",
  style: BASEMAPS.streets,
  center: [100.5, 13.7],
  zoom: 1.6,
  hash: true,              // keep the map position in the URL so links can be shared
  attributionControl: { compact: true },
});
map.addControl(new maplibregl.ScaleControl(), "bottom-right");

map.on("style.load", () => {
  map.setProjection({ type: state.globe ? "globe" : "mercator" });
  try {
    map.setSky({ "sky-color": "#1d6fd1", "horizon-color": "#ffffff", "atmosphere-blend": ["interpolate", ["linear"], ["zoom"], 0, 1, 5, 1, 7, 0] });
  } catch (e) { /* บางแผนที่ฐานไม่รองรับ ไม่เป็นไร */ }
  addAllLayers(map);
  redrawAll();
});

// Slowly rotate the globe until the user interacts
const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
setInterval(() => {
  if (state.userMoved || reduceMotion || map.getZoom() > 3 || !state.globe) return;
  const c = map.getCenter();
  map.easeTo({ center: [c.lng + 2, c.lat], duration: 1000, easing: x => x });
}, 1000);
["mousedown", "touchstart", "wheel", "keydown"].forEach(ev => map.getCanvasContainer().addEventListener(ev, () => { state.userMoved = true; }));

// Reload the forecast grid after pan/zoom (wait 0.5 s after the map stops)
let moveTimer = null;
map.on("moveend", () => {
  clearTimeout(moveTimer);
  moveTimer = setTimeout(loadGrid, 500);
});

// ======================================================================
// Hazard category buttons (chips)
// ======================================================================
function renderChips() {
  const box = document.getElementById("chips");
  box.innerHTML = "";
  for (const id of CHIP_ORDER) {
    const b = document.createElement("button");
    b.className = "chip" + (state.enabled.has(id) ? " on" : "");
    b.textContent = TEXT[LANG].chips[id];
    b.onclick = () => toggleLayer(id);
    box.appendChild(b);
  }
}

function toggleLayer(id, forceOn = false) {
  if (state.enabled.has(id) && !forceOn) {
    state.enabled.delete(id);
  } else {
    if (GRID_LAYERS.includes(id)) GRID_LAYERS.forEach(g => state.enabled.delete(g));
    state.enabled.add(id);
  }
  renderChips();
  if (GRID_LAYERS.includes(id) || forceOn) loadGrid();
  if (id === "radar") loadRadar();
  redrawAll();
  updateLayerInfo();
}

function activeGridVariable() {
  return GRID_LAYERS.find(g => state.enabled.has(g)) || null;
}

// ======================================================================
// Load layer data
// ======================================================================
let lastGridKey = "";
let gridRetryTimer = null;

async function loadGrid() {
  const variable = activeGridVariable();
  showLegend(variable);
  if (!variable) {
    DATA.grid = null;
    lastGridKey = "";
    if (map.getSource("grid")) { map.getSource("grid").setData(EMPTY); map.getSource("wind-arrows").setData(EMPTY); }
    updateLayerInfo();
    return;
  }
  const zoom = map.getZoom();
  let w = -180, s = -60, e = 180, n = 70;
  if (zoom >= 3) {
    const b = map.getBounds();
    w = Math.max(b.getWest(), -180); e = Math.min(b.getEast(), 180); s = b.getSouth(); n = b.getNorth();
  }
  // same layer + about the same area as last time -> nothing to download (e.g. while the globe rotates)
  const key = [variable, Math.round(w), Math.round(s), Math.round(e), Math.round(n), Math.floor(zoom)].join("|");
  if (key === lastGridKey && DATA.grid && DATA.grid.variable === variable) return;
  try {
    const grid = await getJson(`/map/grid?variable=${variable}&west=${w}&south=${s}&east=${e}&north=${n}&zoom=${zoom.toFixed(1)}`);
    if (activeGridVariable() !== variable) return;   // the user already switched layers
    DATA.grid = grid;
    lastGridKey = key;
    state.gridError = null;
    if (grid.times.length) setTimes(grid.times);
    drawGrid(map, state.timeIndex);
  } catch (err) {
    console.warn("grid", err);
    state.gridError = err.message;
    clearTimeout(gridRetryTimer);
    gridRetryTimer = setTimeout(loadGrid, 60 * 1000);   // try again in 1 minute
  }
  updateLayerInfo();
}

// Short status text next to the legend, so an empty layer is never a mystery
function updateLayerInfo() {
  const box = document.getElementById("layer-info");
  const th = LANG === "th";
  const lines = [];
  const variable = activeGridVariable();
  if (variable && state.gridError) {
    const quota = state.gridError.includes("429") || state.gridError.includes("quota");
    lines.push("⚠️ " + (quota
      ? (th ? "แหล่งข้อมูลพยากรณ์ฟรี (Open-Meteo) ใช้เกินโควตาชั่วคราว ระบบจะลองใหม่อัตโนมัติ" : "The free forecast API (Open-Meteo) is over its quota for now; retrying automatically")
      : (th ? "โหลดข้อมูลพยากรณ์ไม่ได้ ระบบจะลองใหม่ใน 1 นาที" : "Could not load forecast data; retrying in 1 minute")));
  } else if (variable === "precipitation" && DATA.grid) {
    const wet = DATA.grid.cells.filter(c => (c.values[state.timeIndex] ?? 0) >= 0.2).length;
    if (wet === 0) {
      lines.push("☀️ " + (th ? "ไม่มีฝนในพื้นที่นี้ช่วงเวลานี้ — ลองเลื่อนแถบเวลา หรือเปิด 📡 เรดาร์"
                              : "No rain in this area at this time — move the timeline or turn on 📡 Radar"));
    }
  }
  if (state.enabled.has("radar") && DATA.radarFrames.length === 0) {
    lines.push("📡 " + (th ? "ยังไม่มีข้อมูลเรดาร์" : "No radar data yet"));
  }
  box.innerHTML = lines.map(l => `<div class="line">${escapeHtml(l)}</div>`).join("");

  // storm list: storms are often far away (e.g. in the Pacific), so offer a button to fly there
  if (state.enabled.has("storms")) {
    const storms = DATA.events.filter(e => e.hazard === "STORM");
    const title = document.createElement("div");
    title.className = "line";
    title.textContent = storms.length
      ? `🌀 ${th ? "พายุที่กำลังเกิดอยู่" : "Active storms"}: ${storms.length}`
      : `🌀 ${th ? "ตอนนี้ไม่มีพายุที่กำลังเกิด" : "No active storms right now"}`;
    box.appendChild(title);
    storms.slice(0, 5).forEach(storm => {
      const b = document.createElement("button");
      b.textContent = "→ " + storm.title + (storm.place ? ` (${storm.place})` : "");
      b.onclick = () => goToEvent(storm);
      const line = document.createElement("div");
      line.className = "line";
      line.appendChild(b);
      box.appendChild(line);
    });
  }
  box.classList.toggle("hidden", box.childElementCount === 0);
}

async function loadEvents() {
  try {
    const data = await getJson("/hazards/events?window=7d");
    DATA.events = [...data.earthquakes, ...data.events];
    DATA.storms = data.events.filter(e => e.hazard === "STORM" && e.track);
    drawEvents(map, state.enabled);
    updateLayerInfo();
  } catch (err) {
    console.warn("events", err);
  }
}

async function loadRadar() {
  try {
    DATA.radarFrames = (await getJson("/map/radar")).frames;
    drawRadar(map, state.enabled, currentTimeMs());
    updateLayerInfo();
  } catch (err) {
    console.warn("radar", err);
  }
}

function redrawAll() {
  drawGrid(map, state.timeIndex);
  drawEvents(map, state.enabled);
  drawRadar(map, state.enabled, currentTimeMs());
  drawRoutes(map);
  drawPoi(map);
}

// ======================================================================
// Timeline: past 24 h to +72 h forecast (hourly)
// ======================================================================
function defaultTimes() {
  const start = new Date();
  start.setUTCHours(0, 0, 0, 0);
  start.setUTCDate(start.getUTCDate() - 1);
  return Array.from({ length: 96 }, (_, i) => new Date(start.getTime() + i * 3.6e6).toISOString());
}

function nearestIndex(times, ms) {
  let best = 0;
  times.forEach((t, i) => { if (Math.abs(new Date(t) - ms) < Math.abs(new Date(times[best]) - ms)) best = i; });
  return best;
}

function setTimes(times) {
  const keepMs = state.times.length ? currentTimeMs() : Date.now();
  state.times = times;
  state.timeIndex = nearestIndex(times, keepMs);
  const slider = document.getElementById("time-slider");
  slider.max = times.length - 1;
  slider.value = state.timeIndex;
  updateTimeLabel();
}

function currentTimeMs() {
  return state.times.length ? new Date(state.times[state.timeIndex]).getTime() : Date.now();
}

function formatLocal(iso, withDate = true) {
  const d = new Date(iso);
  const opts = { timeZone: "Asia/Bangkok", hour: "2-digit", minute: "2-digit" };
  if (withDate) Object.assign(opts, { weekday: "short", day: "numeric", month: "short" });
  return d.toLocaleString(LANG === "th" ? "th-TH" : "en-GB", opts);
}

function updateTimeLabel() {
  const ms = currentTimeMs();
  const diffH = Math.round((ms - Date.now()) / 3.6e6);
  const rel = diffH === 0 ? t("now") : (diffH > 0 ? `+${diffH} h` : `${diffH} h`);
  document.getElementById("time-label").textContent = `${formatLocal(new Date(ms).toISOString())} (${rel})`;
}

function setTimeIndex(i) {
  state.timeIndex = Math.max(0, Math.min(state.times.length - 1, i));
  document.getElementById("time-slider").value = state.timeIndex;
  updateTimeLabel();
  drawGrid(map, state.timeIndex);
  drawRadar(map, state.enabled, currentTimeMs());
  updateLayerInfo();
}

document.getElementById("time-slider").addEventListener("input", e => setTimeIndex(Number(e.target.value)));
document.getElementById("now-btn").onclick = () => setTimeIndex(nearestIndex(state.times, Date.now()));
document.getElementById("play-btn").onclick = e => {
  if (state.playing) {
    clearInterval(state.playing);
    state.playing = null;
    e.target.textContent = "▶";
  } else {
    e.target.textContent = "⏸";
    state.playing = setInterval(() => setTimeIndex((state.timeIndex + 1) % state.times.length), 700);
  }
};

// ======================================================================
// Side panel
// ======================================================================
function openPanel(name) {
  document.getElementById("panel").classList.remove("hidden");
  document.querySelectorAll(".panel-page").forEach(p => p.classList.add("hidden"));
  document.getElementById("panel-" + name).classList.remove("hidden");
  document.querySelectorAll(".rail-btn").forEach(b => b.classList.toggle("active", b.dataset.panel === name));
}
document.querySelectorAll(".rail-btn").forEach(b => { b.onclick = () => openPanel(b.dataset.panel); });
document.getElementById("panel-close").onclick = () => document.getElementById("panel").classList.add("hidden");
document.getElementById("directions-btn").onclick = () => openPanel("trip");

function sevBadge(sev) {
  return `<span class="sev sev-${sev}">${escapeHtml(TEXT[LANG].sevNames[sev])}</span>`;
}

// ======================================================================
// Map clicks
// ======================================================================
map.on("click", e => {
  const layers = ["ev-quakes", "ev-other", "poi"].filter(id => map.getLayer(id));
  const hits = map.queryRenderedFeatures(e.point, { layers });
  if (hits.length) {
    showFeaturePopup(hits[0], e.lngLat);
  } else {
    showPointInfo(e.lngLat.lat, e.lngLat.lng);
  }
});
["ev-quakes", "ev-other", "poi"].forEach(id => {
  map.on("mouseenter", id, () => { map.getCanvas().style.cursor = "pointer"; });
  map.on("mouseleave", id, () => { map.getCanvas().style.cursor = ""; });
});

function showFeaturePopup(feature, lngLat) {
  const p = feature.properties;
  let html = `<b>${escapeHtml(p.title || p.name)}</b><br>`;
  if (p.hazard === "EARTHQUAKE") {
    html += `M${escapeHtml(p.mag)} · ${escapeHtml(formatLocal(p.time))}<br><small>${escapeHtml(LANG === "th"
      ? "แผ่นดินไหวไม่สามารถพยากรณ์ล่วงหน้าได้" : "Earthquakes cannot be predicted")}</small><br>`;
  } else if (p.hazard) {
    html += `${escapeHtml(TEXT[LANG].hazardNames[p.hazard] || p.hazard)} · ${escapeHtml(p.extra)}<br>`;
  }
  html += `<span class="where">${escapeHtml(whereText({ lat: lngLat.lat, lon: lngLat.lng, place: p.place }, false))}</span><br>`;
  if (p.source) html += `<small>${t("sources")}: ${escapeHtml(p.source)}</small><br>`;
  if (p.url && p.url.startsWith("http")) html += `<a href="${escapeHtml(p.url)}" target="_blank" rel="noopener">รายละเอียด / details</a>`;
  new maplibregl.Popup().setLngLat(lngLat).setHTML(html).addTo(map);
}

let pointMarker = null;

async function showPointInfo(lat, lon) {
  openPanel("point");
  if (pointMarker) pointMarker.remove();
  pointMarker = new maplibregl.Marker({ color: "#1a73e8" }).setLngLat([lon, lat]).addTo(map);
  const body = document.getElementById("point-body");
  body.innerHTML = `<p><span class="spinner"></span>${t("loading")}</p>`;
  try {
    const d = await getJson(`/forecast/point?lat=${lat.toFixed(4)}&lon=${lon.toFixed(4)}&lang=${LANG}`);
    const name = d.place && d.place.name ? d.place.name : `${lat.toFixed(3)}, ${lon.toFixed(3)}`;
    body.innerHTML = `
      <h3>${escapeHtml(name)}</h3>
      <p class="meta">${escapeHtml(d.place ? d.place.label : "")}</p>
      <div class="card"><h3>${t("hazards48")}</h3>
        ${d.hazards.map(h => `<div class="hazard-row"><span><b>${escapeHtml(TEXT[LANG].hazardNames[h.hazard] || h.hazard)}</b>:
          ${escapeHtml(LANG === "th" ? h.text_th : h.text_en)}</span>${sevBadge(h.severity)}</div>`).join("")}
      </div>
      <div class="card"><h3>${t("chart48")}</h3>${forecastChart(d.forecast)}</div>
      ${d.degraded.length ? `<p class="meta">${t("degraded")} ${escapeHtml(d.degraded.join(", "))}</p>` : ""}
      <div class="buttons">
        <button class="secondary" id="pt-origin">${t("setOrigin")}</button>
        <button class="secondary" id="pt-dest">${t("setDest")}</button>
        <button class="secondary" id="pt-ask">${t("askHere")}</button>
        <button class="secondary" id="pt-near">${t("nearby")}</button>
        <button class="secondary" id="pt-sub">🔔 ${t("subscribe")}</button>
      </div>
      <p class="meta">${t("sources")}: Open-Meteo, USGS, GDACS, NASA EONET, OpenStreetMap · ${t("updated")} ${escapeHtml(formatLocal(d.fetched_at))}</p>`;
    const form = document.getElementById("trip-form");
    document.getElementById("pt-origin").onclick = () => { form.origin.value = name; openPanel("trip"); };
    document.getElementById("pt-dest").onclick = () => { form.destination.value = name; openPanel("trip"); };
    document.getElementById("pt-ask").onclick = () => {
      openPanel("chat");
      sendChat(LANG === "th" ? `สภาพอากาศและภัยที่${name}` : `weather and hazards in ${name}`, lat, lon);
    };
    document.getElementById("pt-near").onclick = () => loadNearby(lat, lon);
    document.getElementById("pt-sub").onclick = async e => {
      try {
        await postJson("/subscriptions", { name, lat, lon, radius_km: 100, hazards: [], min_severity: 3, lang: LANG });
        e.target.textContent = "✓ " + t("subscribed");
        e.target.disabled = true;
        loadMyAlerts();
      } catch (err) {
        alert(t("errorMsg") + ": " + err.message);
      }
    };
  } catch (err) {
    body.innerHTML = `<p>${t("errorMsg")}: ${escapeHtml(err.message)}</p>`;
  }
}

async function loadNearby(lat, lon) {
  try {
    DATA.poi = await getJson(`/places/nearby?lat=${lat}&lon=${lon}`);
    drawPoi(map);
    map.flyTo({ center: [lon, lat], zoom: 12 });
  } catch (err) {
    alert(t("errorMsg") + ": " + err.message);
  }
}

// Simple 48 h chart (SVG): line = temperature, bars = rain
function forecastChart(fc) {
  const start = nearestIndex(fc.time, Date.now());
  const times = fc.time.slice(start, start + 48);
  // missing values (null) would break Math.min/max, so reuse the previous value (or 0 for rain)
  const temps = [], rains = [];
  let lastTemp = fc.temperature_2m.find(v => v !== null) ?? 0;
  for (let i = start; i < start + times.length; i++) {
    if (fc.temperature_2m[i] !== null) lastTemp = fc.temperature_2m[i];
    temps.push(lastTemp);
    rains.push(fc.precipitation[i] ?? 0);
  }
  if (temps.length < 2) return "";
  const W = 360, H = 120, pad = 22;
  const tMin = Math.min(...temps) - 1, tMax = Math.max(...temps) + 1;
  const rMax = Math.max(5, ...rains);
  const x = i => pad + (i * (W - pad * 2)) / (temps.length - 1);
  const yT = v => H - pad - ((v - tMin) / (tMax - tMin)) * (H - pad * 2);
  const bars = rains.map((r, i) => {
    const h = (r / rMax) * (H - pad * 2);
    return `<rect x="${x(i) - 2}" y="${H - pad - h}" width="4" height="${h}" fill="#4292c6"></rect>`;
  }).join("");
  const line = temps.map((v, i) => `${i ? "L" : "M"}${x(i).toFixed(1)},${yT(v).toFixed(1)}`).join(" ");
  const labels = times.map((tm, i) => (i % 12 === 0 ? `<text x="${x(i)}" y="${H - 6}" font-size="9" fill="currentColor" text-anchor="middle">${escapeHtml(formatLocal(tm, false))}</text>` : "")).join("");
  return `<svg class="chart" viewBox="0 0 ${W} ${H}" role="img" aria-label="${t("chart48")}">
    ${bars}<path d="${line}" fill="none" stroke="#e8710a" stroke-width="2"></path>${labels}
    <text x="2" y="12" font-size="9" fill="#e8710a">${Math.round(tMax)}°C</text>
    <text x="2" y="${H - pad}" font-size="9" fill="#e8710a">${Math.round(tMin)}°C</text>
    <text x="${W - 2}" y="12" font-size="9" fill="#4292c6" text-anchor="end">${rMax.toFixed(0)} mm/h</text></svg>`;
}

// ======================================================================
// Trip planner
// ======================================================================
document.getElementById("trip-form").addEventListener("submit", async e => {
  e.preventDefault();
  const form = e.target;
  const btn = form.querySelector("button[type=submit]");
  if (btn.disabled) return;   // prevent double submit
  btn.disabled = true;
  const progress = document.getElementById("trip-progress");
  progress.classList.remove("hidden");
  progress.innerHTML = `<span class="spinner"></span>${t("steps")}`;
  document.getElementById("trip-result").innerHTML = "";
  try {
    const resp = await postJson("/trip", {
      origin: form.origin.value.trim(), destination: form.destination.value.trim(),
      departure_time: form.departure_time.value || null, travel_mode: form.travel_mode.value, lang: LANG,
    });
    showResult(resp, document.getElementById("trip-result"));
  } catch (err) {
    document.getElementById("trip-result").innerHTML = `<p>${t("errorMsg")}: ${escapeHtml(err.message)}</p>`;
  } finally {
    btn.disabled = false;
    progress.classList.add("hidden");
  }
});

// Render a recommendation (used by both the trip panel and chat)
function showResult(resp, container) {
  let html = "";
  if (resp.response_type === "RECOMMENDATION" && resp.action_code) {
    const icon = { NORMAL: "✓", CHANGE_ROUTE: "⚠", DELAY: "⏱", AVOID: "✕" }[resp.action_code];
    html += `<div class="action-badge act-${resp.action_code}">${icon} ${escapeHtml(resp.action_text)}</div>
      <p class="meta">${t("risk")}: <b>${escapeHtml(t(resp.risk_level))}</b> · ${t("confidence")}: ${Math.round(resp.confidence * 100)}%</p>`;
  } else if (resp.response_type === "EMERGENCY") {
    html += `<div class="action-badge act-EMERGENCY">✚ ${LANG === "th" ? "คำแนะนำฉุกเฉิน" : "Emergency instructions"}</div>`;
  }
  html += `<p>${escapeHtml(resp.summary)}</p>`;
  if (resp.suggested_departure_time) {
    html += `<div class="card"><b>${t("suggestedTime")}:</b> ${escapeHtml(formatLocal(resp.suggested_departure_time))}</div>`;
  }
  if (resp.immediate_actions && resp.immediate_actions.length) {
    html += `<div class="card"><h3>${t("whatToDo")}</h3><ul>${resp.immediate_actions.map(a => `<li>${escapeHtml(a)}</li>`).join("")}</ul></div>`;
  }
  if (resp.emergency_contacts && resp.emergency_contacts.length) {
    html += `<div class="card contacts"><h3>${t("contacts")}</h3>${resp.emergency_contacts.map(c =>
      `<a href="tel:${escapeHtml(c.phone)}">${escapeHtml(c.phone)} ${escapeHtml(c.name)}</a>`).join("")}</div>`;
  }
  if (resp.routes && resp.routes.length) {
    html += `<div class="card"><h3>${t("routes")}</h3>${resp.routes.map(r => `
      <div class="card route-item ${r.selected ? "selected" : ""}" data-route="${escapeHtml(r.route_id)}">
        <b>${escapeHtml(r.label)}</b> ${r.selected ? "⭐" : ""} — ${r.distance_km} ${t("km")}, ${Math.round(r.duration_min)} ${t("min")}
        <br>${t("risk")}: <span style="color:${RISK_COLORS[r.risk_level]}">●</span> ${escapeHtml(t(r.risk_level))}
        ${r.extra_minutes > 0 ? ` (+${Math.round(r.extra_minutes)} ${t("min")})` : ""}</div>`).join("")}</div>`;
  }
  if (resp.reasons && resp.reasons.length) {
    html += `<div class="card"><h3>${t("reasons")}</h3><ul>${resp.reasons.map(r => `<li>${escapeHtml(r)}</li>`).join("")}</ul></div>`;
  }
  if (resp.citations && resp.citations.length) {
    html += `<div class="card"><h3>${t("citations")}</h3><ul>${resp.citations.map(c => `<li>${escapeHtml(c.title)}${c.section ? " — " + escapeHtml(c.section) : ""}
      ${c.url && c.url.startsWith("http") ? ` <a href="${escapeHtml(c.url)}" target="_blank" rel="noopener">🔗</a>` : ""}</li>`).join("")}</ul></div>`;
  }
  if (resp.nearby_places && resp.nearby_places.length) {
    html += `<div class="card"><h3>${t("places")}</h3><ul>${resp.nearby_places.map(p => `<li>${escapeHtml(p.name)}</li>`).join("")}</ul></div>`;
  }
  if ((resp.limitations && resp.limitations.length) || (resp.degraded_services && resp.degraded_services.length)) {
    html += `<div class="card"><h3>${t("limitations")}</h3><ul>${[...(resp.limitations || []), ...(resp.degraded_services || []).map(s => t("degraded") + " " + s)]
      .map(x => `<li>${escapeHtml(x)}</li>`).join("")}</ul></div>`;
  }
  if (resp.understood_by === "llama" || (resp.versions && String(resp.versions.generator || "").startsWith("llama"))) {
    html += `<p class="meta">🦙 ${LANG === "th" ? "ใช้ Llama API ช่วยวิเคราะห์คำถาม/เรียบเรียงคำอธิบาย (คำแนะนำมาจากกฎความปลอดภัย)"
      : "Llama API helped understand the question / word the explanation (the advice itself comes from safety rules)"}</p>`;
  }
  if (resp.sources && resp.sources.length) {
    html += `<p class="meta">${t("sources")}: ${escapeHtml(resp.sources.join(", "))} · ${t("updated")} ${escapeHtml(formatLocal(resp.fetched_at))}</p>`;
  }
  if (resp.response_type === "RECOMMENDATION") {
    html += `<p class="meta">${t("feedbackQ")}</p><div class="buttons">
      <button class="secondary fb" data-cat="HELPFUL">👍</button><button class="secondary fb" data-cat="INCORRECT">👎</button>
      <button class="secondary fb" data-cat="UNSAFE">⚠ ${LANG === "th" ? "ไม่ปลอดภัย" : "Unsafe"}</button></div>`;
  }
  container.innerHTML = html;

  container.querySelectorAll(".route-item").forEach(el => {
    el.onclick = () => { DATA.selectedRoute = el.dataset.route; drawRoutes(map); };
  });
  container.querySelectorAll(".fb").forEach(el => {
    el.onclick = async () => {
      await postJson("/feedback", { request_id: resp.request_id, category: el.dataset.cat }).catch(() => {});
      el.parentElement.innerHTML = `<span class="meta">${t("thanks")}</span>`;
    };
  });

  // Draw routes / events / places on the map
  if (resp.routes && resp.routes.length) {
    DATA.routes = resp.routes;
    DATA.selectedRoute = (resp.routes.find(r => r.selected) || resp.routes[0]).route_id;
    drawRoutes(map);
  }
  if (resp.nearby_places && resp.nearby_places.length) {
    DATA.poi = resp.nearby_places;
    drawPoi(map);
  }
  applyUiActions(resp.ui_actions || []);
}

// Apply ui_actions sent by the agent (move the map to match the answer)
function applyUiActions(actions) {
  const panelOpen = !document.getElementById("panel").classList.contains("hidden") && window.innerWidth > 760;
  const padding = { top: 130, bottom: 110, left: panelOpen ? 500 : 100, right: 80 };
  for (const a of actions) {
    if (a.type === "FIT_BOUNDS" && a.bbox) {
      state.userMoved = true;
      map.fitBounds([[a.bbox[0], a.bbox[1]], [a.bbox[2], a.bbox[3]]], { padding, maxZoom: 11, duration: 1500 });
    } else if (a.type === "FLY_TO" && a.center) {
      state.userMoved = true;
      map.flyTo({ center: [a.center.lon, a.center.lat], zoom: a.zoom || 8, duration: 1500 });
    } else if (a.type === "ENABLE_LAYERS" && a.layers) {
      a.layers.forEach(l => { if (CHIP_ORDER.includes(l) && !state.enabled.has(l)) toggleLayer(l, true); });
    } else if (a.type === "SET_TIME" && a.time && state.times.length) {
      setTimeIndex(nearestIndex(state.times, new Date(a.time).getTime()));
    }
  }
}

// ======================================================================
// Chat with the assistant
// ======================================================================
function addMessage(text, who) {
  const div = document.createElement("div");
  div.className = "msg " + who;
  div.textContent = text;
  document.getElementById("chat-log").appendChild(div);
  div.scrollIntoView({ behavior: "smooth" });
  return div;
}

async function sendChat(text, lat, lon) {
  if (!text.trim()) return;
  addMessage(text, "user");
  const wait = addMessage("…", "bot");
  const center = map.getCenter();
  try {
    const resp = await postJson("/chat", { text, lang: LANG, map_lat: lat ?? center.lat, map_lon: lon ?? center.lng });
    wait.textContent = "";
    showResult(resp, wait);
  } catch (err) {
    wait.textContent = t("errorMsg") + ": " + err.message;
  }
}

document.getElementById("chat-form").addEventListener("submit", e => {
  e.preventDefault();
  const input = document.getElementById("chat-input");
  sendChat(input.value);
  input.value = "";
});
document.querySelectorAll(".example").forEach(b => { b.onclick = () => sendChat(b.textContent); });

// ======================================================================
// Place search (or type a question and send it to the assistant)
// ======================================================================
const searchInput = document.getElementById("search");
const suggestions = document.getElementById("suggestions");
let searchTimer = null;

function looksLikeQuestion(text) {
  return /ไหม|มั้ย|อย่างไร|ยังไง|จาก.+ไป|\?|ฝน|น้ำท่วม|แผ่นดินไหว|พายุ|ไฟป่า|ฝุ่น|safe|from .+ to|earthquake|rain|storm/i.test(text);
}

searchInput.addEventListener("input", () => {
  clearTimeout(searchTimer);
  const q = searchInput.value.trim();
  if (q.length < 2 || looksLikeQuestion(q)) { suggestions.classList.add("hidden"); return; }
  searchTimer = setTimeout(async () => {
    try {
      const places = await getJson(`/places/search?q=${encodeURIComponent(q)}&lang=${LANG}`);
      suggestions.innerHTML = places.map((p, i) => `<li data-i="${i}">${escapeHtml(p.label)}</li>`).join("");
      suggestions.classList.toggle("hidden", places.length === 0);
      suggestions.querySelectorAll("li").forEach(li => {
        li.onclick = () => {
          const p = places[li.dataset.i];
          suggestions.classList.add("hidden");
          searchInput.value = p.name;
          state.userMoved = true;
          map.flyTo({ center: [p.lon, p.lat], zoom: 10 });
          showPointInfo(p.lat, p.lon);
        };
      });
    } catch (err) {
      suggestions.classList.add("hidden");
    }
  }, 400);
});

function submitSearch() {
  const q = searchInput.value.trim();
  if (!q) return;
  suggestions.classList.add("hidden");
  if (looksLikeQuestion(q)) {
    openPanel("chat");
    sendChat(q);
    return;
  }
  clearTimeout(searchTimer);   // the user pressed Enter: search now, do not wait for the dropdown
  getJson(`/places/search?q=${encodeURIComponent(q)}&lang=${LANG}`).then(places => {
    if (!places.length) {
      alert(LANG === "th" ? "ไม่พบสถานที่นี้" : "Place not found");
      return;
    }
    const p = places[0];
    state.userMoved = true;
    map.flyTo({ center: [p.lon, p.lat], zoom: 10 });
    showPointInfo(p.lat, p.lon);
  }).catch(err => alert(t("errorMsg") + ": " + err.message));
}
searchInput.addEventListener("keydown", e => { if (e.key === "Enter") submitSearch(); });
document.getElementById("search-btn").onclick = submitSearch;

// ======================================================================
// Alerts + data provider status
// ======================================================================
// ---------- where is an event? + go there ----------
function fixTime(text) {
  // some sources send times without a time zone; they are UTC
  return text.includes("Z") || text.includes("+") ? text : text + "Z";
}

function coordText(lat, lon) {
  const ns = lat >= 0 ? "N" : "S", ew = lon >= 0 ? "E" : "W";
  return `${Math.abs(lat).toFixed(2)}°${ns} ${Math.abs(lon).toFixed(2)}°${ew}`;
}

function whereText(e, withDistance = true) {
  // "📍 place · coordinates · about N km from the map center"
  const parts = [];
  if (e.place || e.area_name) parts.push(e.place || e.area_name);
  parts.push(coordText(e.lat, e.lon));
  if (withDistance) {
    const center = map.getCenter();
    const km = Math.round(distKm([center.lng, center.lat], [e.lon, e.lat]));
    parts.push(LANG === "th" ? `ห่างจากจุดที่ดูอยู่ ~${km.toLocaleString()} กม.` : `~${km.toLocaleString()} km from the map center`);
  }
  return "📍 " + parts.join(" · ");
}

let eventMarker = null;

function goToEvent(e) {
  // turn on the matching layer, fly there, and show a marker with a popup
  const layer = { EARTHQUAKE: "earthquakes", STORM: "storms", FLOOD: "floods", FIRE: "fires", VOLCANO: "volcanoes" }[e.hazard];
  if (layer && !state.enabled.has(layer)) toggleLayer(layer, true);
  state.userMoved = true;
  map.flyTo({ center: [e.lon, e.lat], zoom: Math.max(map.getZoom(), 6), duration: 1500 });
  if (eventMarker) eventMarker.remove();
  const sev = e.severity ?? 0;
  const html = `<b>${escapeHtml(e.title || "")}</b><br>${sev ? sevBadge(sev) + " " : ""}${escapeHtml(TEXT[LANG].hazardNames[e.hazard] || e.hazard)}<br>
    <span class="where">${escapeHtml(whereText(e, false))}</span>
    ${e.time ? `<br><small>${escapeHtml(formatLocal(fixTime(e.time)))}</small>` : ""}
    ${e.url && String(e.url).startsWith("http") ? `<br><a href="${escapeHtml(e.url)}" target="_blank" rel="noopener">${LANG === "th" ? "รายละเอียด" : "Details"}</a>` : ""}`;
  eventMarker = new maplibregl.Marker({ color: "#c62828" })
    .setLngLat([e.lon, e.lat])
    .setPopup(new maplibregl.Popup({ offset: 25 }).setHTML(html))
    .addTo(map);
  eventMarker.togglePopup();
}

// pop-up message for new severe events (each event is shown only once)
const seenAlertIds = new Set();
let firstAlertLoad = true;

function showToastForNewAlerts(alerts) {
  const fresh = alerts.filter(a => !seenAlertIds.has(a.id));
  alerts.forEach(a => seenAlertIds.add(a.id));
  if (!fresh.length) return;
  const top = fresh[0];   // the list is sorted: most severe first
  const th = LANG === "th";
  const box = document.getElementById("toast");
  const intro = firstAlertLoad
    ? (th ? `⚠️ มีเหตุการณ์รุนแรง ${alerts.length} รายการ ล่าสุด:` : `⚠️ ${alerts.length} severe events. Latest:`)
    : (th ? "⚠️ เหตุการณ์รุนแรงใหม่:" : "⚠️ New severe event:");
  firstAlertLoad = false;
  box.innerHTML = `${escapeHtml(intro)} <b>${escapeHtml(TEXT[LANG].hazardNames[top.hazard] || top.hazard)}</b> — ${escapeHtml(top.title || "")}
    <small>${escapeHtml(whereText(top))} · ${th ? "คลิกเพื่อดูบนแผนที่" : "click to see it on the map"}</small>`;
  box.classList.remove("hidden");
  box.onclick = () => { box.classList.add("hidden"); goToEvent(top); };
  clearTimeout(box.hideTimer);
  if (top.severity < 4) box.hideTimer = setTimeout(() => box.classList.add("hidden"), 15000);  // emergencies stay
}

async function loadAlerts() {
  try {
    const data = await getJson("/alerts");
    const list = document.getElementById("alerts-list");
    const count = document.getElementById("alert-count");
    count.textContent = data.alerts.length;
    count.classList.toggle("hidden", data.alerts.length === 0);
    if (!data.alerts.length) { list.innerHTML = `<p class="hint">${t("noAlerts")}</p>`; return; }
    list.innerHTML = data.alerts.map((a, i) => `<div class="card alert-item" data-i="${i}">
      ${sevBadge(a.severity)} <b>${escapeHtml(TEXT[LANG].hazardNames[a.hazard] || a.hazard)}</b><br>
      ${escapeHtml(a.title || a.place)}<br>
      <span class="where">${escapeHtml(whereText(a))}</span><br>
      <span class="meta">${escapeHtml(a.source)} · ${a.time ? escapeHtml(formatLocal(fixTime(a.time))) : ""}</span></div>`).join("");
    list.querySelectorAll(".alert-item").forEach(el => {
      el.onclick = () => goToEvent(data.alerts[el.dataset.i]);
    });
    showToastForNewAlerts(data.alerts);
  } catch (err) {
    console.warn("alerts", err);
  }
}

async function loadMyAlerts() {
  try {
    const [areas, notes] = await Promise.all([getJson("/subscriptions"), getJson("/notifications")]);
    const areaBox = document.getElementById("my-areas");
    areaBox.innerHTML = areas.length ? areas.map(a => `<div class="card">📍 <b>${escapeHtml(a.name)}</b>
        <span class="meta">(${a.radius_km} ${t("km")})</span>
        <button class="secondary" data-del="${escapeHtml(a.id)}" style="float:right">${t("remove")}</button></div>`).join("")
      : `<p class="hint">${t("noAreas")}</p>`;
    areaBox.querySelectorAll("[data-del]").forEach(b => {
      b.onclick = async () => { await postJson("/subscriptions/" + b.dataset.del, null, "DELETE").catch(() => {}); loadMyAlerts(); };
    });
    const noteBox = document.getElementById("my-notifications");
    const shown = notes.slice(0, 10);
    noteBox.innerHTML = shown.length ? shown.map((n, i) => `<div class="card alert-item" data-i="${i}">
        ${sevBadge(n.severity)} <b>${escapeHtml(n.area_name || "")}</b>: ${escapeHtml(n.title)}
        <br><span class="where">${escapeHtml(whereText(n))}</span>
        <br><span class="meta">${LANG === "th" ? "ห่างจากพื้นที่ของคุณ" : "from your area"} ${n.distance_km} ${t("km")} · ${escapeHtml(formatLocal(n.created_at))}</span></div>`).join("")
      : (areas.length ? `<p class="hint">${t("noNotifications")}</p>` : "");
    noteBox.querySelectorAll(".alert-item").forEach(el => {
      el.onclick = () => goToEvent(shown[el.dataset.i]);
    });
    const count = document.getElementById("alert-count");
    if (notes.length) { count.textContent = notes.length; count.classList.remove("hidden"); }
  } catch (err) {
    console.warn("my alerts", err);
  }
}

async function loadProviderHealth() {
  try {
    const status = await getJson("/providers/health");
    const down = Object.entries(status).filter(([, v]) => v.status === "DOWN").map(([k]) => k);
    const box = document.getElementById("degraded");
    box.textContent = `${t("degraded")} ${down.join(", ")}`;
    box.classList.toggle("hidden", down.length === 0);
  } catch (err) {
    const box = document.getElementById("degraded");
    box.textContent = LANG === "th" ? "เชื่อมต่อ API ไม่ได้ — ตรวจสอบว่าเปิดเซิร์ฟเวอร์ครบแล้ว (port 8000-8006)" : "Cannot reach the API (ports 8000-8006)";
    box.classList.remove("hidden");
  }
}

// ======================================================================
// Buttons
// ======================================================================
document.getElementById("zoomin-btn").onclick = () => map.zoomIn();
document.getElementById("zoomout-btn").onclick = () => map.zoomOut();
document.getElementById("globe-btn").onclick = () => {
  state.globe = !state.globe;
  map.setProjection({ type: state.globe ? "globe" : "mercator" });
};
document.getElementById("locate-btn").onclick = () => {
  if (!navigator.geolocation) return;
  navigator.geolocation.getCurrentPosition(pos => {
    state.userMoved = true;
    map.flyTo({ center: [pos.coords.longitude, pos.coords.latitude], zoom: 11 });
    showPointInfo(pos.coords.latitude, pos.coords.longitude);
  });
};
document.querySelectorAll("#basemaps button").forEach(b => {
  b.onclick = () => {
    state.basemap = b.dataset.base;
    document.querySelectorAll("#basemaps button").forEach(x => x.classList.toggle("active", x === b));
    map.setStyle(BASEMAPS[state.basemap]);   // style.load redraws the overlay layers
  };
});
document.getElementById("lang-btn").onclick = () => {
  LANG = LANG === "th" ? "en" : "th";
  localStorageSet("lang", LANG);
  applyLanguage();
  renderChips();
  updateTimeLabel();
  showLegend(activeGridVariable());
  updateLayerInfo();
  loadAlerts();
};

// ======================================================================
// Start-up
// ======================================================================
if (location.hash && location.hash !== "#") state.userMoved = true;   // opened from a shared link
applyLanguage();
renderChips();
setTimes(defaultTimes());
map.once("load", () => {
  loadGrid();
  loadEvents();
  loadAlerts();
  loadMyAlerts();
  loadProviderHealth();
});
setInterval(loadMyAlerts, 5 * 60 * 1000);
setInterval(loadEvents, 5 * 60 * 1000);
setInterval(loadAlerts, 5 * 60 * 1000);
setInterval(loadProviderHealth, 2 * 60 * 1000);
