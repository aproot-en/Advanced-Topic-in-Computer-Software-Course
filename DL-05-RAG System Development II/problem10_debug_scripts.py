# -*- coding: utf-8 -*-
# Problem 10: Debugging the RAG Pipeline from a script (uses sex_q_a.txt as the source data)
from data_loader import load_qa

PIPELINE = [
    ("data_loader.py::load_qa", "Extract Text from sex_q_a.txt"),
    ("lab02_chunking.py", "Chunking"),
    ("lab03_create_embeddings.py", "Document Embedding"),
    ("lab04_create_vector_db.py", "Vector Database / Index"),
    ("lab05_query_embedding.py", "Query Embedding"),
    ("lab06_similarity_search.py", "Similarity Search"),
    ("lab07_complete_retrieval.py", "Complete Retrieval"),
]

PROBLEMS = {
    "sex_q_a.txt has data but fails to parse (wrong format)": "data_loader.py::load_qa",
    "Text is split at the wrong context boundaries": "lab02_chunking.py",
    "Chunk has no Vector": "lab03_create_embeddings.py",
    "Embedding exists but there is no Index": "lab04_create_vector_db.py",
    "Query is still plain text": "lab05_query_embedding.py",
    "Vector DB has data but the search finds nothing": "lab06_similarity_search.py",
}


def run():
    print("RAG Pipeline:")
    for i, (script, job) in enumerate(PIPELINE, 1):
        print(f"{i}. {script:<30} {job}")

    data = load_qa()
    print(f"\nVerifying Stage 1 (Extract Text) for real: loaded {len(data)} Q&A entries from sex_q_a.txt")
    if len(data) == 0:
        print("!! Stage 1 failed: check the path/format of sex_q_a.txt")

    print("\nDebug examples:")
    for symptom, script in PROBLEMS.items():
        print(f"- {symptom}")
        print(f"  -> Check {script}")

    print("\nPrinciple: Debug from the earliest stage toward the final stage")
