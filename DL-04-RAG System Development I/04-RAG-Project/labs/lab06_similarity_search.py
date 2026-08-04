# LAB 6: Load the FAISS index and perform similarity search on a sample query.
# Display the top-k most similar chunks.
# Run: python labs/lab06_similarity_search.py



import os
import sys

# ให้ import config และ src ได้ ไม่ว่าจะรันจากโฟลเดอร์ไหน
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from src.embedding_model import EmbeddingModel
from src.vector_store import VectorStore, load_chunk_store


def main():
    print("=== Lab 6: Similarity Search ===")

    model = EmbeddingModel()

    store = VectorStore()
    store.load(config.FAISS_INDEX_FILE)
    chunks = load_chunk_store(config.CHUNK_STORE_FILE)

    query = "ถุงยางอนามัยแตกต้องทำยังไง"
    print(f"Exp Query: {query}")

    query_vector = model.encode_query(query)
    hits = store.search(query_vector, config.TOP_K)

    print(f"\n Results top-{config.TOP_K}:")
    for rank, (idx, score) in enumerate(hits, start=1):
        chunk = chunks[idx]
        print(f"\n[{rank}] Point of Similarity: {score:.4f}")
        print(f"    Category: {chunk['category']}")
        print(f"    Question: {chunk['question']}")
        print(f"    Answer: {chunk['answer'][:150]}...")


if __name__ == "__main__":
    main()
