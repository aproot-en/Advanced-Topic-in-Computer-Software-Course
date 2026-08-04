

# LAB 2: Split the extracted Q&A pairs into text chunks.
# Save the results to outputs/chunks.json.
# Run: python labs/lab02_chunking.py



import json
import os
import sys

# ให้ import config และ src ได้ ไม่ว่าจะรันจากโฟลเดอร์ไหน
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from src.text_splitter import build_chunks


def main():
    print("=== Lab 2: Chunking ===")
    print(f"Reading file: {config.EXTRACTED_TEXT_FILE}")

    with open(config.EXTRACTED_TEXT_FILE, "r", encoding="utf-8") as f:
        records = json.load(f)

    chunks = build_chunks(records, config.CHUNK_SIZE, config.CHUNK_OVERLAP)
    print(f"Found a total of {len(chunks)} chunks from {len(records)} question-answer pairs")

    with open(config.CHUNKS_FILE, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

    print(f"Results saved to: {config.CHUNKS_FILE}")

    print("\nSample chunk:")
    print(f"  {chunks[0]['text'][:100]}...")


if __name__ == "__main__":
    main()
