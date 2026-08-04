



# Create data/golden_set.json from the existing chunk store.
#
# Each chunk comes from a real Q&A pair, so the correct target chunk is already known.
# This provides automatic ground truth without writing every test item manually.
#
# Original questions are too easy because BM25 can match the same words directly.
# To create more realistic tests, each question is converted into four query types:
#
# verbatim  Original question for checking the system's upper limit.
# slang     Medical terms rewritten in everyday language.
# partial   Short keyword-style query.
# natural   Natural user-style question for realistic evaluation.
#
# The gap between verbatim and natural results shows how well the system handles
# real user queries.
#
# Set the number of items with config.GOLDEN_SET_SIZE.
# Run: python -m evaluation.build_golden_set



import json
import random
import re

import config

# ตรงข้ามกับ SLANG_MAP ใน query_transform: ศัพท์แพทย์ → ที่คนพูดกันจริง
TO_SLANG = {
    "อวัยวะเพศชาย": "น้องชาย",
    "อวัยวะเพศหญิง": "น้องสาว",
    "ถุงยางอนามัย": "ถุงยาง",
    "โรคติดต่อทางเพศสัมพันธ์": "โรคจากเซ็กส์",
    "มีเพศสัมพันธ์": "มีอะไรกัน",
    "เอชไอวี": "เอดส์",
    "ประจำเดือน": "เมนส์",
    "การตั้งครรภ์": "ท้อง",
}

PREFIXES = ["อยากรู้ว่า", "ขอถามหน่อย", "สงสัยว่า", ""]
SUFFIXES = ["ครับ", "คะ", "อ่ะ", ""]
SEED = 42        # ล็อกค่าสุ่มไว้ เพื่อให้ได้ชุดข้อสอบเดิมทุกครั้ง

STOPWORDS = {"คือ", "อะไร", "ที่", "และ", "หรือ", "ของ", "ใน", "มี", "บ้าง",
             "ได้", "ไหม", "อย่างไร", "ยังไง", "การ", "ความ", "เป็น", "ให้"}


def make_variants(question, rng):
    """สร้างคำถาม 4 แบบจากคำถามต้นฉบับ 1 ข้อ"""
    variants = {"verbatim": question}

    # slang: แทนศัพท์แพทย์ด้วยภาษาพูด (ถ้ามีคำให้แทน)
    slang = question
    for formal, casual in TO_SLANG.items():
        slang = slang.replace(formal, casual)
    if slang != question:
        variants["slang"] = slang

    # partial: ตัด stopword เหลือแต่คำเนื้อหา
    words = [w for w in re.split(r"[\s()/]+", re.sub(r"\(.*?\)", "", question))
             if w and w not in STOPWORDS and len(w) > 1]
    if len(words) >= 2:
        variants["partial"] = " ".join(words[:max(2, int(len(words) * 0.6))])

    # natural: ใส่คำนำ/คำลงท้ายแบบภาษาพูด
    core = re.sub(r"\s*(คืออะไร|มีอะไรบ้าง|อย่างไร|ยังไง)\s*$", "", question).strip()
    variants["natural"] = f"{rng.choice(PREFIXES)}{core} ยังไง{rng.choice(SUFFIXES)}".strip()

    return variants


def main():
    print("=== สร้าง Golden Set ===")
    with open(config.CHUNK_STORE_FILE, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    # chunk ทุกชิ้นที่มาจาก qa_id เดียวกัน ถือว่าถูกหมด
    # (คำตอบยาวถูกตัดเป็น 3 ชิ้น ค้นเจอชิ้นไหนก็นับว่าถูก)
    by_qa = {}
    for chunk in chunks:
        by_qa.setdefault(chunk["qa_id"], []).append(chunk["chunk_id"])

    # ใช้เฉพาะ part_idx == 0 เพราะเป็นชิ้นที่มีคำถามเต็ม
    primary = [c for c in chunks if c.get("part_idx", 0) == 0]

    # สุ่มแบบกระจายตามหมวด ไม่ให้หมวดใหญ่กินพื้นที่หมด
    rng = random.Random(SEED)
    by_category = {}
    for chunk in primary:
        by_category.setdefault(chunk["category"], []).append(chunk)

    selected = []
    per_category = max(1, config.GOLDEN_SET_SIZE // len(by_category))
    for pool in by_category.values():
        rng.shuffle(pool)
        selected.extend(pool[:per_category])
    selected = sorted(selected, key=lambda c: c["chunk_id"])[:config.GOLDEN_SET_SIZE]

    items = [
        {
            "id": f"g{c['qa_id']:04d}",
            "category": c["category"],
            "question": c["question"],
            "variants": make_variants(c["question"], rng),
            "relevant_chunk_ids": sorted(by_qa[c["qa_id"]]),
            "reference_answer": c["answer"],
        }
        for c in selected
    ]

    with open(config.GOLDEN_SET_FILE, "w", encoding="utf-8") as f:
        json.dump({"size": len(items), "items": items}, f, ensure_ascii=False, indent=2)

    print(f"สร้าง {len(items)} ข้อ จาก {len(chunks)} chunks")
    print("\nตัวอย่าง:")
    for name, text in items[0]["variants"].items():
        print(f"  {name:9s}: {text}")
    print(f"  ควรค้นเจอ: {items[0]['relevant_chunk_ids']}")
    print(f"\nบันทึกที่ {config.GOLDEN_SET_FILE}")


if __name__ == "__main__":
    main()
