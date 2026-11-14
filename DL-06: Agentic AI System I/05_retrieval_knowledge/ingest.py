### ingest.py - 05 ingestion pipeline (run again when documents change)
### Steps: load -> clean -> chunk -> embed -> save index with metadata
### Run: python ingest.py

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "09_backend"))
import setup_path  ### add folders 02-09 to sys.path (must come first)
import json
import re
import torch
from tqdm import tqdm

import config
import embedder
from thai_text import clean_text, dedup_lines, count_tokens

### leftover UI/web text to remove (e.g. "button on your keyboard.)" from web_app.png)
JUNK_PATTERNS = [r"button on your keyboard", r"click here", r"cookie", r"^menu$", r"^page \d+$",
                 r"^หน้า \d+$", r"คลิกที่นี่"]


def is_junk(line):
    low = line.lower()
    if any(re.search(p, low) for p in JUNK_PATTERNS):
        return True
    ### too short, or less than half real letters = boilerplate
    letters = len(re.findall(r"[\w฀-๿]", line))
    return len(line) < 8 or letters / max(len(line), 1) < 0.5


def clean_lines(lines):
    lines = [clean_text(x) for x in lines]
    lines = [x for x in lines if x and not is_junk(x)]
    return dedup_lines(lines)


def make_chunks(lines):
    ### join lines (articles/paragraphs) into chunks up to CHUNK_SIZE_TOKENS
    ### the last line of a chunk is repeated as overlap
    chunks, current, size = [], [], 0
    for line in lines:
        n = count_tokens(line)
        if current and size + n > config.CHUNK_SIZE_TOKENS:
            chunks.append("\n".join(current))
            last = current[-1]
            current = [last] if count_tokens(last) <= config.CHUNK_OVERLAP_TOKENS else []
            size = sum(count_tokens(x) for x in current)
        current.append(line)
        size += n
    if current:
        chunks.append("\n".join(current))
    return chunks


def build_index():
    ### load all data/kb_*.json (kb_docs = sample rules, kb_curriculum = CPE curriculum)
    docs = []
    for path in sorted(config.KB_DIR.glob("kb_*.json")):
        docs += json.loads(path.read_text(encoding="utf-8"))
    chunks = []
    for doc in docs:
        ### "mixed" = Thai + English text, searchable from both languages
        for lang in ["th", "en", "mixed"]:
            lines = clean_lines(doc.get("text_" + lang, []))
            for i, text in enumerate(make_chunks(lines)):
                chunks.append({
                    "chunk_id": f"{doc['doc_id']}-{lang}-{i}",
                    "text": text,
                    "lang": lang,
                    "metadata": {
                        "doc_id": doc["doc_id"], "title": doc.get("title_" + lang) or doc["title_th"],
                        "source_url": doc["source_url"], "page": doc["page"],
                        "category": doc["category"], "published_at": doc["published_at"],
                        "effective_date": doc["effective_date"], "expired_date": doc["expired_date"],
                        "status": doc["status"], "superseded_by": doc["superseded_by"],
                        "access_level": doc["access_level"], "faculty": doc["faculty"],
                    },
                })

    ### embed in batches (with a progress bar)
    texts = [c["metadata"]["title"] + " " + c["text"] for c in chunks]
    vectors = []
    for i in tqdm(range(0, len(texts), 16), desc="embedding"):
        vectors.append(embedder.encode(texts[i:i + 16]))
    vectors = torch.cat(vectors)

    config.INDEX_DIR.mkdir(exist_ok=True)
    (config.INDEX_DIR / "chunks.json").write_text(
        json.dumps(chunks, ensure_ascii=False, indent=1), encoding="utf-8")
    torch.save({"model": config.EMBEDDING_MODEL, "vectors": vectors},
               config.INDEX_DIR / "embeddings.pt")
    print(f"indexed {len(docs)} documents -> {len(chunks)} chunks, dim={vectors.shape[1]}")


if __name__ == "__main__":
    build_index()
