


# Combine BM25 keyword search and dense retrieval using Reciprocal Rank Fusion (RRF).
# Hybrid retrieval improves both keyword matching and semantic search.
# Supports optional reranking for higher retrieval accuracy.
# Enable or disable features in config.py.



import os
import pickle
import re

from rank_bm25 import BM25Okapi

import config
from src.embedding_model import EmbeddingModel
from src.vector_store import VectorStore, load_chunk_store


#step 1: ตัดคำภาษาไทย
# Thai text has no spaces between words, so split() does not work.
# Tokenize the text with PyThaiNLP before building the BM25 index.
# This enables accurate keyword matching.

THAI_PATTERN = re.compile(r"[ก-๙]+")            # ตัวอักษรไทยติดกัน
ENGLISH_PATTERN = re.compile(r"[A-Za-z0-9]+")   # คำอังกฤษหรือตัวเลข


def tokenize(text):
# Tokenize text for BM25.
# Convert English words to lowercase for case-insensitive matching.
# Example: "PrEP กับ PEP ต่างกันยังไง" → ['prep', 'pep', 'กับ', 'ต่างกัน', 'ยังไง']

    tokens = []

    # คำอังกฤษ / ตัวเลข — เก็บทั้งคำ
    for match in ENGLISH_PATTERN.finditer(text):
        tokens.append(match.group().lower())

    # คำไทย — ต้องตัดคำก่อน
    for thai_text in THAI_PATTERN.findall(text):
        tokens.extend(tokenize_thai(thai_text))

    return tokens


def tokenize_thai(text):  #ตัดคำไทยด้วย pythainlp ถ้าไม่ได้ติดตั้งไว้ จะใช้วิธีสำรองที่คุณภาพแย่กว่า
    try:
        from pythainlp.tokenize import word_tokenize

        return [word for word in word_tokenize(text, engine="newmm") if word.strip()]
    except ImportError:
        # วิธีสำรอง: ตัดทีละ 3 ตัวอักษรแบบเหลื่อมกัน ("สวัสดี" → สวั, วัส, ัสด, สดี)
        # ใช้ได้แต่แย่กว่าชัดเจน — แนะนำให้ pip install pythainlp
        return [text[i:i + 3] for i in range(max(1, len(text) - 2))]


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


# Step 3: RRF — รวมผลจากหลายวิธี
def reciprocal_rank_fusion(ranked_lists):
# Merge multiple ranked lists into a single ranking.
# Uses Reciprocal Rank Fusion (RRF) to combine retrieval results.
# Higher-ranked items receive higher scores.
# Items found by multiple methods receive a score boost.
# Example: 
# Dense=[12,5,88], 
# BM25=[5,300,12] → 5 ranks above 12.

    scores = {}
    for ranked in ranked_lists:
        for rank, position in enumerate(ranked, start=1):
            scores[position] = scores.get(position, 0.0) + 1.0 / (config.RRF_K + rank)

    # เรียงจากคะแนนมากไปน้อย
    return sorted(scores.items(), key=lambda item: item[1], reverse=True)


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

        # get_scores คืนคะแนนของ "ทุก chunk" มา ต้องเรียงเองแล้วตัดเอา top_k
        all_scores = self.bm25.get_scores(tokenize(query))
        best_positions = sorted(
            range(len(all_scores)),
            key=lambda i: all_scores[i],
            reverse=True,
        )[:top_k]

        return [(position, float(all_scores[position])) for position in best_positions]



# Retrieve the top_k most relevant chunks.
# extra_queries contains alternative query versions from query transformation.
# Each query is searched separately.
# The results are combined using Reciprocal Rank Fusion (RRF).

    def retrieve(self, query, top_k=config.TOP_K, extra_queries=None):

        queries = [query] + list(extra_queries or [])

        # ค้นด้วยทุกวิธี เก็บเป็นรายการอันดับ 
        ranked_lists = []
        dense_scores = {}
        bm25_scores = {}

        for one_query in queries:
            dense_hits = self.dense_search(one_query, config.CANDIDATE_K)
            ranked_lists.append([position for position, _ in dense_hits])
            dense_scores.update(dense_hits)

            if config.USE_HYBRID:
                bm25_hits = self.bm25_search(one_query, config.CANDIDATE_K)
                ranked_lists.append([position for position, _ in bm25_hits])
                bm25_scores.update(bm25_hits)

        # รวมอันดับด้วย RRF 
        fused = reciprocal_rank_fusion(ranked_lists)

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


