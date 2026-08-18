# query_transform.py
# Improve user queries before retrieval.
#
# Problem
# Retrieval quality depends on the user's query. Real users often write
# short or ambiguous questions, or use slang.
#
#     "I have a sore on my private part"   ← slang
#     Knowledge base: "penis"
#
#     "So what's the difference?"          ← unclear without context
#
# Since the knowledge base uses medical terms, query transformation helps
# bridge the gap between user language and stored documents.
#
# Two levels are available:
#
# Level 1 — normalize_query()
#     No AI required. Expands slang with formal terms using a lookup table.
#     Fast, free, and always enabled.
#
# Level 2 — transform()
#     Uses an LLM when config.USE_QUERY_TRANSFORM is enabled.
#
#     rewrite
#         Rewrite the query into a clearer question.
#
#     multi_query
#         Generate multiple equivalent queries and search all of them.
#
#     hyde
#         Generate a hypothetical answer and use it as the search query.
#         This works because answer-like text is often closer to the
#         correct document than the original question.

import re

import config
from src.prompt_templates import HYDE_PROMPT, MULTI_QUERY_PROMPT, REWRITE_PROMPT

# ตารางแทนคำแสลง — เพิ่มคำได้ตามต้องการ ไม่ต้องแก้โค้ดส่วนอื่น
SLANG_MAP = {
    "น้องชาย": "อวัยวะเพศชาย",
    "น้องสาว": "อวัยวะเพศหญิง",
    "จู๋": "อวัยวะเพศชาย",
    "จิ๋ม": "อวัยวะเพศหญิง",
    "ถุงยาง": "ถุงยางอนามัย",
    "เอดส์": "เอชไอวี",
    "มีอะไรกัน": "มีเพศสัมพันธ์",
    "โรคจากเซ็กส์": "โรคติดต่อทางเพศสัมพันธ์",
    "เมนส์": "ประจำเดือน",
    "เพร็พ": "PrEP ยาป้องกันเอชไอวีก่อนสัมผัสเชื้อ",
    "ผัว": "สามี คู่สมรส",
    "เมีย": "ภรรยา คู่สมรส",
    "ควย": "อวัยวะเพศชาย",
    "น้ำเงี่ยน": "น้ำอสุจิ",
    "เงี่ยน": "ความต้องการทางเพศ",
    "ฟิน": "ความพึงพอใจทางเพศ จุดสุดยอด",
    "เย็ดตูด": "เพศสัมพันธ์ทางทวารหนัก",
    "เย็ด": "เพศสัมพันธ์",
    "กะเทย": "คนข้ามเพศ",
    "แข็งค้าง": "อวัยวะเพศแข็งตัวค้าง priapism",
    "ไม่ขึ้น": "อวัยวะเพศไม่แข็งตัว",
    "เสร็จ": "ถึงจุดสุดยอด",
    "น้ำแตก": "หลั่งน้ำอสุจิ",
    "เชื้ออ่อน": "คุณภาพอสุจิ",
}

# คำลงท้ายที่ไม่ช่วยในการค้นหา
ENDING_WORDS = re.compile(r"\s*(ครับ|ค่ะ|คะ|จ้า|น้า|หน่อย)\s*$")


def normalize_query(query):
    """
    ปรับคำถามแบบไม่ใช้ AI — เร็วและฟรี

        "เป็นแผลที่น้องชายครับ"  →  "เป็นแผลที่น้องชาย อวัยวะเพศชาย"
    """
    text = re.sub(r"\s+", " ", query).strip()       # ตัดช่องว่างซ้ำซ้อน

    text = ENDING_WORDS.sub("", text)

    # เก็บคำเดิมไว้เพื่อให้ BM25 ยังจับคำตรงได้ แล้วเติมศัพท์ทางการเพื่อช่วย
    # dense retrieval และเอกสารที่ใช้คนละสำนวนกับผู้ใช้
    expansions = []
    for slang, formal in SLANG_MAP.items():
        if slang in text and formal not in text:
            expansions.append(formal)

    if expansions:
        text = f"{text} {' '.join(dict.fromkeys(expansions))}"
    return text.strip() or query.strip()            # ถ้าตัดจนหมด ใช้ของเดิม


def clean_line(line):
    """ตัดเลขข้อ เครื่องหมายคำพูด และคำนำหน้า ที่ LLM ชอบใส่มาให้"""
    text = line.strip()
    text = re.sub(r"^\s*(\d+[\.\)]|[-*•])\s*", "", text)    # "1. " หรือ "- "
    text = re.sub(r"^(คำถาม|คำค้นหา|Query)\s*[:：]\s*", "", text)
    return text.strip().strip('"').strip("'")


class QueryTransformer:
    def __init__(self, llm):
        self.llm = llm

    def ask_llm(self, prompt):
        return self.llm.chat([{"role": "user", "content": prompt}])

    def rewrite(self, query, history):
        """ให้ LLM เขียนคำถามใหม่ให้ชัดเจนและสมบูรณ์ในตัวเอง"""
        history_block = f"บทสนทนาก่อนหน้า:\n{history}\n\n" if history else ""
        prompt = REWRITE_PROMPT.format(history=history_block, question=query)
        return [clean_line(self.ask_llm(prompt))]

    def multi_query(self, query):
        """ให้ LLM แต่งคำถามที่ความหมายเดียวกันหลายแบบ"""
        prompt = MULTI_QUERY_PROMPT.format(n=config.MULTI_QUERY_COUNT, question=query)
        answer = self.ask_llm(prompt)

        queries = [normalize_query(query)]           # เก็บคำถามเดิมไว้เป็นตัวแรก
        for line in answer.splitlines():
            new_query = clean_line(line)
            if new_query and new_query not in queries:
                queries.append(new_query)

        return queries[: config.MULTI_QUERY_COUNT + 1]

    def hyde(self, query):
        """ให้ LLM แต่งคำตอบสมมติ แล้วใช้คำตอบนั้นเป็นคำค้นด้วย"""
        fake_answer = self.ask_llm(HYDE_PROMPT.format(question=query)).strip()

        # เก็บคำถามเดิมไว้ด้วย เผื่อคำตอบสมมติหลุดประเด็น
        return [normalize_query(query), fake_answer]

    def transform(self, query, history=""):
        """
        คืน list ของคำถามที่จะเอาไปค้น — อย่างน้อย 1 ข้อเสมอ

        ถ้า LLM ใช้ไม่ได้ จะคืนคำถามเดิม การค้นหาจึงไม่พังเพราะขั้นนี้
        """
        if not config.USE_QUERY_TRANSFORM:
            return [normalize_query(query)]

        try:
            if config.QUERY_TRANSFORM_MODE == "rewrite":
                return self.rewrite(query, history)
            if config.QUERY_TRANSFORM_MODE == "hyde":
                return self.hyde(query)
            return self.multi_query(query)

        except Exception as error:
            print(f"[query_transform] ล้มเหลว ({error}) — ใช้คำถามเดิม")
            return [normalize_query(query)]


