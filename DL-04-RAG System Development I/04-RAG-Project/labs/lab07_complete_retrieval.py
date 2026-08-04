# LAB 7: Combine query embedding, FAISS search, and answer retrieval into one pipeline.
# Test multiple queries and save the results to outputs/retrieval_results.json.
# Run: python labs/lab07_complete_retrieval.py




import json
import os
import sys

# ให้ import config และ src ได้ ไม่ว่าจะรันจากโฟลเดอร์ไหน
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from src.retriever import Retriever

# Questions for testing the retrieval system 
# (covering multiple categories in the data) 
SAMPLE_QUERIES = [
    "ถุงยางอนามัยแตกต้องทำยังไง",
    "PrEP กับ PEP ต่างกันยังไง",
    "ควรตรวจโรคติดต่อทางเพศสัมพันธ์บ่อยแค่ไหน",
    "ความยินยอมในเรื่องเพศคืออะไร",
]

def main():
    print("Lab 7: Complete retrieval pipeline")

    retriever = Retriever()

    all_results = []

    for query in SAMPLE_QUERIES:
        print(f"\nQuery: {query}")
        results = retriever.retrieve(query, top_k=config.TOP_K)

        for rank, item in enumerate(results, start=1):
            print(f"  [{rank}] ({item['score']:.4f}) {item['question']}")

        all_results.append({
            "query": query,
            "results": results,
        })

    with open(config.RETRIEVAL_RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    print(f"\nSaved all results to: {config.RETRIEVAL_RESULTS_FILE}")


if __name__ == "__main__":
    main()
