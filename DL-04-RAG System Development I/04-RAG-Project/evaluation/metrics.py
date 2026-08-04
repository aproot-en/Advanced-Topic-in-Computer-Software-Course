

# metrics.py
# Retrieval evaluation metrics implemented from scratch for clarity.
#
# Each function takes:
#     retrieved   A ranked list of retrieved chunk IDs.
#     relevant    The correct chunk ID(s) from the golden set.
#
# Metric definitions:
#     Hit@k        Whether a relevant chunk appears in the top-k results.
#     Recall@k     Percentage of all relevant chunks retrieved.
#     Precision@k  Percentage of retrieved chunks that are relevant.
#     MRR          Reciprocal rank of the first relevant chunk.
#     nDCG@k       Ranking quality with position-based discounting.
#
# nDCG@k is recommended as the overall retrieval metric.


import math


def hit_at_k(retrieved, relevant, k):
    """1.0 ถ้ามีชิ้นถูกอยู่ใน top-k"""
    return 1.0 if set(relevant) & set(retrieved[:k]) else 0.0


def recall_at_k(retrieved, relevant, k):
    """สัดส่วนของชิ้นถูกทั้งหมด ที่เจอใน top-k"""
    if not relevant:
        return 0.0
    return len(set(relevant) & set(retrieved[:k])) / len(set(relevant))


def precision_at_k(retrieved, relevant, k):
    """สัดส่วนของ top-k ที่เป็นชิ้นถูก"""
    return len(set(relevant) & set(retrieved[:k])) / k if k else 0.0


def reciprocal_rank(retrieved, relevant):
    """1/อันดับของชิ้นถูกชิ้นแรก (0 ถ้าไม่เจอเลย)"""
    for rank, doc_id in enumerate(retrieved, start=1):
        if doc_id in set(relevant):
            return 1.0 / rank
    return 0.0


def ndcg_at_k(retrieved, relevant, k):
    """DCG หารด้วย DCG ที่ดีที่สุดที่เป็นไปได้ — เทียบข้ามคำถามได้"""
    relevant = set(relevant)
    if not relevant:
        return 0.0

    dcg = sum(
        1.0 / math.log2(rank + 1)
        for rank, doc_id in enumerate(retrieved[:k], start=1)
        if doc_id in relevant
    )
    ideal = sum(1.0 / math.log2(i + 1) for i in range(1, min(len(relevant), k) + 1))
    return dcg / ideal if ideal else 0.0


def evaluate_one(retrieved, relevant, k_values):
    """คำนวณทุกตัววัดสำหรับคำถามเดียว"""
    scores = {"mrr": reciprocal_rank(retrieved, relevant)}
    for k in k_values:
        scores[f"hit@{k}"] = hit_at_k(retrieved, relevant, k)
        scores[f"recall@{k}"] = recall_at_k(retrieved, relevant, k)
        scores[f"precision@{k}"] = precision_at_k(retrieved, relevant, k)
        scores[f"ndcg@{k}"] = ndcg_at_k(retrieved, relevant, k)
    return scores


def average(rows):
    """เฉลี่ยข้ามคำถาม (ทุกคำถามน้ำหนักเท่ากัน)"""
    if not rows:
        return {}
    return {
        key: round(sum(r.get(key, 0.0) for r in rows) / len(rows), 4)
        for key in rows[0]
    }


def print_table(results, metrics):
    """แสดง {ชื่อการทดลอง: คะแนน} เป็นตารางเทียบกัน"""
    if not results:
        return
    name_width = max(len(n) for n in results) + 2
    widths = [max(11, len(m) + 2) for m in metrics]

    header = "run".ljust(name_width) + "".join(m.rjust(w) for m, w in zip(metrics, widths))
    print(header)
    print("-" * len(header))
    for name, scores in results.items():
        row = name.ljust(name_width)
        row += "".join(f"{scores.get(m, 0.0):{w}.4f}" for m, w in zip(metrics, widths))
        print(row)


if __name__ == "__main__":
    # python -m evaluation.metrics — ตรวจสูตรด้วยค่าที่คำนวณมือไว้แล้ว
    retrieved, relevant = [5, 12, 3, 99, 7], [3, 7]

    assert hit_at_k(retrieved, relevant, 1) == 0.0
    assert hit_at_k(retrieved, relevant, 3) == 1.0
    assert recall_at_k(retrieved, relevant, 5) == 1.0
    assert precision_at_k(retrieved, relevant, 5) == 0.4
    assert abs(reciprocal_rank(retrieved, relevant) - 1 / 3) < 1e-9
    assert abs(ndcg_at_k([3, 7], [3, 7], 2) - 1.0) < 1e-9

    print("ตรวจสูตรผ่านทั้งหมด\n")
    for key, value in evaluate_one(retrieved, relevant, [1, 3, 5]).items():
        print(f"  {key:14s} {value:.4f}")
