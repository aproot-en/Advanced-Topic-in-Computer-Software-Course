# -*- coding: utf-8 -*-
# Problem 06: The Relevant Document ends up ranked near the bottom by First-stage Retrieval
# Uses real data from sex_q_a.txt (sexual health / HIV category)
from data_loader import load_qa

GENERIC_TERMS = ["เอชไอวี", "ตรวจ"]
SPECIFIC_TERMS = ["ฟักตัว", "window"]


def first_stage(doc):
    text = doc["question"] + doc["answer"]
    return sum(t in text for t in GENERIC_TERMS)


def rerank(doc):
    text = doc["question"] + doc["answer"]
    score = first_stage(doc)
    score += sum(3 for t in SPECIFIC_TERMS if t in text)
    return score


def run():
    data = [d for d in load_qa() if d["lang"] == "ทางการ"]

    first = sorted(data, key=first_stage, reverse=True)[:6]
    second = sorted(first, key=rerank, reverse=True)

    print("Before Re-ranking (Top 6 from First-stage: generic terms 'เอชไอวี','ตรวจ'):")
    for d in first:
        print(f"  score={first_stage(d)} | {d['question']}")

    print("\nAfter Re-ranking (extra weight for specific terms, e.g. 'ระยะฟักตัว'):")
    for d in second:
        print(f"  score={rerank(d)} | {d['question']}")

    print("\nCause: First-stage Retrieval weighs generic terms equally, so the document that is most")
    print("specific and best matches the query can end up ranked near the bottom")
    print("Re-ranking uses finer-grained signals to push the relevant document toward the top")
