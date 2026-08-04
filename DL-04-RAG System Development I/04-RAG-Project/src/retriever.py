

# Perform dense retrieval using a FAISS vector database.
#
# Pipeline:
# Query → Embedding → FAISS Search → Retrieved Chunks
#
# This is the simplest retrieval method and serves as the baseline.
# Useful for understanding dense retrieval and comparing with hybrid retrieval.
#
# Usage:
# for chunk in Retriever().retrieve("What should I do if a condom breaks?"):
#     print(chunk["score"], chunk["question"])


import config
from src.embedding_model import EmbeddingModel
from src.vector_store import VectorStore, load_chunk_store


class Retriever:
    def __init__(self):
        self.model = EmbeddingModel()
        self.store = VectorStore()
        self.store.load(config.FAISS_INDEX_FILE)
        self.chunks = load_chunk_store(config.CHUNK_STORE_FILE)

    def retrieve(self, query, top_k=config.TOP_K):
        """คืน chunk ที่ใกล้เคียงคำถามที่สุด top_k ชิ้น พร้อมคะแนน"""
        # 1. แปลงคำถามเป็นเวกเตอร์
        query_vector = self.model.encode_query(query)

        # 2. ให้ FAISS หาเวกเตอร์ที่ใกล้ที่สุด
        hits = self.store.search(query_vector, top_k)

        # 3. แปลงตำแหน่งที่ FAISS คืนมา กลับเป็นเนื้อหา chunk
        results = []
        for position, score in hits:
            chunk = dict(self.chunks[position])
            chunk["score"] = score
            results.append(chunk)
        return results
