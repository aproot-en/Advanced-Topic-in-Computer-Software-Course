# LAB 3: Generate embedding vectors from outputs/chunks.json.
# Save the embeddings to outputs/embeddings.npy.
# Run: python labs/lab03_create_embeddings.py



import json
import os
import sys

import numpy as np

# ให้ import config และ src ได้ ไม่ว่าจะรันจากโฟลเดอร์ไหน
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from src.embedding_model import EmbeddingModel


def main():
    print("=== Lab 3: Create Embeddings ===")
    print(f"Reading file: {config.CHUNKS_FILE}")

    with open(config.CHUNKS_FILE, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    texts = [chunk["text"] for chunk in chunks]

    model = EmbeddingModel()
    embeddings = model.encode(texts)

    print(f"Found embeddings of size: {embeddings.shape}  (number of chunks, \
          number of dimensions)")

    np.save(config.EMBEDDINGS_FILE, embeddings)
    print(f"Results saved to: {config.EMBEDDINGS_FILE}")


if __name__ == "__main__":
    main()
