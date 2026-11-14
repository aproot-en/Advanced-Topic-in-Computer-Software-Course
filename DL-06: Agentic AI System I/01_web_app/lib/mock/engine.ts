// Mock of stages 02-07 so the Web App can be developed without the Python backend.
// It follows the planned behaviour (decision order, hybrid RRF retrieval, citations,
// response_type) with simple heuristics; it is not a real model.

import type {
  ChatRequest,
  ChatResponse,
  Engine,
  Locale,
  ResponseType,
  RetrievalMethod,
  Source,
} from "../types";
import { KB, type KbDoc } from "./kb";
import { appendTurns } from "./store";

const THAI_RE = /[฀-๿]/;
const RRF_K = 60;
const VECTOR_MIN = 0.35;
const RAG_VECTOR_MIN = 0.5;

const DECLINE_PATTERNS = [
  "รหัสผ่าน", "เกรดของเพื่อน", "เกรดของคนอื่น", "ข้อมูลส่วนตัวของ", "เบอร์โทรของ", "แฮก",
  "โกงข้อสอบ", "password", "hack", "someone else's", "other student's", "cheat",
];
const LOCAL_PATTERNS = ["ทำนาย", "พยากรณ์", "ความเสี่ยง", "จัดประเภท", "predict", "risk", "classify"];
const GREETINGS = ["สวัสดี", "หวัดดี", "hello", "hi", "hey"];
const AMBIGUOUS = ["ช่วยด้วย", "สอบถามหน่อย", "มีคำถาม", "ถามหน่อย", "help", "question"];

export const isThai = (s: string) => THAI_RE.test(s);

function normalize(s: string) {
  return s.toLowerCase().replace(/[\s\p{P}\p{S}]+/gu, "");
}

const EN_STOPWORDS = new Set([
  "the", "and", "for", "what", "when", "how", "can", "are", "with", "does", "many", "much",
  "need", "you", "your", "this", "that", "from", "about", "there", "which", "who", "why",
]);

function bigrams(s: string): Set<string> {
  const t = normalize(s);
  const out = new Set<string>();
  for (let i = 0; i < t.length - 1; i++) out.add(t.slice(i, i + 2));
  return out;
}

function words(s: string): Set<string> {
  const out = new Set<string>();
  for (const w of s.toLowerCase().match(/[a-z0-9]+/g) ?? []) {
    if (w.length >= 3 && !EN_STOPWORDS.has(w)) out.add(`w:${w.replace(/s$/, "")}`);
  }
  return out;
}

// Query features: character bigrams for Thai (no spaces between words), words for English.
function features(s: string): Set<string> {
  return isThai(s) ? bigrams(s) : words(s);
}

// Bigram/word "embedding" with IDF weights: a stand-in for semantic search that works on
// Thai text without a tokenizer.
const ACTIVE = KB.filter((d) => d.status === "active");
const DOC_GRAMS = new Map<string, Set<string>>(
  KB.map((d) => {
    const text = [d.title_th, d.title_en, d.keywords.join(" "), ...d.content_th, ...d.content_en].join(" ");
    return [d.id, new Set([...Array.from(bigrams(text)), ...Array.from(words(text))])];
  }),
);
const DF = new Map<string, number>();
for (const d of ACTIVE) DOC_GRAMS.get(d.id)!.forEach((g) => DF.set(g, (DF.get(g) ?? 0) + 1));

function idf(g: string) {
  const df = DF.get(g) ?? 0;
  return Math.log(1 + ACTIVE.length / (df || 1));
}

function similarity(q: Set<string>, d: Set<string>) {
  let hit = 0;
  let total = 0;
  q.forEach((g) => {
    const w = idf(g);
    total += w;
    if (d.has(g)) hit += w;
  });
  return total ? hit / total : 0;
}

function keywordScore(query: string, doc: KbDoc) {
  const q = query.toLowerCase();
  return doc.keywords.filter((k) => q.includes(k.toLowerCase())).length;
}

