# rag.py
# Simple Disaster RAG (no vector database, no model download)
#   1) read the documents in knowledge/*.md
#   2) split into chunks by "## ..." headings (never cut an emergency step list)
#   3) count matching words — Thai has no spaces between words, so it is split into character bigrams
#   4) filter by hazard / language / document expiry, and report "not found" when the score is too low

import os
import re
from datetime import date

KNOWLEDGE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "knowledge")
MIN_SCORE = 3.0     # below this score we say "no guidance found"
COLLECTION_VERSION = "kb-2026.11"


def tokenize(text):
    text = text.lower()
    tokens = re.findall(r"[a-z0-9.]+", text)                 # English words / numbers
    for part in re.findall(r"[฀-๿]+", text):        # Thai text
        tokens += [part[i:i + 2] for i in range(len(part) - 1)] or [part]
    return tokens


def load_documents(folder=KNOWLEDGE_DIR):
    chunks = []
    for name in sorted(os.listdir(folder)):
        if not name.endswith(".md"):
            continue
        with open(os.path.join(folder, name), encoding="utf-8") as f:
            text = f.read()
        header, _, body = text.partition("\n## ")
        meta = {}
        for line in header.splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                meta[key.strip()] = value.strip()
        sections = ("## " + body).split("\n## ")
        for i, sec in enumerate(sections):
            sec = sec.lstrip("# ").strip()
            if not sec:
                continue
            heading, _, content = sec.partition("\n")
            lang = "en" if heading.endswith("(en)") else "th"
            chunks.append({
                "evidence_id": f"{name[:-3]}#{i}", "document_id": name[:-3], "title": meta.get("title", name),
                "section": heading.replace("(th)", "").replace("(en)", "").strip(), "text": content.strip(),
                "lang": lang, "authority": meta.get("authority", ""), "url": meta.get("url"),
                "hazards": [h.strip() for h in meta.get("hazards", "").split(",") if h.strip()],
                "effective_date": meta.get("effective_date"), "expiry_date": meta.get("expiry_date"),
            })
    return chunks


class DisasterRAG:
    def __init__(self, folder=KNOWLEDGE_DIR):
        self.chunks = load_documents(folder)
        # a set of words for each chunk, so we can count matching words quickly
        self.words = [set(tokenize(c["section"] + " " + c["text"])) for c in self.chunks]

    def score(self, query_words, chunk_words, chunk, hazards):
        """Score 0-12: share of query words found in the chunk (0-10) + 2 if the hazard type matches."""
        matches = len(query_words & chunk_words)
        score = matches / max(len(query_words), 1) * 10
        if hazards and set(hazards) & set(chunk["hazards"]):
            score += 2.0
        return round(score, 2)

    def search(self, query, hazards=None, lang="th", top_k=3, today=None):
        today = (today or date.today()).isoformat()
        query_words = set(tokenize(query + " " + " ".join(hazards or [])))
        results = []
        for chunk, chunk_words in zip(self.chunks, self.words):
            if chunk["lang"] != lang:
                continue
            if chunk["expiry_date"] and chunk["expiry_date"] < today:
                continue    # expired document, skip
            if chunk["effective_date"] and chunk["effective_date"] > today:
                continue    # not valid yet
            score = self.score(query_words, chunk_words, chunk, hazards)
            if score > 0:
                results.append({**chunk, "score": score})
        results.sort(key=lambda r: -r["score"])
        top = results[:top_k]
        found = len(top) > 0 and top[0]["score"] >= MIN_SCORE
        return {"evidence_found": found, "collection_version": COLLECTION_VERSION, "passages": top}
