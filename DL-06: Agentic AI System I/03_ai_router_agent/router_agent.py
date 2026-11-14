### router_agent.py — 03 AI Router / Agent
### Picks the route and response_type in this order:
### (a) safety/scope -> decline  (b) classifier (PyTorch)  (c) Thai keyword fallback
### (d) still low confidence -> clarify

import json
import logging
import re

import config
import local_ai
from pythainlp.tokenize import word_tokenize
from thai_text import tokenize, detect_language, count_tokens

log = logging.getLogger("router")

DECLINE_PATTERNS = ["รหัสผ่าน", "เกรดของเพื่อน", "เกรดของคนอื่น", "ข้อมูลส่วนตัวของ", "เบอร์โทรของ",
                    "แฮก", "โกงข้อสอบ", "ทุจริตสอบ", "password", "hack", "someone else's",
                    "other student's", "cheat", "ignore previous instructions", "ไม่ต้องสนคำสั่ง"]
AMBIGUOUS = ["ช่วยด้วย", "สอบถามหน่อย", "มีคำถาม", "ถามหน่อย", "help", "question", "สงสัย"]
GREETINGS = ["สวัสดี", "หวัดดี", "hello", "hi", "hey"]

### keywords per route (matched after PyThaiNLP tokenizing)
KEYWORDS = {
    "university_rag": ["ระเบียบ", "ประกาศ", "รายวิชา", "วิชา", "ลงทะเบียน", "ค่าเทอม", "หลักสูตร",
                       "หน่วยกิต", "ทุน", "ลาพัก", "เกียรตินิยม", "สหกิจ", "ค่าธรรมเนียม", "ผ่อนชำระ",
                       "regulation", "announcement", "course", "credit", "credits", "tuition",
                       "scholarship", "curriculum", "prerequisite", "prerequisites", "graduation"],
    "local_ai": ["ทำนาย", "พยากรณ์", "จัดประเภท", "ความเสี่ยง", "เสี่ยง", "predict", "classify", "risk"],
}
ROUTE_TO_TYPE = {"general_ai": "answer", "university_rag": "answer_with_citations",
                 "local_ai": "local_task"}
FOLLOWUP_WORDS = ["นี้", "นั้น", "ดังกล่าว", "ล่ะ", "it", "that", "this", "those", "them"]
CLARIFY_OPTIONS = {
    "th": ["การลงทะเบียนเรียน", "ค่าธรรมเนียมการศึกษา", "รายวิชาในหลักสูตรวิศวกรรมคอมพิวเตอร์",
           "เกณฑ์การสำเร็จการศึกษา"],
    "en": ["Course registration", "Tuition fees", "Computer Engineering courses",
           "Graduation requirements"],
}

_cache = {}
CACHE_MAX = 1000


def is_unsafe(text):
    low = text.lower()
    return any(p in low for p in DECLINE_PATTERNS)


def keyword_route(text):
    ### count keyword hits after tokenizing (Thai has no spaces between words)
    tokens = set(tokenize(text))
    best, best_hits = None, 0
    for route, words in KEYWORDS.items():
        hits = sum(1 for w in words if w in tokens)
        if hits > best_hits:
            best, best_hits = route, hits
    confidence = min(0.6 + 0.1 * best_hits, 0.9) if best else 0.0
    return best, confidence


def rewrite_query(query, history):
    ### turn a follow-up into a full question by adding the previous question
    last_user = [t["content"] for t in history if t["role"] == "user"]
    if not last_user:
        return query
    low = query.lower().strip()
    words = set(word_tokenize(low, keep_whitespace=False))
    if low.startswith(("แล้ว", "and ", "what about")) or words & set(FOLLOWUP_WORDS):
        return last_user[-1] + " " + query
    return query


def trim_history(history):
    ### keep history under MAX_CONTEXT_TOKENS (drop the oldest turns first)
    history = list(history)
    while history and sum(count_tokens(t["content"]) for t in history) > config.MAX_CONTEXT_TOKENS:
        history.pop(0)
    return history


def make_decision(route, response_type, confidence, language, query, reasoning, options=None):
    return {"route": route, "response_type": response_type, "confidence": round(confidence, 3),
            "language": language, "rewritten_query": query, "reasoning": reasoning,
            "clarify_options": options or []}


def decide(query, history, locale="th"):
    language = detect_language(query, locale)
    ### remove only spaces and punctuation (\W would also remove Thai vowel marks)
    plain = re.sub(r"[\s?!.,~]+", "", query.lower())

    ### (a) safety / scope
    if is_unsafe(query):
        return make_decision("none", "decline", 0.95, language, query, "unsafe_or_out_of_scope")
    if plain in AMBIGUOUS or len(plain) < 2:
        return make_decision("none", "clarify", 0.3, language, query, "ambiguous",
                             CLARIFY_OPTIONS[language])
    if plain in GREETINGS:
        return make_decision("general_ai", "answer", 0.95, language, query, "greeting")

    rewritten = rewrite_query(query, history)
    cache_key = (rewritten, language)
    if cache_key in _cache:
        return _cache[cache_key]

    ### (b) classifier: embedding + MLP (PyTorch)
    try:
        route, confidence, version = local_ai.predict_text("router", rewritten)
        reasoning = f"classifier {version}"
    except Exception as e:
        route, confidence, reasoning = None, 0.0, f"classifier_error: {e}"

    ### (c) Thai keyword fallback when confidence is low
    if confidence < config.ROUTE_CONFIDENCE_MIN:
        kw_route, kw_conf = keyword_route(rewritten)
        if kw_route and kw_conf > confidence:
            route, confidence, reasoning = kw_route, kw_conf, "keyword_fallback"

    ### (d) still not sure -> ask the user
    if route is None or confidence < config.CLARIFY_THRESHOLD:
        decision = make_decision("none", "clarify", confidence, language, rewritten,
                                 "low_confidence", CLARIFY_OPTIONS[language])
    else:
        decision = make_decision(route, ROUTE_TO_TYPE[route], confidence, language, rewritten,
                                 reasoning)
    ### cache only normal classifier results, with a size limit
    if not reasoning.startswith("classifier_error"):
        if len(_cache) >= CACHE_MAX:
            _cache.clear()
        _cache[cache_key] = decision
    log.info(json.dumps({"event": "route_decision", **decision}, ensure_ascii=False))
    return decision