interface Ranked {
  doc: KbDoc;
  vector: number;
  keyword: number;
}

function retrieve(query: string, method: RetrievalMethod, topK: number): Ranked[] {
  const qg = features(query);
  // Only active documents are searchable: cancelled/superseded rules are never cited.
  const scored: Ranked[] = ACTIVE.map((doc) => ({
    doc,
    vector: similarity(qg, DOC_GRAMS.get(doc.id)!),
    keyword: keywordScore(query, doc),
  }));
  const byKeyword = scored.filter((r) => r.keyword > 0).sort((a, b) => b.keyword - a.keyword);
  const byVector = scored.filter((r) => r.vector >= VECTOR_MIN).sort((a, b) => b.vector - a.vector);

  if (method === "bm25") return byKeyword.slice(0, topK);
  if (method === "vector") return byVector.slice(0, topK);

  // Reciprocal Rank Fusion: score = sum(1 / (k + rank))
  const fused = new Map<string, { r: Ranked; score: number }>();
  for (const list of [byKeyword, byVector]) {
    list.forEach((r, i) => {
      const cur = fused.get(r.doc.id) ?? { r, score: 0 };
      cur.score += 1 / (RRF_K + i + 1);
      fused.set(r.doc.id, cur);
    });
  }
  return Array.from(fused.values())
    .sort((a, b) => b.score - a.score)
    .map((x) => x.r)
    .slice(0, topK);
}

function pickSentences(query: string, sentences: string[], n: number) {
  const qg = features(query);
  return sentences
    .map((s) => ({ s, score: similarity(qg, isThai(query) ? bigrams(s) : words(s)) }))
    .sort((a, b) => b.score - a.score)
    .slice(0, n)
    .filter((x) => x.score > 0)
    .map((x) => x.s);
}

function includesAny(text: string, patterns: string[]) {
  const t = text.toLowerCase();
  return patterns.some((p) => t.includes(p.toLowerCase()));
}

interface Draft {
  response_type: ResponseType;
  engine_used: Engine;
  answer: string;
  confidence: number;
  sources?: Source[];
  clarify_options?: string[];
  degraded_services?: string[];
}

function ragAnswer(query: string, ranked: Ranked[], lang: Locale, degraded: string[]): Draft {
  const sources: Source[] = [];
  const bullets: string[] = [];
  const seen = new Set<string>();

  const topVector = ranked[0].vector;
  ranked.forEach((r, i) => {
    // Secondary documents need keyword evidence or a vector score close to the best one.
    const relevant = i === 0 || r.keyword > 0 || r.vector >= Math.max(RAG_VECTOR_MIN, topVector * 0.9);
    if (!relevant || bullets.length >= 4) return;
    const picked = pickSentences(query, lang === "th" ? r.doc.content_th : r.doc.content_en, i === 0 ? 3 : 1);
    const fresh = picked.filter((s) => !seen.has(s));
    if (!fresh.length) return;
    const ref = sources.length + 1;
    sources.push({
      ref,
      title: lang === "th" ? r.doc.title_th : r.doc.title_en,
      url: r.doc.url,
      page: r.doc.page,
      published_at: r.doc.published_at,
      category: r.doc.category,
    });
    for (const s of fresh) {
      if (bullets.length >= 4) break;
      seen.add(s);
      bullets.push(`- ${s} [${ref}]`);
    }
  });

  const top = ranked[0];
  if (!sources.length) {
    sources.push({
      ref: 1,
      title: lang === "th" ? top.doc.title_th : top.doc.title_en,
      url: top.doc.url,
      page: top.doc.page,
      published_at: top.doc.published_at,
      category: top.doc.category,
    });
    bullets.push(`- ${(lang === "th" ? top.doc.content_th : top.doc.content_en)[0]} [1]`);
  }
  const intro =
    lang === "th"
      ? `จากเอกสาร **${sources[0].title}** และเอกสารที่เกี่ยวข้อง สรุปได้ดังนี้ [1]`
      : `Based on **${sources[0].title}** and related documents: [1]`;
  const outro =
    lang === "th"
      ? "กดหมายเลขอ้างอิงเพื่อดูเอกสารต้นฉบับ"
      : "Click a reference number to see the source document.";
  const confidence = Math.min(0.95, 0.35 + top.vector * 0.4 + (top.keyword > 0 ? 0.25 : 0));

  return {
    response_type: "answer_with_citations",
    engine_used: "university_rag",
    answer: [intro, "", ...bullets, "", outro].join("\n"),
    confidence,
    sources,
    degraded_services: degraded,
  };
}

