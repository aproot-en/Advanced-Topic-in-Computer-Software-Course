# -*- coding: utf-8 -*-
# Problem 04: Chunk too large / too small / Overlap
# Uses real content (combined answers from a category) from sex_q_a.txt
from data_loader import load_qa

CATEGORY = "สุขภาพทางเพศและการป้องกัน"


def chunk(words, size, overlap=0):
    step = size - overlap
    return [" ".join(words[i:i + size]) for i in range(0, len(words), step)]


def run():
    data = load_qa()
    doc = " ".join(d["answer"] for d in data if d["category"] == CATEGORY and d["lang"] == "ทางการ")
    words = doc.split()

    print(f"Sample document: combined answers from category '{CATEGORY}' ({len(words)} words)")

    print("\nLarge chunk (size=200):")
    for c in chunk(words, 200)[:2]:
        print("-", c[:150] + "...")

    print("\nSmall chunk (size=15):")
    for c in chunk(words, 15)[:5]:
        print("-", c)

    print("\nChunk + Overlap (size=60, overlap=15):")
    for c in chunk(words, 60, 15)[:3]:
        print("-", c[:120] + "...")

    print("\nCause:")
    print("- Too large: multiple Q&A pairs get mixed into a single chunk, diluting the Embedding")
    print("- Too small: an explanation may be cut off mid-sentence, losing context")
    print("- Overlap: preserves context at the boundary between chunks")
