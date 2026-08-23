# -*- coding: utf-8 -*-
# Problem 08: Analyzing the Configuration of a RAG system that uses sex_q_a.txt as its knowledge base
from data_loader import load_qa

CONFIG = {
    "KB_SOURCE": "sex_q_a.txt",
    "USE_HYBRID": True,
    "USE_RERANK": False,
    "USE_MEMORY": True,
    "USE_LLM": True,
    "SHOW_SOURCES": False,
}


def run():
    data = load_qa()
    print("CONFIG =", CONFIG)
    print(f"Loaded Knowledge Base from {CONFIG['KB_SOURCE']}: {len(data)} Q&A entries")
    print("\nPipeline:")

    if CONFIG["USE_MEMORY"]:
        print("1. Using Conversation Memory")

    if CONFIG["USE_HYBRID"]:
        print(f"2. Using BM25 + Dense Retrieval on {len(data)} documents")
    else:
        print(f"2. Using Dense Retrieval on {len(data)} documents")

    if CONFIG["USE_RERANK"]:
        print("3. Performing Re-ranking")
    else:
        print("3. Not performing Re-ranking")

    if CONFIG["USE_LLM"]:
        print("4. Generating the answer with an LLM (grounded in Context from sex_q_a.txt)")

    if CONFIG["SHOW_SOURCES"]:
        print("5. Showing Sources")
    else:
        print("5. Not showing Sources")

    print("\nThe system's behavior results from toggling each Component on/off in the Config")
