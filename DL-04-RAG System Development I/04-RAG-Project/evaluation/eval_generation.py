


# Evaluate retrieval performance using data/golden_set.json.
#
# This script compares whether BM25 and reranking improve retrieval quality.
# It runs multiple retrieval methods on the same evaluation queries.
#
#     dense_only      Semantic retrieval only (baseline from Labs 1–7)
#     bm25_only       Keyword retrieval only
#     hybrid          BM25 + Dense retrieval with RRF
#     hybrid+rerank   Hybrid retrieval with cross-encoder reranking
#                     (only when USE_RERANK = True)
#
# How to interpret the results:
#   * Hybrid should perform best on partial queries and English abbreviations.
#   * Reranking should improve MRR and nDCG more than Hit@10 because it only
#     reorders retrieved results.
#   * Strong performance only on verbatim queries indicates exact word matching
#     rather than robust retrieval.


import json
import re

import config
from evaluation.eval_retrieval import load_golden_set
from src.hybrid_retriever import tokenize
from src.prompt_templates import format_context

# กี่ข้อ — การเรียก LLM ช้า จึงตั้งไว้น้อย
LIMIT = 20

# ใช้คำถามรูปแบบไหน (natural = ภาษาพูดจริง เป็นเคสที่ใช้ตัดสิน)
VARIANT = "natural"


def word_overlap(text_a, text_b):
    """
    สัดส่วนคำใน text_a ที่ปรากฏใน text_b ด้วย (0.0 - 1.0)

    ถ้าคำตอบถูก "คัดลอก / เรียบเรียง" มาจากเอกสาร ค่าจะสูง
    ถ้าแต่งขึ้นเอง ค่าจะต่ำ
    """
    words_a = set(tokenize(text_a))
    if not words_a:
        return 0.0

    words_b = set(tokenize(text_b))
    return len(words_a & words_b) / len(words_a)


def is_refusal(answer):
    """คำตอบนี้คือการบอกว่า 'ไม่รู้' ใช่ไหม"""
    phrases = ["ไม่พบข้อมูล", "ไม่มีข้อมูล", "ไม่สามารถตอบ"]
    return any(phrase in answer for phrase in phrases)


def evaluate_one_item(rag, item):
    """ทดสอบคำถาม 1 ข้อ คืน dict ของคะแนน"""
    query = item["variants"].get(VARIANT, item["question"])
    result = rag.ask(query)

    answer = result["answer"].replace(config.DISCLAIMER, "").strip()
    context = format_context(result["retrieved"])

    found_ids = {chunk["chunk_id"] for chunk in result["retrieved"]}
    correct_ids = set(item["relevant_chunk_ids"])

    return {
        "id": item["id"],
        "query": query,
        "answer": answer,
        "refused": is_refusal(answer),
        "context_hit": bool(found_ids & correct_ids),   # ค้นเจอ chunk ที่ถูกไหม
        "has_citation": bool(re.search(r"\[\d+\]", result["answer"])),
        "faithfulness": round(word_overlap(answer, context), 4),
        "correctness": round(word_overlap(answer, item["reference_answer"]), 4),
        "relevance": round(word_overlap(query, answer), 4),
        "seconds": result["timings"]["รวม"],
    }


def summarize(rows):
    """เฉลี่ยคะแนนของทุกข้อ"""
    def mean(key):
        return round(sum(row[key] for row in rows) / len(rows), 4)

    return {
        "จำนวนข้อ": len(rows),
        "อัตราการตอบว่าไม่รู้": mean("refused"),
        "อัตราค้นเจอ chunk ที่ถูก": mean("context_hit"),
        "มีการอ้างอิง [n]": mean("has_citation"),
        "faithfulness": mean("faithfulness"),
        "correctness": mean("correctness"),
        "relevance": mean("relevance"),
        "เวลาเฉลี่ย (วินาที)": mean("seconds"),
    }


def main():
    print("=== วัดคุณภาพคำตอบ ===")

    from src.rag_pipeline import RAGPipeline

    items = load_golden_set()["items"][:LIMIT]

    # ปิด memory เพราะแต่ละข้อต้องเป็นอิสระ ไม่ให้ข้อก่อนหน้ามีผลกับข้อถัดไป
    original_memory = config.USE_MEMORY
    config.USE_MEMORY = False

    rag = RAGPipeline()
    rag.show_settings()

    if not config.USE_LLM:
        print("\n! USE_LLM = False — คำตอบเป็นการตัดข้อความมา ไม่ใช่การสร้างจริง")
        print("  ตั้ง USE_LLM = True ใน config.py เพื่อให้ตัวเลขมีความหมาย")

    rows = []
    for number, item in enumerate(items, start=1):
        print(f"  [{number}/{len(items)}] {item['id']}", end="\r", flush=True)
        rows.append(evaluate_one_item(rag, item))

    config.USE_MEMORY = original_memory     # คืนค่าเดิม

    summary = summarize(rows)

    print("\n\n=== สรุป ===")
    for name, value in summary.items():
        print(f"  {name:26s} {value}")

    print("\n=== คำตอบที่ยึดตามเอกสารน้อยที่สุด (น่าสงสัยว่าแต่งเอง) ===")
    for row in sorted(rows, key=lambda r: r["faithfulness"])[:3]:
        print(f"  {row['id']} ({row['faithfulness']:.3f}) {row['query'][:50]}")
        print(f"      {row['answer'][:100]}...")

    with open(config.EVAL_GENERATION_FILE, "w", encoding="utf-8") as f:
        json.dump({"summary": summary, "results": rows}, f, ensure_ascii=False, indent=2)
    print(f"\nบันทึกรายงานที่ {config.EVAL_GENERATION_FILE}")


if __name__ == "__main__":
    main()
