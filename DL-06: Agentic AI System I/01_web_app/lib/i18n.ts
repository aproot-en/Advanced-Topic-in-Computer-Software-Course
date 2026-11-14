// UI strings for Thai (default) and English.

import type { Engine, Locale, RetrievalMethod, SourceCategory } from "./types";

export type Topic = "registration" | "tuition" | "honors" | "course" | "leave" | "scholarship";

export interface SuggestionCard {
  topic: Topic;
  label: string;
  q: string;
}

export interface Dict {
  appName: string;
  brandSub: string;
  documents: (n: number) => string;
  kbUpdated: (date: string) => string;
  modeLabel: (mode: "mock" | "live") => string;
  newChat: string;
  recent: string;
  noHistory: string;
  loading: string;
  close: string;
  menu: string;
  settings: string;
  method: string;
  references: string;
  language: string;
  themeLight: string;
  themeDark: string;
  heroTitle: string;
  heroSubtitle: string;
  suggestionCards: SuggestionCard[];
  placeholder: string;
  send: string;
  footer: string;
  methods: Record<RetrievalMethod, string>;
  methodHints: Record<RetrievalMethod, string>;
  engines: Record<Engine, string>;
  categories: Record<SourceCategory, string>;
  confidence: (level: "high" | "medium" | "low") => string;
  dataAsOf: (date: string) => string;
  degraded: (services: string) => string;
  sourcesTitle: (n: number) => string;
  page: (p: number) => string;
  helpful: string;
  notHelpful: string;
  thanks: string;
  copy: string;
  copied: string;
  contactStaff: string;
  advisory: string;
  clarifyHint: string;
  error: string;
  retry: string;
  searching: string;
  micStart: string;
  micStop: string;
  micUnsupported: string;
}

const th: Dict = {
  appName: "UniRAG",
  brandSub: "ผู้ช่วยมหาวิทยาลัยอัจฉริยะ",
  documents: (n) => `${n.toLocaleString("th-TH")} เอกสาร`,
  kbUpdated: (d) => `อัปเดต ${d}`,
  modeLabel: (m) => (m === "mock" ? "Mock API" : "Live API"),
  newChat: "แชตใหม่",
  recent: "ล่าสุด",
  noHistory: "ยังไม่มีประวัติการสนทนา",
  loading: "กำลังโหลด...",
  close: "ปิด",
  menu: "เมนู",
  settings: "ตั้งค่าการค้นหา",
  method: "วิธีค้นหา",
  references: "จำนวนเอกสารอ้างอิง",
  language: "ภาษา",
  themeLight: "โหมดสว่าง",
  themeDark: "โหมดมืด",
  heroTitle: "สวัสดี มีอะไรให้ช่วยวันนี้?",
  heroSubtitle: "ถามเรื่องระเบียบ ประกาศ ค่าเทอม หรือรายวิชา ทุกคำตอบอ้างอิงจากเอกสารของมหาวิทยาลัย",
  suggestionCards: [
    { topic: "registration", label: "ลงทะเบียน", q: "ลงทะเบียนเรียนได้สูงสุดกี่หน่วยกิต?" },
    { topic: "tuition", label: "ค่าเทอม", q: "ค่าเทอมภาคเรียนที่ 2/2569 ต้องจ่ายภายในวันไหน?" },
    { topic: "honors", label: "เกียรตินิยม", q: "เงื่อนไขการได้เกียรตินิยมอันดับหนึ่งคืออะไร?" },
    { topic: "course", label: "รายวิชา", q: "วิชาการเรียนรู้ของเครื่องมีวิชาบังคับก่อนอะไร?" },
    { topic: "leave", label: "ลาพักการศึกษา", q: "ขอลาพักการศึกษาได้กี่ภาคเรียน?" },
    { topic: "scholarship", label: "ทุนการศึกษา", q: "ทุนการศึกษาเปิดรับสมัครเมื่อไหร่?" },
  ],
  placeholder: "ถามอะไรก็ได้เกี่ยวกับการเรียน...",
  send: "ส่ง",
  footer: "หลักสูตร CPE มทร.ธัญบุรี 2568 + ระเบียบตัวอย่าง · โปรดตรวจสอบกับประกาศทางการก่อนดำเนินการ",
  methods: {
    hybrid_rrf: "Hybrid",
    bm25: "BM25",
    vector: "Vector",
  },
  methodHints: {
    hybrid_rrf: "BM25 + Vector รวมผลด้วย RRF",
    bm25: "ค้นด้วยคำสำคัญ",
    vector: "ค้นด้วยความหมาย",
  },
  engines: {
    general_ai: "General AI",
    university_rag: "University RAG",
    local_ai: "Local AI Model",
    none: "ผู้ช่วย",
  },
  categories: {
    regulation: "ระเบียบ",
    announcement: "ประกาศ",
    course: "รายวิชา",
    handbook: "คู่มือ",
  },
  confidence: (l) => `ความมั่นใจ${{ high: "สูง", medium: "ปานกลาง", low: "ต่ำ" }[l]}`,
  dataAsOf: (d) => `ข้อมูล ณ ${d}`,
  degraded: (s) => `บางบริการไม่พร้อมใช้งาน (${s}) คำตอบนี้อาจไม่ครบถ้วน`,
  sourcesTitle: (n) => `แหล่งอ้างอิง · ${n}`,
  page: (p) => `หน้า ${p}`,
  helpful: "มีประโยชน์",
  notHelpful: "ไม่มีประโยชน์",
  thanks: "ขอบคุณสำหรับความคิดเห็น",
  copy: "คัดลอก",
  copied: "คัดลอกแล้ว",
  contactStaff: "ติดต่อเจ้าหน้าที่",
  advisory: "ผลนี้เป็นคำแนะนำเบื้องต้น ไม่ใช่คำตัดสิน โปรดปรึกษาอาจารย์ที่ปรึกษาก่อนตัดสินใจ",
  clarifyHint: "เลือกหัวข้อ หรือพิมพ์รายละเอียดเพิ่มเติม",
  error: "เชื่อมต่อระบบไม่สำเร็จ กรุณาลองใหม่อีกครั้ง",
  retry: "ลองใหม่",
  searching: "กำลังค้นหาเอกสาร",
  micStart: "พูดคำถาม",
  micStop: "หยุดฟัง",
  micUnsupported: "เบราว์เซอร์นี้ไม่รองรับการพูด",
};

