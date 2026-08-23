# -*- coding: utf-8 -*-
# Problem 05: Similarity Search returns a document with the right content but wrong Metadata (register/tone)
# Uses real data from sex_q_a.txt, which has formal/casual/slang variants
from data_loader import load_qa

QUERY = "ถุงยาง หลุด ทำไง"


def score(query, text):
    return sum(word in text for word in query.split())


def search(data, query, lang=None):
    docs = data if lang is None else [d for d in data if d["lang"] == lang]
    return max(docs, key=lambda d: score(query, d["question"] + " " + d["answer"]))


def run():
    data = load_qa()

    bad = search(data, QUERY)
    good = search(data, QUERY, lang="ทางการ")

    print("Query:", QUERY)
    print("\nWithout filtering by Metadata (lang) -> picks the document with the most keyword matches, ignoring tone:")
    print(f"  [{bad['lang']}] {bad['question']}")

    print("\nFilter lang='ทางการ' (want a formal-tone answer for a clinical chatbot):")
    print(f"  [{good['lang']}] {good['question']}")

    print("\nCause: Keyword/Semantic Similarity picks the document with the most matching words")
    print("but does not guarantee the document has the correct Metadata (e.g. register/tone) the system needs")
