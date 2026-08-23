# -*- coding: utf-8 -*-
# Problem 09: CHUNK_SIZE / OVERLAP / EVAL_K_VALUES on real data from sex_q_a.txt
from data_loader import load_qa

CHUNK_SIZE = 400
CHUNK_OVERLAP = 50
EVAL_K_VALUES = [1, 3, 5, 10]


def ranges(total):
    result = []
    step = CHUNK_SIZE - CHUNK_OVERLAP
    start = 0
    while start < total:
        end = min(start + CHUNK_SIZE, total)
        result.append((start, end))
        start += step
    return result


def run():
    data = load_qa()
    full_text = " ".join(d["text"] for d in data)
    total_chars = len(full_text)

    r = ranges(total_chars)
    print(f"Real document from sex_q_a.txt is {total_chars} characters long ({len(data)} Q&A)")
    print(f"Number of chunks produced (CHUNK_SIZE={CHUNK_SIZE}, OVERLAP={CHUNK_OVERLAP}):", len(r))
    print("First few chunk ranges:")
    for x in r[:5]:
        print(x)

    print("\nOverlap Chunk 1/2 =", r[0][1] - r[1][0])

    print("\nRetrieval Evaluation:")
    print("Golden Set =", len(data), "(uses every question in sex_q_a.txt as the test set)")
    for k in EVAL_K_VALUES:
        print(f"Check whether the Relevant Document appears within Top-{k}")

    print("\nExample:")
    print("Relevant Document is at Rank 8")
    print("Top-5 = not found, Top-10 = found")
    print("This means the Retriever can find the document, but the ranking is not yet good at the top")
