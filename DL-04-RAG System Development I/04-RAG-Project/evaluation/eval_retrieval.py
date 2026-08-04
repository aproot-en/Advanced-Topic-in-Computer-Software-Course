

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
#
# Run: python -m evaluation.eval_retrieval

import json
import os
import time

import config
from evaluation.metrics import average, evaluate_one, print_table

# จำนวนข้อที่จะทดสอบ (None = ทั้งหมด) — ลดลงถ้าอยากให้เร็ว
LIMIT = None

# รูปแบบคำถามที่จะทดสอบ
VARIANTS = ["verbatim", "slang", "partial", "natural"]


def load_golden_set():
    if not os.path.exists(config.GOLDEN_SET_FILE):
        print(f"ไม่พบ {config.GOLDEN_SET_FILE}")
        print("สร้างก่อนด้วย:  python -m evaluation.build_golden_set")
        raise SystemExit(1)

    with open(config.GOLDEN_SET_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def run_one_setting(retriever, items, top_k, use_bm25, use_dense):
    """
    ทดสอบการค้นหาแบบหนึ่ง กับคำถามทุกข้อทุก variant

    คืน dict {variant: คะแนนเฉลี่ย} และรายการข้อที่ค้นไม่เจอ
    """
    config.USE_HYBRID = use_bm25        # สลับสวิตช์ตรง ๆ
    retriever.bm25 = retriever.bm25 if use_bm25 else None

    scores_by_variant = {variant: [] for variant in VARIANTS}
    misses = []

    for item in items:
        for variant in VARIANTS:
            query = item["variants"].get(variant)
            if not query:
                continue

            if not use_dense:
                # bm25_only — เรียก BM25 ตรง ๆ ไม่ผ่าน RRF
                hits = retriever.bm25_search(query, top_k)
                found = [retriever.chunks[position]["chunk_id"] for position, _ in hits]
            else:
                chunks = retriever.retrieve(query, top_k=top_k)
                found = [chunk["chunk_id"] for chunk in chunks]

            scores = evaluate_one(found, item["relevant_chunk_ids"], config.EVAL_K_VALUES)
            scores_by_variant[variant].append(scores)

            if variant == "natural" and scores[f"hit@{top_k}"] == 0:
                misses.append((item["id"], query, item["relevant_chunk_ids"], found[:5]))

    return scores_by_variant, misses


def main():
    print("=== วัดคุณภาพการค้นหา ===")

    golden = load_golden_set()
    items = golden["items"][:LIMIT] if LIMIT else golden["items"]
    top_k = max(config.EVAL_K_VALUES)
    print(f"จำนวนข้อ: {len(items)} | รูปแบบคำถาม: {', '.join(VARIANTS)}\n")

    from src.hybrid_retriever import HybridRetriever, load_bm25
    from src.rerankers import get_reranker

    # จำค่าเดิมไว้ แล้วบังคับเปิด BM25 เพื่อให้โหลด index มาเตรียมไว้
    original_hybrid = config.USE_HYBRID
    config.USE_HYBRID = True

    # สร้างตัวค้นครั้งเดียว เพราะการโหลดโมเดลคือส่วนที่ช้าที่สุด
    retriever = HybridRetriever()
    bm25_index = retriever.bm25

    # (ชื่อ, ใช้ BM25?, ใช้ dense?, ใช้ rerank?)
    settings = [
        ("dense_only", False, True, False),
        ("bm25_only", True, False, False),
        ("hybrid", True, True, False),
    ]
    if config.USE_RERANK:
        settings.append(("hybrid+rerank", True, True, True))

    reranker = get_reranker()
    results = {}
    all_misses = []

    for name, use_bm25, use_dense, use_rerank in settings:
        start_time = time.time()

        retriever.bm25 = bm25_index if use_bm25 else None
        retriever.reranker = reranker if use_rerank else None

        scores_by_variant, misses = run_one_setting(
            retriever, items, top_k, use_bm25, use_dense
        )

        all_scores = [s for scores in scores_by_variant.values() for s in scores]
        results[name] = {
            "overall": average(all_scores),
            "by_variant": {v: average(s) for v, s in scores_by_variant.items() if s},
            "ms_per_query": round((time.time() - start_time) * 1000 / len(all_scores), 1),
        }
        all_misses = misses

        print(f"  {name:16s} เสร็จใน {time.time() - start_time:.1f}s")

    config.USE_HYBRID = original_hybrid     # คืนค่าเดิม

    # ---------------------------------------------------------- รายงาน
    columns = ["hit@1", f"hit@{top_k}", "mrr", "ndcg@3"]

    print("\n=== ภาพรวม (ทุกรูปแบบคำถาม) ===")
    print_table({name: r["overall"] for name, r in results.items()}, columns)

    for variant in VARIANTS:
        rows = {name: r["by_variant"].get(variant, {}) for name, r in results.items()}
        if any(rows.values()):
            print(f"\n=== รูปแบบ: {variant} ===")
            print_table(rows, columns)

    print("\n=== ความเร็ว ===")
    for name, report in results.items():
        print(f"  {name:16s} {report['ms_per_query']:8.1f} ms ต่อคำถาม")

    baseline = results["dense_only"]["overall"]["mrr"]
    best_name = max(results, key=lambda n: results[n]["overall"]["mrr"])
    best = results[best_name]["overall"]["mrr"]
    if best_name != "dense_only" and baseline > 0:
        change = (best - baseline) / baseline * 100
        print(f"\nดีที่สุด: {best_name} — MRR {best:.4f}")
        print(f"เทียบกับ dense_only {baseline:.4f}  ({change:+.1f}%)")

    if all_misses:
        print(f"\n=== ตัวอย่างที่ค้นไม่เจอ (รูปแบบ natural) ===")
        for item_id, query, expected, found in all_misses[:5]:
            print(f"  {item_id}: {query[:55]}")
            print(f"      ควรได้ {expected} | ได้ {found}")

    with open(config.EVAL_RETRIEVAL_FILE, "w", encoding="utf-8") as f:
        json.dump({"n_items": len(items), "results": results}, f,
                  ensure_ascii=False, indent=2)
    print(f"\nบันทึกรายงานที่ {config.EVAL_RETRIEVAL_FILE}")


if __name__ == "__main__":
    main()
