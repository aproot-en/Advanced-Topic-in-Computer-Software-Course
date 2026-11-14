// i18n.js — UI text in two languages (Thai / English)
const TEXT = {
  th: {
    railPoint: "ข้อมูลจุด", railTrip: "เส้นทาง", railChat: "ผู้ช่วย", railAlerts: "แจ้งเตือน",
    searchPlaceholder: "ค้นหาสถานที่ หรือถามผู้ช่วย…", pointTitle: "ข้อมูลจุดที่เลือก",
    pointHint: "คลิกที่ใดก็ได้บนแผนที่เพื่อดูพยากรณ์และภัยในอีก 48 ชั่วโมง",
    tripTitle: "วางแผนเดินทาง", origin: "ต้นทาง", destination: "ปลายทาง", departure: "เวลาออกเดินทาง (ว่าง = ตอนนี้)",
    mode: "การเดินทาง", checkSafety: "ตรวจสอบความปลอดภัย", chatTitle: "ผู้ช่วยการเดินทาง",
    chatPlaceholder: "เช่น พรุ่งนี้เช้าจากกรุงเทพไปเชียงใหม่ปลอดภัยไหม", alertsTitle: "เหตุการณ์รุนแรงล่าสุด",
    baseStreets: "แผนที่", baseSatellite: "ดาวเทียม", baseDark: "กลางคืน", now: "ตอนนี้",
    loading: "กำลังโหลด…", setOrigin: "ตั้งเป็นต้นทาง", setDest: "ตั้งเป็นปลายทาง", askHere: "ถามผู้ช่วยเกี่ยวกับจุดนี้",
    nearby: "โรงพยาบาล/ตำรวจใกล้ ๆ", reasons: "เหตุผล", whatToDo: "สิ่งที่ควรทำ", routes: "เส้นทาง",
    contacts: "เบอร์ฉุกเฉิน", sources: "แหล่งข้อมูล", limitations: "ข้อจำกัด", risk: "ความเสี่ยง",
    confidence: "ความมั่นใจ", updated: "อัปเดต", suggestedTime: "เวลาที่แนะนำให้ออกเดินทาง",
    km: "กม.", min: "นาที", feedbackQ: "คำแนะนำนี้มีประโยชน์ไหม?", thanks: "ขอบคุณสำหรับความคิดเห็น",
    degraded: "ข้อมูลบางส่วนไม่พร้อมใช้งาน:", noAlerts: "ไม่มีเหตุการณ์ระดับเตือนภัยใน 24 ชม.",
    temp: "อุณหภูมิ", rain: "ฝน", errorMsg: "เกิดข้อผิดพลาด", steps: "กำลังตรวจสอบสภาพอากาศ → ภัยพิบัติ → เส้นทาง → ประเมินความเสี่ยง…",
    hazards48: "ภัยใน 48 ชม.", subscribe: "แจ้งเตือนภัยบริเวณนี้", subscribed: "บันทึกพื้นที่แจ้งเตือนแล้ว",
    myAlertsTitle: "การแจ้งเตือนพื้นที่ของฉัน", noAreas: "ยังไม่มีพื้นที่ — คลิกบนแผนที่แล้วกด \"แจ้งเตือนภัยบริเวณนี้\"",
    noNotifications: "ยังไม่มีการแจ้งเตือน", remove: "ลบ", citations: "อ้างอิงคู่มือ", chart48: "พยากรณ์ 48 ชม. (เส้น = อุณหภูมิ, แท่ง = ฝน)", places: "สถานที่ใกล้เคียง",
    LOW: "ต่ำ", MEDIUM: "ปานกลาง", HIGH: "สูง",
    chips: { temperature: "🌡 อากาศ", precipitation: "🌧 ฝน", radar: "📡 เรดาร์", floods: "🌊 น้ำท่วม", wind: "💨 ลม",
             storms: "🌀 พายุ", fires: "🔥 ไฟป่า", earthquakes: "〰 แผ่นดินไหว", pm25: "😷 PM2.5", volcanoes: "🌋 ภูเขาไฟ" },
    sevNames: ["ปกติ", "เฝ้าระวัง", "ระวัง", "เตือนภัย", "อันตรายร้ายแรง"],
    hazardNames: { RAIN: "ฝน", WIND: "ลม", HEAT: "ความร้อน", WEATHER: "อากาศ", AIR_QUALITY: "PM2.5", FLOOD: "น้ำในแม่น้ำ",
                   EARTHQUAKE: "แผ่นดินไหว", STORM: "พายุ", FIRE: "ไฟป่า", VOLCANO: "ภูเขาไฟ", FOG: "หมอก", DROUGHT: "ภัยแล้ง" },
  },
  en: {
    railPoint: "Point", railTrip: "Route", railChat: "Assistant", railAlerts: "Alerts",
    searchPlaceholder: "Search places or ask the assistant…", pointTitle: "Selected point",
    pointHint: "Click anywhere on the map to see the forecast and hazards for the next 48 hours",
    tripTitle: "Plan a trip", origin: "Origin", destination: "Destination", departure: "Departure (empty = now)",
    mode: "Travel mode", checkSafety: "Check safety", chatTitle: "Travel assistant",
    chatPlaceholder: "e.g. from Bangkok to Chiang Mai tomorrow morning", alertsTitle: "Latest severe events",
    baseStreets: "Map", baseSatellite: "Satellite", baseDark: "Night", now: "Now",
    loading: "Loading…", setOrigin: "Set as origin", setDest: "Set as destination", askHere: "Ask about this point",
    nearby: "Nearby hospitals/police", reasons: "Reasons", whatToDo: "What to do", routes: "Routes",
    contacts: "Emergency numbers", sources: "Sources", limitations: "Limitations", risk: "Risk",
    confidence: "Confidence", updated: "Updated", suggestedTime: "Suggested departure",
    km: "km", min: "min", feedbackQ: "Was this helpful?", thanks: "Thanks for your feedback",
    degraded: "Some data is unavailable:", noAlerts: "No warning-level events in the last 24 h.",
    temp: "Temperature", rain: "Rain", errorMsg: "Something went wrong", steps: "Checking weather → hazards → routes → risk…",
    hazards48: "Hazards in 48 h", subscribe: "Alert me for this area", subscribed: "Area saved for alerts",
    myAlertsTitle: "My area alerts", noAreas: "No areas yet — click the map and press \"Alert me for this area\"",
    noNotifications: "No notifications yet", remove: "Remove", citations: "Guidance references", chart48: "48 h forecast (line = temperature, bars = rain)", places: "Nearby places",
    LOW: "Low", MEDIUM: "Medium", HIGH: "High",
    chips: { temperature: "🌡 Weather", precipitation: "🌧 Rain", radar: "📡 Radar", floods: "🌊 Flood", wind: "💨 Wind",
             storms: "🌀 Storm", fires: "🔥 Fire", earthquakes: "〰 Earthquake", pm25: "😷 PM2.5", volcanoes: "🌋 Volcano" },
    sevNames: ["Normal", "Advisory", "Watch", "Warning", "Emergency"],
    hazardNames: { RAIN: "Rain", WIND: "Wind", HEAT: "Heat", WEATHER: "Weather", AIR_QUALITY: "PM2.5", FLOOD: "River",
                   EARTHQUAKE: "Earthquake", STORM: "Storm", FIRE: "Wildfire", VOLCANO: "Volcano", FOG: "Fog", DROUGHT: "Drought" },
  },
};

let LANG = localStorageGet("lang") || "th";

function t(key) {
  return TEXT[LANG][key] ?? key;
}

function localStorageGet(key) {
  try { return localStorage.getItem(key); } catch (e) { return null; }
}

function localStorageSet(key, value) {
  try { localStorage.setItem(key, value); } catch (e) { /* ไม่เป็นไร */ }
}

function applyLanguage() {
  document.documentElement.lang = LANG;
  document.querySelectorAll("[data-i18n]").forEach(el => { el.textContent = t(el.dataset.i18n); });
  document.querySelectorAll("[data-i18n-placeholder]").forEach(el => { el.placeholder = t(el.dataset.i18nPlaceholder); });
}
