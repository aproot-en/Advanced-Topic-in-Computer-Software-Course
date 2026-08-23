# -*- coding: utf-8 -*-
# Load and parse sex_q_a.txt into records shared by problem01-10.
#
# File format: each entry is separated by a blank line and has 3 lines
#     [หมวด: <category>]                       or [หมวด: <category> | ภาษา: <variant>]
#     Q: <question>
#     A: <answer>
# Lines starting with # are file header/comments and are skipped.
import os
import re

DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sex_q_a.txt")

_HEADER_RE = re.compile(r"\[หมวด:\s*(.+?)\]")


def load_qa(path=DATA_PATH):
    # Returns a list of dict: id, category, lang, question, answer, text
    with open(path, encoding="utf-8") as f:
        raw = f.read()

    entries = []
    for block in raw.split("\n\n"):
        block = block.strip()
        if not block or block.startswith("#"):
            continue

        lines = block.split("\n")
        if len(lines) < 3:
            continue
        header, q_line, a_line = lines[0], lines[1], lines[2]

        m = _HEADER_RE.match(header)
        if not m:
            continue
        raw_category = m.group(1).strip()

        if "|" in raw_category:
            category, lang = [p.strip() for p in raw_category.split("|", 1)]
            lang = lang.replace("ภาษา:", "").strip()
        else:
            category, lang = raw_category, "ทางการ"

        question = q_line[2:].strip() if q_line.startswith("Q:") else q_line.strip()
        answer = a_line[2:].strip() if a_line.startswith("A:") else a_line.strip()
        if not question or not answer:
            continue

        entries.append({
            "id": len(entries),
            "category": category,
            "lang": lang,
            "question": question,
            "answer": answer,
            "text": f"{question} {answer}",
        })
    return entries


def categories(entries=None):
    entries = entries if entries is not None else load_qa()
    return sorted(set(e["category"] for e in entries))


if __name__ == "__main__":
    data = load_qa()
    print("Total Q&A count:", len(data))
    print("Number of categories (including language variants):", len(categories(data)))
    print("First entry example:", data[0])