const en: Dict = {
  appName: "UniRAG",
  brandSub: "Smart University Assistant",
  documents: (n) => `${n.toLocaleString("en-US")} documents`,
  kbUpdated: (d) => `Updated ${d}`,
  modeLabel: (m) => (m === "mock" ? "Mock API" : "Live API"),
  newChat: "New chat",
  recent: "Recent",
  noHistory: "No conversations yet",
  loading: "Loading...",
  close: "Close",
  menu: "Menu",
  settings: "Search settings",
  method: "Retrieval method",
  references: "Number of references",
  language: "Language",
  themeLight: "Light mode",
  themeDark: "Dark mode",
  heroTitle: "Hi, how can I help today?",
  heroSubtitle: "Ask about regulations, announcements, tuition or courses. Every answer cites university documents.",
  suggestionCards: [
    { topic: "registration", label: "Registration", q: "What is the maximum number of credits I can register for?" },
    { topic: "tuition", label: "Tuition", q: "When is the tuition deadline for semester 2/2026?" },
    { topic: "honors", label: "Honors", q: "What GPA do I need for first-class honors?" },
    { topic: "course", label: "Courses", q: "What are the prerequisites for Machine Learning?" },
    { topic: "leave", label: "Leave of absence", q: "How many semesters of leave can I take?" },
    { topic: "scholarship", label: "Scholarships", q: "When do scholarship applications open?" },
  ],
  placeholder: "Ask anything about your studies...",
  send: "Send",
  footer: "CPE RMUTT 2568 curriculum + sample regulations · Check official announcements before acting",
  methods: {
    hybrid_rrf: "Hybrid",
    bm25: "BM25",
    vector: "Vector",
  },
  methodHints: {
    hybrid_rrf: "BM25 + Vector fused with RRF",
    bm25: "Keyword search",
    vector: "Semantic search",
  },
  engines: {
    general_ai: "General AI",
    university_rag: "University RAG",
    local_ai: "Local AI Model",
    none: "Assistant",
  },
  categories: {
    regulation: "Regulation",
    announcement: "Announcement",
    course: "Course",
    handbook: "Handbook",
  },
  confidence: (l) => `${{ high: "High", medium: "Medium", low: "Low" }[l]} confidence`,
  dataAsOf: (d) => `Data as of ${d}`,
  degraded: (s) => `Some services are unavailable (${s}); this answer may be limited.`,
  sourcesTitle: (n) => `Sources · ${n}`,
  page: (p) => `p. ${p}`,
  helpful: "Helpful",
  notHelpful: "Not helpful",
  thanks: "Thanks for your feedback",
  copy: "Copy",
  copied: "Copied",
  contactStaff: "Contact staff",
  advisory: "This result is advisory, not a decision. Please talk to your advisor before acting on it.",
  clarifyHint: "Pick a topic, or type more details",
  error: "Could not reach the server. Please try again.",
  retry: "Retry",
  searching: "Searching documents",
  micStart: "Speak your question",
  micStop: "Stop listening",
  micUnsupported: "Speech input is not supported in this browser",
};

export const DICTS: Record<Locale, Dict> = { th, en };

export function confidenceLevel(c: number): "high" | "medium" | "low" {
  return c >= 0.8 ? "high" : c >= 0.5 ? "medium" : "low";
}

export function formatTime(iso: string, locale: Locale) {
  return new Intl.DateTimeFormat(locale === "th" ? "th-TH" : "en-US", {
    hour: "2-digit",
    minute: "2-digit",
    timeZone: "Asia/Bangkok",
  }).format(new Date(iso));
}

export function formatDate(isoDate: string, locale: Locale) {
  return new Intl.DateTimeFormat(locale === "th" ? "th-TH" : "en-GB", {
    day: "numeric",
    month: "short",
    year: "numeric",
    timeZone: "Asia/Bangkok",
  }).format(new Date(`${isoDate}T00:00:00+07:00`));
}
