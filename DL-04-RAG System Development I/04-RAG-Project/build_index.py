# build_index.py
# Build the search index from the source dataset.
# Run this script whenever the dataset or embedding settings change.




import json
import time

import numpy as np

import config
from src import index_meta
from src.document_loader import load_qa_file
from src.embedding_model import EmbeddingModel
from src.hybrid_retriever import build_bm25, save_bm25
from src.text_splitter import build_chunks
from src.vector_store import VectorStore, save_chunk_store



def main():
    print("--" * 30)
    print("Build Index")
    print("--" * 30)
    print(f"Source file : {config.SOURCE_FILE}")
    print(f"Model       : {config.EMBEDDING_MODEL_NAME}")
    print(f"Chunk size  : {config.CHUNK_SIZE} characters (overlap {config.CHUNK_OVERLAP})")
    print()

    start_time = time.time()

    # Step 1: Load the Q&A dataset
    records = load_qa_file(config.SOURCE_FILE)

    if not records:
        print("No Q&A pairs found. The dataset format may be incorrect.")
        print("Expected format:")
        print("    [Category: Category Name]")
        print("    Q: Question")
        print("    A: Answer")
        return

    save_json(records, config.EXTRACTED_TEXT_FILE)
    #print(f"[1/5] Loaded {len(records)} Q&A pairs")

    # Step 2: Split long answers into smaller chunks
    chunks = build_chunks(records, config.CHUNK_SIZE, config.CHUNK_OVERLAP)
    save_json(chunks, config.CHUNKS_FILE)
    #print(f"[2/5] Created {len(chunks)} chunks")

    # Step 3: Generate embedding vectors (slowest step)
    texts = [chunk["text"] for chunk in chunks]
    embeddings = EmbeddingModel().encode(texts)
    np.save(config.EMBEDDINGS_FILE, embeddings)
    #print(f"[3/5] Generated {embeddings.shape[0]} vectors × {embeddings.shape[1]} dimensions")

    # FAISS returns the index position, which maps to chunks[i]
    # Stop if the number of vectors and chunks does not match.
    if len(embeddings) != len(chunks):
        print(f"Error: {len(embeddings)} vectors but {len(chunks)} chunks")
        return

    # Step 4: Build the FAISS index (semantic search)
    store = VectorStore()
    store.build(embeddings)
    store.save(config.FAISS_INDEX_FILE)
    save_chunk_store(chunks, config.CHUNK_STORE_FILE)
    #print("[4/5] FAISS index created")

    # Step 5: Build the BM25 index (keyword search)
    save_bm25(build_bm25(chunks))
    #print("[5/5] BM25 index created")

    # Save metadata for index validation
    index_meta.save(len(chunks))

    #print()
    #print(f"Completed in {time.time() - start_time:.1f} seconds")
    #print("Next step: python main.py")


def save_json(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()

