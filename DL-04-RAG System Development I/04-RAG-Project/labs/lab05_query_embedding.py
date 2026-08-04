


# LAB 5: Convert a user query into an embedding vector using the model from LAB 3.
# Display the generated embedding vector.
# Run: python labs/lab05_query_embedding.py



import os
import sys

# ให้ import config และ src ได้ ไม่ว่าจะรันจากโฟลเดอร์ไหน
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from src.embedding_model import EmbeddingModel


def main():
    print("Lab 5: Query Embedding")

    model = EmbeddingModel()

    query = "ถุงยางอนามัยแตกต้องทำยังไง"
    print(f" Exp Query: {query}")

    query_vector = model.encode_query(query)
    print(f"Found query vector of size: {query_vector.shape} dimensions")
    print(f"Example of first 5 numerical values: {query_vector[:5]}")


if __name__ == "__main__":
    main()