function localTaskAnswer(query: string, lang: Locale): Draft {
  const classify = includesAny(query, ["จัดประเภท", "classify"]);
  if (classify) {
    return {
      response_type: "local_task",
      engine_used: "local_ai",
      confidence: 0.81,
      answer:
        lang === "th"
          ? "**ประเภทคำร้องที่คาดการณ์:** งานทะเบียนและประมวลผล (ความมั่นใจ 0.81)\n\nระบบจะส่งคำร้องไปยังกองทะเบียนโดยอัตโนมัติเมื่อเชื่อมต่อ backend จริง"
          : "**Predicted request type:** Registration and records (confidence 0.81)\n\nWith the real backend, the request would be forwarded to the Registrar automatically.",
    };
  }
  return {
    response_type: "local_task",
    engine_used: "local_ai",
    confidence: 0.74,
    answer:
      lang === "th"
        ? "**ผลการประเมินเบื้องต้น:** ความเสี่ยงต่ำ (คะแนน 0.18)\n\nปัจจัยหลัก:\n- เกรดเฉลี่ยสะสมอยู่ในเกณฑ์ปกติ\n- ลงทะเบียนครบตามแผนการเรียน\n- ไม่มีประวัติค้างชำระค่าธรรมเนียม"
        : "**Preliminary assessment:** Low risk (score 0.18)\n\nMain factors:\n- Cumulative GPA is in the normal range\n- Registered according to the study plan\n- No outstanding fees",
  };
}

function declineAnswer(lang: Locale): Draft {
  return {
    response_type: "decline",
    engine_used: "none",
    confidence: 0.9,
    answer:
      lang === "th"
        ? "ขออภัย ผู้ช่วยไม่สามารถช่วยเรื่องนี้ได้ เนื่องจากเกี่ยวข้องกับข้อมูลส่วนบุคคลของผู้อื่นหรืออยู่นอกขอบเขตการให้บริการ หากต้องการความช่วยเหลือ โปรดติดต่อเจ้าหน้าที่"
        : "Sorry, I can't help with this because it involves other people's personal data or is outside the scope of this service. Please contact university staff for help.",
  };
}

function clarifyAnswer(lang: Locale): Draft {
  return {
    response_type: "clarify",
    engine_used: "none",
    confidence: 0.4,
    answer:
      lang === "th"
        ? "ช่วยระบุเพิ่มเติมได้ไหมว่าต้องการสอบถามเรื่องใด"
        : "Could you tell me a bit more about what you'd like to know?",
    clarify_options:
      lang === "th"
        ? ["การลงทะเบียนเรียน", "ค่าธรรมเนียมการศึกษา", "ทุนการศึกษา", "เงื่อนไขการสำเร็จการศึกษา"]
        : ["Course registration", "Tuition fees", "Scholarships", "Graduation requirements"],
  };
}

