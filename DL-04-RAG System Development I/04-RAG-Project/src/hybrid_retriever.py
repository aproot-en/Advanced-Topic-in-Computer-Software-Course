


# Combine BM25 keyword search and dense retrieval using Reciprocal Rank Fusion (RRF).
# Hybrid retrieval improves both keyword matching and semantic search.
# Supports optional reranking for higher retrieval accuracy.
# Enable or disable features in config.py.



import os
import pickle

from rank_bm25 import BM25Okapi

import config
from src.embedding_model import EmbeddingModel
from src.retrieval_utils import (
    reciprocal_rank_fusion,
    tokenize,
    top_positive_scores,
)
from src.vector_store import VectorStore, load_chunk_store


# Step 2: BM25 
def build_bm25(chunks):
    """สร้าง BM25 index จาก chunk ทั้งหมด (ใช้ไลบรารี rank_bm25)"""
    corpus = []
    for chunk in chunks:
        # ใส่คำถามซ้ำ 2 ครั้ง เพราะผู้ใช้พิมพ์คำถามมา
        # การตรงกับ "คำถาม" จึงเป็นสัญญาณที่ดีกว่าการตรงกับ "คำตอบ"
        text = f"{chunk['question']} {chunk['question']} {chunk['text']}"
        corpus.append(tokenize(text))

    print(f"[hybrid] สร้าง BM25 index จาก {len(corpus)} chunks")
    return BM25Okapi(corpus)


def save_bm25(bm25):
    with open(config.BM25_INDEX_FILE, "wb") as f:
        pickle.dump(bm25, f)
    print(f"[hybrid] บันทึก BM25 index ที่ {config.BM25_INDEX_FILE}")


def load_bm25(chunks):
    """โหลด index ที่บันทึกไว้ ถ้ายังไม่มีก็สร้างใหม่ให้เลย"""
    if os.path.exists(config.BM25_INDEX_FILE):
        with open(config.BM25_INDEX_FILE, "rb") as f:
            return pickle.load(f)

    bm25 = build_bm25(chunks)
    save_bm25(bm25)
    return bm25


# Step 4: The Retriever

class HybridRetriever:
    def __init__(self, reranker=None):
        self.chunks = load_chunk_store(config.CHUNK_STORE_FILE)
        self.model = EmbeddingModel()
        self.store = VectorStore()
        self.store.load(config.FAISS_INDEX_FILE)
        self.reranker = reranker

        # โหลด BM25 เฉพาะเมื่อเปิดใช้
        self.bm25 = load_bm25(self.chunks) if config.USE_HYBRID else None

    def dense_search(self, query, top_k):  # ค้นด้วยความหมาย — คืน
        
        query_vector = self.model.encode_query(query)
        return self.store.search(query_vector, top_k)

    def bm25_search(self, query, top_k):  # ค้นด้วยคำตรงตัว — คืน [(ตำแหน่ง, คะแนน),
        if self.bm25 is None:
            return []

        # คะแนนศูนย์หมายถึงไม่มีคำตรงกัน จึงไม่ควรได้รับอันดับ RRF เหมือนผลจริง
        all_scores = self.bm25.get_scores(tokenize(query))
        return top_positive_scores(all_scores, top_k)



# Retrieve the top_k most relevant chunks.
# extra_queries contains alternative query versions from query transformation.
# Each query is searched separately.
# The results are combined using Reciprocal Rank Fusion (RRF).

    def retrieve(self, query, top_k=config.TOP_K, extra_queries=None):

        queries = [query] + list(extra_queries or [])

        # ค้นด้วยทุกวิธี เก็บเป็นรายการอันดับ 
        ranked_lists = []
        rank_weights = []
        dense_scores = {}
        bm25_scores = {}

        for query_index, one_query in enumerate(queries):
            query_weight = 1.0 if query_index == 0 else config.EXTRA_QUERY_RRF_WEIGHT

            dense_hits = self.dense_search(one_query, config.CANDIDATE_K)
            if dense_hits:
                ranked_lists.append([position for position, _ in dense_hits])
                rank_weights.append(config.DENSE_RRF_WEIGHT * query_weight)
                for position, score in dense_hits:
                    dense_scores[position] = max(dense_scores.get(position, score), score)

            if config.USE_HYBRID:
                bm25_hits = self.bm25_search(one_query, config.CANDIDATE_K)
                if bm25_hits:
                    ranked_lists.append([position for position, _ in bm25_hits])
                    rank_weights.append(config.BM25_RRF_WEIGHT * query_weight)
                    for position, score in bm25_hits:
                        bm25_scores[position] = max(bm25_scores.get(position, score), score)

        # รวมอันดับด้วย RRF 
        fused = reciprocal_rank_fusion(ranked_lists, rank_weights)

        # ถ้าจะ rerank ต่อ ต้องส่งผู้เข้ารอบให้มันมากกว่า top_k
        keep = config.CANDIDATE_K if self.reranker else top_k

        # แปลงตำแหน่งกลับเป็นเนื้อหา
        results = []
        for position, score in fused[:keep]:
            chunk = dict(self.chunks[position])
            chunk["score"] = score
            chunk["dense_score"] = dense_scores.get(position)
            chunk["bm25_score"] = bm25_scores.get(position)
            results.append(chunk)

        #  จัดอันดับใหม่
        if self.reranker:
            results = self.reranker.rerank(query, results, top_k)

        return results[:top_k]



# Display dense and BM25 retrieval results before fusion.
# Useful for debugging and comparing retrieval methods.
# Enable only when needed.

    def explain(self, query, top_k=5):

        def describe(hits):
            return [
                (position, round(score, 4), self.chunks[position]["question"][:55])
                for position, score in hits
            ]

        fused = self.retrieve(query, top_k)
        return {
            "dense": describe(self.dense_search(query, top_k)),
            "bm25": describe(self.bm25_search(query, top_k)),
            "fused": [
                (c["chunk_id"], round(c["score"], 5), c["question"][:55]) for c in fused
            ],
        }


