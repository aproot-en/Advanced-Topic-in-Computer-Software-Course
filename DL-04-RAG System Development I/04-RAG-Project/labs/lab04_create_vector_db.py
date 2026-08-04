# LAB 4: Build a vector database from the embedding vectors generated in LAB 3.
# Create the FAISS index and chunk store (metadata) for retrieval.
# Save the results to vector_db/document.index and vector_db/chunk_store.json.
# Run: python labs/lab04_create_vector_db.py



import json
import os
import sys

import numpy as np

# ให้ import config และ src ได้ ไม่ว่าจะรันจากโฟลเดอร์ไหน
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from src.vector_store import VectorStore, save_chunk_store


def main():
    print("=== Lab 4: Create Vector Database ===")

    embeddings = np.load(config.EMBEDDINGS_FILE)
    with open(config.CHUNKS_FILE, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    print(f"Vector Number: {len(embeddings)}, Number of chunks: {len(chunks)}")
    assert len(embeddings) == len(chunks), "Vector Number and chunk Number must be equal"

    store = VectorStore()
    store.build(embeddings)
    store.save(config.FAISS_INDEX_FILE)

    save_chunk_store(chunks, config.CHUNK_STORE_FILE)

    print("Vector database created successfully")

if __name__ == "__main__":
    main()
