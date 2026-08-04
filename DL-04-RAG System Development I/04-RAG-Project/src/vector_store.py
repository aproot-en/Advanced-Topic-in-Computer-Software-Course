

# Store and search embedding vectors using FAISS.
# IndexFlatIP uses inner product to compare normalized vectors.
# With normalized embeddings, inner product is equal to cosine similarity.
# Higher scores indicate more similar vectors.


import json

import faiss
import numpy as np


class VectorStore:
    def __init__(self):
        self.index = None

    def build(self, embeddings):
        """สร้าง index ใหม่จากเวกเตอร์ทั้งหมด (numpy array 2 มิติ)"""
        embeddings = np.asarray(embeddings, dtype="float32")
        n_vectors, n_dimensions = embeddings.shape

        self.index = faiss.IndexFlatIP(n_dimensions)
        self.index.add(embeddings)
        return self

    def save(self, path):
        faiss.write_index(self.index, path)
        print(f"[vector_store] บันทึก index ที่ {path}")

    def load(self, path):
        self.index = faiss.read_index(path)
        return self

    def search(self, query_vector, top_k):
# Find the top_k vectors most similar to the query vector.
# Returns a list of (index, score) pairs sorted by similarity.
# The index maps directly to the corresponding chunk in chunk_store.


        # FAISS รับข้อมูลเป็น 2 มิติเสมอ จึงต้องครอบ [ ] ให้กลายเป็น 1 แถว
        query_vector = np.asarray([query_vector], dtype="float32")
        scores, positions = self.index.search(query_vector, top_k)

        results = []
        for position, score in zip(positions[0], scores[0]):
            if position != -1:      # -1 = FAISS หาไม่เจอ (เกิดเมื่อ index เล็กกว่า top_k)
                results.append((int(position), float(score)))
        return results


def save_chunk_store(chunks, path):
    """บันทึกเนื้อหา chunk ทั้งหมด — ลำดับต้องตรงกับ index เป๊ะ ๆ"""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    print(f"[vector_store] บันทึก chunk store ที่ {path}")


def load_chunk_store(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
