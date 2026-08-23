# -*- coding: utf-8 -*-
# Problem 03: Duplicate / Noise / Broken Text / Normalization
# Simulates the kind of noise commonly seen during scraping/OCR on real questions from sex_q_a.txt
# and also checks for duplicates across the whole real file
import re
from data_loader import load_qa


def make_noisy_samples(data, n=2):
    base = [d["question"] for d in data[:n]]
    raw = []
    for q in base:
        raw.append(q)                                       # original
        raw.append(q)                                        # exact duplicate
        raw.append("   " + q + "   ")                        # extra whitespace
        raw.append(q.replace(" ", "_") + "!!!")               # symbol noise
    raw.append("")                                            # empty row from a broken scrape
    return raw


def normalize(text):
    text = text.lower()
    text = re.sub(r"[_@!\-]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def run():
    data = load_qa()
    raw = make_noisy_samples(data)

    print("Before cleaning (simulated noise on real questions from the KB):")
    for x in raw:
        print(repr(x))

    normalized = [normalize(x) for x in raw if x.strip()]
    unique = list(dict.fromkeys(normalized))

    print("\nAfter Normalization + Deduplication:")
    for x in unique:
        print(repr(x))

    print("\nCount before:", len(raw))
    print("Count after:", len(unique))

    all_q_normalized = [normalize(d["question"]) for d in data]
    dup_count = len(all_q_normalized) - len(set(all_q_normalized))
    print(f"\nChecked the full sex_q_a.txt file ({len(data)} entries): found {dup_count} duplicate question(s) after normalization")
    print("Cause: Duplicates add redundant data, while noise makes text inconsistent enough that the system treats identical entries as different ones")