function generalAnswer(query: string, lang: Locale): Draft {
  if (includesAny(normalize(query), GREETINGS) && normalize(query).length <= 12) {
    return {
      response_type: "answer",
      engine_used: "general_ai",
      confidence: 0.9,
      answer:
        lang === "th"
          ? "สวัสดีครับ มีอะไรให้ช่วยเกี่ยวกับการเรียนในมหาวิทยาลัยไหมครับ เช่น การลงทะเบียน ค่าเทอม ทุนการศึกษา หรือรายวิชา"
          : "Hello! How can I help with your studies? For example: registration, tuition fees, scholarships or courses.",
    };
  }
  return {
    response_type: "answer",
    engine_used: "general_ai",
    confidence: 0.6,
    answer:
      lang === "th"
        ? "คำถามนี้เป็นคำถามทั่วไป ระบบจะส่งไปที่ **General AI** (Gemini / OpenAI)\n\nขณะนี้เว็บแอปทำงานใน **โหมดจำลอง (Mock API)** จึงยังไม่มีคำตอบจากโมเดลจริง เมื่อเชื่อมต่อ 02_api_backend แล้ว คำตอบจะถูกสร้างที่ 06_llm_generation\n\nลองถามเรื่องการลงทะเบียน ค่าเทอม ทุนการศึกษา หรือรายวิชา เพื่อดูคำตอบพร้อมเอกสารอ้างอิง"
        : "This is a general question, so it would be routed to **General AI** (Gemini / OpenAI).\n\nThe web app is running in **mock mode**, so there is no real model answer yet. Once 02_api_backend is connected, the answer is generated by 06_llm_generation.\n\nTry asking about registration, tuition, scholarships or courses to see an answer with citations.",
  };
}

// Decision order from 03_ai_router_agent: safety → local task → ambiguous → RAG → clarify → general.
function route(req: ChatRequest): Draft {
  let query = req.message;
  const lang: Locale = isThai(query) ? "th" : /[a-z]/i.test(query) ? "en" : req.locale;

  if (includesAny(query, DECLINE_PATTERNS)) return declineAnswer(lang);
  if (includesAny(query, LOCAL_PATTERNS)) return localTaskAnswer(query, lang);
  if (AMBIGUOUS.some((a) => normalize(query) === normalize(a))) return clarifyAnswer(lang);

  // "#degraded" simulates the vector DB being down: hybrid falls back to BM25 only.
  const degraded: string[] = [];
  let method = req.method;
  if (query.includes("#degraded")) {
    query = query.replace("#degraded", "").trim();
    degraded.push("vector_db");
    if (method !== "bm25") method = "bm25";
  }

  const ranked = retrieve(query, method, req.top_k);
  const best = ranked[0];
  if (best && (best.keyword > 0 || best.vector >= RAG_VECTOR_MIN)) {
    return ragAnswer(query, ranked, lang, degraded);
  }

  const n = normalize(query);
  const greeting = includesAny(n, GREETINGS) && n.length <= 12;
  if (!greeting && n.length < 4) {
    return clarifyAnswer(lang);
  }
  const draft = generalAnswer(query, lang);
  draft.degraded_services = degraded;
  return draft;
}

function bangkokIso(date = new Date()) {
  return new Date(date.getTime() + 7 * 3600_000).toISOString().replace("Z", "+07:00");
}

function traceId() {
  return crypto.randomUUID().replace(/-/g, "");
}

export function handleChat(req: ChatRequest): ChatResponse {
  const started = Date.now();
  const draft = route(req);
  const sources = draft.sources ?? [];
  const sessionId = req.session_id ?? crypto.randomUUID();

  const response: ChatResponse = {
    message_id: crypto.randomUUID(),
    session_id: sessionId,
    response_type: draft.response_type,
    answer: draft.answer,
    clarify_options: draft.clarify_options ?? [],
    sources,
    engine_used: draft.engine_used,
    confidence: Math.round(draft.confidence * 100) / 100,
    data_freshness: sources.length ? sources.map((s) => s.published_at).sort().at(-1)! : null,
    degraded_services: draft.degraded_services ?? [],
    latency_ms: Date.now() - started,
    trace_id: traceId(),
    timestamp: bangkokIso(),
  };

  appendTurns(sessionId, req.message, response);
  return response;
}
